#collectors\entra\tests\unit\test_client.py


"""
Microsoft Entra client unit tests.

Validates:
- Client initialization
- Base URL
- Pagination support
"""

from __future__ import annotations

from unittest.mock import Mock

from collectors.entra.client import EntraClient


def create_client() -> EntraClient:
    """
    Create a test client.
    """

    authenticator = Mock()

    config = {}

    return EntraClient(
        authenticator,
        config,
    )


def test_base_url():

    client = create_client()

    assert (
        client.BASE_URL
        == "https://graph.microsoft.com/v1.0"
    )


def test_default_retry_settings():

    client = create_client()

    assert client.DEFAULT_RETRIES == 3

    assert client.DEFAULT_BACKOFF == 1.0


def test_session_created():

    client = create_client()

    assert client.session is not None


def test_get_all_pages_empty_result():

    client = create_client()

    client.get = Mock(
        return_value=Mock(
            json=lambda: {
                "value": [],
            }
        )
    )

    result = client.get_all_pages(
        "/users",
        "token",
    )

    assert result == []


def test_get_all_pages_multiple_pages():

    client = create_client()

    responses = [

        {
            "value": [
                {
                    "id": "1",
                }
            ],
            "@odata.nextLink": "next",
        },

        {
            "value": [
                {
                    "id": "2",
                }
            ],
        },

    ]

    client.get = Mock(
        side_effect=[
            Mock(
                json=lambda: responses[0]
            ),
            Mock(
                json=lambda: responses[1]
            ),
        ]
    )

    result = client.get_all_pages(
        "/users",
        "token",
    )

    assert len(result) == 2

    assert result[0]["id"] == "1"

    assert result[1]["id"] == "2"
