#!/usr/bin/env python3

"""
Test Microsoft Entra high privilege directory role assignments.
"""

from __future__ import annotations

from pathlib import Path
import os
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from collectors.entra.collector import EntraCollector

config = {
    "tenant_id": os.environ["TENANT_ID"],
    "client_id": os.environ["CLIENT_ID"],
    "client_secret": os.environ["CLIENT_SECRET"],
    "scope": os.getenv(
        "GRAPH_SCOPE",
        "https://graph.microsoft.com/.default",
    ),
}


HIGH_PRIVILEGE_ROLES = [
    "Global Administrator",
    "Privileged Role Administrator",
    "Security Administrator",
    "Conditional Access Administrator",
    "Exchange Administrator",
]


collector = EntraCollector(
    config=config,
)


collector.authenticate()

token = collector.authenticator.token


roles = collector.client.get_all_pages(
    "/directoryRoles",
    token,
)


for role in roles:
    if role.get("displayName") in HIGH_PRIVILEGE_ROLES:

        print("\n================================")
        print("ROLE:", role["displayName"])
        print("ID:", role["id"])

        members = collector.client.get_all_pages(
            f"/directoryRoles/{role['id']}/members",
            token,
            params={"$select": ("id," "displayName," "userPrincipalName," "appId")},
        )

        if not members:
            print("NO ASSIGNED MEMBERS")

        else:
            print("MEMBERS:")

            for member in members:
                print(
                    " -",
                    member.get("displayName"),
                    "|",
                    member.get("userPrincipalName"),
                    "|",
                    member.get("@odata.type"),
                )
