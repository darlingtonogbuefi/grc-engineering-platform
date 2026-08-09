"""
Azure query definition unit tests.

Validates:
- Query YAML files load
- Required query metadata exists
- Referenced normalizers exist
- Query structure is consistent
"""

from __future__ import annotations

import importlib
from pathlib import Path

import yaml

QUERY_PATH = Path("collectors/azure/queries")


NORMALIZER_PATH = "collectors.azure.normalizers"


EXPECTED_QUERIES = [
    "activity-logs",
    "backup-vaults",
    "defender-settings",
    "diagnostic-settings",
    "firewalls",
    "key-vaults",
    "network-security-groups",
    "policy-assignments",
    "policy-definitions",
    "resource-groups",
    "resources",
    "role-assignments",
    "role-definitions",
    "sql-databases",
    "storage-accounts",
    "subscriptions",
    "virtual-machines",
    "virtual-networks",
]


def load_query(
    name: str,
) -> dict:

    path = QUERY_PATH / f"{name}.yml"

    assert path.exists(), f"Missing query file: {name}"

    with path.open(
        "r",
        encoding="utf-8",
    ) as stream:

        data = yaml.safe_load(stream)

    assert isinstance(
        data,
        dict,
    )

    return data


def test_query_files_exist():

    for query in EXPECTED_QUERIES:

        path = QUERY_PATH / f"{query}.yml"

        assert path.exists(), f"Missing Azure query {query}"


def test_queries_load():

    for query in EXPECTED_QUERIES:

        data = load_query(query)

        assert data is not None


def test_query_required_fields():

    required = [
        "id",
        "name",
        "service",
        "resource",
        "method",
        "endpoint",
        "api_version",
        "scope",
        "authentication",
        "response",
        "normalizer",
        "primary_key",
        "fields",
        "metadata",
        "profiles",
    ]

    for query in EXPECTED_QUERIES:

        data = load_query(query)

        for field in required:

            assert field in data, f"{query} missing {field}"


def test_query_ids_are_unique():

    ids = []

    for query in EXPECTED_QUERIES:

        data = load_query(query)

        ids.append(data["id"])

    assert len(ids) == len(set(ids))


def test_query_endpoints_are_valid():

    for query in EXPECTED_QUERIES:

        data = load_query(query)

        endpoint = data["endpoint"]

        assert endpoint.startswith("/"), f"{query} endpoint invalid"


def test_query_methods():

    allowed_methods = [
        "GET",
    ]

    for query in EXPECTED_QUERIES:

        data = load_query(query)

        assert data["method"] in allowed_methods


def test_query_normalizers_exist():

    for query in EXPECTED_QUERIES:

        data = load_query(query)

        normalizer = data["normalizer"]

        module_name = normalizer.replace(
            "Normalizer",
            "",
        ).lower()

        try:

            importlib.import_module(f"{NORMALIZER_PATH}.{module_name}")

        except ModuleNotFoundError as exc:

            raise AssertionError(
                f"{query} references missing normalizer " f"{normalizer}"
            ) from exc


def test_query_fields_are_defined():

    for query in EXPECTED_QUERIES:

        data = load_query(query)

        fields = data["fields"]

        assert isinstance(
            fields,
            list,
        )

        assert len(fields) > 0, f"{query} has no fields"


def test_query_profiles_are_defined():

    for query in EXPECTED_QUERIES:

        data = load_query(query)

        profiles = data["profiles"]

        assert isinstance(
            profiles,
            list,
        )

        assert "default" in profiles
