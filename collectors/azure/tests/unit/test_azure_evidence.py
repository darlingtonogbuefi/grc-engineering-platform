"""
Azure evidence writer unit tests.

Validates:
- Evidence writer loads
- Evidence can be written
- Evidence can be read
- Evidence existence checks work
- Evidence deletion works
- Metadata is returned correctly
"""

from __future__ import annotations

from pathlib import Path

from collectors.azure.evidence import LocalEvidenceWriter


def get_writer(tmp_path: Path) -> LocalEvidenceWriter:
    """
    Create evidence writer using temporary storage.
    """

    writer = LocalEvidenceWriter(
        {
            "storage_path": str(tmp_path / "evidence"),
        }
    )

    return writer


def test_evidence_writer_loads(tmp_path):

    writer = get_writer(tmp_path)

    assert writer is not None


def test_save_evidence(tmp_path):

    writer = get_writer(tmp_path)

    evidence = {
        "collector": "azure.resources",
        "run_id": "test-run-001",
        "provider": "azure",
        "items": [
            {
                "id": "/subscriptions/test/resourceGroups/demo",
                "name": "demo",
            }
        ],
    }

    output = writer.save(
        evidence
    )

    assert output

    assert Path(
        output
    ).exists()


def test_evidence_exists(tmp_path):

    writer = get_writer(tmp_path)

    evidence = {
        "collector": "azure.resources",
        "run_id": "test-run-002",
        "items": [],
    }

    writer.save(
        evidence
    )

    assert writer.exists(
        "azure.resources",
        "test-run-002",
    )


def test_read_evidence(tmp_path):

    writer = get_writer(tmp_path)

    evidence = {
        "collector": "azure.resources",
        "run_id": "test-run-003",
        "items": [
            {
                "id": "resource-001",
            }
        ],
    }

    writer.save(
        evidence
    )

    result = writer.read(
        "azure.resources",
        "test-run-003",
    )

    assert isinstance(
        result,
        dict,
    )

    assert result["collector"] == (
        "azure.resources"
    )

    assert result["items"][0]["id"] == (
        "resource-001"
    )


def test_delete_evidence(tmp_path):

    writer = get_writer(tmp_path)

    evidence = {
        "collector": "azure.resources",
        "run_id": "test-run-004",
    }

    writer.save(
        evidence
    )

    assert writer.exists(
        "azure.resources",
        "test-run-004",
    )

    deleted = writer.delete(
        "azure.resources",
        "test-run-004",
    )

    assert deleted is True

    assert not writer.exists(
        "azure.resources",
        "test-run-004",
    )


def test_delete_missing_evidence(tmp_path):

    writer = get_writer(tmp_path)

    result = writer.delete(
        "azure.resources",
        "missing-run",
    )

    assert result is False


def test_evidence_metadata(tmp_path):

    writer = get_writer(tmp_path)

    metadata = writer.metadata()

    assert isinstance(
        metadata,
        dict,
    )

    assert metadata["type"] == (
        "filesystem"
    )

    assert metadata["format"] == (
        "json"
    )

    assert metadata["provider"] == (
        "azure"
    )
