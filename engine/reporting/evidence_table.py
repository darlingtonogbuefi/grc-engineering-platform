# engine\reporting\evidence_table.py

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# ============================================================================
# Standard report columns
# ============================================================================

EVIDENCE_COLUMNS = [
    "selection",
    "time",
    "compliance_check",
    "evidence_by_type",
    "data_source",
    "event_name",
    "event_source",
    "assessment_report_selection",
]


# ============================================================================
# Standard evidence row
# ============================================================================


@dataclass
class EvidenceTableRow:
    selection: str = "☐"
    time: str = ""
    compliance_check: str = "—"
    evidence_by_type: str = ""
    data_source: str = ""
    event_name: str = ""
    event_source: str = ""
    assessment_report_selection: str = "No"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the evidence row into the standard report representation.
        """

        return {
            "selection": self.selection,
            "time": self.time,
            "compliance_check": self.compliance_check,
            "evidence_by_type": self.evidence_by_type,
            "data_source": self.data_source,
            "event_name": self.event_name,
            "event_source": self.event_source,
            "assessment_report_selection": self.assessment_report_selection,
        }


# ============================================================================
# Evidence table
# ============================================================================


@dataclass
class EvidenceTable:
    title: str = "Evidence"

    rows: list[EvidenceTableRow] = field(
        default_factory=list,
    )

    @property
    def total_evidence(self) -> int:
        """
        Return the number of evidence rows in the table.
        """

        return len(self.rows)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the complete evidence table into a serializable dictionary.
        """

        return {
            "title": self.title,
            "total_evidence": self.total_evidence,
            "columns": list(EVIDENCE_COLUMNS),
            "rows": [row.to_dict() for row in self.rows],
        }


# ============================================================================
# Universal evidence builder
# ============================================================================


