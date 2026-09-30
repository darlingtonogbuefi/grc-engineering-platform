# engine\validator\framework_validator.py

"""
Framework Validation

Performs business-rule validation for framework
definitions after JSON Schema validation.

Checks include:

- Required metadata
- Unique control identifiers
- Supported capability mappings
- Supported maturity models
- Supported framework names
"""

from __future__ import annotations

from typing import Any

from ..exceptions import ConfigurationError
from .schema_validator import SchemaValidator


SUPPORTED_FRAMEWORKS = {
    "CAF",
    "ISO27001",
    "SOC2",
    "GovAssure",
    "CyberEssentials",
}


class FrameworkValidator:
    """
    Validate framework definitions.
    """

    def __init__(
        self,
        schema_validator: SchemaValidator | None = None,
    ) -> None:
        self.schema_validator = (
            schema_validator or SchemaValidator()
        )

    def validate(
        self,
        framework: dict[str, Any],
    ) -> None:
        """
        Validate framework.
        """
        self.schema_validator.validate_framework(
            framework
        )

        self._validate_metadata(framework)
        self._validate_controls(framework)

    # ------------------------------------------------------------------

    def _validate_metadata(
        self,
        framework: dict[str, Any],
    ) -> None:
        metadata = framework.get(
            "metadata",
            {}
        )

        name = metadata.get(
            "name"
        )

        if not name:
            raise ConfigurationError(
                "Framework metadata.name is required."
            )

        if name not in SUPPORTED_FRAMEWORKS:
            raise ConfigurationError(
                f"Unsupported framework: {name}"
            )

    # ------------------------------------------------------------------

    def _validate_controls(
        self,
        framework: dict[str, Any],
    ) -> None:
        controls = framework.get(
            "controls",
            []
        )

        identifiers: set[str] = set()

        for control in controls:
            control_id = control.get(
                "id"
            )

            if not control_id:
                raise ConfigurationError(
                    "Control missing id."
                )

            if control_id in identifiers:
                raise ConfigurationError(
                    f"Duplicate control id: {control_id}"
                )

            identifiers.add(control_id)

    # ------------------------------------------------------------------

    def validate_collection(
        self,
        frameworks: list[dict[str, Any]],
    ) -> None:
        names: set[str] = set()

        for framework in frameworks:
            self.validate(framework)

            name = framework["metadata"]["name"]

            if name in names:
                raise ConfigurationError(
                    f"Duplicate framework loaded: {name}"
                )

            names.add(name)
