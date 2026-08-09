# tests\integration\test_endpoints.py


"""
Microsoft Entra Graph endpoint integration tests.

Calls Microsoft Graph endpoints and saves
responses as fixtures for offline testing.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from collectors.entra.auth import EntraAuthenticator
from collectors.entra.client import EntraClient


FIXTURE_PATH = Path(
    "collectors/entra/tests/fixtures"
)


ENDPOINTS = {

    "organization":
        "/organization",

    "users":
        "/users",

    "groups":
        "/groups",

    "devices":
        "/devices",

    "applications":
        "/applications",

    "roles":
        "/directoryRoles",

    "conditional_access":
        "/identity/conditionalAccess/policies",

    "audit_logs":
        "/auditLogs/directoryAudits",

    "signins":
        "/auditLogs/signIns",

    "identity_protection":
        "/identityProtection/riskyUsers",
}


def get_authenticator() -> EntraAuthenticator:
    """
    Create Microsoft Entra authentication provider.
    """

    config = {
        "tenant_id": os.environ["TENANT_ID"],
        "client_id": os.environ["CLIENT_ID"],
        "client_secret": os.environ["CLIENT_SECRET"],
        "scope": os.environ.get(
            "GRAPH_SCOPE",
            "https://graph.microsoft.com/.default",
        ),
    }

    return EntraAuthenticator(
        config
    )


def test_graph_endpoints():

    authenticator = get_authenticator()

    token = authenticator.get_token()

    assert token, (
        "Failed to acquire Microsoft Graph token"
    )

    client = EntraClient(authenticator)

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

            output = (
                FIXTURE_PATH /
                f"{name}.json"
            )

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

    assert not failures, (
        f"Graph endpoint failures: {failures}"
    )
