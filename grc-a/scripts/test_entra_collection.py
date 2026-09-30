# scripts\test_entra_collection.py

#!/usr/bin/env python3
"""
Production test for the Microsoft Entra collector.

Validates:
- Microsoft Graph authentication
- Collector metadata
- Resource discovery
- Evidence collection
- Directory role membership resolution
- Evidence normalization
"""

from __future__ import annotations

from pathlib import Path
import os
import sys

# Add project root to Python module search path
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from collectors.entra.collector import EntraCollector
from collectors.entra.auth import EntraAuthenticator

config = {
    "tenant_id": os.environ["TENANT_ID"],
    "client_id": os.environ["CLIENT_ID"],
    "client_secret": os.environ["CLIENT_SECRET"],
    "scope": os.getenv(
        "GRAPH_SCOPE",
        "https://graph.microsoft.com/.default",
    ),
}


#
# Validate authentication independently
#
auth = EntraAuthenticator(config)

auth.acquire_token()

token = auth.token

print(
    "Token acquired:",
    bool(token),
)


#
# Collector initialization
#
collector = EntraCollector(
    manifest=None,
    evidence_writer=None,
    normalizer=None,
    validator=None,
    config=config,
)

collector.authenticate()

print("\nCollector metadata:")
print(collector.metadata())


#
# Discovery
#
print("\nDiscovering resources...")

resources = collector.discover()

print(resources)


#
# Collection
#
print("\nCollecting evidence...")

evidence = collector.collect(
    resources,
)

print(
    "\nCollected resource types:",
    len(evidence),
)

for resource, items in evidence.items():

    count = len(items) if isinstance(items, list) else 1

    print(f"{resource}: {count}")


#
# Sample evidence output
#
print("\nSample data:")

for resource, items in evidence.items():

    if isinstance(items, list) and items:
        print(f"\n{resource}")

        print(items[0])


#
# Verify normalization pipeline
#
print("\nNormalizing evidence...")

normalized = collector.normalize(
    evidence,
)

print(
    "\nNormalized evidence records:",
    len(normalized),
)


#
# Inspect normalized directory role evidence
#
print("\nNormalized directory roles:")

for record in normalized:

    #
    # EvidenceRecord stores the normalized
    # payload inside the data attribute.
    #
    if hasattr(record, "data"):
        data = record.data

    elif hasattr(record, "model_dump"):
        dumped = record.model_dump()
        data = dumped.get("data", dumped)

    elif hasattr(record, "dict"):
        dumped = record.dict()
        data = dumped.get("data", dumped)

    elif isinstance(record, dict):
        data = record.get(
            "data",
            record,
        )

    else:
        continue

    #
    # Skip anything that isn't a directory role.
    #
    if data.get("type") != "role":
        continue

    print("\n================================")

    print(
        "ROLE:",
        data.get("display_name"),
    )

    print(
        "RESOURCE ID:",
        data.get("id"),
    )

    print(
        "HIGH PRIVILEGE:",
        data.get("is_high_privilege"),
    )

    print(
        "ASSIGNMENT COUNT:",
        data.get("assignment_count"),
    )

    print("\nFULL NORMALIZED PAYLOAD:")

    print(data)

    members = data.get(
        "members",
        [],
    )

    if not members:
        print("\nNO ASSIGNED MEMBERS")
        continue

    print("\nMEMBERS:")

    for member in members:

        print(
            " -",
            member.get("display_name"),
            "|",
            member.get("upn"),
            "|",
            member.get("type"),
        )


#
# Verify that the normalized flag exists
#
print("\n\nVerified high-privilege roles from normalized evidence:")

found = False

for record in normalized:

    if hasattr(record, "data"):
        data = record.data

    elif hasattr(record, "model_dump"):
        dumped = record.model_dump()
        data = dumped.get("data", dumped)

    elif hasattr(record, "dict"):
        dumped = record.dict()
        data = dumped.get("data", dumped)

    elif isinstance(record, dict):
        data = record.get(
            "data",
            record,
        )

    else:
        continue

    if data.get("type") == "role" and data.get("is_high_privilege"):

        found = True

        print("\n================================")

        print(
            "ROLE:",
            data.get("display_name"),
        )

        print(
            "HIGH PRIVILEGE:",
            data.get("is_high_privilege"),
        )

        print(
            "ASSIGNMENT COUNT:",
            data.get("assignment_count"),
        )

if not found:

    print("No normalized high-privilege roles found.")


#
# Original verification against raw Graph data
# (retained for comparison)
#
HIGH_PRIVILEGE_ROLES = [
    "Global Administrator",
    "Privileged Role Administrator",
    "Security Administrator",
    "Conditional Access Administrator",
    "Exchange Administrator",
    "SharePoint Administrator",
    "User Administrator",
    "Authentication Administrator",
    "Application Administrator",
    "Cloud Application Administrator",
]


print("\n\nHigh privilege role assignments (raw Graph evidence):")

directory_roles = evidence.get(
    "directory_roles",
    [],
)

for role in directory_roles:

    role_name = role.get("displayName")

    if role_name not in HIGH_PRIVILEGE_ROLES:
        continue

    print("\n================================")

    print(
        "ROLE:",
        role_name,
    )

    print(
        "ID:",
        role.get("id"),
    )

    members = role.get(
        "members",
        [],
    )

    print(
        "ASSIGNED MEMBERS:",
        len(members),
    )

    if not members:

        print("NO ASSIGNED MEMBERS")

        continue

    for member in members:

        print(
            " -",
            member.get("displayName"),
            "|",
            member.get("userPrincipalName"),
            "|",
            member.get("@odata.type"),
        )
