"""
Azure evidence validation tests.

Validates normalized Azure evidence.
"""

from __future__ import annotations

import json
from pathlib import Path

from collectors.azure.normalizers import AzureNormalizer
from collectors.azure.validator import AzureValidator

FIXTURE_PATH = Path("collectors/azure/tests/fixtures")


def load_fixture(name: str):
    path = FIXTURE_PATH / f"{name}.json"

    assert path.exists(), f"Missing fixture: {path}"

    return json.loads(
        path.read_text(
            encoding="utf-8",
        )
    )


def test_normalized_evidence_passes_validation():

    raw = {
        "resources": load_fixture("resources"),
    }

    normalizer = AzureNormalizer()

    records = normalizer.normalize(raw)

    assert records

    validator = AzureValidator()

    for record in records:

        evidence = {
            "collector": "azure",
            "provider": record.data["provider"],
            "resource_id": record.resource_id,
            "data": record.data,
        }

        result = validator.validate(evidence)

        assert result is True
