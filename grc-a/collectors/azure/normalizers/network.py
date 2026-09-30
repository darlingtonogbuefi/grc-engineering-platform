# collectors\azure\normalizers\network.py

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

from datetime import UTC, datetime
from typing import Any

from collectors.base.normalizer import BaseNormalizer
from collectors.base.models import EvidenceRecord


class NetworkNormalizer(BaseNormalizer):
    """Normalize Azure networking resources."""

    RESOURCE_TYPES = {
        "Microsoft.Network/virtualNetworks": "azure.network.virtual_network",
        "Microsoft.Network/virtualNetworks/subnets": "azure.network.subnet",
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

        Nested Azure networking configuration is retained in
        ``properties`` and ``raw`` for evidence preservation.

        Report-facing fields are additionally flattened into
        concise values/lists so downstream reporting does not
        need to understand the Azure ARM object structure.

        A single UTC collection timestamp is generated for
        the normalization run and retained on every normalized
        Azure network record.
        """

        records: list[EvidenceRecord] = []

        #
        # Generate one timestamp for the entire normalization
        # run.
        #
        # Azure Resource Manager network resources do not provide
        # a universal per-resource observation timestamp suitable
        # for every normalized record. This timestamp therefore
        # represents when the live evidence batch was
        # normalized/observed.
        #
        # One timestamp is intentionally shared by the complete
        # batch so all records from this collection run have a
        # consistent evidence timestamp.
        #
        collection_timestamp = datetime.now(
            UTC,
        ).isoformat()

        for resource in data.get(
            "value",
            [],
        ):

            #
            # Defensive handling:
            # skip malformed entries without changing behavior
            # for valid Azure resource dictionaries.
            #
            if not isinstance(
                resource,
                dict,
            ):
                continue

            azure_type = resource.get(
                "type",
                "",
            )

            if not isinstance(
                azure_type,
                str,
            ):
                continue

            #
            # Azure resource type casing should normally be
            # consistent, but matching case-insensitively makes
            # normalization more defensive without changing the
            # supported resource mappings.
            #
            resource_type_key = self._resource_type_key(
                azure_type,
            )

            if resource_type_key is None:
                continue

            resource_id = resource.get(
                "id",
                "",
            )

            if not isinstance(
                resource_id,
                str,
            ):
                resource_id = ""

            properties = resource.get(
                "properties",
                {},
            )

            if not isinstance(
                properties,
                dict,
            ):
                properties = {}

            sku = resource.get(
                "sku",
                {},
            )

            if not isinstance(
                sku,
                dict,
            ):
                sku = {}

            tags = resource.get(
                "tags",
                {},
            )

            if not isinstance(
                tags,
                dict,
            ):
                tags = {}

            records.append(
                self.create_record(
                    resource_type=self.RESOURCE_TYPES[resource_type_key],
                    resource_id=resource_id,
                    data={
                        #
                        # Collection timestamp.
                        #
                        # This is the UTC timestamp for the
                        # live network evidence normalization run.
                        #
                        # It is deliberately stored as a normalized
                        # field so report generation can display it
                        # as the evidence timestamp.
                        #
                        "timestamp": collection_timestamp,
                        # -------------------------------------------------
                        # Core resource identity.
                        # -------------------------------------------------
                        "name": resource.get(
                            "name",
                            "",
                        ),
                        "provider": "azure",
                        "service": "networking",
                        "location": resource.get(
                            "location",
                        ),
                        "subscription_id": self._subscription_id(
                            resource_id,
                        ),
                        "resource_group": self._resource_group(
                            resource_id,
                        ),
                        "azure_type": azure_type,
                        "kind": resource.get(
                            "kind",
                        ),
                        "sku": sku,
                        # -------------------------------------------------
                        # Flattened network evidence.
                        #
                        # These fields are intended for reporting and
                        # querying. The original nested Azure structures
                        # remain preserved below.
                        # -------------------------------------------------
                        "address_space": self._address_space(
                            properties,
                        ),
                        "subnet_names": self._subnet_names(
                            properties,
                        ),
                        "subnet_count": self._subnet_count(
                            properties,
                        ),
                        "dns_servers": self._dns_servers(
                            properties,
                        ),
                        "network_security_group_id": (
                            self._network_security_group_id(
                                properties,
                            )
                        ),
                        "security_rule_count": (
                            self._security_rule_count(
                                properties,
                            )
                        ),
                        "inbound_security_rule_count": (
                            self._security_rule_count(
                                properties,
                                direction="Inbound",
                            )
                        ),
                        "outbound_security_rule_count": (
                            self._security_rule_count(
                                properties,
                                direction="Outbound",
                            )
                        ),
                        "enabled_security_rule_count": (
                            self._security_rule_count(
                                properties,
                                enabled=True,
                            )
                        ),
                        "disabled_security_rule_count": (
                            self._security_rule_count(
                                properties,
                                enabled=False,
                            )
                        ),
                        "route_count": self._route_count(
                            properties,
                        ),
                        "route_names": self._route_names(
                            properties,
                        ),
                        "firewall_policy_id": (
                            self._firewall_policy_id(
                                properties,
                            )
                        ),
                        "firewall_sku_name": self._sku_value(
                            sku,
                            "name",
                        ),
                        "firewall_sku_tier": self._sku_value(
                            sku,
                            "tier",
                        ),
                        "public_ip_address": (
                            self._public_ip_address(
                                properties,
                            )
                        ),
                        "public_ip_allocation_method": (
                            self._public_ip_allocation_method(
                                properties,
                            )
                        ),
                        "public_ip_sku": self._sku_value(
                            sku,
                            "name",
                        ),
                        "public_ip_sku_tier": self._sku_value(
                            sku,
                            "tier",
                        ),
                        "frontend_ip_configuration_count": (
                            self._collection_count(
                                properties.get(
                                    "frontendIPConfigurations",
                                )
                            )
                        ),
                        "backend_pool_count": (
                            self._collection_count(
                                properties.get(
                                    "backendAddressPools",
                                )
                            )
                        ),
                        "load_balancing_rule_count": (
                            self._collection_count(
                                properties.get(
                                    "loadBalancingRules",
                                )
                            )
                        ),
                        "probe_count": (
                            self._collection_count(
                                properties.get(
                                    "probes",
                                )
                            )
                        ),
                        "inbound_nat_rule_count": (
                            self._collection_count(
                                properties.get(
                                    "inboundNatRules",
                                )
                            )
                        ),
                        "outbound_rule_count": (
                            self._collection_count(
                                properties.get(
                                    "outboundRules",
                                )
                            )
                        ),
                        "frontend_ip_addresses": (
                            self._frontend_ip_addresses(
                                properties,
                            )
                        ),
                        "backend_pool_names": (
                            self._backend_pool_names(
                                properties,
                            )
                        ),
                        # -------------------------------------------------
                        # Existing tags functionality.
                        # -------------------------------------------------
                        "tags": tags,
                        # -------------------------------------------------
                        # Evidence preservation.
                        #
                        # Do not use these fields directly as report-table
                        # cells. They contain the original Azure objects.
                        # -------------------------------------------------
                        "properties": properties,
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

    def _resource_type_key(
        self,
        resource_type: str,
    ) -> str | None:
        """
        Resolve a supported Azure resource type.

        Matching is case-insensitive while returning the canonical
        key used by RESOURCE_TYPES.
        """

        if not resource_type:
            return None

        normalized_type = resource_type.lower()

        for supported_type in self.RESOURCE_TYPES:
            if supported_type.lower() == normalized_type:
                return supported_type

        return None

    def _address_space(
        self,
        properties: dict[str, Any],
    ) -> list[str]:
        """
        Extract VNet address-space prefixes.

        Azure commonly returns:

            addressSpace:
                addressPrefixes:
                    - 10.0.0.0/16
        """

        address_space = properties.get(
            "addressSpace",
            {},
        )

        if not isinstance(
            address_space,
            dict,
        ):
            return []

        prefixes = address_space.get(
            "addressPrefixes",
            [],
        )

        if not isinstance(
            prefixes,
            list,
        ):
            return []

        return [str(prefix) for prefix in prefixes if prefix]

    def _subnet_names(
        self,
        properties: dict[str, Any],
    ) -> list[str]:
        """Extract VNet subnet names."""

        subnets = properties.get(
            "subnets",
            [],
        )

        if not isinstance(
            subnets,
            list,
        ):
            return []

        names: list[str] = []

        for subnet in subnets:
            if not isinstance(
                subnet,
                dict,
            ):
                continue

            name = subnet.get(
                "name",
            )

            if not name:
                name = self._nested_name(
                    subnet.get(
                        "properties",
                    ),
                )

            if name:
                names.append(
                    str(name),
                )

        return self._unique(
            names,
        )

    def _subnet_count(
        self,
        properties: dict[str, Any],
    ) -> int:
        """Return number of configured VNet subnets."""

        return self._collection_count(
            properties.get(
                "subnets",
            ),
        )

    def _dns_servers(
        self,
        properties: dict[str, Any],
    ) -> list[str]:
        """Extract configured DNS server addresses."""

        dns_servers = properties.get(
            "dhcpOptions",
            {},
        )

        if isinstance(
            dns_servers,
            dict,
        ):
            dns_servers = dns_servers.get(
                "dnsServers",
                [],
            )
        else:
            return []

        if not isinstance(
            dns_servers,
            list,
        ):
            return []

        return [str(server) for server in dns_servers if server]

    def _network_security_group_id(
        self,
        properties: dict[str, Any],
    ) -> str | None:
        """
        Extract a directly associated NSG resource ID.

        This is useful for resources such as subnets where the
        NSG is represented as:

            networkSecurityGroup:
                id: ...
        """

        nsg = properties.get(
            "networkSecurityGroup",
        )

        return self._resource_reference_id(
            nsg,
        )

    def _security_rule_count(
        self,
        properties: dict[str, Any],
        direction: str | None = None,
        enabled: bool | None = None,
    ) -> int:
        """
        Count NSG security rules.

        Counts the nested Azure security rule objects without
        exposing those objects directly as report-table values.
        """

        rules = properties.get(
            "securityRules",
            [],
        )

        if not isinstance(
            rules,
            list,
        ):
            return 0

        count = 0

        for rule in rules:
            if not isinstance(
                rule,
                dict,
            ):
                continue

            rule_properties = rule.get(
                "properties",
                {},
            )

            if not isinstance(
                rule_properties,
                dict,
            ):
                rule_properties = {}

            if direction is not None:
                rule_direction = rule_properties.get(
                    "direction",
                ) or rule.get(
                    "direction",
                )

                if (
                    isinstance(
                        rule_direction,
                        str,
                    )
                    and rule_direction.lower() != direction.lower()
                ):
                    continue

            if enabled is not None:
                rule_enabled = rule_properties.get(
                    "enabled",
                    rule.get(
                        "enabled",
                    ),
                )

                if rule_enabled is not enabled:
                    continue

            count += 1

        return count

    def _route_count(
        self,
        properties: dict[str, Any],
    ) -> int:
        """Return number of configured route entries."""

        return self._collection_count(
            properties.get(
                "routes",
            ),
        )

    def _route_names(
        self,
        properties: dict[str, Any],
    ) -> list[str]:
        """Extract route names."""

        routes = properties.get(
            "routes",
            [],
        )

        if not isinstance(
            routes,
            list,
        ):
            return []

        names: list[str] = []

        for route in routes:
            if not isinstance(
                route,
                dict,
            ):
                continue

            name = route.get(
                "name",
            )

            if not name:
                route_properties = route.get(
                    "properties",
                    {},
                )

                if isinstance(
                    route_properties,
                    dict,
                ):
                    name = route_properties.get(
                        "name",
                    )

            if name:
                names.append(
                    str(name),
                )

        return self._unique(
            names,
        )

    def _firewall_policy_id(
        self,
        properties: dict[str, Any],
    ) -> str | None:
        """Extract Azure Firewall Policy resource ID."""

        policy = properties.get(
            "firewallPolicy",
        )

        return self._resource_reference_id(
            policy,
        )

    def _public_ip_address(
        self,
        properties: dict[str, Any],
    ) -> str | None:
        """Extract assigned public IP address."""

        return self._first_value(
            properties.get(
                "ipAddress",
            ),
            properties.get(
                "publicIPAddress",
            ),
        )

    def _public_ip_allocation_method(
        self,
        properties: dict[str, Any],
    ) -> str | None:
        """Extract public IP allocation method."""

        return self._first_value(
            properties.get(
                "publicIPAllocationMethod",
            ),
            properties.get(
                "allocationMethod",
            ),
        )

    def _frontend_ip_addresses(
        self,
        properties: dict[str, Any],
    ) -> list[str]:
        """
        Extract load balancer frontend IP addresses/references.

        Azure may expose the address directly or through a nested
        publicIPAddress reference.
        """

        configurations = properties.get(
            "frontendIPConfigurations",
            [],
        )

        if not isinstance(
            configurations,
            list,
        ):
            return []

        addresses: list[str] = []

        for configuration in configurations:
            if not isinstance(
                configuration,
                dict,
            ):
                continue

            configuration_properties = configuration.get(
                "properties",
                {},
            )

            if not isinstance(
                configuration_properties,
                dict,
            ):
                configuration_properties = {}

            address = configuration_properties.get(
                "privateIPAddress",
            )

            if address:
                addresses.append(
                    str(address),
                )
                continue

            public_ip = configuration_properties.get(
                "publicIPAddress",
            )

            public_ip_id = self._resource_reference_id(
                public_ip,
            )

            if public_ip_id:
                addresses.append(
                    public_ip_id,
                )

        return self._unique(
            addresses,
        )

    def _backend_pool_names(
        self,
        properties: dict[str, Any],
    ) -> list[str]:
        """Extract load balancer backend pool names."""

        pools = properties.get(
            "backendAddressPools",
            [],
        )

        if not isinstance(
            pools,
            list,
        ):
            return []

        names: list[str] = []

        for pool in pools:
            if not isinstance(
                pool,
                dict,
            ):
                continue

            name = pool.get(
                "name",
            )

            if name:
                names.append(
                    str(name),
                )

        return self._unique(
            names,
        )

    def _sku_value(
        self,
        sku: Any,
        key: str,
    ) -> str | None:
        """Extract a simple SKU value."""

        if not isinstance(
            sku,
            dict,
        ):
            return None

        value = sku.get(
            key,
        )

        if value is None:
            return None

        return str(value)

    def _collection_count(
        self,
        value: Any,
    ) -> int:
        """Return the number of entries in an Azure collection."""

        if not isinstance(
            value,
            list,
        ):
            return 0

        return len(value)

    def _resource_reference_id(
        self,
        reference: Any,
    ) -> str | None:
        """
        Extract an Azure resource ID from a nested resource reference.

        Supports:

            {"id": "/subscriptions/..."}

        and a direct string resource ID.
        """

        if isinstance(
            reference,
            str,
        ):
            return reference

        if isinstance(
            reference,
            dict,
        ):
            value = reference.get(
                "id",
            )

            if isinstance(
                value,
                str,
            ):
                return value

        return None

    def _nested_name(
        self,
        value: Any,
    ) -> str | None:
        """Extract a nested resource name."""

        if not isinstance(
            value,
            dict,
        ):
            return None

        name = value.get(
            "name",
        )

        if isinstance(
            name,
            str,
        ):
            return name

        return None

    def _first_value(
        self,
        *values: Any,
    ) -> str | None:
        """Return the first usable scalar value."""

        for value in values:
            if isinstance(
                value,
                str,
            ):
                if value:
                    return value

            elif isinstance(
                value,
                int,
            ) and not isinstance(
                value,
                bool,
            ):
                return str(value)

            elif isinstance(
                value,
                dict,
            ):
                nested_value = (
                    value.get("value") or value.get("id") or value.get("name")
                )

                if (
                    isinstance(
                        nested_value,
                        str,
                    )
                    and nested_value
                ):
                    return nested_value

        return None

    def _unique(
        self,
        values: list[str],
    ) -> list[str]:
        """Return unique values while preserving source order."""

        seen: set[str] = set()
        result: list[str] = []

        for value in values:
            if value in seen:
                continue

            seen.add(value)
            result.append(value)

        return result

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
                "subscriptions",
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
                "resourceGroups",
            )

            return parts[index + 1]

        except (
            ValueError,
            IndexError,
        ):
            return None
