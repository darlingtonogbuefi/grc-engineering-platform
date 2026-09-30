# collectors\azure\normalizers\policy.py

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

from datetime import UTC, datetime
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

        Common policy attributes are flattened into
        report-friendly scalar values.

        Complex policy structures such as parameters,
        policy rules, metadata, and the complete raw
        resource are deliberately retained as evidence
        but should not be rendered directly as normal
        report-table cells.
        """

        records: list[EvidenceRecord] = []

        #
        # Generate one UTC timestamp for the entire
        # normalization run.
        #
        # This represents when the Azure Policy evidence
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

            if not isinstance(
                properties,
                dict,
            ):
                properties = {}

            records.append(
                self.create_record(
                    resource_type=self.RESOURCE_TYPES[azure_type],
                    resource_id=resource_id,
                    data={
                        #
                        # Collection timestamp.
                        #
                        # This is the UTC timestamp for the
                        # live Azure Policy evidence normalization
                        # run. Every record from this collection
                        # run receives the same timestamp.
                        #
                        "timestamp": collection_timestamp,
                        #
                        # Core resource identity.
                        #
                        "name": self._name(resource),
                        "provider": "azure",
                        "service": "governance",
                        "location": resource.get("location"),
                        "subscription_id": self._subscription_id(resource_id),
                        "resource_group": self._resource_group(resource_id),
                        "azure_type": azure_type,
                        #
                        # Policy identity and classification.
                        #
                        "display_name": properties.get("displayName"),
                        "description": properties.get("description"),
                        "policy_type": properties.get("policyType"),
                        "mode": properties.get("mode"),
                        #
                        # Generic Azure provisioning state.
                        #
                        "provisioning_state": self._scalar_property(
                            properties,
                            "provisioningState",
                        ),
                        #
                        # Policy assignment fields.
                        #
                        "scope": properties.get("scope"),
                        "enforcement_mode": properties.get("enforcementMode"),
                        #
                        # Policy definition / initiative fields.
                        #
                        # These are intentionally scalar summaries.
                        # The complete nested structures remain below.
                        #
                        "policy_definition_id": self._policy_definition_id(properties),
                        "policy_definition_version": (properties.get("version")),
                        "policy_rule_effect": self._policy_rule_effect(
                            properties.get("policyRule")
                        ),
                        "parameter_count": self._collection_count(
                            properties.get("parameters")
                        ),
                        "policy_rule_condition_count": (
                            self._policy_rule_condition_count(
                                properties.get("policyRule")
                            )
                        ),
                        #
                        # Initiative / policy set summary.
                        #
                        "policy_definition_reference_count": (
                            self._collection_count(properties.get("policyDefinitions"))
                        ),
                        #
                        # Exemption summary.
                        #
                        "exemption_category": properties.get("exemptionCategory"),
                        "expires_on": properties.get("expiresOn"),
                        "assignment_count": self._collection_count(
                            properties.get("policyAssignmentId")
                        ),
                        #
                        # Complex policy evidence.
                        #
                        # These fields MUST remain available for
                        # auditability and technical investigation.
                        #
                        # The reporting layer should render them in
                        # an evidence/detail section rather than
                        # directly serializing them into the primary
                        # report table.
                        #
                        "parameters": properties.get("parameters"),
                        "policy_rule": properties.get("policyRule"),
                        "metadata": properties.get("metadata"),
                        #
                        # Preserve complete Azure resource evidence.
                        #
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

        properties = resource.get(
            "properties",
            {},
        )

        if not isinstance(
            properties,
            dict,
        ):
            properties = {}

        return resource.get("name") or properties.get("displayName") or ""

    def _policy_definition_id(
        self,
        properties: dict[str, Any],
    ) -> str | None:
        """
        Return the policy definition ID where available.

        Policy assignments normally expose this as
        policyDefinitionId. The value is retained as a
        scalar so it can be displayed directly in reports.
        """

        value = properties.get("policyDefinitionId")

        if value is None:
            return None

        return str(value)

    def _policy_rule_effect(
        self,
        policy_rule: Any,
    ) -> str | None:
        """
        Extract the primary policy rule effect.

        Azure Policy commonly represents the effect as:

            {
                "if": {...},
                "then": {
                    "effect": "audit"
                }
            }

        Some policies use a parameter expression instead.
        In that case the expression is returned as a string.
        """

        if not isinstance(
            policy_rule,
            dict,
        ):
            return None

        then_clause = policy_rule.get(
            "then",
            {},
        )

        if not isinstance(
            then_clause,
            dict,
        ):
            return None

        effect = then_clause.get("effect")

        if effect is None:
            return None

        if isinstance(
            effect,
            (dict, list),
        ):
            return None

        return str(effect)

    def _policy_rule_condition_count(
        self,
        policy_rule: Any,
    ) -> int | None:
        """
        Return a lightweight summary of policy rule conditions.

        This deliberately does not recursively flatten the entire
        Azure Policy rule. Complex policy logic remains available
        through ``policy_rule`` for technical evidence.
        """

        if not isinstance(
            policy_rule,
            dict,
        ):
            return None

        if_clause = policy_rule.get("if")

        if not isinstance(
            if_clause,
            dict,
        ):
            return None

        count = 0

        for key in (
            "allOf",
            "anyOf",
        ):
            value = if_clause.get(key)

            if isinstance(
                value,
                list,
            ):
                count += len(value)

        if count:
            return count

        return 1 if if_clause else 0

    def _collection_count(
        self,
        value: Any,
    ) -> int | None:
        """
        Return the size of a collection.

        For dictionaries, return the number of entries.

        For lists, return the number of items.

        For scalar values, return None rather than exposing
        an artificial count.
        """

        if isinstance(
            value,
            (list, dict),
        ):
            return len(value)

        return None

    def _scalar_property(
        self,
        properties: dict[str, Any],
        key: str,
    ) -> Any:
        """
        Safely return a scalar Azure Policy property.

        Nested dictionaries and lists are deliberately excluded
        from report-friendly normalized fields.
        """

        value = properties.get(key)

        if isinstance(
            value,
            (dict, list),
        ):
            return None

        return value

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
