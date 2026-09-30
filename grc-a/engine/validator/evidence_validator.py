# engine\validator\evidence_validator.py

"""
Evidence Validation

Validates normalised evidence after parsing.

Checks include:

- JSON Schema compliance
- Required metadata
- Collector identity
- Tenant identity
- Timestamp
- Evidence payload
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ..exceptions import ConfigurationError
from .schema_validator import SchemaValidator


class EvidenceValidator:
    """
    Validate collected evidence.
    """

    REQUIRED_FIELDS = {
        "evidence_id",
        "collected_at",
        "source",
        "status",
        "data",
    }

    VALID_STATUSES = {
        "collected",
        "validated",
        "processed",
        "failed",
    }

    def __init__(
        self,
        schema_validator: SchemaValidator | None = None,
    ) -> None:
        self.schema_validator = schema_validator or SchemaValidator()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(
        self,
        evidence: dict[str, Any],
    ) -> None:
        self.schema_validator.validate_evidence(evidence)

        self._validate_required_fields(evidence)

        self._validate_timestamp(evidence)

        self._validate_status(evidence)

        self._validate_payload(evidence)

    # ------------------------------------------------------------------

    def _validate_required_fields(
        self,
        evidence: dict[str, Any],
    ) -> None:
        missing = self.REQUIRED_FIELDS.difference(evidence.keys())

        if missing:
            raise ConfigurationError(
                "Evidence missing required fields: " + ", ".join(sorted(missing))
            )

    # ------------------------------------------------------------------

    def _validate_timestamp(
        self,
        evidence: dict[str, Any],
    ) -> None:
        timestamp = evidence.get("collected_at")

        if not isinstance(timestamp, str):
            raise ConfigurationError("collected_at must be a string.")

        try:
            datetime.fromisoformat(
                timestamp.replace(
                    "Z",
                    "+00:00",
                )
            )
        except ValueError as exc:
            raise ConfigurationError("Invalid collected_at timestamp.") from exc

    # ------------------------------------------------------------------

    def _validate_status(
        self,
        evidence: dict[str, Any],
    ) -> None:
        status = evidence.get("status")

        if status not in self.VALID_STATUSES:
            raise ConfigurationError(f"Unsupported evidence status: {status}")

    # ------------------------------------------------------------------

    def _validate_payload(
        self,
        evidence: dict[str, Any],
    ) -> None:
        payload = evidence.get("data")

        if not isinstance(
            payload,
            dict,
        ):
            raise ConfigurationError("Evidence payload must be an object.")

    # ------------------------------------------------------------------

    def validate_collection(
        self,
        evidence_items: list[dict[str, Any]],
    ) -> None:
        for evidence in evidence_items:
            self.validate(evidence)
