"""
Mock Azure Resource Manager API responses.

Provides reusable fake ARM payloads for unit tests
without requiring Azure connectivity.
"""

from __future__ import annotations

SUBSCRIPTION_RESPONSE = {
    "id": "/subscriptions/00000000-0000-0000-0000-000000000000",
    "subscriptionId": "00000000-0000-0000-0000-000000000000",
    "displayName": "Mock Azure Subscription",
    "tenantId": "00000000-0000-0000-0000-000000000000",
    "state": "Enabled",
}


RESOURCE_GROUPS_RESPONSE = {
    "value": [
        {
            "id": (
                "/subscriptions/"
                "00000000-0000-0000-0000-000000000000/"
                "resourceGroups/mock-rg"
            ),
            "name": "mock-rg",
            "type": "Microsoft.Resources/resourceGroups",
            "location": "uksouth",
            "tags": {"environment": "test"},
            "properties": {"provisioningState": "Succeeded"},
        }
    ]
}


RESOURCES_RESPONSE = {
    "value": [
        {
            "id": (
                "/subscriptions/"
                "00000000-0000-0000-0000-000000000000/"
                "resourceGroups/mock-rg/"
                "providers/Microsoft.Storage/"
                "storageAccounts/mockstorage"
            ),
            "name": "mockstorage",
            "type": ("Microsoft.Storage/" "storageAccounts"),
            "location": "uksouth",
            "tags": {"environment": "test"},
        }
    ]
}


STORAGE_ACCOUNTS_RESPONSE = {
    "value": [
        {
            "id": "/storageAccounts/mockstorage",
            "name": "mockstorage",
            "type": "Microsoft.Storage/storageAccounts",
            "location": "uksouth",
            "properties": {
                "provisioningState": "Succeeded",
                "minimumTlsVersion": "TLS1_2",
                "supportsHttpsTrafficOnly": True,
                "allowBlobPublicAccess": False,
            },
        }
    ]
}


KEY_VAULTS_RESPONSE = {
    "value": [
        {
            "id": "/vaults/mockvault",
            "name": "mockvault",
            "type": "Microsoft.KeyVault/vaults",
            "location": "uksouth",
            "properties": {
                "enableSoftDelete": True,
                "enablePurgeProtection": True,
                "enableRbacAuthorization": True,
            },
        }
    ]
}


ROLE_ASSIGNMENTS_RESPONSE = {
    "value": [
        {
            "id": "/roleAssignments/mock",
            "name": "mock-role-assignment",
            "type": ("Microsoft.Authorization/" "roleAssignments"),
            "properties": {
                "principalId": "mock-user-id",
                "principalType": "User",
                "roleDefinitionId": "mock-role-id",
                "scope": "/subscriptions/mock",
            },
        }
    ]
}


POLICY_ASSIGNMENTS_RESPONSE = {
    "value": [
        {
            "id": "/policyAssignments/mock",
            "name": "mock-policy",
            "type": ("Microsoft.Authorization/" "policyAssignments"),
            "properties": {
                "displayName": "Mock Security Policy",
                "enforcementMode": "Default",
            },
        }
    ]
}


ACTIVITY_LOGS_RESPONSE = {
    "value": [
        {
            "eventDataId": "mock-event-id",
            "eventTimestamp": "2026-01-01T00:00:00Z",
            "operationName": {"value": "Microsoft.Resources/deployments/write"},
            "category": {"value": "Administrative"},
            "status": {"value": "Succeeded"},
        }
    ]
}


EMPTY_RESPONSE = {"value": []}
