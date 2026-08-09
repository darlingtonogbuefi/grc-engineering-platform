"""
Azure normalizer unit tests.

Validates:
- Normalizer modules load
- Expected normalization functions exist
- Returned data structure is consistent
"""

from __future__ import annotations

import importlib

NORMALIZERS = [
    "compute",
    "iam",
    "logging",
    "network",
    "policy",
    "resource",
    "security",
    "storage",
    "subscription",
]


def test_normalizer_modules_load():

    for normalizer in NORMALIZERS:

        module = importlib.import_module(f"collectors.azure.normalizers.{normalizer}")

        assert module is not None


def test_normalizers_have_normalize_function():

    for normalizer in NORMALIZERS:

        module = importlib.import_module(f"collectors.azure.normalizers.{normalizer}")

        assert hasattr(
            module,
            "normalize",
        ), f"{normalizer} missing normalize()"


def test_resource_normalizer():

    module = importlib.import_module("collectors.azure.normalizers.resource")

    data = {
        "id": "/subscriptions/sub-001/resourceGroups/demo",
        "name": "demo",
        "type": "Microsoft.Resources/resourceGroups",
        "location": "uksouth",
        "tags": {
            "env": "test",
        },
    }

    result = module.normalize(data)

    assert isinstance(
        result,
        dict,
    )

    assert result["id"] == ("/subscriptions/sub-001/resourceGroups/demo")

    assert result["name"] == "demo"


def test_subscription_normalizer():

    module = importlib.import_module("collectors.azure.normalizers.subscription")

    data = {
        "id": "/subscriptions/sub-001",
        "subscriptionId": "sub-001",
        "displayName": "Production",
        "tenantId": "tenant-001",
        "state": "Enabled",
    }

    result = module.normalize(data)

    assert isinstance(
        result,
        dict,
    )

    assert result["subscription_id"] == "sub-001"

    assert result["display_name"] == "Production"


def test_network_normalizer():

    module = importlib.import_module("collectors.azure.normalizers.network")

    data = {
        "id": "/subscriptions/sub-001/network/vnet01",
        "name": "vnet01",
        "location": "uksouth",
        "properties": {
            "provisioningState": "Succeeded",
        },
    }

    result = module.normalize(data)

    assert isinstance(
        result,
        dict,
    )

    assert result["id"].endswith("vnet01")


def test_security_normalizer():

    module = importlib.import_module("collectors.azure.normalizers.security")

    data = {
        "id": "/subscriptions/sub-001/vault01",
        "name": "vault01",
        "properties": {
            "enableSoftDelete": True,
            "enablePurgeProtection": True,
        },
    }

    result = module.normalize(data)

    assert isinstance(
        result,
        dict,
    )

    assert result["id"] == ("/subscriptions/sub-001/vault01")


def test_storage_normalizer():

    module = importlib.import_module("collectors.azure.normalizers.storage")

    data = {
        "id": "/subscriptions/sub-001/storage01",
        "name": "storage01",
        "properties": {
            "supportsHttpsTrafficOnly": True,
        },
    }

    result = module.normalize(data)

    assert isinstance(
        result,
        dict,
    )

    assert result["id"].endswith("storage01")


def test_policy_normalizer():

    module = importlib.import_module("collectors.azure.normalizers.policy")

    data = {
        "id": "/subscriptions/sub-001/policy01",
        "name": "Require HTTPS",
        "properties": {
            "displayName": "Require HTTPS",
        },
    }

    result = module.normalize(data)

    assert isinstance(
        result,
        dict,
    )

    assert result["name"] == "Require HTTPS"


def test_logging_normalizer():

    module = importlib.import_module("collectors.azure.normalizers.logging")

    data = {
        "eventDataId": "event-001",
        "operationName": {
            "value": "Create Resource",
        },
        "status": {
            "value": "Succeeded",
        },
    }

    result = module.normalize(data)

    assert isinstance(
        result,
        dict,
    )

    assert result["event_id"] == "event-001"


def test_iam_normalizer():

    module = importlib.import_module("collectors.azure.normalizers.iam")

    data = {
        "id": "/subscriptions/sub-001/roleAssignments/a1",
        "properties": {
            "principalId": "user-001",
            "roleDefinitionId": "role-001",
        },
    }

    result = module.normalize(data)

    assert isinstance(
        result,
        dict,
    )

    assert result["principal_id"] == "user-001"
