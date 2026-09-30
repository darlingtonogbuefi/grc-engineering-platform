"""
Microsoft Entra profile unit tests.

Validates:
- YAML profiles exist
- Profiles load correctly
- Required metadata exists
"""

from __future__ import annotations

from pathlib import Path

import yaml


PROFILE_PATH = Path(
    "collectors/entra/profiles"
)


PROFILES = [

    "baseline.yml",
    "caf.yml",
    "cyberessentials.yml",
    "full.yml",
    "govassure.yml",
    "iso27001.yml",
    "iso42001.yml",
    "soc2.yml",
]


REQUIRED_FIELDS = [

    "id",
    "name",
    "version",
    "description",
    "collector",
    "queries",
]


def load_profile(
    filename: str,
) -> dict:

    path = PROFILE_PATH / filename

    assert path.exists(), (
        f"Profile missing: {filename}"
    )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return yaml.safe_load(
            file
        )


def test_profiles_exist():

    for profile in PROFILES:

        path = PROFILE_PATH / profile

        assert path.exists(), (
            f"Missing profile: {profile}"
        )


def test_profiles_load():

    for profile in PROFILES:

        data = load_profile(
            profile
        )

        assert isinstance(
            data,
            dict,
        )


def test_profile_required_fields():

    for profile in PROFILES:

        data = load_profile(
            profile
        )

        for field in REQUIRED_FIELDS:

            assert field in data, (
                f"{profile} missing "
                f"field: {field}"
            )


def test_profile_collector():

    for profile in PROFILES:

        data = load_profile(
            profile
        )

        assert data["collector"] == "entra"


def test_profile_queries():

    for profile in PROFILES:

        data = load_profile(
            profile
        )

        assert isinstance(
            data["queries"],
            dict,
        )
