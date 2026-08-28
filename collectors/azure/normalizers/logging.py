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

from datetime import UTC, datetime
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

        A single UTC collection timestamp is generated for
        the normalization run and retained on every normalized
        Azure logging record.
        """

        records: list[EvidenceRecord] = []

        #
        # Generate one timestamp for the entire normalization
        # run.
        #
        # Azure logging/activity responses do not necessarily
        # provide a universal evidence timestamp suitable for
        # every normalized record. This timestamp represents
        # when the live evidence batch was normalized/observed.
        #
        # A single timestamp is used for the complete batch so
        # all records from this collection run have a consistent
        # evidence timestamp.
        #
        collection_timestamp = datetime.now(
            UTC,
        ).isoformat()

        for item in data.get(
            "value",
            [],
        ):

            #
            # Defensive handling:
            # skip malformed entries without changing behavior
            # for valid Azure logging dictionaries.
            #
            if not isinstance(
                item,
                dict,
            ):
                continue

            item_type = self._detect_type(item)

            resource_id = item.get(
                "id",
                "",
            )

            properties = item.get(
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
                    resource_type=self.RESOURCE_TYPES.get(
                        item_type,
                        "azure.logging.unknown",
                    ),
                    resource_id=resource_id,
                    data={
                        #
                        # Collection timestamp.
                        #
                        # This is the UTC timestamp for the
                        # live logging evidence normalization run.
                        #
                        # It is deliberately stored as a normalized
                        # field so report generation can display it
                        # as the evidence timestamp.
                        #
                        "timestamp": collection_timestamp,
                        "name": self._name(item),
                        "provider": "azure",
                        "service": "monitoring",
                        "location": item.get("location"),
                        "subscription_id": self._subscription_id(resource_id),
                        "resource_group": self._resource_group(resource_id),
                        # Existing activity-log evidence.
                        "operation_name": self._operation_name(item),
                        "status": self._value(item.get("status")),
                        "caller": self._caller(item),
                        "event_timestamp": self._event_timestamp(item),
                        # Flattened diagnostic/logging evidence.
                        #
                        # These fields are intentionally simple and
                        # report-friendly. The original nested structures
                        # remain available below in "properties" and "raw".
                        "workspace_id": self._workspace_id(
                            item,
                            properties,
                        ),
                        "storage_account_id": self._storage_account_id(
                            item,
                            properties,
                        ),
                        "event_categories": self._event_categories(
                            item,
                            properties,
                        ),
                        "enabled_event_categories": self._enabled_event_categories(
                            item,
                            properties,
                        ),
                        "disabled_event_categories": self._disabled_event_categories(
                            item,
                            properties,
                        ),
                        "metric_categories": self._metric_categories(
                            item,
                            properties,
                        ),
                        "enabled_metric_categories": self._enabled_metric_categories(
                            item,
                            properties,
                        ),
                        "retention_enabled": self._retention_enabled(
                            item,
                            properties,
                        ),
                        "retention_days": self._retention_days(
                            item,
                            properties,
                        ),
                        # Keep the existing properties/raw evidence.
                        #
                        # These are evidence-preservation fields and should
                        # not be used directly as report-table cells.
                        "properties": properties,
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

        operation_name = item.get(
            "operationName",
            {},
        )

        if isinstance(operation_name, dict):
            operation_name = operation_name.get("value")

        return item.get("name") or operation_name or "unknown"

    def _operation_name(
        self,
        item: dict[str, Any],
    ) -> str | None:
        """Extract activity operation name."""

        operation = item.get("operationName")

        if isinstance(operation, dict):
            return operation.get("value")

        return operation

    def _caller(
        self,
        item: dict[str, Any],
    ) -> str | None:
        """
        Extract the activity-log caller.

        Azure may expose caller as a string, while some API responses
        may provide a nested value.
        """

        caller = item.get("caller")

        if isinstance(caller, dict):
            return caller.get("value") or caller.get("name") or caller.get("id")

        return caller

    def _event_timestamp(
        self,
        item: dict[str, Any],
    ) -> str | None:
        """
        Extract the event timestamp.

        Supports the normal Azure Activity Log field and avoids
        returning a nested object if an API variant provides one.
        """

        timestamp = item.get("eventTimestamp")

        if isinstance(timestamp, dict):
            return timestamp.get("value") or timestamp.get("timestamp")

        return timestamp

    def _workspace_id(
        self,
        item: dict[str, Any],
        properties: dict[str, Any],
    ) -> str | None:
        """Extract Log Analytics workspace ID."""

        return self._first_value(
            item.get("workspaceId"),
            properties.get("workspaceId"),
            properties.get("workspaceResourceId"),
            item.get("workspaceResourceId"),
        )

    def _storage_account_id(
        self,
        item: dict[str, Any],
        properties: dict[str, Any],
    ) -> str | None:
        """Extract storage account resource ID."""

        return self._first_value(
            item.get("storageAccountId"),
            properties.get("storageAccountId"),
        )

    def _event_categories(
        self,
        item: dict[str, Any],
        properties: dict[str, Any],
    ) -> list[str]:
        """
        Extract configured diagnostic log categories.

        Azure diagnostic settings commonly expose these as:

            logs: [
                {
                    "category": "AuditEvent",
                    "enabled": true
                }
            ]

        Only the category names are returned here. The original
        objects remain available in properties/raw.
        """

        logs = properties.get(
            "logs",
            item.get("logs", []),
        )

        if not isinstance(logs, list):
            return []

        categories: list[str] = []

        for log in logs:
            if isinstance(log, dict):
                category = log.get("category")

                if category:
                    categories.append(str(category))

            elif isinstance(log, str):
                categories.append(log)

        return self._unique(categories)

    def _enabled_event_categories(
        self,
        item: dict[str, Any],
        properties: dict[str, Any],
    ) -> list[str]:
        """Return enabled diagnostic log categories."""

        return self._diagnostic_categories_by_state(
            item,
            properties,
            enabled=True,
        )

    def _disabled_event_categories(
        self,
        item: dict[str, Any],
        properties: dict[str, Any],
    ) -> list[str]:
        """Return disabled diagnostic log categories."""

        return self._diagnostic_categories_by_state(
            item,
            properties,
            enabled=False,
        )

    def _diagnostic_categories_by_state(
        self,
        item: dict[str, Any],
        properties: dict[str, Any],
        *,
        enabled: bool,
    ) -> list[str]:
        """Extract diagnostic log categories by enabled state."""

        logs = properties.get(
            "logs",
            item.get("logs", []),
        )

        if not isinstance(logs, list):
            return []

        categories: list[str] = []

        for log in logs:
            if not isinstance(log, dict):
                continue

            category = log.get("category")

            if not category:
                continue

            if log.get("enabled") is enabled:
                categories.append(str(category))

        return self._unique(categories)

    def _metric_categories(
        self,
        item: dict[str, Any],
        properties: dict[str, Any],
    ) -> list[str]:
        """
        Extract configured diagnostic metric categories.

        Returns only category names rather than the complete nested
        metric configuration.
        """

        metrics = properties.get(
            "metrics",
            item.get("metrics", []),
        )

        if not isinstance(metrics, list):
            return []

        categories: list[str] = []

        for metric in metrics:
            if isinstance(metric, dict):
                category = metric.get("category")

                if category:
                    categories.append(str(category))

            elif isinstance(metric, str):
                categories.append(metric)

        return self._unique(categories)

    def _enabled_metric_categories(
        self,
        item: dict[str, Any],
        properties: dict[str, Any],
    ) -> list[str]:
        """Return enabled diagnostic metric categories."""

        metrics = properties.get(
            "metrics",
            item.get("metrics", []),
        )

        if not isinstance(metrics, list):
            return []

        categories: list[str] = []

        for metric in metrics:
            if not isinstance(metric, dict):
                continue

            category = metric.get("category")

            if category and metric.get("enabled") is True:
                categories.append(str(category))

        return self._unique(categories)

    def _retention_enabled(
        self,
        item: dict[str, Any],
        properties: dict[str, Any],
    ) -> bool | None:
        """
        Extract diagnostic log retention configuration.

        This is evidence extraction only; it does not assess whether
        the configured retention is compliant.
        """

        retention_policy = properties.get(
            "retentionPolicy",
            item.get("retentionPolicy"),
        )

        if isinstance(retention_policy, dict):
            enabled = retention_policy.get("enabled")

            if isinstance(enabled, bool):
                return enabled

        return None

    def _retention_days(
        self,
        item: dict[str, Any],
        properties: dict[str, Any],
    ) -> int | None:
        """Extract configured diagnostic retention days."""

        retention_policy = properties.get(
            "retentionPolicy",
            item.get("retentionPolicy"),
        )

        if not isinstance(retention_policy, dict):
            return None

        days = retention_policy.get("days")

        if isinstance(days, bool):
            return None

        if isinstance(days, int):
            return days

        if isinstance(days, str):
            try:
                return int(days)
            except ValueError:
                return None

        return None

    def _value(
        self,
        value: Any,
    ) -> Any:
        """
        Flatten a simple Azure value.

        Azure responses occasionally return values as objects such as
        {"value": "..."} rather than directly as strings.
        """

        if isinstance(value, dict):
            return value.get("value") or value.get("name") or value.get("id")

        return value

    def _first_value(
        self,
        *values: Any,
    ) -> Any:
        """Return the first usable scalar value."""

        for value in values:
            flattened = self._value(value)

            if flattened not in (
                None,
                "",
                [],
                {},
            ):
                return flattened

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
