#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from collectors.entra.normalizers.roles import normalize_directory_roles

sample_roles = [
    {
        "id": "123",
        "displayName": "Global Administrator",
        "description": "Full access",
        "roleTemplateId": "abc",
        "members": [
            {
                "id": "user1",
                "displayName": "DARLINGTON OGBUEFI",
                "userPrincipalName": "admin@cribr.co.uk",
                "@odata.type": "#microsoft.graph.user",
            }
        ],
    },
    {
        "id": "456",
        "displayName": "User Administrator",
        "description": "Manage users",
        "roleTemplateId": "def",
        "members": [],
    },
]


normalized = normalize_directory_roles(sample_roles)


print("\nNormalized roles:")

for role in normalized:

    print("\n====================")

    print(
        "ROLE:",
        role["display_name"],
    )

    print(
        "Assignments:",
        role["assignment_count"],
    )

    print(
        "PRIVILEGED ROLE:",
        "YES" if role.get("is_high_privilege") else "NO",
    )

    for member in role["members"]:

        print(
            " -",
            member.get("display_name"),
            "|",
            member.get("upn"),
            "|",
            member.get("type"),
        )
