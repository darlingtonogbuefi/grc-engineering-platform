"""
Microsoft Entra query module unit tests.

Validates:
- Query modules load correctly
- Query definitions return expected structure
- Required query metadata exists
"""

from __future__ import annotations

import importlib


QUERY_MODULES = [

    "users",
    "groups",
    "devices",
    "applications",
    "audit_logs",
    "authentication_methods",
    "conditional_access",
    "directory_roles",
    "licenses",
    "organization",
    "privileged_identity_management",
    "service_principals",
    "signins",
]


REQUIRED_FIELDS = [
    "name",
    "endpoint",
    "method",
    "params",
]


def test_query_modules_load():

    for module_name in QUERY_MODULES:

        module = importlib.import_module(
            f"collectors.entra.queries.{module_name}"
        )

        assert module is not None


def test_query_definitions():

    for module_name in QUERY_MODULES:

        module = importlib.import_module(
            f"collectors.entra.queries.{module_name}"
        )

        result = module.query()

        assert isinstance(
            result,
            dict,
        )

        for field in REQUIRED_FIELDS:

            assert field in result, (
                f"{module_name} missing "
                f"required field: {field}"
            )


def test_query_methods():

    for module_name in QUERY_MODULES:

        module = importlib.import_module(
            f"collectors.entra.queries.{module_name}"
        )

        result = module.query()

        assert result["method"] in [
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        ]


def test_query_params():

    for module_name in QUERY_MODULES:

        module = importlib.import_module(
            f"collectors.entra.queries.{module_name}"
        )

        result = module.query()

        assert isinstance(
            result["params"],
            dict,
        )
