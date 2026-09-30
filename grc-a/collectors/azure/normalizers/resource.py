# collectors\azure\normalizers\resource.py

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

from datetime import UTC, datetime
from typing import Any

from collectors.base.models import EvidenceRecord
from collectors.base.normalizer import BaseNormalizer


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

        Common Azure resource attributes are flattened into
        report-friendly scalar fields.

        The complete ``properties`` and ``raw`` objects are
        deliberately retained as evidence for audit and
        traceability, but should not be used directly as
        report-table cells.

        A single UTC collection timestamp is generated for
        the normalization run and retained on every normalized
        Azure resource record.
        """

        records: list[EvidenceRecord] = []

        #
        # Generate one timestamp for the entire normalization
        # run.
        #
        # Azure Resource Manager generic resource inventory does
        # not provide a universal per-resource observation timestamp.
        # Therefore this timestamp represents when the live evidence
        # batch was normalized/observed.
        #
        # Using one timestamp for the complete batch also means that
        # every resource collected during this normalization run has
        # a consistent evidence timestamp.
        #
        collection_timestamp = datetime.now(
            UTC,
        ).isoformat()

        for resource in data.get("value", []):

            #
            # Defensive handling:
            # skip malformed entries without changing the behavior
            # for valid Azure resource dictionaries.
            #
            if not isinstance(
                resource,
                dict,
            ):
                continue

            resource_id = resource.get(
                "id",
                "",
            )

            resource_type = resource.get(
                "type",
                "",
            )

            properties = resource.get(
                "properties",
                {},
            )

            sku = resource.get(
                "sku",
                {},
            )

            tags = resource.get(
                "tags",
                {},
            )

            records.append(
                self.create_record(
                    resource_type=self.RESOURCE_TYPE,
                    resource_id=resource_id,
                    data={
                        #
                        # Collection timestamp.
                        #
                        # This is the actual UTC timestamp for
                        # this live normalization/observation run.
                        #
                        # It is deliberately stored as a normalized
                        # field so report generation can display it
                        # as the evidence timestamp.
                        #
                        "timestamp": collection_timestamp,
                        #
                        # Core resource identity.
                        #
                        "name": resource.get(
                            "name",
                            "",
                        ),
                        "provider": "azure",
                        "service": self._service_name(
                            resource_type,
                        ),
                        "location": resource.get(
                            "location",
                        ),
                        "subscription_id": self._subscription_id(
                            resource_id,
                        ),
                        "resource_group": self._resource_group(
                            resource_id,
                        ),
                        "azure_type": resource_type,
                        #
                        # Generic Azure resource metadata.
                        #
                        "managed_by": resource.get(
                            "managedBy",
                        ),
                        "kind": resource.get(
                            "kind",
                        ),
                        #
                        # Flattened SKU fields.
                        #
                        # The original SKU object remains below as
                        # retained evidence.
                        #
                        "sku_name": self._sku_value(
                            sku,
                            "name",
                        ),
                        "sku_tier": self._sku_value(
                            sku,
                            "tier",
                        ),
                        "sku_size": self._sku_value(
                            sku,
                            "size",
                        ),
                        "sku_family": self._sku_value(
                            sku,
                            "family",
                        ),
                        "sku_capacity": self._sku_value(
                            sku,
                            "capacity",
                        ),
                        #
                        # Generic provisioning state.
                        #
                        # Many Azure resource providers expose this
                        # under properties.provisioningState.
                        #
                        "provisioning_state": self._property_value(
                            properties,
                            "provisioningState",
                        ),
                        #
                        # Useful generic resource identifiers that
                        # may be exposed by individual providers.
                        #
                        "resource_provider": self._resource_provider(
                            resource_type,
                        ),
                        #
                        # Tags are retained as structured evidence.
                        #
                        # Reporting should selectively flatten or
                        # summarize tags rather than serializing the
                        # complete dictionary into a table cell.
                        #
                        "tags": tags,
                        #
                        # Retain the original SKU object.
                        #
                        # This preserves evidence that may contain
                        # provider-specific fields not represented by
                        # the flattened values above.
                        #
                        "sku": sku,
                        #
                        # Preserve the complete Azure properties object.
                        #
                        # This is evidence, not a normal report-table
                        # field.
                        #
                        "properties": properties,
                        #
                        # Preserve the complete original Azure resource.
                        #
                        # This MUST remain available for evidence
                        # traceability and troubleshooting.
                        #
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

    def _resource_provider(
        self,
        resource_type: str | None,
    ) -> str | None:
        """
        Extract the Azure resource provider namespace.

        Example:

        Microsoft.Compute/virtualMachines

        becomes:

        Microsoft.Compute
        """

        if not resource_type:
            return None

        try:
            provider, _ = resource_type.split(
                "/",
                1,
            )

            return provider

        except ValueError:
            return resource_type or None

    def _sku_value(
        self,
        sku: Any,
        key: str,
    ) -> Any:
        """
        Safely extract a value from the Azure SKU object.

        Azure resource providers do not all expose the same
        SKU structure, so this method deliberately returns
        None when the requested field is unavailable.
        """

        if not isinstance(
            sku,
            dict,
        ):
            return None

        return sku.get(key)

    def _property_value(
        self,
        properties: Any,
        key: str,
    ) -> Any:
        """
        Safely extract a top-level Azure resource property.

        This is intentionally limited to simple scalar values
        and does not flatten arbitrary nested provider-specific
        objects.
        """

        if not isinstance(
            properties,
            dict,
        ):
            return None

        value = properties.get(key)

        if isinstance(
            value,
            (dict, list),
        ):
            return None

        return value

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
