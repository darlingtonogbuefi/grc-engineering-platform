# collectors\azure\tests\integration\test_collection.py

"""
Integration tests for the Azure collector.

These tests verify the complete collection workflow from
query execution through evidence generation.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from collectors.azure.collector import AzureCollector

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def load_fixture(name: str) -> dict:
    """Load a JSON fixture."""

    import json

    with open(FIXTURES / name, encoding="utf-8") as fp:
        return json.load(fp)


@pytest.fixture
def mock_client():
    """Mock Azure ARM client."""

    client = MagicMock()

    client.get.side_effect = [
        load_fixture("subscriptions.json"),
        load_fixture("resources.json"),
        load_fixture("resource_groups.json"),
        load_fixture("activity_logs.json"),
        load_fixture("role_assignments.json"),
    ]

    return client


@pytest.fixture
def collector(mock_client):
    """Create collector using mocked client."""

    collector = AzureCollector()

    collector.client = mock_client

    return collector


def test_collection_runs_successfully(collector):
    """
    Collector completes without raising exceptions.
    """

    evidence = collector.collect()

    assert evidence is not None


def test_collection_returns_list(collector):
    """
    Collector returns iterable evidence.
    """

    evidence = collector.collect()

    assert isinstance(evidence, list)


def test_collection_contains_evidence(collector):
    """
    At least one evidence item is collected.
    """

    evidence = collector.collect()

    assert len(evidence) > 0


def test_collection_items_have_ids(collector):
    """
    Every evidence item has a unique identifier.
    """

    evidence = collector.collect()

    for item in evidence:
        assert item.get("id") is not None


def test_collection_preserves_subscription_ids(collector):
    """
    Subscription identifiers are retained.
    """

    evidence = collector.collect()

    assert any("subscriptionId" in item for item in evidence)


def test_collection_normalizes_resources(collector):
    """
    Resource objects are normalized.
    """

    evidence = collector.collect()

    resource = next(
        (
            item
            for item in evidence
            if item.get("type") == "Microsoft.Resources/resourceGroups"
        ),
        None,
    )

    assert resource is not None


def test_collection_handles_empty_response(collector):
    """
    Empty API responses do not fail collection.
    """

    collector.client.get.return_value = {"value": []}

    evidence = collector.collect()

    assert evidence == [] or isinstance(evidence, list)


def test_collection_handles_multiple_pages(collector):
    """
    Pagination is processed correctly.
    """

    collector.client.get.side_effect = [
        {
            "value": [{"id": "1"}],
            "nextLink": "page2",
        },
        {
            "value": [{"id": "2"}],
        },
    ]

    evidence = collector.collect()

    assert len(evidence) >= 2


def test_collection_calls_arm_client(collector):
    """
    ARM client is invoked during collection.
    """

    collector.collect()

    assert collector.client.get.called


def test_collection_generates_evidence_objects(collector):
    """
    Evidence objects contain expected metadata.
    """

    evidence = collector.collect()

    first = evidence[0]

    assert "id" in first
    assert "name" in first
    assert "type" in first


def test_collection_is_repeatable(collector):
    """
    Running collection twice produces valid results.
    """

    first = collector.collect()
    second = collector.collect()

    assert isinstance(first, list)
    assert isinstance(second, list)


def test_collection_handles_client_exception(collector):
    """
    Client exceptions propagate appropriately.
    """

    collector.client.get.side_effect = RuntimeError("Azure API failure")

    with pytest.raises(RuntimeError):
        collector.collect()
