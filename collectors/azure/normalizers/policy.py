"""
Azure Policy Normalizer.

Normalizes Azure Policy governance resources
into the platform evidence model.

Supported resources:
- Policy Definitions
- Policy Assignments
- Policy Set Definitions
- Policy Exemptions

Does not perform:
- Compliance evaluation
- Policy effectiveness checks
- Framework mappings
- Risk scoring
"""

from __future__ import annotations

from typing import Any

from collectors.base.normalizer import BaseNormalizer
from collectors.base.models import EvidenceRecord


class PolicyNormalizer(BaseNormalizer):
    """Normalize Azure Policy resources."""

    RESOURCE_TYPES = {
        "Microsoft.Authorization/policyDefinitions": "azure.policy.definition",
        "Microsoft.Authorization/policySetDefinitions": "azure.policy.initiative",
        "Microsoft.Authorization/policyAssignments": "azure.policy.assignment",
        "Microsoft.Authorization/policyExemptions": "azure.policy.exemption",
    }

    def __init__(self):
        super().__init__("azure")

    def normalize(
        self,
        data: dict[str, Any],
    ) -> list[EvidenceRecord]:
        """
        Convert Azure Policy responses into
        EvidenceRecord objects.
        """

        records: list[EvidenceRecord] = []

        for resource in data.get(
            "value",
            [],
        ):
            azure_type = resource.get("type")

            if azure_type not in self.RESOURCE_TYPES:
                continue

            resource_id = resource.get(
                "id",
                "",
            )

            properties = resource.get(
                "properties",
                {},
            )

            records.append(
                self.create_record(
                    resource_type=self.RESOURCE_TYPES[azure_type],
                    resource_id=resource_id,
                    data={
                        "name": self._name(resource),
                        "provider": "azure",
                        "service": "governance",
                        "location": resource.get("location"),
                        "subscription_id": self._subscription_id(resource_id),
                        "resource_group": self._resource_group(resource_id),
                        "display_name": properties.get("displayName"),
                        "description": properties.get("description"),
                        "policy_type": properties.get("policyType"),
                        "mode": properties.get("mode"),
                        "parameters": properties.get("parameters"),
                        "policy_rule": properties.get("policyRule"),
                        "scope": properties.get("scope"),
                        "enforcement_mode": properties.get("enforcementMode"),
                        "metadata": properties.get("metadata"),
                        "raw": resource,
                    },
                    metadata={
                        "collector": "azure",
                        "normalizer": "policy",
                    },
                )
            )

        self.validate(records)

        return records

    def _name(
        self,
        resource: dict[str, Any],
    ) -> str:
        """Return best available policy name."""

        return (
            resource.get("name")
            or resource.get(
                "properties",
                {},
            ).get("displayName")
            or ""
        )

    def _subscription_id(
        self,
        resource_id: str | None,
    ) -> str | None:
        """Extract subscription ID."""

        if not resource_id:
            return None

        parts = resource_id.split("/")

        try:
            index = parts.index("subscriptions")

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
        """Extract resource group."""

        if not resource_id:
            return None

        parts = resource_id.split("/")

        try:
            index = parts.index("resourceGroups")

            return parts[index + 1]

        except (
            ValueError,
            IndexError,
        ):
            return None
