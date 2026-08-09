# collectors\entra\tests\unit\test_normalizers.py


"""
Microsoft Entra normalizer unit tests.

Validates:
- Normalizer modules load
- Expected normalization functions exist
- Returned data structure is consistent
"""

from __future__ import annotations

import importlib

NORMALIZERS = [
    "users",
    "groups",
    "devices",
    "applications",
    "roles",
    "logs",
    "policies",
]


def test_normalizer_modules_load():

    for normalizer in NORMALIZERS:

        module = importlib.import_module(f"collectors.entra.normalizers.{normalizer}")

        assert module is not None


def test_normalizers_have_normalize_function():

    for normalizer in NORMALIZERS:

        module = importlib.import_module(f"collectors.entra.normalizers.{normalizer}")

        assert hasattr(
            module,
            "normalize",
        ), f"{normalizer} missing normalize()"


def test_user_normalizer():

    module = importlib.import_module("collectors.entra.normalizers.users")

    data = {
        "id": "user-001",
        "displayName": "Alice Smith",
    }

    result = module.normalize(data)

    assert isinstance(
        result,
        dict,
    )

    assert result["id"] == "user-001"

    assert result["display_name"] == "Alice Smith"


def test_group_normalizer():

    module = importlib.import_module("collectors.entra.normalizers.groups")

    data = {
        "id": "group-001",
        "displayName": "Admins",
    }

    result = module.normalize(data)

    assert isinstance(
        result,
        dict,
    )

    assert result["id"] == "group-001"

    assert result["display_name"] == "Admins"
