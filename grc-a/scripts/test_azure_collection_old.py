#!/usr/bin/env python3
"""
Production test for the Azure collector.

Validates:

- Azure Resource Manager authentication
- Collector metadata
- Resource discovery
- Evidence collection
- Evidence normalization
- Resource inventory summary
- Sample raw resources
- Sample normalized resources
"""

from __future__ import annotations

from collections import Counter
from ctypes import cast
from pathlib import Path
import os
import sys
from typing import Any, cast

#
# Add project root to Python module search path
#

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )

from collectors.azure.auth import AzureAuthenticator
from collectors.azure.collector import AzureCollector


config = {
    "tenant_id": os.environ["TENANT_ID"],
    "client_id": os.environ["CLIENT_ID"],
    "client_secret": os.environ["CLIENT_SECRET"],
    "subscription_id": os.environ["AZURE_SUBSCRIPTION_ID"],
}


#
# Validate authentication independently
#

auth = AzureAuthenticator(config)

auth.acquire_token()

token = auth.token

print(
    "Token acquired:",
    bool(token),
)

#
# Collector initialization
#

collector = AzureCollector(
    manifest=cast(Any, None),
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

queries = collector.discover()

print()

for query in queries:
    print(" -", query)

#
# Collection
#

print("\nCollecting evidence...")

raw_evidence = collector.collect(
    queries,
)

print(
    "\nCollected resources:",
    len(raw_evidence),
)

#
# Resource inventory
#

resource_summary = Counter()

for resource in raw_evidence:

    resource_summary[
        resource.get(
            "type",
            "Unknown",
        )
    ] += 1

print("\nAzure Resource Types")

for resource_type, count in sorted(
    resource_summary.items()
):
    print(
        f"{resource_type}: {count}"
    )

#
# Sample raw resources
#

SAMPLE_TYPES = [
    "Microsoft.Compute/virtualMachines",
    "Microsoft.Storage/storageAccounts",
    "Microsoft.Network/networkSecurityGroups",
    "Microsoft.Network/virtualNetworks",
    "Microsoft.KeyVault/vaults",
    "Microsoft.Web/sites",
    "Microsoft.Authorization/roleAssignments",
    "Microsoft.Authorization/roleDefinitions",
    "Microsoft.Resources/subscriptions",
    "Microsoft.Resources/subscriptions/resourceGroups",
]

print("\n\n==============================")
print("SAMPLE RAW RESOURCES")
print("==============================")

for wanted in SAMPLE_TYPES:

    for resource in raw_evidence:

        if resource.get("type") != wanted:
            continue

        print("\n--------------------------------")
        print(wanted)
        print("--------------------------------")

        print(resource)

        break

#
# Normalization
#

print("\n\nNormalizing evidence...")

normalized = collector.normalize(
    raw_evidence,
)

print(
    "\nNormalized records:",
    len(normalized),
)

#
# Service summary
#

service_summary = Counter()

for record in normalized:

    service_summary[
        record.data.get(
            "service",
            "unknown",
        )
    ] += 1

print("\nAzure Services")

for service, count in sorted(
    service_summary.items()
):
    print(
        f"{service}: {count}"
    )

#
# Normalized resource summary
#

normalized_summary = Counter()

for record in normalized:

    normalized_summary[
        record.data.get(
            "azure_type",
            "Unknown",
        )
    ] += 1

print("\nNormalized Azure Resource Types")

for resource_type, count in sorted(
    normalized_summary.items()
):
    print(
        f"{resource_type}: {count}"
    )

#
# Sample normalized resources
#

print("\n\n==============================")
print("SAMPLE NORMALIZED RESOURCES")
print("==============================")

for wanted in SAMPLE_TYPES:

    for record in normalized:

        if (
            record.data.get(
                "azure_type"
            )
            != wanted
        ):
            continue

        print("\n================================")
        print(
            "RESOURCE TYPE:",
            wanted,
        )
        print("================================")

        print(
            "Name:",
            record.data.get("name"),
        )

        print(
            "Service:",
            record.data.get("service"),
        )

        print(
            "Location:",
            record.data.get("location"),
        )

        print(
            "Subscription:",
            record.data.get(
                "subscription_id",
            ),
        )

        print(
            "Resource Group:",
            record.data.get(
                "resource_group",
            ),
        )

        print(
            "Resource ID:",
            record.resource_id,
        )

        print("\nFull normalized payload:\n")

        print(record.data)

        break

#
# VM inventory
#

print("\n\n==============================")
print("VIRTUAL MACHINES")
print("==============================")

for record in normalized:

    if (
        record.data.get(
            "azure_type"
        )
        != "Microsoft.Compute/virtualMachines"
    ):
        continue

    print(
        f"{record.data.get('name')} | "
        f"{record.data.get('location')} | "
        f"{record.data.get('resource_group')}"
    )

#
# Storage Accounts
#

print("\n\n==============================")
print("STORAGE ACCOUNTS")
print("==============================")

for record in normalized:

    if (
        record.data.get(
            "azure_type"
        )
        != "Microsoft.Storage/storageAccounts"
    ):
        continue

    print(
        f"{record.data.get('name')} | "
        f"{record.data.get('location')} | "
        f"{record.data.get('resource_group')}"
    )

#
# Network Security Groups
#

print("\n\n==============================")
print("NETWORK SECURITY GROUPS")
print("==============================")

for record in normalized:

    if (
        record.data.get(
            "azure_type"
        )
        != "Microsoft.Network/networkSecurityGroups"
    ):
        continue

    print(
        f"{record.data.get('name')} | "
        f"{record.data.get('location')} | "
        f"{record.data.get('resource_group')}"
    )

#
# Virtual Networks
#

print("\n\n==============================")
print("VIRTUAL NETWORKS")
print("==============================")

for record in normalized:

    if (
        record.data.get(
            "azure_type"
        )
        != "Microsoft.Network/virtualNetworks"
    ):
        continue

    print(
        f"{record.data.get('name')} | "
        f"{record.data.get('location')} | "
        f"{record.data.get('resource_group')}"
    )

#
# Key Vaults
#

print("\n\n==============================")
print("KEY VAULTS")
print("==============================")

for record in normalized:

    if (
        record.data.get(
            "azure_type"
        )
        != "Microsoft.KeyVault/vaults"
    ):
        continue

    print(
        f"{record.data.get('name')} | "
        f"{record.data.get('location')} | "
        f"{record.data.get('resource_group')}"
    )

#
# App Services
#

print("\n\n==============================")
print("APP SERVICES")
print("==============================")

for record in normalized:

    if (
        record.data.get(
            "azure_type"
        )
        != "Microsoft.Web/sites"
    ):
        continue

    print(
        f"{record.data.get('name')} | "
        f"{record.data.get('location')} | "
        f"{record.data.get('resource_group')}"
    )

print("\n\nAzure collection completed successfully.")
