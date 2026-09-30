"""
Azure full pipeline live test.

Validates the complete workflow:

Azure authentication
    ->
resource discovery
    ->
resource collection
    ->
normalization
    ->
validation
    ->
evidence writing
"""

from __future__ import annotations

import json
import os

import pytest

from collectors.azure.collector import AzureCollector


@pytest.fixture
def collector(tmp_path):

    config = {
        "tenant_id": os.environ["TENANT_ID"],
        "client_id": os.environ["CLIENT_ID"],
        "client_secret": os.environ["CLIENT_SECRET"],
        "subscription_id": os.environ["AZURE_SUBSCRIPTION_ID"],
        "storage_path": str(tmp_path),
    }

    return AzureCollector(config=config)


@pytest.mark.production
def test_full_azure_pipeline(collector):

    #
    # Authentication
    #
    collector.authenticate()

    assert collector.authenticator.token is not None

    #
    # Discovery
    #
    discovered = collector.discover()

    assert discovered

    print("\nDiscovered queries:")

    for item in discovered:
        print(
            " -",
            item,
        )

    #
    # Collection
    #
    raw_evidence = collector.collect(discovered)

    assert raw_evidence

    print(
        "\nRaw resources collected:",
        len(raw_evidence),
    )

    #
    # Normalization
    #
    normalized = collector.normalize(raw_evidence)

    assert normalized

    print(
        "\nNormalized records:",
        len(normalized),
    )

    #
    # Create evidence envelope
    #
    evidence_payload = {
        "collector": "azure",
        "run_id": collector.run_id,
        "evidence": [record.to_dict() for record in normalized],
    }

    #
    # Validation
    #
    validation_result = collector.validator.validate(evidence_payload)

    assert validation_result is True

    #
    # Evidence writing
    #
    output_file = collector.evidence_writer.save(evidence_payload)

    assert output_file

    assert __import__("pathlib").Path(output_file).exists()

    #
    # Verify written JSON
    #
    saved = json.loads(
        open(
            output_file,
            encoding="utf-8",
        ).read()
    )

    assert saved["collector"] == "azure"

    assert saved["run_id"] == collector.run_id

    assert saved["evidence"]

    print(
        "\nEvidence written:",
        output_file,
    )
