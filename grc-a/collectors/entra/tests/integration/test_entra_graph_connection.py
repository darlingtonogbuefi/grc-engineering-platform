# tests\integration\test_graph_connection.py


"""
Microsoft Entra Graph connection integration tests.

Validates:
- Authentication works
- Microsoft Graph client can connect
- Tenant access is available
"""

import os

from collectors.entra.auth import EntraAuthenticator
from collectors.entra.client import EntraClient


def test_graph_authentication():

    config = {
        "tenant_id": os.environ["TENANT_ID"],
        "client_id": os.environ["CLIENT_ID"],
        "client_secret": os.environ["CLIENT_SECRET"],
        "scope": os.environ.get(
            "GRAPH_SCOPE",
            "https://graph.microsoft.com/.default",
        ),
    }

    auth = EntraAuthenticator(
        config
    )

    token = auth.get_token()

    assert token, (
        "Microsoft Graph token acquisition failed"
    )

    client = EntraClient(auth)

    response = client.get_json(
        "/organization",
        token,
    )

    assert response is not None

    assert "value" in response
