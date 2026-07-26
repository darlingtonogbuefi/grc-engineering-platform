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

from .auth import EntraAuthenticator
from .client import EntraClient

logger = logging.getLogger(__name__)


class EntraCollector(BaseCollector):
    """Microsoft Entra evidence collector."""

    def __init__(
        self,
        manifest,
        evidence_writer: Any,
        normalizer: Any,
        validator: Any,
        config: Dict[str, Any] | None = None,
    ):
        config = config or {}

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
            "conditional_access": (
                "/identity/conditionalAccess/policies"
            ),
            "applications": "/applications",
            "service_principals": (
                "/servicePrincipals"
            ),
            "audit_logs": (
                "/auditLogs/directoryAudits"
            ),
            "sign_ins": (
                "/auditLogs/signIns"
            ),
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

        evidence = {}

        for resource, endpoint in discovered.items():
            logger.info(
                "Collecting %s",
                resource,
            )

            evidence[resource] = (
                self.client.get_all_pages(
                    endpoint,
                    token,
                )
            )

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
            logger.exception(
                "Microsoft Graph health check failed"
            )

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
                "authenticated": (
                    self.authenticator.token
                    is not None
                ),
            }
        )

        return metadata
