"""
Azure evidence writer tests.
"""

from __future__ import annotations

import json
from pathlib import Path

from collectors.azure.evidence import LocalEvidenceWriter


def test_evidence_writer_saves_json(tmp_path):

    writer = LocalEvidenceWriter({"storage_path": str(tmp_path)})

    evidence = {
        "collector": "azure",
        "run_id": "test-run",
        "evidence": [
            {
                "id": "vm-001",
                "type": "azure.compute.virtual_machine",
                "data": {
                    "name": "test-vm",
                    "provider": "azure",
                },
            }
        ],
    }

    output = writer.save(evidence)

    output_file = Path(output)

    assert output_file.exists()

    content = json.loads(output_file.read_text(encoding="utf-8"))

    assert content["collector"] == "azure"

    assert len(content["evidence"]) == 1
