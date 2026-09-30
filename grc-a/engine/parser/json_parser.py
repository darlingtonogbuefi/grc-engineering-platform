# engine\parser\json_parser.py


"""
JSON Parser

Handles:

- Evidence documents
- Schema files
- Reports
- API payloads
"""

from __future__ import annotations

import json

from pathlib import Path

from typing import Any

from ..exceptions import ConfigurationError


class JSONParser:
    """
    Generic JSON parser.
    """

    def load(self, path: Path) -> dict[str, Any]:
        """
        Load JSON document.
        """

        if not path.exists():

            raise ConfigurationError(f"JSON file not found: {path}")

        try:

            with path.open("r", encoding="utf-8") as file:

                data = json.load(file)

        except json.JSONDecodeError as exc:

            raise ConfigurationError(f"Invalid JSON file: {path}") from exc

        if not isinstance(data, dict):

            raise ConfigurationError(f"JSON root must be an object: {path}")

        return data

    def save(self, path: Path, data: dict[str, Any]) -> None:
        """
        Save JSON document.
        """

        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:

            json.dump(data, file, indent=4, ensure_ascii=False)
