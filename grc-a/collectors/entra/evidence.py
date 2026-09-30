# collectors\entra\evidence.py


"""
Microsoft Entra Evidence Writer.

Persists normalized Microsoft Entra evidence
to the local filesystem.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from collectors.base.evidence import BaseEvidenceWriter


class LocalEvidenceWriter(BaseEvidenceWriter):
    """Local filesystem evidence writer."""

    def __init__(
        self,
        config: Dict[str, Any] | None = None,
    ):
        super().__init__(config or {})

    def save(
        self,
        evidence: Dict[str, Any],
    ) -> str:
        """
        Persist evidence to the configured
        storage location.

        Directory structure:

            evidence/
                raw/
                    <collector>/
                        <run_id>/
                            evidence.json
        """

        collector = evidence.get(
            "collector",
            "unknown",
        )

        run_id = evidence.get(
            "run_id",
            "unknown",
        )

        output_dir = self.storage_path / collector / run_id

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = output_dir / "evidence.json"

        with output_file.open(
            "w",
            encoding="utf-8",
        ) as stream:
            json.dump(
                evidence,
                stream,
                indent=2,
                sort_keys=True,
                default=str,
            )

        return str(output_file)

    def exists(
        self,
        collector: str,
        run_id: str,
    ) -> bool:
        """
        Check whether evidence already exists.
        """

        path = self.storage_path / collector / run_id / "evidence.json"

        return path.exists()

    def read(
        self,
        collector: str,
        run_id: str,
    ) -> Dict[str, Any]:
        """
        Read previously stored evidence.
        """

        path = self.storage_path / collector / run_id / "evidence.json"

        with path.open(
            "r",
            encoding="utf-8",
        ) as stream:
            return json.load(stream)

    def delete(
        self,
        collector: str,
        run_id: str,
    ) -> bool:
        """
        Delete a stored evidence artifact.
        """

        path = self.storage_path / collector / run_id / "evidence.json"

        if not path.exists():
            return False

        path.unlink()

        try:
            path.parent.rmdir()
        except OSError:
            pass

        return True

    def metadata(
        self,
    ) -> Dict[str, Any]:
        """
        Return evidence writer metadata.
        """

        metadata = super().metadata()

        metadata.update(
            {
                "type": "filesystem",
                "format": "json",
            }
        )

        return metadata
