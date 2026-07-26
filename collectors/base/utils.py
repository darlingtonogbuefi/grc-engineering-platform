"""
Collector Utility Functions.

Shared helpers used across evidence collectors.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict
from pathlib import Path
import hashlib
import json
import re
import uuid


def utc_now() -> datetime:
    """Return current UTC timestamp."""

    return datetime.now(timezone.utc)


def generate_id() -> str:
    """Generate unique identifier."""

    return str(uuid.uuid4())


def json_hash(
    data: Any,
) -> str:
    """
    Generate SHA256 hash from JSON data.
    """

    payload = json.dumps(
        data,
        sort_keys=True,
        default=str,
    ).encode("utf-8")

    return hashlib.sha256(
        payload
    ).hexdigest()


def json_serialise(
    data: Any,
    indent: int | None = None,
) -> str:
    """
    Safely serialise object to JSON.
    """

    return json.dumps(
        data,
        indent=indent,
        default=str,
    )


def normalise_name(
    value: str,
) -> str:
    """
    Convert names into safe identifiers.

    Example:

        "Conditional Access Policy"
        ->
        "conditional_access_policy"
    """

    value = value.lower()

    value = re.sub(
        r"[^a-z0-9]+",
        "_",
        value,
    )

    return value.strip("_")


def ensure_directory(
    path: str | Path,
) -> Path:
    """
    Create directory if missing.
    """

    directory = Path(path)

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return directory


def get_nested(
    data: Dict[str, Any],
    path: str,
    default: Any = None,
) -> Any:
    """
    Safely retrieve nested dictionary value.

    Example:

        get_nested(
            user,
            "department.name"
        )
    """

    current = data

    for key in path.split("."):

        if not isinstance(
            current,
            dict,
        ):
            return default

        current = current.get(
            key,
            default,
        )

    return current


def chunk_list(
    items: list,
    size: int,
) -> list[list]:
    """
    Split list into chunks.

    Useful for API limits.
    """

    return [
        items[index:index + size]
        for index in range(
            0,
            len(items),
            size,
        )
    ]
