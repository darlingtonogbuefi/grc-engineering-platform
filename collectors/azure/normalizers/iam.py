"""
Azure IAM Normalizer.

Normalizes Azure identity and access management
evidence into the platform evidence model.

Supported resources:
- Role assignments
- Role definitions
- Managed identities

Does not perform:
- Compliance evaluation
- Access reviews
- Privilege analysis
- Risk scoring
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from collectors.base.normalizer import BaseNormalizer
from collectors.base.models import EvidenceRecord


class IAMNormalizer(BaseNormalizer):
    """Normalize Azure identity and access resources."""

    RESOURCE_TYPES = {
        "role_assignment":
            "azure.iam.role_assignment",

        "role_definition":
            "azure.iam.role_definition",

        "managed_identity":
            "azure.iam.managed_identity",
    }

    def normalize(
        self,
        data: dict[str, Any],
    ) -> list[EvidenceRecord]:
        """
        Convert Azure IAM API responses
        into EvidenceRecord objects.
        """

        records: list[EvidenceRecord] = []

        collected_at = datetime.now(
            timezone.utc
        )

        for item in data.get("value", []):
            item_type = self._detect_type(item)

            resource_id = item.get(
                "id",
                "",
            )

            records.append(
                EvidenceRecord(
                    source="azure",
                    resource_type=self.RESOURCE_TYPES.get(
                        item_type,
                        "azure.iam.unknown",
                    ),
                    resource_id=resource_id,
                    data={
                        "name": self._name(item),
                        "provider": "azure",
                        "service": "identity_access",
                        "subscription_id": self._subscription_id(
                            resource_id
                        ),
                        "resource_group": self._resource_group(
                            resource_id
                        ),
                        "principal_id": item.get(
                            "principalId"
                        ),
                        "principal_type": item.get(
                            "principalType"
                        ),
                        "role_definition_id": item.get(
                            "roleDefinitionId"
                        ),
                        "role_definition_name": item.get(
                            "roleDefinitionName"
                        ),
                        "scope": item.get(
                            "scope"
                        ),
                        "tenant_id": item.get(
                            "tenantId"
                        ),
                        "properties": item.get(
                            "properties",
                            {},
                        ),
                        "raw": item,
                    },
                    collected_at=collected_at,
                    metadata={
                        "collector": "azure",
                        "normalizer": "iam",
                    },
                )
            )

        return records

    def _detect_type(
        self,
        item: dict[str, Any],
    ) -> str:
        """Determine IAM resource type."""

        resource_id = item.get(
            "id",
            "",
        ).lower()

        resource_type = item.get(
            "type",
            "",
        ).lower()

        if "roleassignments" in resource_id:
            return "role_assignment"

        if "roledefinitions" in resource_id:
            return "role_definition"

        if "managedidentities" in resource_id:
            return "managed_identity"

        if "userassignedidentities" in resource_type:
            return "managed_identity"

        return "unknown"

    def _name(
        self,
        item: dict[str, Any],
    ) -> str:
        """Return best available resource name."""

        return (
            item.get("name")
            or item.get("roleDefinitionName")
            or item.get("displayName")
            or ""
        )

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
