"""
Azure Network Normalizer.

Normalizes Azure networking resources into the
platform evidence model.

Supported resources:
- Virtual Networks
- Subnets
- Network Security Groups
- Azure Firewall
- Route Tables
- Public IP Addresses
- Load Balancers

Does not perform:
- Security assessment
- Compliance evaluation
- Network risk scoring
"""

from __future__ import annotations

from typing import Any

from collectors.base.normalizer import BaseNormalizer
from collectors.base.models import EvidenceRecord


class NetworkNormalizer(BaseNormalizer):
    """Normalize Azure networking resources."""

    RESOURCE_TYPES = {
        "Microsoft.Network/virtualNetworks": "azure.network.virtual_network",
        "Microsoft.Network/networkSecurityGroups": "azure.network.network_security_group",
        "Microsoft.Network/azureFirewalls": "azure.network.firewall",
        "Microsoft.Network/routeTables": "azure.network.route_table",
        "Microsoft.Network/publicIPAddresses": "azure.network.public_ip",
        "Microsoft.Network/loadBalancers": "azure.network.load_balancer",
    }

    def __init__(self):
        super().__init__("azure")

    def normalize(
        self,
        data: dict[str, Any],
    ) -> list[EvidenceRecord]:
        """
        Convert Azure network resources into
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
                        "service": "networking",
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
                        "normalizer": "network",
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
