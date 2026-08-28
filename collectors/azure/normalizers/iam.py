# collectors\azure\normalizers\iam.py

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

from datetime import UTC, datetime
from typing import Any

from collectors.base.normalizer import BaseNormalizer
from collectors.base.models import EvidenceRecord


class IAMNormalizer(BaseNormalizer):
    """Normalize Azure identity and access resources."""

    RESOURCE_TYPES = {
        "role_assignment": "azure.iam.role_assignment",
        "role_definition": "azure.iam.role_definition",
        "managed_identity": "azure.iam.managed_identity",
    }

    def __init__(self):
        super().__init__("azure")

        #
        # Timestamp for the current normalization run.
        #
        # This is populated at the start of normalize() and passed
        # through to every IAM record created during that run.
        #
        self._collection_timestamp: str | None = None

    def normalize(
        self,
        data: dict[str, Any],
    ) -> list[EvidenceRecord]:
        """
        Convert Azure IAM API responses
        into EvidenceRecord objects.

        Raw Azure response data is preserved in record metadata,
        while the EvidenceRecord data contains only normalized,
        report-friendly fields.

        A single UTC collection timestamp is generated for the
        normalization run and retained on every normalized IAM
        record.
        """

        records: list[EvidenceRecord] = []

        #
        # Azure IAM API responses do not provide one universal
        # observation timestamp for every returned resource.
        #
        # Therefore use the actual UTC time at which this live
        # evidence batch is normalized/observed.
        #
        # One timestamp is deliberately shared by the complete
        # batch so all records from this normalization run have
        # a consistent evidence timestamp.
        #
        self._collection_timestamp = datetime.now(
            UTC,
        ).isoformat()

        for item in data.get("value", []):

            #
            # Defensive handling:
            # preserve existing behaviour for valid dictionaries
            # while safely ignoring malformed/null entries.
            #
            if not isinstance(
                item,
                dict,
            ):
                continue

            if not item:
                continue

            item_type = self._detect_type(item)

            if item_type == "role_assignment":
                records.append(self._normalize_role_assignment(item))

            elif item_type == "role_definition":
                records.append(self._normalize_role_definition(item))

            elif item_type == "managed_identity":
                records.append(self._normalize_managed_identity(item))

            else:
                records.append(self._normalize_unknown(item))

        self.validate(records)

        #
        # Do not leave a stale timestamp associated with a later
        # normalization call on the same normalizer instance.
        #
        self._collection_timestamp = None

        return records

    def _normalize_role_assignment(
        self,
        item: dict[str, Any],
    ) -> EvidenceRecord:
        """
        Normalize an Azure role assignment.

        Role assignments identify which principal has which role
        at which Azure scope.

        The nested Azure properties object is intentionally not
        placed into the report-facing data structure.
        """

        resource_id = item.get(
            "id",
            "",
        )

        properties = (
            item.get(
                "properties",
                {},
            )
            or {}
        )

        principal_id = item.get("principalId") or properties.get("principalId")

        principal_type = item.get("principalType") or properties.get("principalType")

        role_definition_id = item.get("roleDefinitionId") or properties.get(
            "roleDefinitionId"
        )

        role_definition_name = (
            item.get("roleDefinitionName")
            or properties.get("roleDefinitionName")
            or properties.get("roleName")
        )

        scope = item.get("scope") or properties.get("scope")

        tenant_id = item.get("tenantId") or properties.get("tenantId")

        return self.create_record(
            resource_type=self.RESOURCE_TYPES["role_assignment"],
            resource_id=resource_id,
            data={
                #
                # Evidence collection timestamp.
                #
                "timestamp": self._collection_timestamp,
                "name": self._name(item),
                "provider": "azure",
                "service": "identity_access",
                "subscription_id": self._subscription_id(resource_id),
                "resource_group": self._resource_group(resource_id),
                "azure_type": item.get("type"),
                "principal_id": principal_id,
                "principal_type": principal_type,
                "role_definition_id": role_definition_id,
                "role_definition_name": role_definition_name,
                "scope": scope,
                "tenant_id": tenant_id,
            },
            metadata={
                "collector": "azure",
                "normalizer": "iam",
                "evidence_type": "role_assignment",
                # Preserve the original Azure evidence without
                # exposing the nested object as a report table field.
                "raw_properties": properties,
                "raw": item,
            },
        )

    def _normalize_role_definition(
        self,
        item: dict[str, Any],
    ) -> EvidenceRecord:
        """
        Normalize an Azure RBAC role definition.

        Azure role definitions can contain deeply nested
        permission structures. Those structures are flattened
        into concise, report-friendly permission fields while
        preserving the original Azure object in metadata.
        """

        resource_id = item.get(
            "id",
            "",
        )

        properties = (
            item.get(
                "properties",
                {},
            )
            or {}
        )

        permissions = properties.get("permissions") or item.get("permissions") or []

        permission_data = self._normalize_permissions(permissions)

        role_name = (
            properties.get("roleName")
            or item.get("roleDefinitionName")
            or item.get("displayName")
            or item.get("name")
            or ""
        )

        role_type = properties.get("type") or item.get("roleType") or item.get("type")

        description = properties.get("description") or item.get("description")

        assignable_scopes = (
            properties.get("assignableScopes") or item.get("assignableScopes") or []
        )

        return self.create_record(
            resource_type=self.RESOURCE_TYPES["role_definition"],
            resource_id=resource_id,
            data={
                #
                # Evidence collection timestamp.
                #
                "timestamp": self._collection_timestamp,
                "name": role_name,
                "provider": "azure",
                "service": "identity_access",
                "subscription_id": self._subscription_id(resource_id),
                "resource_group": self._resource_group(resource_id),
                "azure_type": item.get("type"),
                "role_definition_id": resource_id,
                "role_definition_name": role_name,
                "role_type": role_type,
                "description": description,
                "assignable_scopes": assignable_scopes,
                # Flattened permission evidence.
                "actions": permission_data["actions"],
                "not_actions": permission_data["not_actions"],
                "data_actions": permission_data["data_actions"],
                "not_data_actions": permission_data["not_data_actions"],
                "permission_counts": {
                    "actions": len(permission_data["actions"]),
                    "not_actions": len(permission_data["not_actions"]),
                    "data_actions": len(permission_data["data_actions"]),
                    "not_data_actions": len(permission_data["not_data_actions"]),
                },
                "permission_summary": (permission_data["permission_summary"]),
            },
            metadata={
                "collector": "azure",
                "normalizer": "iam",
                "evidence_type": "role_definition",
                # Preserve complete source evidence.
                "raw_properties": properties,
                "raw": item,
            },
        )

    def _normalize_managed_identity(
        self,
        item: dict[str, Any],
    ) -> EvidenceRecord:
        """
        Normalize an Azure managed identity.

        Supports user-assigned and similar managed identity
        resources while retaining the existing resource metadata
        extraction behaviour.
        """

        resource_id = item.get(
            "id",
            "",
        )

        properties = (
            item.get(
                "properties",
                {},
            )
            or {}
        )

        principal_id = item.get("principalId") or properties.get("principalId")

        client_id = item.get("clientId") or properties.get("clientId")

        tenant_id = item.get("tenantId") or properties.get("tenantId")

        return self.create_record(
            resource_type=self.RESOURCE_TYPES["managed_identity"],
            resource_id=resource_id,
            data={
                #
                # Evidence collection timestamp.
                #
                "timestamp": self._collection_timestamp,
                "name": self._name(item),
                "provider": "azure",
                "service": "identity_access",
                "subscription_id": self._subscription_id(resource_id),
                "resource_group": self._resource_group(resource_id),
                "azure_type": item.get("type"),
                "principal_id": principal_id,
                "client_id": client_id,
                "tenant_id": tenant_id,
            },
            metadata={
                "collector": "azure",
                "normalizer": "iam",
                "evidence_type": "managed_identity",
                # Preserve complete source evidence.
                "raw_properties": properties,
                "raw": item,
            },
        )

    def _normalize_unknown(
        self,
        item: dict[str, Any],
    ) -> EvidenceRecord:
        """
        Preserve the existing behaviour for previously unknown
        Azure IAM resource types without exposing the complete
        nested object as normal report data.
        """

        resource_id = item.get(
            "id",
            "",
        )

        properties = (
            item.get(
                "properties",
                {},
            )
            or {}
        )

        return self.create_record(
            resource_type="azure.iam.unknown",
            resource_id=resource_id,
            data={
                #
                # Evidence collection timestamp.
                #
                "timestamp": self._collection_timestamp,
                "name": self._name(item),
                "provider": "azure",
                "service": "identity_access",
                "subscription_id": self._subscription_id(resource_id),
                "resource_group": self._resource_group(resource_id),
                "azure_type": item.get("type"),
                "principal_id": (
                    item.get("principalId") or properties.get("principalId")
                ),
                "principal_type": (
                    item.get("principalType") or properties.get("principalType")
                ),
                "role_definition_id": (
                    item.get("roleDefinitionId") or properties.get("roleDefinitionId")
                ),
                "role_definition_name": (
                    item.get("roleDefinitionName")
                    or properties.get("roleDefinitionName")
                    or properties.get("roleName")
                ),
                "scope": (item.get("scope") or properties.get("scope")),
                "tenant_id": (item.get("tenantId") or properties.get("tenantId")),
            },
            metadata={
                "collector": "azure",
                "normalizer": "iam",
                "evidence_type": "unknown",
                # Preserve source evidence for investigation/debugging.
                "raw_properties": properties,
                "raw": item,
            },
        )

    def _normalize_permissions(
        self,
        permissions: list[dict[str, Any]],
    ) -> dict[str, list[str] | list[dict[str, Any]]]:
        """
        Flatten Azure RBAC permission definitions.

        Azure role definitions can contain multiple permission
        blocks. This combines those blocks into simple lists
        suitable for normalized evidence and later reporting.
        """

        actions: list[str] = []
        not_actions: list[str] = []
        data_actions: list[str] = []
        not_data_actions: list[str] = []

        for permission in permissions:
            if not isinstance(permission, dict):
                continue

            actions.extend(self._string_list(permission.get("actions")))

            not_actions.extend(self._string_list(permission.get("notActions")))

            data_actions.extend(self._string_list(permission.get("dataActions")))

            not_data_actions.extend(self._string_list(permission.get("notDataActions")))

        actions = self._unique(actions)
        not_actions = self._unique(not_actions)
        data_actions = self._unique(data_actions)
        not_data_actions = self._unique(not_data_actions)

        permission_summary = self._permission_summary(
            actions=actions,
            not_actions=not_actions,
            data_actions=data_actions,
            not_data_actions=not_data_actions,
        )

        return {
            "actions": actions,
            "not_actions": not_actions,
            "data_actions": data_actions,
            "not_data_actions": not_data_actions,
            "permission_summary": permission_summary,
        }

    def _permission_summary(
        self,
        actions: list[str],
        not_actions: list[str],
        data_actions: list[str],
        not_data_actions: list[str],
    ) -> list[dict[str, Any]]:
        """
        Produce concise permission evidence.

        The original Azure action strings remain available in
        data_actions/actions. This method adds a compact summary
        that reporting can use without dumping the full RBAC
        definition into a table cell.
        """

        summary: list[dict[str, Any]] = []

        if actions:
            summary.append(
                {
                    "category": "management",
                    "count": len(actions),
                    "description": ("Management-plane actions permitted"),
                }
            )

        if not_actions:
            summary.append(
                {
                    "category": "management_exclusions",
                    "count": len(not_actions),
                    "description": ("Management-plane actions excluded"),
                }
            )

        if data_actions:
            summary.append(
                {
                    "category": "data",
                    "count": len(data_actions),
                    "description": ("Data-plane actions permitted"),
                }
            )

        if not_data_actions:
            summary.append(
                {
                    "category": "data_exclusions",
                    "count": len(not_data_actions),
                    "description": ("Data-plane actions excluded"),
                }
            )

        return summary

    def _string_list(
        self,
        value: Any,
    ) -> list[str]:
        """
        Safely convert an Azure value into a list of strings.
        """

        if not value:
            return []

        if isinstance(value, str):
            return [value]

        if not isinstance(value, list):
            return []

        return [
            value_item
            for value_item in value
            if isinstance(value_item, str) and value_item
        ]

    def _unique(
        self,
        values: list[str],
    ) -> list[str]:
        """
        Remove duplicate values while preserving source order.
        """

        return list(dict.fromkeys(values))

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

        properties = (
            item.get(
                "properties",
                {},
            )
            or {}
        )

        return (
            item.get("roleDefinitionName")
            or item.get("displayName")
            or properties.get("roleName")
            or properties.get("displayName")
            or item.get("name")
            or item.get("id", "")
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
