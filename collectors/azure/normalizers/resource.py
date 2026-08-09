"""
Azure Resource Normalizer.

Normalizes generic Azure resources into the
platform evidence model.

This normalizer provides the baseline inventory
representation for all Azure resources.

Specialized normalizers add deeper service-specific
evidence.

Does not perform:
- Compliance evaluation
- Risk scoring
- Framework mappings
"""

from __future__ import annotations

from typing import Any

from collectors.base.normalizer import BaseNormalizer
from collectors.base.models import EvidenceRecord


class ResourceNormalizer(BaseNormalizer):
    """Normalize generic Azure resources."""

    RESOURCE_TYPE = "azure.resource"

    def __init__(self):
        super().__init__("azure")

    def normalize(
        self,
        data: dict[str, Any],
    ) -> list[EvidenceRecord]:
        """
        Convert Azure resource inventory responses
        into EvidenceRecord objects.
        """

        records: list[EvidenceRecord] = []

        for resource in data.get("value", []):

            resource_id = resource.get(
                "id",
                "",
            )

            resource_type = resource.get(
                "type",
                "",
            )

            records.append(
                self.create_record(
                    resource_type=self.RESOURCE_TYPE,
                    resource_id=resource_id,
                    data={
                        "name": resource.get(
                            "name",
                            "",
                        ),
                        "provider": "azure",
                        "service": self._service_name(resource_type),
                        "location": resource.get("location"),
                        "subscription_id": self._subscription_id(resource_id),
                        "resource_group": self._resource_group(resource_id),
                        "azure_type": resource_type,
                        "managed_by": resource.get("managedBy"),
                        "kind": resource.get("kind"),
                        "sku": resource.get("sku"),
                        "tags": resource.get(
                            "tags",
                            {},
                        ),
                        "properties": resource.get(
                            "properties",
                            {},
                        ),
                        "raw": resource,
                    },
                    metadata={
                        "collector": "azure",
                        "normalizer": "resource",
                    },
                )
            )

        self.validate(records)

        return records

    def _service_name(
        self,
        resource_type: str | None,
    ) -> str:
        """
        Extract Azure provider service name.

        Example:

        Microsoft.Compute/virtualMachines

        becomes:

        compute
        """

        if not resource_type:
            return "unknown"

        try:
            provider, _ = resource_type.split(
                "/",
                1,
            )

            return provider.replace(
                "Microsoft.",
                "",
            ).lower()

        except ValueError:
            return "unknown"

    def _subscription_id(
        self,
        resource_id: str,
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
        resource_id: str,
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
