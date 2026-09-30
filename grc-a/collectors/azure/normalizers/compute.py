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

        Raw Azure properties are deliberately retained as evidence,
        while commonly useful fields are flattened into report-friendly
        scalar values.
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
                    resource_type=self.RESOURCE_TYPES[azure_type],
                    resource_id=resource_id,
                    data={
                        #
                        # Core resource identity.
                        #
                        "name": resource.get(
                            "name",
                            "",
                        ),
                        "provider": "azure",
                        "service": "compute",
                        "location": resource.get("location"),
                        "subscription_id": self._subscription_id(
                            resource_id
                        ),
                        "resource_group": self._resource_group(
                            resource_id
                        ),
                        "kind": resource.get("kind"),

                        #
                        # Resource type.
                        #
                        "azure_type": azure_type,

                        #
                        # Flattened SKU information.
                        #
                        # Keep the original SKU object below as evidence,
                        # but expose the commonly useful fields separately
                        # so reporting does not need to render the nested
                        # object.
                        #
                        "sku_name": (
                            sku.get("name")
                            if isinstance(sku, dict)
                            else None
                        ),
                        "sku_tier": (
                            sku.get("tier")
                            if isinstance(sku, dict)
                            else None
                        ),
                        "sku_capacity": (
                            sku.get("capacity")
                            if isinstance(sku, dict)
                            else None
                        ),

                        #
                        # Common compute state.
                        #
                        "provisioning_state": self._provisioning_state(
                            properties
                        ),

                        #
                        # Virtual machine fields.
                        #
                        "vm_size": self._vm_size(
                            properties
                        ),
                        "os_type": self._os_type(
                            properties
                        ),
                        "computer_name": self._computer_name(
                            properties
                        ),

                        #
                        # VM storage summary.
                        #
                        "os_disk_size_gb": self._os_disk_size_gb(
                            properties
                        ),
                        "os_disk_type": self._os_disk_type(
                            properties
                        ),

                        #
                        # VM networking summary.
                        #
                        "network_interface_count": self._network_interface_count(
                            properties
                        ),

                        #
                        # VM Scale Set fields.
                        #
                        "instance_count": self._instance_count(
                            properties
                        ),
                        "upgrade_policy_mode": self._upgrade_policy_mode(
                            properties
                        ),

                        #
                        # Managed disk fields.
                        #
                        "disk_size_gb": self._disk_size_gb(
                            properties
                        ),
                        "disk_state": self._disk_state(
                            properties
                        ),
                        "disk_sku_name": self._disk_sku_name(
                            resource
                        ),
                        "managed_by": properties.get("managedBy"),

                        #
                        # Availability Set fields.
                        #
                        "platform_fault_domain_count": (
                            properties.get(
                                "platformFaultDomainCount"
                            )
                        ),
                        "platform_update_domain_count": (
                            properties.get(
                                "platformUpdateDomainCount"
                            )
                        ),

                        #
                        # Tags remain available as structured evidence.
                        #
                        # Reporting should selectively flatten/display
                        # these rather than serializing the entire object
                        # into a single table cell.
                        #
                        "tags": tags,

                        #
                        # Preserve the complete Azure properties object.
                        #
                        # This MUST NOT be treated as the primary report
                        # table value. It is retained for audit/evidence
                        # traceability.
                        #
                        "properties": properties,

                        #
                        # Preserve the complete raw Azure resource.
                        #
                        # This is evidence, not a report-table field.
                        #
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

    def _provisioning_state(
        self,
        properties: dict[str, Any],
    ) -> str | None:
        """Return the Azure resource provisioning state."""

        value = properties.get(
            "provisioningState"
        )

        if value is None:
            return None

        return str(value)

    def _vm_size(
        self,
        properties: dict[str, Any],
    ) -> str | None:
        """
        Return the virtual machine size.

        Example:
            Standard_D4s_v5
        """

        hardware_profile = properties.get(
            "hardwareProfile",
            {},
        )

        if not isinstance(
            hardware_profile,
            dict,
        ):
            return None

        value = hardware_profile.get(
            "vmSize"
        )

        return str(value) if value is not None else None

    def _os_type(
        self,
        properties: dict[str, Any],
    ) -> str | None:
        """
        Return the operating system type where available.

        Handles both common Azure VM representations:
        - storageProfile.osDisk.osType
        - osProfile / related resource representations
        """

        storage_profile = properties.get(
            "storageProfile",
            {},
        )

        if isinstance(
            storage_profile,
            dict,
        ):
            os_disk = storage_profile.get(
                "osDisk",
                {},
            )

            if isinstance(
                os_disk,
                dict,
            ):
                value = os_disk.get(
                    "osType"
                )

                if value is not None:
                    return str(value)

        value = properties.get(
            "osType"
        )

        return str(value) if value is not None else None

    def _computer_name(
        self,
        properties: dict[str, Any],
    ) -> str | None:
        """Return the VM computer name where available."""

        os_profile = properties.get(
            "osProfile",
            {},
        )

        if not isinstance(
            os_profile,
            dict,
        ):
            return None

        value = os_profile.get(
            "computerName"
        )

        return str(value) if value is not None else None

    def _os_disk_size_gb(
        self,
        properties: dict[str, Any],
    ) -> int | float | None:
        """Return the VM OS disk size in GB."""

        storage_profile = properties.get(
            "storageProfile",
            {},
        )

        if not isinstance(
            storage_profile,
            dict,
        ):
            return None

        os_disk = storage_profile.get(
            "osDisk",
            {},
        )

        if not isinstance(
            os_disk,
            dict,
        ):
            return None

        value = os_disk.get(
            "diskSizeGB"
        )

        return value if isinstance(
            value,
            (int, float),
        ) else None

    def _os_disk_type(
        self,
        properties: dict[str, Any],
    ) -> str | None:
        """Return the VM OS disk storage type."""

        storage_profile = properties.get(
            "storageProfile",
            {},
        )

        if not isinstance(
            storage_profile,
            dict,
        ):
            return None

        os_disk = storage_profile.get(
            "osDisk",
            {},
        )

        if not isinstance(
            os_disk,
            dict,
        ):
            return None

        value = (
            os_disk.get("managedDisk", {})
            if isinstance(
                os_disk.get("managedDisk", {}),
                dict,
            )
            else {}
        )

        storage_account_type = value.get(
            "storageAccountType"
        )

        if storage_account_type is not None:
            return str(storage_account_type)

        return None

    def _network_interface_count(
        self,
        properties: dict[str, Any],
    ) -> int:
        """Return the number of network interfaces attached to a VM."""

        network_profile = properties.get(
            "networkProfile",
            {},
        )

        if not isinstance(
            network_profile,
            dict,
        ):
            return 0

        interfaces = network_profile.get(
            "networkInterfaces",
            [],
        )

        if not isinstance(
            interfaces,
            list,
        ):
            return 0

        return len(interfaces)

    def _instance_count(
        self,
        properties: dict[str, Any],
    ) -> int | None:
        """
        Return the VM Scale Set instance count where available.

        Azure can expose this through sku.capacity or, depending on
        the API representation, through a property such as
        virtualMachineProfile. This method intentionally avoids
        inventing a value when it is not present.
        """

        value = properties.get(
            "instanceCount"
        )

        if isinstance(
            value,
            int,
        ):
            return value

        return None

    def _upgrade_policy_mode(
        self,
        properties: dict[str, Any],
    ) -> str | None:
        """Return VM Scale Set upgrade policy mode."""

        upgrade_policy = properties.get(
            "upgradePolicy",
            {},
        )

        if not isinstance(
            upgrade_policy,
            dict,
        ):
            return None

        value = upgrade_policy.get(
            "mode"
        )

        return str(value) if value is not None else None

    def _disk_size_gb(
        self,
        properties: dict[str, Any],
    ) -> int | float | None:
        """Return managed disk size in GB."""

        value = properties.get(
            "diskSizeGB"
        )

        return value if isinstance(
            value,
            (int, float),
        ) else None

    def _disk_state(
        self,
        properties: dict[str, Any],
    ) -> str | None:
        """Return managed disk state."""

        value = properties.get(
            "diskState"
        )

        return str(value) if value is not None else None

    def _disk_sku_name(
        self,
        resource: dict[str, Any],
    ) -> str | None:
        """Return the managed disk SKU name."""

        sku = resource.get(
            "sku",
            {},
        )

        if not isinstance(
            sku,
            dict,
        ):
            return None

        value = sku.get(
            "name"
        )

        return str(value) if value is not None else None

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
