# collectors\azure\normalizers\compute.py


"""
Azure Compute Normalizer.

Normalizes Azure compute resources into the platform
evidence model.

Supported resources:
- Virtual Machines
- Virtual Machine Scale Sets
- Managed Disks
- Availability Sets

Does not perform:
- Compliance evaluation
- Security scoring
- Framework mappings
"""

from __future__ import annotations

from typing import Any

from collectors.base.normalizer import BaseNormalizer
from collectors.base.models import EvidenceRecord


class ComputeNormalizer(BaseNormalizer):
    """Normalize Azure compute resources."""

    RESOURCE_TYPES = {
        "Microsoft.Compute/virtualMachines": "azure.compute.virtual_machine",
        "Microsoft.Compute/virtualMachineScaleSets": "azure.compute.vm_scale_set",
        "Microsoft.Compute/disks": "azure.compute.disk",
        "Microsoft.Compute/availabilitySets": "azure.compute.availability_set",
    }

    def __init__(self):
        super().__init__("azure")

    def normalize(
        self,
        data: dict[str, Any],
    ) -> list[EvidenceRecord]:
        """
        Convert Azure compute API responses
        into EvidenceRecord objects.
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

            records.append(
                self.create_record(
                    resource_type=self.RESOURCE_TYPES[azure_type],
                    resource_id=resource_id,
                    data={
                        "name": resource.get(
                            "name",
                            "",
                        ),
                        "provider": "azure",
                        "service": "compute",
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
                        "normalizer": "compute",
                    },
                )
            )

        self.validate(records)

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
        """Extract resource group from Azure resource ID."""

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
