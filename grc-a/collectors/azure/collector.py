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

        Hybrid collection:
        - Keeps the generic `resources` ARM inventory.
        - Keeps all existing specialized queries.
        - Deduplicates records using the Azure resource ID.
        - Preserves specialized evidence.
        - Preserves records that have no resource ID.
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

        return self._merge_evidence_by_resource_id(
            evidence,
        )


    def _merge_evidence_by_resource_id(
        self,
        evidence: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Merge Azure evidence by resource ID.

        The first record normally comes from the generic ARM
        `resources` query because that query appears early in
        the default profile.

        Later specialized query results are merged into it.

        Therefore:
            generic ARM = broad inventory
            specialized queries = richer evidence

        Specialized values take precedence when the same field
        exists in both records.
        """

        merged: Dict[str, Dict[str, Any]] = {}
        records_without_id: List[Dict[str, Any]] = []

        for resource in evidence:

            if not isinstance(resource, dict):
                continue

            resource_id = resource.get("id")

            #
            # Some evidence may not represent a normal ARM
            # resource and therefore may not have an ID.
            #
            # Preserve it instead of accidentally deleting it.
            #
            if not resource_id:
                records_without_id.append(
                    resource,
                )
                continue

            #
            # Azure resource IDs are treated case-insensitively.
            #
            normalized_id = str(
                resource_id,
            ).lower()

            existing = merged.get(
                normalized_id,
            )

            #
            # First occurrence.
            #
            if existing is None:
                merged[normalized_id] = dict(
                    resource,
                )
                continue

            #
            # Same Azure resource was already discovered.
            #
            # Merge the specialized evidence into the generic
            # ARM record rather than creating a duplicate.
            #
            for key, value in resource.items():

                if (
                    key in existing
                    and isinstance(
                        existing[key],
                        dict,
                    )
                    and isinstance(
                        value,
                        dict,
                    )
                ):
                    #
                    # Preserve nested generic fields while adding
                    # or overriding them with specialized fields.
                    #
                    existing[key] = {
                        **existing[key],
                        **value,
                    }

                else:
                    #
                    # Later/specialized evidence wins.
                    #
                    existing[key] = value

        result = list(
            merged.values(),
        )

        #
        # Evidence without IDs is deliberately retained.
        #
        result.extend(
            records_without_id,
        )

        logger.info(
            "Hybrid Azure evidence merge: "
            "%d input records -> %d resource records "
            "+ %d records without IDs",
            len(evidence),
            len(merged),
            len(records_without_id),
        )

        return result

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
