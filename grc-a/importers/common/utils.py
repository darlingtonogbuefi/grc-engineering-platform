"""
Importer Utility Functions

Shared helper functions used throughout the importer pipeline.

Responsibilities:

- Clean imported text
- Parse multi-line spreadsheet cells
- Parse comma-separated values
- Normalise identifiers
- Convert Excel column letters into indexes

These utilities are framework-independent.
"""

import re
from typing import Any, List, Optional


# ---------------------------------------------------------------------------
# Text Cleaning
# ---------------------------------------------------------------------------

def clean_text(value: Any) -> str:
    """
    Clean imported text values.

    Handles:
    - None values
    - Excel empty cells
    - Leading/trailing whitespace
    - Multiple spaces

    Example:

        clean_text("  CAF Control  ")
        returns:
        "CAF Control"
    """

    if value is None:
        return ""

    text = str(value)

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ---------------------------------------------------------------------------
# Multi-line Cell Parsing
# ---------------------------------------------------------------------------

def split_lines(value: Any) -> List[str]:
    """
    Split multi-line spreadsheet cells into a list.

    Example Excel cell:

        Control 1
        Control 2
        Control 3

    Returns:

        [
            "Control 1",
            "Control 2",
            "Control 3"
        ]
    """

    if not value:
        return []

    lines = str(value).splitlines()

    return [
        clean_text(line)
        for line in lines
        if clean_text(line)
    ]


# ---------------------------------------------------------------------------
# CSV / List Parsing
# ---------------------------------------------------------------------------

def split_csv(value: Any) -> List[str]:
    """
    Convert comma-separated values into a list.

    Example:

        "NIST, ISO27001, CIS"

    Returns:

        [
            "NIST",
            "ISO27001",
            "CIS"
        ]
    """

    if not value:
        return []

    return [
        clean_text(item)
        for item in str(value).split(",")
        if clean_text(item)
    ]


# ---------------------------------------------------------------------------
# Identifier Normalisation
# ---------------------------------------------------------------------------

def normalise_identifier(value: Any) -> str:
    """
    Convert identifiers into consistent format.

    Examples:

        "A1.a"
            ->
        "A1_A"

        "ISO 27001"
            ->
        "ISO_27001"

    Used for:
    - control IDs
    - framework IDs
    - capability IDs
    """

    if not value:
        return ""

    value = clean_text(value)

    value = value.lower()

    value = re.sub(
        r"[^a-z0-9]+",
        "_",
        value
    )

    return value.strip("_")


# ---------------------------------------------------------------------------
# Excel Column Handling
# ---------------------------------------------------------------------------

def column_letter_to_index(column: str) -> int:
    """
    Convert Excel column letters into zero-based indexes.

    Examples:

        A -> 0
        B -> 1
        Z -> 25
        AA -> 26

    Compatible with Python lists.
    """

    if not column:
        raise ValueError(
            "Column letter cannot be empty"
        )

    column = column.upper()

    if not re.match(
        r"^[A-Z]+$",
        column
    ):
        raise ValueError(
            f"Invalid Excel column: {column}"
        )

    index = 0

    for char in column:
        index = (
            index * 26
            +
            ord(char)
            -
            ord("A")
            +
            1
        )

    return index - 1


# ---------------------------------------------------------------------------
# Dictionary Helpers
# ---------------------------------------------------------------------------

def get_nested_value(
    data: dict,
    keys: List[str],
    default: Optional[Any] = None
):
    """
    Safely retrieve nested dictionary values.

    Example:

        get_nested_value(
            config,
            ["columns", "id"]
        )
    """

    current = data

    for key in keys:

        if not isinstance(current, dict):
            return default

        if key not in current:
            return default

        current = current[key]

    return current


# ---------------------------------------------------------------------------
# File Helpers
# ---------------------------------------------------------------------------

def ensure_list(value: Any) -> List[Any]:
    """
    Ensure a value is always returned as a list.

    Examples:

        "CAF"
            ->
        ["CAF"]

        ["CAF", "ISO"]
            ->
        ["CAF", "ISO"]
    """

    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]
