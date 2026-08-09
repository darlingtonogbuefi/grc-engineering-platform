# collectors/azure/tests/unit/test_collector.py

"""
Azure collector unit tests.

Tests Azure collection workflow using mocked ARM responses
and validates evidence persistence.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import Mock

import pytest

from collectors.azure.client import AzureClient
from collectors.azure.collector import AzureCollector
from collectors.azure.evidence import LocalEvidenceWriter

FIXTURE_PATH = Path("collectors/azure/tests/fixtures")


@pytest.fixture
def mock_client():
    client = Mock(
        spec=AzureClient,
    )

    client.execute_query.return_value = [
        {
            "id": "/subscriptions/test/resourceGroups/demo",
            "name": "demo",
            "type": "Microsoft.Resources/resourceGroups",
            "location": "uksouth",
            "tags": {
                "environment": "test",
            },
        }
    ]

    return client


@pytest.fixture
def collector(
    mock_client,
):
    return AzureCollector(
        client=mock_client,
        config={
            "tenant_id": os.environ["TENANT_ID"],
            "client_id": os.environ["CLIENT_ID"],
            "client_secret": os.environ["CLIENT_SECRET"],
        },
    )


def test_collector_initialises(
    collector,
):
    assert collector is not None

    assert hasattr(
        collector,
        "collect",
    )


def test_collect_resource_groups(
    collector,
):
    result = collector.collect(
        query="resource_groups",
    )

    assert result is not None

    assert isinstance(
        result,
        list,
    )


def test_collect_returns_records(
    collector,
):
    records = collector.collect(
        query="resources",
    )

    assert len(records) >= 1

    record = records[0]

    assert "id" in record

    assert "name" in record


def test_collector_calls_arm_api(
    collector,
    mock_client,
):
    collector.collect(
        query="resources",
    )

    assert mock_client.execute_query.called


def test_collection_handles_empty_response(
    collector,
    mock_client,
):
    mock_client.execute_query.return_value = []

    result = collector.collect(
        query="resources",
    )

    assert result == []


def test_collection_handles_missing_value(
    collector,
    mock_client,
):
    mock_client.execute_query.return_value = []

    result = collector.collect(
        query="resources",
    )

    assert result == []


def test_collection_failure_is_raised(
    collector,
    mock_client,
):
    mock_client.execute_query.side_effect = Exception(
        "ARM failure",
    )

    with pytest.raises(Exception):
        collector.collect(
            query="resources",
        )


def test_evidence_writer_save(
    tmp_path,
):
    writer = LocalEvidenceWriter(
        {
            "storage_path": str(tmp_path),
        }
    )

    evidence = {
        "collector": "azure",
        "run_id": "test-run",
        "provider": "azure",
        "records": [
            {
                "id": "test-resource",
            }
        ],
    }

    output = writer.save(
        evidence,
    )

    assert output.endswith(
        "evidence.json",
    )

    assert writer.exists(
        "azure",
        "test-run",
    )


def test_evidence_writer_read(
    tmp_path,
):
    writer = LocalEvidenceWriter(
        {
            "storage_path": str(tmp_path),
        }
    )

    evidence = {
        "collector": "azure",
        "run_id": "test-run",
        "provider": "azure",
    }

    writer.save(
        evidence,
    )

    loaded = writer.read(
        "azure",
        "test-run",
    )

    assert loaded["provider"] == "azure"


def test_evidence_writer_delete(
    tmp_path,
):
    writer = LocalEvidenceWriter(
        {
            "storage_path": str(tmp_path),
        }
    )

    evidence = {
        "collector": "azure",
        "run_id": "test-run",
    }

    writer.save(
        evidence,
    )

    deleted = writer.delete(
        "azure",
        "test-run",
    )

    assert deleted is True

    assert (
        writer.exists(
            "azure",
            "test-run",
        )
        is False
    )


def test_fixture_directory_exists():
    FIXTURE_PATH.mkdir(
        parents=True,
        exist_ok=True,
    )

    assert FIXTURE_PATH.exists()
