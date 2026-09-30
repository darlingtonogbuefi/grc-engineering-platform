#  engine\parser\yaml_parser.py


"""
YAML Configuration Parser

Handles:

- Framework definitions
- Collector definitions
- Tenant configuration
- Reporting configuration
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ..exceptions import ConfigurationError


class YAMLParser:
    """
    Generic YAML parser.
    """

    def load(self, path: Path) -> dict[str, Any]:
        """
        Load YAML file.

        Args:
            path:
                YAML file location

        Returns:
            Parsed dictionary
        """

        if not path.exists():

            raise ConfigurationError(f"YAML file not found: {path}")

        try:

            with path.open("r", encoding="utf-8") as file:

                data = yaml.safe_load(file)

        except yaml.YAMLError as exc:

            raise ConfigurationError(f"Unable to parse YAML: {path}") from exc

        if data is None:

            return {}

        if not isinstance(data, dict):

            raise ConfigurationError(f"Invalid YAML structure: {path}")

        return data

    def load_multiple(self, paths: list[Path]) -> dict[str, dict[str, Any]]:
        """
        Load multiple YAML files.
        """

        results: dict[str, dict[str, Any]] = {}

        for path in paths:

            results[path.stem] = self.load(path)

        return results
