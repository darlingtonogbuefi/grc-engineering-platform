"""
Common Microsoft Entra normalizers.

Provides shared normalization helpers used
across Entra evidence collectors.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional


def normalize_datetime(
    value: Optional[str],
) -> Optional[str]:
    """
    Normalize Microsoft Graph datetime values.

    Keeps ISO-8601 format while ensuring
    consistent handling of empty values.
    """

    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00",
            )
        )

        return parsed.isoformat()

    except ValueError:
        return value


def normalize_object_id(
    obj: Dict[str, Any],
) -> Optional[str]:
    """
    Extract a Microsoft Graph object ID.
    """

    return obj.get(
        "id"
    )


def normalize_name(
    obj: Dict[str, Any],
) -> Optional[str]:
    """
    Extract common display name fields.
    """

    return (
        obj.get(
            "displayName"
        )
        or obj.get(
            "name"
        )
        or obj.get(
            "userPrincipalName"
        )
    )


def normalize_collection(
    items: Optional[
        Iterable[Dict[str, Any]]
    ],
) -> List[Dict[str, Any]]:
    """
    Normalize a Graph object collection.

    Keeps only commonly useful evidence
    fields.
    """

    if not items:
        return []

    return [
        remove_empty_values(
            {
                "id": item.get(
                    "id"
                ),
                "display_name": (
                    item.get(
                        "displayName"
                    )
                    or item.get(
                        "name"
                    )
                ),
            }
        )
        for item in items
    ]


def normalize_reference(
    obj: Optional[
        Dict[str, Any]
    ],
) -> Optional[
    Dict[str, Any]
]:
    """
    Normalize a Graph reference object.
    """

    if not obj:
        return None

    return remove_empty_values(
        {
            "id": obj.get(
                "id"
            ),
            "display_name": (
                obj.get(
                    "displayName"
                )
                or obj.get(
                    "name"
                )
            ),
        }
    )


def normalize_boolean(
    value: Any,
) -> Optional[bool]:
    """
    Normalize boolean values returned
    by Microsoft Graph.
    """

    if value is None:
        return None

    if isinstance(
        value,
        bool,
    ):
        return value

    if isinstance(
        value,
        str,
    ):
        return value.lower() in (
            "true",
            "yes",
            "1",
        )

    return bool(
        value
    )


def remove_empty_values(
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Recursively remove None values from
    evidence objects.

    Nested dictionaries and lists are
    cleaned while preserving empty lists
    and other valid values.
    """

    def _clean(
        value: Any,
    ) -> Any:
        if isinstance(
            value,
            dict,
        ):
            return {
                key: _clean(
                    item
                )
                for key, item in value.items()
                if item is not None
            }

        if isinstance(
            value,
            list,
        ):
            return [
                _clean(
                    item
                )
                for item in value
                if item is not None
            ]

        return value

    return {
        key: _clean(
            value
        )
        for key, value in data.items()
        if value is not None
    }
