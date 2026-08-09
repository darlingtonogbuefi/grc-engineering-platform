# collectors\azure\collector.py


"""
Azure Evidence Collector.

Collects Azure platform evidence based on
configured collection profiles.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from collectors.base.collector import BaseCollector
from collectors.base.loader import load_collector_manifest
from collectors.base.models import EvidenceRecord

from .auth import AzureAuthenticator
from .client import AzureClient
from .evidence import LocalEvidenceWriter
from .normalizers import AzureNormalizer
from .validator import AzureValidator

logger = logging.getLogger(__name__)


class AzureCollector(BaseCollector):
    """Azure evidence collector."""

    def __init__(
        self,
        manifest=None,
        client: AzureClient | None = None,
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
            manifest = load_collector_manifest(
                "collectors/azure/manifest.yml",
            )

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
            normalizer = AzureNormalizer()

        if validator is None:
            validator = AzureValidator()

        #
        # Authentication handling
        #
        # Preserve injected clients for tests and external callers.
        # Mock clients may not expose an authenticator attribute.
        #
        if client is not None:
            self.authenticator = getattr(
                client,
                "authenticator",
                None,
            )

            if self.authenticator is None:
                self.authenticator = AzureAuthenticator(
                    config,
                )

        else:
            self.authenticator = AzureAuthenticator(
                config,
            )

            client = AzureClient(
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

        self.profile = self.config.get(
            "profile",
            "default",
        )

    @property
    def provider(self) -> str:
        """
        Return provider identifier.
        """

        return "azure"

    def authenticate(self) -> None:
        """
        Authenticate to Azure Resource Manager.
        """

        if self.authenticator is None:
            raise RuntimeError(
                "Azure authenticator is not configured",
            )

        self.authenticator.acquire_token()

    def discover(self) -> List[str]:
        """
        Load enabled Azure queries from the
        configured collection profile.
        """

        return self.client.load_profile(
            self.profile,
        )

    def collect(
        self,
        discovered: List[str] | None = None,
        query: str | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute Azure evidence queries.

        Supports both:
        - Production workflow:
            collect(discovered=["resource_groups"])
        - Direct query execution:
            collect(query="resource_groups")
        """

        if discovered is None:
            discovered = self.discover()

        if query is not None:
            discovered = [
                query,
            ]

        token = getattr(
            self.authenticator,
            "token",
            None,
        )

        evidence: List[Dict[str, Any]] = []

        for query_name in discovered:

            logger.info(
                "Collecting Azure evidence",
                extra={
                    "query": query_name,
                    "run_id": self.run_id,
                },
            )

            collected = self.client.execute_query(
                query_name,
                token,
            )

            if collected:
                logger.warning(
                    "QUERY=%s FIRST_ITEM_KEYS=%s",
                    query_name,
                    list(
                        collected[0].keys()
                    ),
                )

            evidence.extend(
                collected,
            )

        return evidence

    def normalize(
        self,
        evidence: List[Dict[str, Any]],
    ) -> List[EvidenceRecord]:
        """
        Convert Azure resources into
        standardized evidence records.

        AzureCollector.collect() returns a flat list
        of ARM resources.

        AzureNormalizer expects resources grouped
        by evidence collection type, so this method
        adapts the shape without changing collection
        behaviour.
        """

        if not evidence:
            return []

        #
        # Preserve compatibility with callers that
        # already provide grouped evidence.
        #
        if isinstance(evidence, dict):
            return self.normalizer.normalize(
                evidence,
            )

        grouped: Dict[str, Dict[str, Any]] = {}

        for resource in evidence:

            resource_type = resource.get(
                "type",
                "",
            )

            if not resource_type:
                continue

            #
            # Match Azure ARM resource types to
            # AzureNormalizer keys.
            #
            if resource_type.startswith(
                "Microsoft.Compute/",
            ):
                key = "virtual_machines"

            elif resource_type.startswith(
                "Microsoft.Storage/",
            ):
                key = "storage_accounts"

            elif resource_type.startswith(
                "Microsoft.Network/",
            ):
                key = "network_security_groups"

            elif resource_type.startswith(
                "Microsoft.Authorization/roleAssignments",
            ):
                key = "role_assignments"

            elif resource_type.startswith(
                "Microsoft.Authorization/roleDefinitions",
            ):
                key = "role_definitions"

            elif resource_type.startswith(
                "Microsoft.KeyVault/",
            ):
                key = "key_vaults"

            elif resource_type.startswith(
                "Microsoft.Security/",
            ):
                key = "security_settings"

            else:
                key = "resources"

            if key not in grouped:
                grouped[key] = {
                    "value": [],
                }

            grouped[key]["value"].append(
                resource,
            )

        return self.normalizer.normalize(
            grouped,
        )

    def health_check(self) -> bool:
        """
        Verify Azure Resource Manager
        connectivity.
        """

        try:
            token = getattr(
                self.authenticator,
                "token",
                None,
            )

            self.client.get(
                "/subscriptions",
                token,
                params={
                    "api-version": self.client.api_version,
                },
            )

            return True

        except Exception:
            logger.exception(
                "Azure Resource Manager health check failed",
            )

            return False

    def metadata(self) -> Dict[str, Any]:
        """
        Return collector metadata.
        """

        metadata = super().metadata()

        metadata.update(
            {
                "api": "Azure Resource Manager",
                "base_url": self.client.BASE_URL,
                "subscription_id": self.client.subscription_id,
                "authenticated": (
                    getattr(
                        self.authenticator,
                        "token",
                        None,
                    )
                    is not None
                ),
            }
        )

        return metadata
