"""
Azure normalization tests.

Validates that raw Azure ARM responses
are converted into platform EvidenceRecords.
"""

from __future__ import annotations

import json
from pathlib import Path

from collectors.azure.normalizers.resource import ResourceNormalizer
from collectors.base.models import EvidenceRecord

FIXTURE_PATH = Path("collectors/azure/tests/fixtures")


def load_fixture(name: str):
    path = FIXTURE_PATH / f"{name}.json"

    assert path.exists(), f"Missing fixture: {path}"

    return json.loads(path.read_text(encoding="utf-8"))


def test_azure_resources_normalize():
    raw = load_fixture("resources")

    normalizer = ResourceNormalizer()

    records = normalizer.normalize(raw)

    assert records

    assert all(
        isinstance(
            record,
            EvidenceRecord,
        )
        for record in records
    )


def test_normalized_records_have_required_fields():
    raw = load_fixture("resources")

    normalizer = ResourceNormalizer()

    records = normalizer.normalize(raw)

    assert records

    for record in records:

        # EvidenceRecord fields
        assert record.source
        assert record.resource_type
        assert record.resource_id

        # Normalized payload
        assert record.data

        assert record.data["provider"] == "azure"

        assert "name" in record.data

        assert "service" in record.data

        # Original Azure object preserved
        assert "raw" in record.data
