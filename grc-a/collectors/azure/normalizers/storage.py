# collectors\azure\normalizers\storage.py

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

from datetime import UTC, datetime
from typing import Any

from collectors.base.normalizer import BaseNormalizer
from collectors.base.models import EvidenceRecord


class StorageNormalizer(BaseNormalizer):
    """Normalize Azure storage resources."""

    RESOURCE_TYPES = {
        "Microsoft.Storage/storageAccounts": "azure.storage.account",
        "Microsoft.Storage/storageAccounts/blobServices": "azure.storage.blob_service",
        "Microsoft.Storage/storageAccounts/fileServices": "azure.storage.file_service",
        "Microsoft.Storage/storageAccounts/queueServices": "azure.storage.queue_service",
        "Microsoft.Storage/storageAccounts/tableServices": "azure.storage.table_service",
    }

    def __init__(self):
        super().__init__("azure")

    def normalize(
        self,
        data: dict[str, Any],
    ) -> list[EvidenceRecord]:
        """
        Convert Azure storage API responses
        into EvidenceRecord objects.
        """

        records: list[EvidenceRecord] = []

        #
        # Generate one UTC timestamp for the entire
        # normalization run.
        #
        # This represents when the Azure Storage evidence
        # batch was observed/normalized.
        #
        collection_timestamp = datetime.now(
            UTC,
        ).isoformat()

        for resource in data.get(
            "value",
            [],
        ):
            azure_type = resource.get("type")

            if not azure_type:
                continue

            normalized_type = self._resource_type(azure_type)

            if normalized_type is None:
                continue

            resource_id = resource.get(
                "id",
                "",
            )

            records.append(
                self.create_record(
                    resource_type=normalized_type,
                    resource_id=resource_id,
                    data={
                        #
                        # Collection timestamp.
                        #
                        # This is the UTC timestamp for the
                        # live Azure Storage evidence normalization
                        # run. Every record from this collection
                        # run receives the same timestamp.
                        #
                        "timestamp": collection_timestamp,
                        "name": resource.get(
                            "name",
                            "",
                        ),
                        "provider": "azure",
                        "service": "storage",
                        "location": resource.get("location"),
                        "subscription_id": self._subscription_id(resource_id),
                        "resource_group": self._resource_group(resource_id),
                        "kind": resource.get("kind"),
                        "sku": resource.get("sku"),
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
                    metadata={
                        "collector": "azure",
                        "normalizer": "storage",
                    },
                )
            )

        self.validate(records)

        return records

    def _resource_type(
        self,
        azure_type: str | None,
    ) -> str | None:
        """
        Resolve the normalized evidence resource type.

        Azure resource type casing is normally consistent, but
        comparison is made case-insensitive to avoid silently
        dropping valid resources.
        """

        if not azure_type:
            return None

        normalized_azure_type = azure_type.lower()

        for resource_type, evidence_type in self.RESOURCE_TYPES.items():
            if resource_type.lower() == normalized_azure_type:
                return evidence_type

        return None

    def _subscription_id(
        self,
        resource_id: str | None,
    ) -> str | None:
        """Extract subscription ID from Azure resource ID."""

        if not resource_id:
            return None

        parts = resource_id.split("/")

        try:
            index = next(
                index
                for index, part in enumerate(parts)
                if part.lower() == "subscriptions"
            )

            return parts[index + 1]

        except (
            StopIteration,
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
            index = next(
                index
                for index, part in enumerate(parts)
                if part.lower() == "resourcegroups"
            )

            return parts[index + 1]

        except (
            StopIteration,
            IndexError,
        ):
            return None
