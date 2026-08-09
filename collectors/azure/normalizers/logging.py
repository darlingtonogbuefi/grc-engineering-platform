# collectors\azure\normalizers\logging.py

"""
Azure Logging Normalizer.

Normalizes Azure monitoring, audit, and logging
configuration evidence into the platform evidence model.

Supported resources:
- Activity Logs
- Diagnostic Settings
- Log Analytics references

Does not perform:
- Compliance evaluation
- Retention assessment
- Control scoring
"""

from __future__ import annotations

from typing import Any

from collectors.base.normalizer import BaseNormalizer
from collectors.base.models import EvidenceRecord


class LoggingNormalizer(BaseNormalizer):
    """Normalize Azure logging resources."""

    RESOURCE_TYPES = {
        "activity_log": "azure.logging.activity_log",
        "diagnostic_setting": "azure.logging.diagnostic_setting",
        "log_analytics": "azure.logging.log_analytics",
    }

    def __init__(self):
        super().__init__("azure")

    def normalize(
        self,
        data: dict[str, Any],
    ) -> list[EvidenceRecord]:
        """
        Convert Azure logging responses into
        EvidenceRecord objects.
        """

        records: list[EvidenceRecord] = []

        for item in data.get(
            "value",
            [],
        ):
            item_type = self._detect_type(item)

            resource_id = item.get(
                "id",
                "",
            )

            records.append(
                self.create_record(
                    resource_type=self.RESOURCE_TYPES.get(
                        item_type,
                        "azure.logging.unknown",
                    ),
                    resource_id=resource_id,
                    data={
                        "name": self._name(item),
                        "provider": "azure",
                        "service": "monitoring",
                        "location": item.get("location"),
                        "subscription_id": self._subscription_id(resource_id),
                        "resource_group": self._resource_group(resource_id),
                        "operation_name": self._operation_name(item),
                        "status": item.get("status"),
                        "caller": item.get("caller"),
                        "event_timestamp": item.get("eventTimestamp"),
                        "workspace_id": item.get("workspaceId"),
                        "storage_account_id": item.get("storageAccountId"),
                        "event_categories": item.get(
                            "logs",
                            [],
                        ),
                        "metrics": item.get(
                            "metrics",
                            [],
                        ),
                        "properties": item.get(
                            "properties",
                            {},
                        ),
                        "raw": item,
                    },
                    metadata={
                        "collector": "azure",
                        "normalizer": "logging",
                    },
                )
            )

        self.validate(records)

        return records

    def _detect_type(
        self,
        item: dict[str, Any],
    ) -> str:
        """Identify logging resource type."""

        resource_id = item.get(
            "id",
            "",
        ).lower()

        if "diagnosticsettings" in resource_id:
            return "diagnostic_setting"

        if (
            "workspaces" in resource_id
            and "microsoft.operationalinsights" in resource_id
        ):
            return "log_analytics"

        if "eventtimestamp" in item:
            return "activity_log"

        return "unknown"

    def _name(
        self,
        item: dict[str, Any],
    ) -> str:
        """Return resource name."""

        return (
            item.get("name")
            or item.get(
                "operationName",
                {},
            ).get("value")
            or "unknown"
        )

    def _operation_name(
        self,
        item: dict[str, Any],
    ) -> str | None:
        """Extract activity operation name."""

        operation = item.get("operationName")

        if isinstance(operation, dict):
            return operation.get("value")

        return operation

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
