#!/usr/bin/env python3
"""
Production test for the Azure collector.

Validates:

- Azure Resource Manager authentication
- Collector metadata
- Resource discovery
- Existing hard-coded resource queries
- Generic Azure ARM resource inventory
- Evidence collection
- Evidence normalization
- Resource inventory summary
- Comparison between generic ARM inventory and collector inventory
- Sample raw resources
- Sample normalized resources
- VM inventory
- Storage account inventory
- Network security group inventory
- Virtual network inventory
- Key Vault inventory
- App Service inventory

The generic ARM inventory is intentionally tested alongside the existing
collector queries. This allows the ARM approach to be verified before
removing or changing the existing hard-coded collection method.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from typing import Any, cast

# ============================================================================
# Add project root to Python module search path
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from collectors.azure.auth import AzureAuthenticator
from collectors.azure.collector import AzureCollector


# ============================================================================
# Configuration
# ============================================================================

config = {
    "tenant_id": os.environ["TENANT_ID"],
    "client_id": os.environ["CLIENT_ID"],
    "client_secret": os.environ["CLIENT_SECRET"],
    "subscription_id": os.environ["AZURE_SUBSCRIPTION_ID"],
}


SUBSCRIPTION_ID = config["subscription_id"]

ARM_BASE_URL = "https://management.azure.com"

ARM_RESOURCE_ENDPOINT = (
    f"{ARM_BASE_URL}"
    f"/subscriptions/{SUBSCRIPTION_ID}"
    f"/resources"
)

ARM_API_VERSION = "2024-03-01"


# ============================================================================
# Expected resource types
#
# These are retained from the existing test.
#
# They are NOT used to limit generic ARM discovery.
# ============================================================================

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


# ============================================================================
# Generic Azure ARM resource collection
#
# This is deliberately independent from collector.collect().
#
# Purpose:
#   Verify that Azure's generic ARM resource endpoint can discover the
#   complete resource inventory before changing the existing collector.
# ============================================================================

def collect_arm_resources(token: str) -> list[dict]:
    """
    Collect every Azure ARM resource visible in the subscription.

    Uses:

        GET /subscriptions/{subscriptionId}/resources

    and follows Azure's nextLink pagination.

    Returns:
        A list containing the raw Azure ARM resource objects.
    """

    resources: list[dict] = []

    url = (
        f"{ARM_RESOURCE_ENDPOINT}"
        f"?api-version={ARM_API_VERSION}"
    )

    request_count = 0

    while url:
        request_count += 1

        print(
            f"ARM request #{request_count}: "
            f"{url}"
        )

        request = Request(
            url,
            method="GET",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
        )

        try:
            with urlopen(request, timeout=120) as response:
                response_body = response.read().decode("utf-8")

        except HTTPError as exc:
            error_body = ""

            try:
                error_body = exc.read().decode("utf-8")
            except Exception:
                pass

            raise RuntimeError(
                "Azure ARM resource request failed. "
                f"HTTP {exc.code}: {error_body}"
            ) from exc

        except URLError as exc:
            raise RuntimeError(
                "Unable to connect to Azure Resource Manager: "
                f"{exc}"
            ) from exc

        payload = json.loads(response_body)

        page_resources = payload.get("value", [])

        if not isinstance(page_resources, list):
            raise RuntimeError(
                "Azure ARM response contained an unexpected "
                "'value' structure."
            )

        resources.extend(page_resources)

        print(
            f"  Resources returned on page: "
            f"{len(page_resources)}"
        )

        url = payload.get("nextLink")

    print(
        f"\nARM generic inventory collected: "
        f"{len(resources)} resources"
    )

    print(
        f"ARM pages requested: {request_count}"
    )

    return resources


# ============================================================================
# ARM inventory summary
# ============================================================================

def summarize_resource_types(
    resources: list[dict],
) -> Counter:
    """
    Build a resource-type count from raw Azure ARM resources.
    """

    summary = Counter()

    for resource in resources:
        resource_type = resource.get(
            "type",
            "Unknown",
        )

        summary[resource_type] += 1

    return summary


# ============================================================================
# Print resource type summary
# ============================================================================

def print_resource_summary(
    title: str,
    summary: Counter,
) -> None:
    """
    Print resource type counts.
    """

    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)

    if not summary:
        print("No resources found.")
        return

    for resource_type, count in sorted(
        summary.items()
    ):
        print(
            f"{resource_type}: {count}"
        )


# ============================================================================
# Compare existing collector inventory against generic ARM inventory
# ============================================================================

def compare_inventories(
    arm_resources: list[dict],
    collector_resources: list[dict],
) -> None:
    """
    Compare resource IDs discovered through the generic ARM endpoint
    against resource IDs returned by the existing collector.

    This does not fail the test because the existing collector may
    intentionally collect additional evidence or special resource
    types differently.

    The purpose is visibility during migration.
    """

    print("\n")
    print("=" * 70)
    print("ARM VS EXISTING COLLECTOR INVENTORY")
    print("=" * 70)

    arm_ids = {
        resource.get("id")
        for resource in arm_resources
        if resource.get("id")
    }

    collector_ids = {
        resource.get("id")
        for resource in collector_resources
        if resource.get("id")
    }

    arm_only = arm_ids - collector_ids
    collector_only = collector_ids - arm_ids
    common = arm_ids & collector_ids

    print(
        f"Generic ARM resources:       {len(arm_ids)}"
    )

    print(
        f"Existing collector resources: {len(collector_ids)}"
    )

    print(
        f"Resources found by both:      {len(common)}"
    )

    print(
        f"ARM-only resources:            {len(arm_only)}"
    )

    print(
        f"Collector-only resources:      {len(collector_only)}"
    )

    if arm_only:
        print("\nARM-only resource types:")

        arm_only_types = Counter()

        arm_resource_by_id = {
            resource.get("id"): resource
            for resource in arm_resources
            if resource.get("id")
        }

        for resource_id in arm_only:
            resource = arm_resource_by_id.get(
                resource_id,
                {},
            )

            arm_only_types[
                resource.get(
                    "type",
                    "Unknown",
                )
            ] += 1

        for resource_type, count in sorted(
            arm_only_types.items()
        ):
            print(
                f"  {resource_type}: {count}"
            )

    if collector_only:
        print("\nCollector-only resource types:")

        collector_only_types = Counter()

        collector_resource_by_id = {
            resource.get("id"): resource
            for resource in collector_resources
            if resource.get("id")
        }

        for resource_id in collector_only:
            resource = collector_resource_by_id.get(
                resource_id,
                {},
            )

            collector_only_types[
                resource.get(
                    "type",
                    "Unknown",
                )
            ] += 1

        for resource_type, count in sorted(
            collector_only_types.items()
        ):
            print(
                f"  {resource_type}: {count}"
            )

    if not arm_only and not collector_only:
        print(
            "\nSUCCESS: Generic ARM and existing "
            "collector inventories contain the same "
            "resource IDs."
        )
    else:
        print(
            "\nINFO: Inventory differences detected."
        )

        print(
            "This is expected during migration and "
            "should be investigated before replacing "
            "the existing hard-coded queries."
        )


# ============================================================================
# Validate expected resource types against generic ARM inventory
# ============================================================================

def validate_expected_types(
    arm_resources: list[dict],
) -> None:
    """
    Check whether the resource types previously collected by the
    hard-coded queries are also visible through generic ARM discovery.
    """

    discovered_types = {
        resource.get("type")
        for resource in arm_resources
    }

    print("\n")
    print("=" * 70)
    print("GENERIC ARM VALIDATION OF EXISTING RESOURCE TYPES")
    print("=" * 70)

    for resource_type in SAMPLE_TYPES:
        count = sum(
            1
            for resource in arm_resources
            if resource.get("type") == resource_type
        )

        if count:
            print(
                f"[FOUND] {resource_type}: {count}"
            )
        else:
            print(
                f"[NOT FOUND] {resource_type}"
            )


# ============================================================================
# Validate authentication independently
# ============================================================================

print("\n")
print("=" * 70)
print("AZURE AUTHENTICATION")
print("=" * 70)

auth = AzureAuthenticator(config)

auth.acquire_token()

token = auth.token

print(
    "Token acquired:",
    bool(token),
)

if not token:
    raise RuntimeError(
        "Azure authentication failed: no token acquired."
    )


# ============================================================================
# Generic ARM inventory verification
#
# This happens BEFORE the existing collector collection.
#
# This proves the new ARM method works independently.
# ============================================================================

print("\n")
print("=" * 70)
print("GENERIC AZURE ARM RESOURCE DISCOVERY")
print("=" * 70)

print(
    "\nEndpoint:"
)

print(
    ARM_RESOURCE_ENDPOINT
)

print(
    "\nAPI version:"
)

print(
    ARM_API_VERSION
)

print(
    "\nCollecting complete ARM resource inventory..."
)

arm_resources = collect_arm_resources(
    token
)

arm_resource_summary = summarize_resource_types(
    arm_resources
)

print_resource_summary(
    "GENERIC ARM RESOURCE TYPES",
    arm_resource_summary,
)

validate_expected_types(
    arm_resources
)


# ============================================================================
# Collector initialization
# ============================================================================

print("\n")
print("=" * 70)
print("EXISTING AZURE COLLECTOR")
print("=" * 70)

collector = AzureCollector(
    manifest=cast(Any, None),
    evidence_writer=None,
    normalizer=None,
    validator=None,
    config=config,
)

collector.authenticate()

print("\nCollector metadata:")

print(
    collector.metadata()
)


# ============================================================================
# Discovery
#
# This remains unchanged.
#
# It allows you to verify that the current hard-coded query method
# continues to work while the generic ARM method is being tested.
# ============================================================================

print("\n")
print("=" * 70)
print("EXISTING COLLECTOR DISCOVERY")
print("=" * 70)

print("\nDiscovering resources...")

queries = collector.discover()

print()

for query in queries:
    print(
        " -",
        query,
    )


# ============================================================================
# Check whether generic resources.yml is being discovered
# ============================================================================

print("\n")
print("=" * 70)
print("GENERIC ARM QUERY DISCOVERY CHECK")
print("=" * 70)

generic_query_found = False

for query in queries:
    query_text = str(query)

    if (
        "azure.resources" in query_text
        or "resources.yml" in query_text
        or "/resources" in query_text
    ):
        generic_query_found = True

        print(
            "Generic ARM resource query detected:"
        )

        print(
            query
        )

if generic_query_found:
    print(
        "\nSUCCESS: The collector discovery "
        "contains the generic ARM resource query."
    )
else:
    print(
        "\nINFO: Generic ARM resource query was "
        "not detected in collector.discover()."
    )

    print(
        "The independent ARM test above still "
        "confirms whether the endpoint itself works."
    )


# ============================================================================
# Existing Collection
# ============================================================================

print("\n")
print("=" * 70)
print("EXISTING COLLECTOR EVIDENCE COLLECTION")
print("=" * 70)

print("\nCollecting evidence...")

raw_evidence = collector.collect(
    queries,
)

print(
    "\nCollected resources:",
    len(raw_evidence),
)


# ============================================================================
# Existing collector resource inventory
# ============================================================================

resource_summary = Counter()

for resource in raw_evidence:
    resource_summary[
        resource.get(
            "type",
            "Unknown",
        )
    ] += 1


print_resource_summary(
    "EXISTING COLLECTOR AZURE RESOURCE TYPES",
    resource_summary,
)


# ============================================================================
# Compare generic ARM inventory against existing collector
# ============================================================================

compare_inventories(
    arm_resources,
    raw_evidence,
)


# ============================================================================
# Sample raw resources
# ============================================================================

print("\n")
print("=" * 70)
print("SAMPLE RAW RESOURCES")
print("=" * 70)

for wanted in SAMPLE_TYPES:

    found = False

    for resource in raw_evidence:

        if resource.get("type") != wanted:
            continue

        print("\n--------------------------------")
        print(wanted)
        print("--------------------------------")

        print(resource)

        found = True
        break

    if not found:
        print("\n--------------------------------")
        print(wanted)
        print("--------------------------------")
        print("Not present in existing collector evidence.")


# ============================================================================
# Generic ARM sample resources
# ============================================================================

print("\n")
print("=" * 70)
print("SAMPLE GENERIC ARM RESOURCES")
print("=" * 70)

for wanted in SAMPLE_TYPES:

    found = False

    for resource in arm_resources:

        if resource.get("type") != wanted:
            continue

        print("\n--------------------------------")
        print(wanted)
        print("--------------------------------")

        print(resource)

        found = True
        break

    if not found:
        print("\n--------------------------------")
        print(wanted)
        print("--------------------------------")
        print("Not present in generic ARM inventory.")


# ============================================================================
# Normalization
# ============================================================================

print("\n")
print("=" * 70)
print("NORMALIZATION")
print("=" * 70)

print("\nNormalizing evidence...")

normalized = collector.normalize(
    raw_evidence,
)

print(
    "\nNormalized records:",
    len(normalized),
)


# ============================================================================
# Service summary
# ============================================================================

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


# ============================================================================
# Normalized resource summary
# ============================================================================

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


# ============================================================================
# Sample normalized resources
# ============================================================================

print("\n")
print("=" * 70)
print("SAMPLE NORMALIZED RESOURCES")
print("=" * 70)

for wanted in SAMPLE_TYPES:

    found = False

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
            record.data.get(
                "name"
            ),
        )

        print(
            "Service:",
            record.data.get(
                "service"
            ),
        )

        print(
            "Location:",
            record.data.get(
                "location"
            ),
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

        print(
            "\nFull normalized payload:\n"
        )

        print(
            record.data
        )

        found = True
        break

    if not found:
        print("\n================================")
        print(
            "RESOURCE TYPE:",
            wanted,
        )
        print("================================")
        print(
            "Not present in normalized evidence."
        )


# ============================================================================
# VM inventory
# ============================================================================

print("\n")
print("=" * 70)
print("VIRTUAL MACHINES")
print("=" * 70)

vm_count = 0

for record in normalized:

    if (
        record.data.get(
            "azure_type"
        )
        != "Microsoft.Compute/virtualMachines"
    ):
        continue

    vm_count += 1

    print(
        f"{record.data.get('name')} | "
        f"{record.data.get('location')} | "
        f"{record.data.get('resource_group')}"
    )

print(
    f"Total virtual machines: {vm_count}"
)


# ============================================================================
# Storage Accounts
# ============================================================================

print("\n")
print("=" * 70)
print("STORAGE ACCOUNTS")
print("=" * 70)

storage_count = 0

for record in normalized:

    if (
        record.data.get(
            "azure_type"
        )
        != "Microsoft.Storage/storageAccounts"
    ):
        continue

    storage_count += 1

    print(
        f"{record.data.get('name')} | "
        f"{record.data.get('location')} | "
        f"{record.data.get('resource_group')}"
    )

print(
    f"Total storage accounts: {storage_count}"
)


# ============================================================================
# Network Security Groups
# ============================================================================

print("\n")
print("=" * 70)
print("NETWORK SECURITY GROUPS")
print("=" * 70)

nsg_count = 0

for record in normalized:

    if (
        record.data.get(
            "azure_type"
        )
        != "Microsoft.Network/networkSecurityGroups"
    ):
        continue

    nsg_count += 1

    print(
        f"{record.data.get('name')} | "
        f"{record.data.get('location')} | "
        f"{record.data.get('resource_group')}"
    )

print(
    f"Total network security groups: {nsg_count}"
)


# ============================================================================
# Virtual Networks
# ============================================================================

print("\n")
print("=" * 70)
print("VIRTUAL NETWORKS")
print("=" * 70)

vnet_count = 0

for record in normalized:

    if (
        record.data.get(
            "azure_type"
        )
        != "Microsoft.Network/virtualNetworks"
    ):
        continue

    vnet_count += 1

    print(
        f"{record.data.get('name')} | "
        f"{record.data.get('location')} | "
        f"{record.data.get('resource_group')}"
    )

print(
    f"Total virtual networks: {vnet_count}"
)


# ============================================================================
# Key Vaults
# ============================================================================

print("\n")
print("=" * 70)
print("KEY VAULTS")
print("=" * 70)

key_vault_count = 0

for record in normalized:

    if (
        record.data.get(
            "azure_type"
        )
        != "Microsoft.KeyVault/vaults"
    ):
        continue

    key_vault_count += 1

    print(
        f"{record.data.get('name')} | "
        f"{record.data.get('location')} | "
        f"{record.data.get('resource_group')}"
    )

print(
    f"Total Key Vaults: {key_vault_count}"
)


# ============================================================================
# App Services
# ============================================================================

print("\n")
print("=" * 70)
print("APP SERVICES")
print("=" * 70)

app_service_count = 0

for record in normalized:

    if (
        record.data.get(
            "azure_type"
        )
        != "Microsoft.Web/sites"
    ):
        continue

    app_service_count += 1

    print(
        f"{record.data.get('name')} | "
        f"{record.data.get('location')} | "
        f"{record.data.get('resource_group')}"
    )

print(
    f"Total App Services: {app_service_count}"
)


# ============================================================================
# Final migration verification
# ============================================================================

print("\n")
print("=" * 70)
print("ARM MIGRATION VERIFICATION")
print("=" * 70)

print(f"Generic ARM inventory:        " f"{len(arm_resources)} resources")

print(f"Existing collector inventory: " f"{len(raw_evidence)} resources")

print(f"Normalized collector records: " f"{len(normalized)}")

print(f"Generic ARM resource types:   " f"{len(arm_resource_summary)}")

print(f"Collector resource types:     " f"{len(resource_summary)}")

# ---------------------------------------------------------------------------
# Generic ARM inventory
#
# Zero resources is valid because the target subscription currently has
# no deployed ARM resources.
# ---------------------------------------------------------------------------

if arm_resources:
    print("\nSUCCESS: Generic Azure ARM resource " "discovery returned resources.")
else:
    print("\nINFO: Generic Azure ARM resource " "discovery returned zero resources.")

    print(
        "The target Azure subscription currently " "contains no deployed ARM resources."
    )

# ---------------------------------------------------------------------------
# Existing collector inventory
#
# Keep this as a real failure condition because the existing collector is
# expected to return its configured subscription, role, definition, and
# security evidence.
# ---------------------------------------------------------------------------

if raw_evidence:
    print("\nSUCCESS: Existing collector still " "returns resources.")
else:
    raise RuntimeError("Existing collector returned zero resources.")

# ---------------------------------------------------------------------------
# Migration status
# ---------------------------------------------------------------------------

print("\nThe existing hard-coded collection method " "has NOT been removed.")

print("The generic ARM method has been tested " "independently.")

print("\nAzure collection completed successfully.")
