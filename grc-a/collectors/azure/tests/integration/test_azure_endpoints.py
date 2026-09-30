# collectors/azure/tests/integration/test_endpoints.py

"""
Azure Resource Manager endpoint integration tests.

Calls Azure ARM REST endpoints and saves
responses as fixtures for offline testing.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from collectors.azure.auth import AzureAuthenticator
from collectors.azure.client import AzureClient

FIXTURE_PATH = Path("collectors/azure/tests/fixtures")


SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]


ENDPOINTS = {
    "subscriptions": "/subscriptions",
    "resource_groups": f"/subscriptions/{SUBSCRIPTION_ID}/resourcegroups",
    "resources": f"/subscriptions/{SUBSCRIPTION_ID}/resources",
    "activity_logs": (
        f"/subscriptions/{SUBSCRIPTION_ID}"
        "/providers/Microsoft.Insights/"
        "eventtypes/management/values"
    ),
    "policy_assignments": (
        f"/subscriptions/{SUBSCRIPTION_ID}"
        "/providers/Microsoft.Authorization/"
        "policyAssignments"
    ),
    "policy_definitions": (
        f"/subscriptions/{SUBSCRIPTION_ID}"
        "/providers/Microsoft.Authorization/"
        "policyDefinitions"
    ),
    "role_assignments": (
        f"/subscriptions/{SUBSCRIPTION_ID}"
        "/providers/Microsoft.Authorization/"
        "roleAssignments"
    ),
    "role_definitions": (
        f"/subscriptions/{SUBSCRIPTION_ID}"
        "/providers/Microsoft.Authorization/"
        "roleDefinitions"
    ),
    "storage_accounts": (
        f"/subscriptions/{SUBSCRIPTION_ID}"
        "/providers/Microsoft.Storage/"
        "storageAccounts"
    ),
    "key_vaults": (
        f"/subscriptions/{SUBSCRIPTION_ID}" "/providers/Microsoft.KeyVault/" "vaults"
    ),
    "virtual_networks": (
        f"/subscriptions/{SUBSCRIPTION_ID}"
        "/providers/Microsoft.Network/"
        "virtualNetworks"
    ),
    "firewalls": (
        f"/subscriptions/{SUBSCRIPTION_ID}"
        "/providers/Microsoft.Network/"
        "azureFirewalls"
    ),
    "network_security_groups": (
        f"/subscriptions/{SUBSCRIPTION_ID}"
        "/providers/Microsoft.Network/"
        "networkSecurityGroups"
    ),
    "backup_vaults": (
        f"/subscriptions/{SUBSCRIPTION_ID}"
        "/providers/Microsoft.DataProtection/"
        "backupVaults"
    ),
}


def get_authenticator() -> AzureAuthenticator:
    """
    Create Azure authentication provider.
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


def test_arm_endpoints():

    authenticator = get_authenticator()

    token = authenticator.get_token()

    assert token, "Failed to acquire Azure ARM token"

    client = AzureClient(authenticator)

    FIXTURE_PATH.mkdir(
        parents=True,
        exist_ok=True,
    )

    failures = []

    for name, endpoint in ENDPOINTS.items():

        try:

            response = client.get_json(
                endpoint,
                token,
            )

            assert response is not None

            output = FIXTURE_PATH / f"{name}.json"

            output.write_text(
                json.dumps(
                    response,
                    indent=2,
                ),
                encoding="utf-8",
            )

        except Exception as exc:

            failures.append(
                {
                    "endpoint": endpoint,
                    "error": str(exc),
                }
            )

    assert not failures, f"ARM endpoint failures: {failures}"