class EvidenceTableBuilder:
    """
    Framework/provider-independent evidence table.

    Works with:

        Azure
        Entra
        AWS
        GCP
        Microsoft 365
        Defender
        Security Hub
        ISO 27001
        SOC 2
        NIST
        CIS
        PCI DSS
        etc.

    The builder converts normalized evidence into the common report
    representation.

    IMPORTANT:

    The original evidence objects are NOT retained here.

    Only the fields needed by the human-readable report table are
    retained.
    """

    def __init__(
        self,
        title: str = "Evidence",
    ) -> None:

        self.title = title

        self._rows: list[EvidenceTableRow] = []

    # =========================================================================
    # Add a single row
    # =========================================================================

    def add(
        self,
        *,
        time: Any = None,
        compliance_check: Any = "Passed",
        evidence_by_type: Any = "",
        data_source: Any = "",
        event_name: Any = "",
        event_source: Any = "",
        assessment_report_selection: Any = "No",
        selection: str = "☐",
    ) -> EvidenceTableRow:
        """
        Add one normalized evidence row.

        Existing callers can continue to pass any values supported by the
        previous implementation.

        Time behaviour:

            - If a source timestamp is supplied, that timestamp is used.
            - If no timestamp is supplied, the evidence table generates the
              current UTC time automatically.
        """

        row = EvidenceTableRow(
            selection=self.to_text(
                selection,
            ),
            time=self.format_time(
                time,
            ),
            compliance_check=self.format_status(
                compliance_check,
            ),
            evidence_by_type=self.to_text(
                evidence_by_type,
            ),
            data_source=self.to_text(
                data_source,
            ),
            event_name=self.to_text(
                event_name,
            ),
            event_source=self.to_text(
                event_source,
            ),
            assessment_report_selection=self.to_text(
                assessment_report_selection,
            ),
        )

        self._rows.append(row)

        return row

    # =========================================================================
    # Add normalized records
    # =========================================================================

    def add_records(
        self,
        records: Iterable[Any],
        *,
        source: str = "",
        evidence_type: str = "",
        default_status: str = "Passed",
        field_mapping: dict[str, str] | None = None,
    ) -> None:
        """
        Add records from any collector.

        `field_mapping` allows a collector with unusual field names
        to map them into the standard table.

        Example:

            builder.add_records(
                azure_records,
                source="Azure",
                evidence_type="Azure resource",
            )

        Or:

            builder.add_records(
                aws_records,
                source="AWS Security Hub",
                evidence_type="Compliance check",
            )

        Timestamp behaviour:

            - A collector-supplied timestamp is used when available.
            - If the collector provides no timestamp, EvidenceTableBuilder
              automatically generates the current UTC time for that row.
        """

        mapping = field_mapping or {}

        for record in records:

            data = self.extract_data(
                record,
            )

            self.add(
                time=self.get_field(
                    data,
                    mapping.get(
                        "time",
                    ),
                    (
                        "timestamp",
                        "time",
                        "created_at",
                        "collected_at",
                        "event_time",
                    ),
                ),
                compliance_check=self.get_field(
                    data,
                    mapping.get(
                        "compliance_check",
                    ),
                    (
                        "compliance_check",
                        "compliance_status",
                        "assessment_status",
                        "status",
                    ),
                    default_status,
                ),
                evidence_by_type=self.get_field(
                    data,
                    mapping.get(
                        "evidence_by_type",
                    ),
                    (
                        "evidence_type",
                        "type",
                        "category",
                    ),
                    evidence_type,
                ),
                data_source=self.get_field(
                    data,
                    mapping.get(
                        "data_source",
                    ),
                    (
                        "data_source",
                        "provider",
                        "source",
                    ),
                    source,
                ),
                event_name=self.get_field(
                    data,
                    mapping.get(
                        "event_name",
                    ),
                    (
                        "event_name",
                        "event",
                        "name",
                        "display_name",
                    ),
                    "",
                ),
                event_source=self.get_field(
                    data,
                    mapping.get(
                        "event_source",
                    ),
                    (
                        "event_source",
                        "source_system",
                        "service",
                        "resource_type",
                    ),
                    "",
                ),
                assessment_report_selection=self.get_field(
                    data,
                    mapping.get(
                        "assessment_report_selection",
                    ),
                    (
                        "assessment_report_selection",
                        "included_in_report",
                        "in_assessment",
                    ),
                    "No",
                ),
            )

    # =========================================================================
    # Build
    # =========================================================================

    def build(self) -> EvidenceTable:
        """
        Build the final evidence table.

        A copy of the current rows is used so subsequent additions to
        the builder do not modify an already-built table.
        """

        return EvidenceTable(
            title=self.title,
            rows=list(
                self._rows,
            ),
        )

    # =========================================================================
    # Helpers
    # =========================================================================

    @staticmethod
    def extract_data(
        record: Any,
    ) -> dict[str, Any]:
        """
        Extract normalized evidence data safely.

        Supported record types:

            1. Dictionary / Mapping-based records

                {
                    "data": {
                        ...
                    }
                }

                or:

                {
                    "timestamp": "...",
                    "provider": "Azure",
                    ...
                }

            2. EvidenceRecord-style objects exposing `data`

            3. Pydantic v2 models exposing `model_dump()`

            4. Pydantic v1 models exposing `dict()`

        The Mapping check is deliberately performed before object-based
        extraction. This prevents dictionary-like records from being
        treated as arbitrary objects.

        The returned dictionary is a new dictionary. The original evidence
        object is never retained or modified.
        """

        # ---------------------------------------------------------------------
        # Mapping-based records
        # ---------------------------------------------------------------------

        if isinstance(
            record,
            Mapping,
        ):

            data = record.get(
                "data",
                record,
            )

            if isinstance(
                data,
                Mapping,
            ):
                return dict(data)

            return {}

        # ---------------------------------------------------------------------
        # EvidenceRecord-style objects
        # ---------------------------------------------------------------------

        data = getattr(
            record,
            "data",
            None,
        )

        if isinstance(
            data,
            Mapping,
        ):
            return dict(data)

        # ---------------------------------------------------------------------
        # Pydantic v2 models
        # ---------------------------------------------------------------------

        model_dump = getattr(
            record,
            "model_dump",
            None,
        )

        if callable(
            model_dump,
        ):

            try:
                dumped = model_dump()

            except (TypeError, ValueError):
                # Some model implementations may require arguments or may
                # reject serialization. They are not usable by this generic
                # extractor, so continue to the Pydantic v1 fallback.
                dumped = None

            if isinstance(
                dumped,
                Mapping,
            ):

                data = dumped.get(
                    "data",
                    dumped,
                )

                if isinstance(
                    data,
                    Mapping,
                ):
                    return dict(data)

        # ---------------------------------------------------------------------
        # Pydantic v1 models
        # ---------------------------------------------------------------------

        dict_method = getattr(
            record,
            "dict",
            None,
        )

        if callable(
            dict_method,
        ):

            try:
                dumped = dict_method()

            except (TypeError, ValueError):
                # Some custom implementations may require arguments.
                dumped = None

            if isinstance(
                dumped,
                Mapping,
            ):

                data = dumped.get(
                    "data",
                    dumped,
                )

                if isinstance(
                    data,
                    Mapping,
                ):
                    return dict(data)

        # ---------------------------------------------------------------------
        # Unsupported / empty record
        # ---------------------------------------------------------------------

        return {}

    # =========================================================================
    # Field lookup
    # =========================================================================

    @staticmethod
    def get_field(
        data: Mapping[str, Any],
        explicit_field: str | None,
        candidates: tuple[str, ...],
        default: Any = "",
    ) -> Any:
        """
        Retrieve a value from normalized evidence.

        Explicit mapping wins over candidate field names.

        Example:

            field_mapping={
                "event_name": "displayName",
            }

        Empty/None values do not override a usable default.
        """

        if explicit_field:

            value = data.get(
                explicit_field,
            )

            if value is not None:
                return value

        for field_name in candidates:

            value = data.get(
                field_name,
            )

            if value is not None:
                return value

        return default

    # =========================================================================
    # Text formatting
    # =========================================================================

    @staticmethod
    def to_text(
        value: Any,
    ) -> str:
        """
        Convert a value into human-readable text.

        Existing dictionary/list formatting is intentionally preserved using
        Python's normal string representation.
        """

        if value is None:
            return ""

        if isinstance(
            value,
            dict,
        ):
            return str(value)

        if isinstance(
            value,
            list,
        ):
            return str(value)

        return str(value)

    # =========================================================================
    # Time formatting
    # =========================================================================

    @staticmethod
    def format_time(
        value: Any,
    ) -> str:
        """
        Normalize timestamps for the report.

        Behaviour:

            1. If a valid datetime is supplied:
                   use the supplied datetime.

            2. If a valid ISO-8601 timestamp string is supplied:
                   use the supplied timestamp.

            3. If the supplied timestamp has no timezone:
                   treat it as UTC.

            4. If no timestamp is supplied:
                   generate the current UTC time.

            5. If a non-empty timestamp string cannot be parsed:
                   preserve the supplied value rather than replacing it.

        All valid timestamps are displayed as time only:

            06:30:00 PM UTC

        This means Azure-supplied timestamps take precedence. If Azure
        supplies no timestamp, the evidence table itself generates one.
        """

        # ---------------------------------------------------------------------
        # No timestamp supplied
        #
        # This is the important fallback. Every evidence row now receives
        # a timestamp even when the collector did not provide one.
        # ---------------------------------------------------------------------

        if value is None:

            return datetime.now(
                timezone.utc,
            ).strftime(
                "%I:%M:%S %p UTC",
            )

        # ---------------------------------------------------------------------
        # Datetime values
        # ---------------------------------------------------------------------

        if isinstance(
            value,
            datetime,
        ):

            if value.tzinfo is None:

                value = value.replace(
                    tzinfo=timezone.utc,
                )

            value = value.astimezone(
                timezone.utc,
            )

            return value.strftime(
                "%I:%M:%S %p UTC",
            )

        # ---------------------------------------------------------------------
        # String timestamps
        # ---------------------------------------------------------------------

        if isinstance(
            value,
            str,
        ):

            text = value.strip()

            # Empty strings are equivalent to no timestamp. Generate the
            # evidence-table timestamp rather than leaving the column blank.
            if not text:

                return datetime.now(
                    timezone.utc,
                ).strftime(
                    "%I:%M:%S %p UTC",
                )

            try:
                # Support ISO-8601 timestamps ending in "Z".
                parsed = datetime.fromisoformat(
                    text.replace(
                        "Z",
                        "+00:00",
                    ),
                )

            except ValueError:
                # The collector did supply a value, but it is not a standard
                # ISO timestamp. Preserve the supplied Azure/source value
                # rather than replacing it.
                return text

            if parsed.tzinfo is None:

                parsed = parsed.replace(
                    tzinfo=timezone.utc,
                )

            parsed = parsed.astimezone(
                timezone.utc,
            )

            return parsed.strftime(
                "%I:%M:%S %p UTC",
            )

        # ---------------------------------------------------------------------
        # Other values
        #
        # Preserve existing behaviour for non-string/non-datetime values.
        # ---------------------------------------------------------------------

        return str(value)

    # =========================================================================
    # Status formatting
    # =========================================================================

    @staticmethod
    def format_status(
        value: Any,
    ) -> str:
        """
        Convert common status values into the standard report format.

        Examples:

            Passed       -> ✓ Passed
            compliant    -> ✓ Passed
            warning      -> ⚠ Warning
            failed       -> ⊗ Failed
            unknown      -> — Not assessed

        Boolean values are also supported:

            True         -> ✓ Passed
            False        -> ⊗ Failed

        Unknown status values are preserved unchanged.
        """

        if value is None:
            return "—"

        # ---------------------------------------------------------------------
        # Boolean status
        #
        # Check bool before converting to string because:
        #
        #     str(True)  -> "True"
        #     str(False) -> "False"
        #
        # ---------------------------------------------------------------------

        if isinstance(
            value,
            bool,
        ):

            if value:
                return "✓ Passed"

            return "⊗ Failed"

        normalized = (
            str(
                value,
            )
            .strip()
            .lower()
        )

        # ---------------------------------------------------------------------
        # Passed
        # ---------------------------------------------------------------------

        if normalized in {
            "pass",
            "passed",
            "success",
            "successful",
            "compliant",
            "ok",
        }:

            return "✓ Passed"

        # ---------------------------------------------------------------------
        # Warning
        # ---------------------------------------------------------------------

        if normalized in {
            "warning",
            "warn",
            "partial",
            "partially_met",
            "partially-met",
            "attention",
            "at_risk",
            "at-risk",
        }:

            return "⚠ Warning"

        # ---------------------------------------------------------------------
        # Failed
        # ---------------------------------------------------------------------

        if normalized in {
            "fail",
            "failed",
            "failure",
            "non_compliant",
            "non-compliant",
            "not_compliant",
            "not-compliant",
            "error",
        }:

            return "⊗ Failed"

        # ---------------------------------------------------------------------
        # Not assessed
        # ---------------------------------------------------------------------

        if normalized in {
            "not_assessed",
            "not-assessed",
            "not assessed",
            "unknown",
            "not_evaluated",
            "not-evaluated",
        }:

            return "— Not assessed"

        # ---------------------------------------------------------------------
        # Preserve unknown status values
        # ---------------------------------------------------------------------

        return str(value)
