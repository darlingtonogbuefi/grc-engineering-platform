"""
Tests for schema validation.
"""

from pathlib import Path

from importers.common.schema_validator import SchemaValidator


def test_validator_initialises():

    validator = SchemaValidator()

    assert validator is not None


def test_validate_missing_file():

    validator = SchemaValidator()

    missing = (
        "does-not-exist.yml"
    )

    try:

        validator.validate(
            missing
        )

        assert False

    except FileNotFoundError:

        assert True
