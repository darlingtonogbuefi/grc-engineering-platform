"""
JSON Schema Validation

Responsible for validating all platform objects
against the schemas located in:

    schemas/

Supported schemas

- evidence.schema.json
- control.schema.json
- framework.schema.json
- collector.schema.json
- tenant.schema.json
- report.schema.json
- risk.schema.json
"""

from __future__ import annotations

import json
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema import ValidationError as JSONSchemaValidationError

from ..config import RuntimeConfig, load_configuration
from ..exceptions import ConfigurationError


class SchemaValidator:
    """
    JSON Schema validator.

    Example

        validator = SchemaValidator()

        validator.validate(
            evidence,
            "evidence.schema.json"
        )
    """

    def __init__(
        self,
        config: RuntimeConfig | None = None,
    ) -> None:

        self.config = config or load_configuration()

        self.schema_directory = (
            self.config.paths.schemas
        )

        self._cache: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Schema loading
    # ------------------------------------------------------------------

    def load_schema(
        self,
        schema_name: str,
    ) -> dict[str, Any]:
        """
        Load a schema from the schemas directory.
        """

        if schema_name in self._cache:
            return self._cache[schema_name]

        schema_file = (
            self.schema_directory /
            schema_name
        )

        if not schema_file.exists():

            raise ConfigurationError(
                f"Schema not found: {schema_file}"
            )

        try:

            with schema_file.open(
                "r",
                encoding="utf-8",
            ) as file:

                schema = json.load(file)

        except json.JSONDecodeError as exc:

            raise ConfigurationError(
                f"Invalid JSON schema: {schema_file}"
            ) from exc

        self._cache[schema_name] = schema

        return schema

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(
        self,
        document: dict[str, Any],
        schema_name: str,
    ) -> None:
        """
        Validate a document against a schema.

        Raises ConfigurationError on failure.
        """

        schema = self.load_schema(
            schema_name
        )

        validator = Draft202012Validator(
            schema
        )

        errors = sorted(
            validator.iter_errors(document),
            key=lambda e: list(e.path),
        )

        if errors:

            message = self._format_errors(
                errors
            )

            raise ConfigurationError(
                message
            )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_errors(
        errors: list[JSONSchemaValidationError],
    ) -> str:
        """
        Convert validation errors into
        a readable message.
        """

        messages: list[str] = []

        for error in errors:

            location = (
                ".".join(
                    str(item)
                    for item in error.path
                )
                or "<root>"
            )

            messages.append(
                f"{location}: {error.message}"
            )

        return (
            "Schema validation failed:\n"
            + "\n".join(messages)
        )

    # ------------------------------------------------------------------
    # Convenience methods
    # ------------------------------------------------------------------

    def validate_evidence(
        self,
        evidence: dict[str, Any],
    ) -> None:

        self.validate(
            evidence,
            "evidence.schema.json",
        )

    def validate_control(
        self,
        control: dict[str, Any],
    ) -> None:

        self.validate(
            control,
            "control.schema.json",
        )

    def validate_framework(
        self,
        framework: dict[str, Any],
    ) -> None:

        self.validate(
            framework,
            "framework.schema.json",
        )

    def validate_collector(
        self,
        collector: dict[str, Any],
    ) -> None:

        self.validate(
            collector,
            "collector.schema.json",
        )

    def validate_tenant(
        self,
        tenant: dict[str, Any],
    ) -> None:

        self.validate(
            tenant,
            "tenant.schema.json",
        )

    def validate_report(
        self,
        report: dict[str, Any],
    ) -> None:

        self.validate(
            report,
            "report.schema.json",
        )

    def validate_risk(
        self,
        risk: dict[str, Any],
    ) -> None:

        self.validate(
            risk,
            "risk.schema.json",
        )

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def available_schemas(
        self,
    ) -> list[str]:
        """
        Return all available schema files.
        """

        return sorted(
            path.name
            for path in self.schema_directory.glob(
                "*.json"
            )
        )
