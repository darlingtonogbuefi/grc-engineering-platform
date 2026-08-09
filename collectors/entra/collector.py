# collectors\entra\collector.py


# collectors\entra\collector.py

"""
Microsoft Entra evidence collector.

Coordinates Microsoft Graph authentication
and collection of Microsoft Entra evidence.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from collectors.base.collector import BaseCollector
from collectors.base.exceptions import ClientError
from collectors.base.loader import load_collector_manifest

from .auth import EntraAuthenticator
from .client import EntraClient
from .evidence import LocalEvidenceWriter
from .normalizers import EntraNormalizer
from .validator import EntraValidator

logger = logging.getLogger(__name__)


class EntraCollector(BaseCollector):
    """Microsoft Entra evidence collector."""

    def __init__(
        self,
        manifest=None,
        evidence_writer: Any | None = None,
        normalizer: Any | None = None,
        validator: Any | None = None,
        config: Dict[str, Any] | None = None,
    ):
        config = config or {}

        #
        # Default dependencies
        #
        if manifest is None:
            manifest = load_collector_manifest("collectors/entra/manifest.yml")

        if evidence_writer is None:
            evidence_writer = LocalEvidenceWriter(
                {
                    "storage_path": config.get(
                        "storage_path",
                        "evidence/raw",
                    )
                }
            )

        if normalizer is None:
            normalizer = EntraNormalizer()

        if validator is None:
            validator = EntraValidator()

        self.authenticator = EntraAuthenticator(config)

        client = EntraClient(
            self.authenticator,
            config,
        )

        super().__init__(
            manifest=manifest,
            client=client,
            evidence_writer=evidence_writer,
            normalizer=normalizer,
            validator=validator,
            config=config,
        )

    @property
    def provider(self) -> str:
        """
        Return provider identifier.
        """

        return "entra"

    def authenticate(self) -> None:
        """
        Authenticate to Microsoft Graph.
        """

        self.authenticator.acquire_token()

    def discover(self) -> Dict[str, str]:
        """
        Discover Microsoft Entra resources
        available for collection.

        Returns:
            Dictionary mapping resource names
            to Microsoft Graph endpoints.
        """

        return {
            "users": "/users",
            "groups": "/groups",
            "directory_roles": "/directoryRoles",
            "devices": "/devices",
            "conditional_access": "/identity/conditionalAccess/policies",
            "applications": "/applications",
            "service_principals": "/servicePrincipals",
            "audit_logs": "/auditLogs/directoryAudits",
            "sign_ins": "/auditLogs/signIns",
        }

    def collect(
        self,
        discovered: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Collect Microsoft Entra evidence.

        Coordinates collection but delegates
        all HTTP communication to EntraClient.
        """

        token = self.authenticator.token

        evidence: Dict[str, Any] = {}

        for resource, endpoint in discovered.items():
            logger.info(
                "Collecting %s",
                resource,
            )

            try:
                collected = self.client.get_all_pages(
                    endpoint,
                    token,
                )

            except ClientError as exc:
                logger.warning(
                    "Skipping resource '%s': %s",
                    resource,
                    exc,
                )

                #
                # Continue collecting remaining resources
                # if this endpoint is unavailable due to
                # permissions, licensing, or other Graph
                # API access restrictions.
                #
                evidence[resource] = []

                continue

            #
            # Directory roles require member resolution.
            #
            # Preserve members returned through Graph expansion.
            # Resolve explicitly only when Graph did not provide them.
            #
            if resource == "directory_roles":
                for role in collected:
                    if role.get("members"):
                        continue

                    role_id = role.get("id")

                    if not role_id:
                        role["members"] = []
                        continue

                    try:
                        role["members"] = self.client.get_all_pages(
                            f"/directoryRoles/{role_id}/members",
                            token,
                        )

                    except ClientError:
                        logger.exception(
                            "Failed collecting members for directory role %s",
                            role.get("displayName"),
                        )

                        role["members"] = []

            evidence[resource] = collected

        return evidence

    def health_check(self) -> bool:
        """
        Verify Microsoft Graph connectivity.
        """

        try:
            self.client.get(
                "/organization",
                self.authenticator.token,
            )

            return True

        except Exception:
            logger.exception("Microsoft Graph health check failed")

            return False

    def metadata(self) -> Dict[str, Any]:
        """
        Return collector metadata.
        """

        metadata = super().metadata()

        metadata.update(
            {
                "api": "Microsoft Graph",
                "base_url": self.client.BASE_URL,
                "authenticated": (self.authenticator.token is not None),
            }
        )

        return metadata
