#collectors\entra\tests\unit\test_collector.py

"""
Microsoft Entra collector unit tests.

Validates:
- Provider metadata
- Resource discovery
- Collector metadata
"""

from __future__ import annotations

from unittest.mock import Mock

from collectors.entra.collector import EntraCollector


def create_collector() -> EntraCollector:
    """
    Create a collector instance.
    """

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


def test_discover_returns_resources():

    collector = create_collector()

    resources = collector.discover()

    assert isinstance(
        resources,
        dict,
    )

    expected = [

        "users",
        "groups",
        "directory_roles",
        "devices",
        "conditional_access",
        "applications",
        "service_principals",
        "audit_logs",
        "sign_ins",

    ]

    for resource in expected:

        assert resource in resources


def test_metadata_contains_expected_fields():

    collector = create_collector()

    metadata = collector.metadata()

    assert metadata["api"] == "Microsoft Graph"

    assert (
        metadata["base_url"]
        == "https://graph.microsoft.com/v1.0"
    )

    assert "authenticated" in metadata


def test_collect_empty():

    collector = create_collector()

    collector.authenticator._token = "token"

    collector.client.get_all_pages = Mock(
        return_value=[]
    )

    result = collector.collect(
        {}
    )

    assert result == {}


def test_collect_single_resource():

    collector = create_collector()

    collector.authenticator._token = "token"

    collector.client.get_all_pages = Mock(
        return_value=[
            {
                "id": "user-001",
            }
        ]
    )

    result = collector.collect(
        {
            "users": "/users",
        }
    )

    assert "users" in result

    assert len(
        result["users"]
    ) == 1

    assert (
        result["users"][0]["id"]
        == "user-001"
    )
