"""
Microsoft Entra authentication unit tests.

Validates:
- Authenticator initialization
- Configuration loading
- Token handling behavior
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from collectors.entra.auth import EntraAuthenticator


def test_authenticator_initialization():

    config = {
        "tenant_id": "tenant-test",
        "client_id": "client-test",
        "client_secret": "secret-test",
    }

    auth = EntraAuthenticator(
        config
    )

    assert auth.tenant_id == "tenant-test"

    assert auth.client_id == "client-test"

    assert auth.client_secret == "secret-test"

    assert auth.scope == (
        "https://graph.microsoft.com/.default"
    )


def test_token_initially_empty():

    config = {
        "tenant_id": "tenant-test",
        "client_id": "client-test",
        "client_secret": "secret-test",
    }

    auth = EntraAuthenticator(
        config
    )

    assert auth.token is None


def test_token_expiry_initially_empty():

    config = {
        "tenant_id": "tenant-test",
        "client_id": "client-test",
        "client_secret": "secret-test",
    }

    auth = EntraAuthenticator(
        config
    )

    assert auth.token_expiry() is None


def test_metadata():

    config = {
        "tenant_id": "tenant-test",
        "client_id": "client-test",
        "client_secret": "secret-test",
    }

    auth = EntraAuthenticator(
        config
    )

    metadata = auth.metadata()

    assert metadata["provider"] == "entra"

    assert metadata["tenant_id"] == "tenant-test"

    assert (
        metadata["scope"]
        == "https://graph.microsoft.com/.default"
    )


def test_get_token_requires_provider_configuration():

    config = {
        "tenant_id": "tenant-test",
        "client_id": "client-test",
        "client_secret": "secret-test",
    }

    auth = EntraAuthenticator(
        config
    )

    with pytest.raises(Exception):

        auth.get_token()
