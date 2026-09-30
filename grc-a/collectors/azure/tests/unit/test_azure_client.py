"""
Azure ARM client unit tests.

Tests:
- client initialisation
- authenticated requests
- JSON responses
- error handling
- pagination handling

No Azure connection required.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from collectors.azure.client import AzureClient


@pytest.fixture
def mock_authenticator():

    authenticator = MagicMock()

    authenticator.get_token.return_value = "fake-arm-token"

    return authenticator


@pytest.fixture
def client(
    mock_authenticator,
):

    return AzureClient(mock_authenticator)


def test_client_initialises(
    client,
):

    assert client is not None


def test_client_stores_authenticator(
    mock_authenticator,
):

    client = AzureClient(mock_authenticator)

    assert client.authenticator == mock_authenticator


@patch("collectors.azure.client.requests.get")
def test_get_json_success(
    mock_get,
    client,
):

    mock_response = MagicMock()

    mock_response.status_code = 200

    mock_response.json.return_value = {"value": [{"id": "resource-1"}]}

    mock_get.return_value = mock_response

    result = client.get_json("/subscriptions")

    assert result == {"value": [{"id": "resource-1"}]}

    mock_get.assert_called_once()


def test_get_json_uses_bearer_token(
    client,
):

    client.authenticator.get_token = MagicMock(return_value="token123")

    with patch("collectors.azure.client.requests.get") as mock_get:

        response = MagicMock()

        response.status_code = 200

        response.json.return_value = {"value": []}

        mock_get.return_value = response

        client.get_json("/subscriptions")

        headers = mock_get.call_args.kwargs["headers"]

        assert headers["Authorization"] == "Bearer token123"


def test_get_json_handles_http_error(
    client,
):

    with patch("collectors.azure.client.requests.get") as mock_get:

        response = MagicMock()

        response.status_code = 403

        response.raise_for_status.side_effect = Exception("Forbidden")

        mock_get.return_value = response

        with pytest.raises(Exception):

            client.get_json("/subscriptions")


def test_get_json_handles_invalid_json(
    client,
):

    with patch("collectors.azure.client.requests.get") as mock_get:

        response = MagicMock()

        response.status_code = 200

        response.json.side_effect = ValueError()

        mock_get.return_value = response

        with pytest.raises(ValueError):

            client.get_json("/subscriptions")


def test_pagination_response(
    client,
):

    with patch("collectors.azure.client.requests.get") as mock_get:

        response = MagicMock()

        response.status_code = 200

        response.json.return_value = {
            "value": [{"id": "resource1"}],
            "nextLink": "https://management.azure.com/page2",
        }

        mock_get.return_value = response

        result = client.get_json("/subscriptions")

        assert "nextLink" in result
