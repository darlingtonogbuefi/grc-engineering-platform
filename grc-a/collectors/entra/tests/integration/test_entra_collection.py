#tests\integration\test_collection.py


"""
Microsoft Entra collector unit tests.
"""

from __future__ import annotations

from unittest.mock import Mock

from collectors.entra.collector import EntraCollector


def create_collector() -> EntraCollector:

    config = {}

    return EntraCollector(
        manifest=Mock(),
        evidence_writer=Mock(),
        normalizer=Mock(),
        validator=Mock(),
        config=config,
    )


def test_provider():

    collector = create_collector()

    assert collector.provider == "entra"


def test_discover():

    collector = create_collector()

    resources = collector.discover()

    assert isinstance(
        resources,
        dict,
    )

    assert "users" in resources
    assert "groups" in resources
    assert "devices" in resources
    assert "applications" in resources
    assert "audit_logs" in resources


def test_metadata():

    collector = create_collector()

    metadata = collector.metadata()

    assert metadata["api"] == "Microsoft Graph"

    assert "base_url" in metadata
