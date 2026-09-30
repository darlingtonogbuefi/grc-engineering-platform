"""
Azure validator unit tests.

Validates:
- Validator module loads
- Validation functions exist
- Valid evidence structures pass
- Invalid evidence structures fail
"""

from __future__ import annotations

import importlib


def get_validator():

    return importlib.import_module("collectors.azure.validator")


def test_validator_module_loads():

    module = get_validator()

    assert module is not None


def test_validator_functions_exist():

    module = get_validator()

    assert hasattr(
        module,
        "validate",
    ), "Azure validator missing validate()"


def test_valid_evidence():

    module = get_validator()

    evidence = {
        "collector": "azure.resources",
        "provider": "azure",
        "resource_id": ("/subscriptions/sub-001/resourceGroups/demo"),
        "resource_type": ("Microsoft.Resources/resourceGroups"),
        "data": {
            "id": ("/subscriptions/sub-001/resourceGroups/demo"),
            "name": "demo",
        },
    }

    result = module.validate(evidence)

    assert result is True


def test_missing_resource_id():

    module = get_validator()

    evidence = {
        "collector": "azure.resources",
        "provider": "azure",
        "data": {
            "name": "demo",
        },
    }

    result = module.validate(evidence)

    assert result is False


def test_missing_provider():

    module = get_validator()

    evidence = {
        "collector": "azure.resources",
        "resource_id": "resource-001",
        "data": {},
    }

    result = module.validate(evidence)

    assert result is False


def test_empty_evidence():

    module = get_validator()

    result = module.validate({})

    assert result is False


def test_validator_handles_none():

    module = get_validator()

    result = module.validate(None)

    assert result is False
