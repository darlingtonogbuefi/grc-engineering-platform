"""
Azure Storage Normalizer.

Normalizes Azure storage resources into the
platform evidence model.

Supported resources:
- Storage Accounts
- Blob Services
- File Services
- Queue Services
- Table Services

Does not perform:
- Compliance evaluation
- Encryption assessment
- Data classification
- Risk scoring
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from collectors.base.normalizer import BaseNormalizer
from collectors.base.models import EvidenceRecord


class StorageNormalizer(BaseNormalizer):
    """Normalize Azure storage resources."""

    RESOURCE_TYPES = {
        "Microsoft.Storage/storageAccounts":
            "azure.storage.account",

        "Microsoft.Storage/storageAccounts/blobServices":
            "azure.storage.blob_service",

        "Microsoft.Storage/storageAccounts/fileServices":
            "azure.storage.file_service",

        "Microsoft.Storage/storageAccounts/queueServices":
            "azure.storage.queue_service",

        "Microsoft.Storage/storageAccounts/tableServices":
            "azure.storage.table_service",
    }

    def normalize(
        self,
        data: dict[str, Any],
    ) -> list[EvidenceRecord]:
        """
        Convert Azure storage API responses
        into EvidenceRecord objects.
        """

        records: list[EvidenceRecord] = []

        collected_at = datetime.now(
            timezone.utc
        )

        for resource in data.get("value", []):
            azure_type = resource.get("type")

            if azure_type not in self.RESOURCE_TYPES:
                continue

            resource_id = resource.get(
                "id",
                "",
            )

            records.append(
                EvidenceRecord(
                    source="azure",
                    resource_type=self.RESOURCE_TYPES[
                        azure_type
                    ],
                    resource_id=resource_id,
                    data={
                        "name": resource.get(
                            "name",
                            "",
                        ),
                        "provider": "azure",
                        "service": "storage",
                        "location": resource.get(
                            "location"
                        ),
                        "subscription_id": self._subscription_id(
                            resource_id
                        ),
                        "resource_group": self._resource_group(
                            resource_id
                        ),
                        "kind": resource.get(
                            "kind"
                        ),
                        "sku": resource.get(
                            "sku"
                        ),
                        "properties": resource.get(
                            "properties",
                            {},
                        ),
                        "tags": resource.get(
                            "tags",
                            {},
                        ),
                        "raw": resource,
                    },
                    collected_at=collected_at,
                    metadata={
                        "collector": "azure",
                        "normalizer": "storage",
                    },
                )
            )

        return records

    def _subscription_id(
        self,
        resource_id: str | None,
    ) -> str | None:
        """Extract subscription ID from Azure resource ID."""

        if not resource_id:
            return None

        parts = resource_id.split("/")

        try:
            index = parts.index(
                "subscriptions"
            )

            return parts[index + 1]

        except (
            ValueError,
            IndexError,
        ):
            return None

    def _resource_group(
        self,
        resource_id: str | None,
    ) -> str | None:
        """Extract resource group from Azure resource ID."""

        if not resource_id:
            return None

        parts = resource_id.split("/")

        try:
            index = parts.index(
                "resourceGroups"
            )

            return parts[index + 1]

        except (
            ValueError,
            IndexError,
        ):
            return None
