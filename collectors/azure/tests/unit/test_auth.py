"""
Azure authentication unit tests.

Tests AzureAuthenticator behaviour without
requiring live Azure credentials.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from collectors.azure.auth import AzureAuthenticator


@pytest.fixture
def auth_config():

    return {
        "tenant_id": "test-tenant-id",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "subscription_id": "test-subscription-id",
    }


def test_authenticator_initialises(auth_config):

    authenticator = AzureAuthenticator(auth_config)

    assert authenticator is not None


def test_authenticator_requires_config():

    with pytest.raises(Exception):

        AzureAuthenticator({})


@patch("collectors.azure.auth.ClientSecretCredential")
def test_get_token(
    mock_credential,
    auth_config,
):

    mock_instance = MagicMock()

    mock_instance.get_token.return_value.token = "fake-arm-token"

    mock_credential.return_value = mock_instance

    authenticator = AzureAuthenticator(auth_config)

    token = authenticator.get_token()

    assert token == ("fake-arm-token")


@patch("collectors.azure.auth.ClientSecretCredential")
def test_token_scope(
    mock_credential,
    auth_config,
):

    mock_instance = MagicMock()

    mock_instance.get_token.return_value.token = "fake-token"

    mock_credential.return_value = mock_instance

    authenticator = AzureAuthenticator(auth_config)

    authenticator.get_token()

    mock_instance.get_token.assert_called_once_with(
        "https://management.azure.com/.default"
    )
