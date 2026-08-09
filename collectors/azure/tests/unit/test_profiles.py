"""
Azure profile unit tests.

Validates:
- Profile YAML files exist
- Profiles load successfully
- Required profile structure exists
- Expected collectors and categories are available
"""

from __future__ import annotations

from pathlib import Path

import yaml

PROFILE_PATH = Path("collectors/azure/profiles")


PROFILES = [
    "default",
    "cyberessentials",
    "caf",
    "govassure",
    "iso27001",
    "iso42001",
    "soc2",
    "full",
]


def load_profile(
    name: str,
) -> dict:

    path = PROFILE_PATH / f"{name}.yml"

    assert path.exists(), f"Missing profile: {name}"

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


def test_profile_files_exist():

    for profile in PROFILES:

        path = PROFILE_PATH / f"{profile}.yml"

        assert path.exists(), f"Missing Azure profile {profile}"


def test_profiles_load():

    for profile in PROFILES:

        data = load_profile(profile)

        assert data is not None


def test_profiles_have_metadata():

    for profile in PROFILES:

        data = load_profile(profile)

        assert (
            "name" in data or "id" in data or "profile" in data
        ), f"{profile} missing metadata"


def test_default_profile():

    profile = load_profile("default")

    assert profile


def test_full_profile():

    profile = load_profile("full")

    assert profile


def test_compliance_profiles_exist():

    compliance_profiles = [
        "cyberessentials",
        "caf",
        "govassure",
        "iso27001",
        "iso42001",
        "soc2",
    ]

    for profile in compliance_profiles:

        data = load_profile(profile)

        assert data is not None


def test_profile_contains_collectors_when_defined():

    for profile in PROFILES:

        data = load_profile(profile)

        if "collectors" in data:

            assert isinstance(
                data["collectors"],
                list,
            )

            assert len(data["collectors"]) > 0


def test_profile_query_references_are_valid():

    query_path = Path("collectors/azure/queries")

    available_queries = {item.stem for item in query_path.glob("*.yml")}

    for profile in PROFILES:

        data = load_profile(profile)

        queries = data.get(
            "queries",
            [],
        )

        for query in queries:

            assert (
                query in available_queries
            ), f"{profile} references missing query {query}"
