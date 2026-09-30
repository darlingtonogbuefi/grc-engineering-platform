# collectors/azure/tests/integration/test_collection_live.py

"""
Live production tests for the Azure collector.

These tests execute against a real Azure subscription and validate
the complete collection workflow using real Azure APIs.

Run manually only:
    pytest collectors/azure/tests/integration/test_collection_live.py -v
"""

import os

import pytest

from collectors.azure.collector import AzureCollector


@pytest.fixture
def collector():
    """
    Create collector using real Azure credentials.
    """

    config = {
        "tenant_id": os.environ["TENANT_ID"],
        "client_id": os.environ["CLIENT_ID"],
        "client_secret": os.environ["CLIENT_SECRET"],
        "subscription_id": os.environ["AZURE_SUBSCRIPTION_ID"],
    }

    return AzureCollector(config=config)


@pytest.mark.production
def test_live_collection_runs_successfully(collector):
    """
    Collector completes against Azure production.
    """

    evidence = collector.collect()

    assert evidence is not None


@pytest.mark.production
def test_live_collection_returns_list(collector):
    """
    Collector returns a list of evidence objects.
    """

    evidence = collector.collect()

    assert isinstance(evidence, list)


@pytest.mark.production
def test_live_collection_contains_evidence(collector):
    """
    Azure resources are collected.
    """

    evidence = collector.collect()

    assert len(evidence) > 0


@pytest.mark.production
def test_live_collection_items_have_ids(collector):
    """
    Every evidence item contains an ID.
    """

    evidence = collector.collect()

    for item in evidence:
        assert item.get("id") is not None


@pytest.mark.production
def test_live_collection_preserves_subscription_ids(collector):
    """
    Subscription IDs are present in collected evidence.
    """

    evidence = collector.collect()

    assert any("subscriptionId" in item for item in evidence)


@pytest.mark.production
def test_live_collection_normalizes_resources(collector):
    """
    Resource objects are normalized correctly.
    """

    evidence = collector.collect()

    for item in evidence:
        assert "id" in item
        assert "type" in item
        assert "name" in item


@pytest.mark.production
def test_live_collection_generates_evidence_objects(collector):
    """
    Evidence objects contain expected metadata.
    """

    evidence = collector.collect()

    first = evidence[0]

    assert "id" in first
    assert "name" in first
    assert "type" in first


@pytest.mark.production
def test_live_collection_is_repeatable(collector):
    """
    Running collection twice produces valid results.
    """

    first = collector.collect()
    second = collector.collect()

    assert isinstance(first, list)
    assert isinstance(second, list)
