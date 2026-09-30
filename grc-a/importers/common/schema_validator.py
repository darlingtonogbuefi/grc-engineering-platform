"""
Schema Validator

Validates generated framework files.

Initial implementation:
- Provides validation interface
- Checks files exist
- Placeholder for JSON Schema validation

Future:
- jsonschema package integration
- schema versioning
- detailed validation reports
"""

from pathlib import Path
from typing import Dict, List


class SchemaValidator:
    """
    Framework YAML validation engine.
    """


    def __init__(
        self,
        schemas: Dict[str, str] | None = None
    ):
        """
        Args:

            schemas:
                Mapping of schema names to files.

        Example:

            {
                "control":
                    "schemas/control.schema.json"
            }
        """

        self.schemas = schemas or {}


    # ------------------------------------------------------------------
    # Single File Validation
    # ------------------------------------------------------------------

    def validate(
        self,
        filename: str,
        schema_name: str | None = None
    ) -> bool:
        """
        Validate a single YAML file.

        Current implementation:
        - Checks file exists

        Future:
        - Load JSON schema
        - Validate YAML structure
        """

        path = Path(filename)


        if not path.exists():

            raise FileNotFoundError(
                f"File not found: {filename}"
            )


        # Placeholder for JSON Schema validation

        return True


    # ------------------------------------------------------------------
    # Directory Validation
    # ------------------------------------------------------------------

    def validate_directory(
        self,
        directory: str
    ) -> Dict[str, bool]:
        """
        Validate all YAML files in a directory.

        Example:

            frameworks/CAF/

        Returns:

        {
            "metadata.yml": True,
            "controls.yml": True
        }
        """

        path = Path(directory)


        if not path.exists():

            raise FileNotFoundError(
                f"Directory not found: {directory}"
            )


        results = {}


        for file in path.glob("*.yml"):

            results[file.name] = self.validate(
                str(file)
            )


        return results
