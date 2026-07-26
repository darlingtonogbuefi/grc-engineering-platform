"""
Azure Security Normalizer.

Normalizes Azure security posture evidence into the
platform evidence model.

Supported resources:
- Defender for Cloud settings
- Security assessments
- Secure Score
- Regulatory compliance assessments
- Security contacts

Does not perform:
- Compliance evaluation
- Risk scoring
- Framework mappings
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from collectors.base.normalizer import BaseNormalizer
from collectors.base.models import EvidenceRecord


class SecurityNormalizer(BaseNormalizer):
    """Normalize Azure security resources."""

    RESOURCE_TYPES = {
        "security_assessment": "azure.security.assessment",
        "secure_score": "azure.security.secure_score",
        "regulatory_compliance": "azure.security.regulatory_compliance",
        "defender_setting": "azure.security.defender_setting",
        "security_contact": "azure.security.contact",
    }

    def normalize(
        self,
        data: dict[str, Any],
    ) -> list[EvidenceRecord]:
        """
        Convert Azure security responses into
        EvidenceRecord objects.
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
                        "azure.security.unknown",
                    ),
                    resource_id=resource_id,
                    data={
                        "name": self._name(item),
                        "provider": "azure",
                        "service": "security",
                        "location": item.get(
                            "location"
                        ),
                        "subscription_id": self._subscription_id(
                            resource_id
                        ),
                        "resource_group": self._resource_group(
                            resource_id
                        ),
                        "azure_type": item.get(
                            "type"
                        ),
                        "status": item.get(
                            "status"
                        ),
                        "severity": item.get(
                            "severity"
                        ),
                        "category": item.get(
                            "category"
                        ),
                        "display_name": item.get(
                            "displayName"
                        ),
                        "description": item.get(
                            "description"
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
                        "normalizer": "security",
                    },
                )
            )

        return records

    def _detect_type(
        self,
        item: dict[str, Any],
    ) -> str:
        """Identify Azure security resource type."""

        resource_id = item.get(
            "id",
            "",
        ).lower()

        resource_type = item.get(
            "type",
            "",
        ).lower()

        if "secure scores" in resource_id:
            return "secure_score"

        if "regulatorycompliancestandards" in resource_id:
            return "regulatory_compliance"

        if "securitycontacts" in resource_id:
            return "security_contact"

        if "securityassessments" in resource_id:
            return "security_assessment"

        if "defender" in resource_type:
            return "defender_setting"

        return "unknown"

    def _name(
        self,
        item: dict[str, Any],
    ) -> str:
        """Return best available security resource name."""

        return (
            item.get("name")
            or item.get("displayName")
            or item.get("id", "")
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
        """Extract resource group."""

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
