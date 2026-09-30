"""
Mock Microsoft Graph responses.

Provides representative Microsoft Graph
responses for unit and integration tests.
"""

from __future__ import annotations


RESPONSES = {

    "/organization": {
        "value": [
            {
                "id": "tenant-001",
                "displayName": "Contoso Ltd",
                "verifiedDomains": [
                    {
                        "name": "contoso.com",
                    }
                ],
            }
        ]
    },

    "/users": {
        "value": [
            {
                "id": "user-001",
                "displayName": "Alice Smith",
                "userPrincipalName": "alice@contoso.com",
                "userType": "Member",
                "accountEnabled": True,
            },
            {
                "id": "user-002",
                "displayName": "Bob Jones",
                "userPrincipalName": "bob@contoso.com",
                "userType": "Guest",
                "accountEnabled": True,
            },
        ]
    },

    "/groups": {
        "value": [
            {
                "id": "group-001",
                "displayName": "IT Administrators",
                "securityEnabled": True,
            }
        ]
    },

    "/devices": {
        "value": [
            {
                "id": "device-001",
                "displayName": "LAPTOP-001",
                "operatingSystem": "Windows",
                "isCompliant": True,
            }
        ]
    },

    "/applications": {
        "value": [
            {
                "id": "app-001",
                "displayName": "Payroll Application",
                "appId": "11111111-1111-1111-1111-111111111111",
            }
        ]
    },

    "/directoryRoles": {
        "value": [
            {
                "id": "role-001",
                "displayName": "Global Administrator",
            }
        ]
    },

    "/servicePrincipals": {
        "value": [
            {
                "id": "sp-001",
                "displayName": "Microsoft Graph",
                "appId": "00000003-0000-0000-c000-000000000000",
            }
        ]
    },

    "/identity/conditionalAccess/policies": {
        "value": [
            {
                "id": "policy-001",
                "displayName": "Require MFA",
                "state": "enabled",
            }
        ]
    },

    "/auditLogs/directoryAudits": {
        "value": [
            {
                "id": "audit-001",
                "activityDisplayName": "Add user",
                "result": "success",
            }
        ]
    },

    "/auditLogs/signIns": {
        "value": [
            {
                "id": "signin-001",
                "userDisplayName": "Alice Smith",
                "status": {
                    "errorCode": 0,
                },
            }
        ]
    },

    "/identityProtection/riskyUsers": {
        "value": [
            {
                "id": "risk-001",
                "userDisplayName": "Bob Jones",
                "riskLevel": "medium",
            }
        ]
    },

}
