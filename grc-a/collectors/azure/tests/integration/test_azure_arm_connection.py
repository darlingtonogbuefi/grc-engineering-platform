# collectors\azure\tests\integration\test_arm_connection.py

"""
Azure Resource Manager connection integration test.

Validates:
- Azure authentication
- ARM token acquisition
- ARM API connectivity
- AzureClient basic request handling
"""

from __future__ import annotations

import os

from collectors.azure.auth import AzureAuthenticator
from collectors.azure.client import AzureClient


def get_authenticator() -> AzureAuthenticator:
    """
    Create Azure ARM authentication provider.
    """

    config = {
        "tenant_id": os.environ["TENANT_ID"],
        "client_id": os.environ["CLIENT_ID"],
        "client_secret": os.environ["CLIENT_SECRET"],
        "scope": os.environ.get(
            "ARM_SCOPE",
            "https://management.azure.com/.default",
        ),
    }

    return AzureAuthenticator(config)


def test_arm_connection():

    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

    authenticator = get_authenticator()

    token = authenticator.get_token()

    assert token, "Failed to acquire Azure ARM token"

    client = AzureClient(authenticator)

    endpoint = f"/subscriptions/" f"{subscription_id}"

    response = client.get_json(
        endpoint,
        token,
    )

    assert response is not None, "Azure ARM returned empty response"

    assert "subscriptionId" in response, "Invalid subscription response"

    assert response["subscriptionId"] == subscription_id
