"""
Base Evidence Writer.

Defines the evidence storage interface used by collectors.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict
from pathlib import Path
import hashlib
import json
import logging
import uuid

from .exceptions import EvidenceError

logger = logging.getLogger(__name__)


class BaseEvidenceWriter(ABC):
    """Abstract evidence storage provider."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.storage_path = Path(
            config.get("storage_path", "evidence")
        )

    def write(
        self,
        collector: str,
        run_id: str,
        evidence: Any,
    ) -> str:
        """
        Store evidence artifact.

        Returns:
            Evidence location.
        """

        try:
            timestamp = datetime.now(
                timezone.utc
            )

            evidence_id = str(
                uuid.uuid4()
            )

            payload = {
                "evidence_id": evidence_id,
                "collector": collector,
                "run_id": run_id,
                "collected_at": timestamp.isoformat(),
                "records": evidence,
            }

            checksum = self.hash(payload)

            payload["checksum"] = checksum

            return self.save(
                payload
            )

        except Exception as exc:
            logger.exception(
                "Evidence write failed"
            )

            raise EvidenceError(
                "Unable to store evidence"
            ) from exc

    @abstractmethod
    def save(
        self,
        evidence: Dict[str, Any],
    ) -> str:
        """
        Persist evidence.

        Implemented by storage provider.

        Examples:

            Local filesystem

            Azure Blob Storage

            S3

            Database

        """
        pass

    def hash(
        self,
        evidence: Dict[str, Any],
    ) -> str:
        """
        Generate evidence integrity hash.
        """

        content = json.dumps(
            evidence,
            sort_keys=True,
            default=str,
        ).encode()

        return hashlib.sha256(
            content
        ).hexdigest()

    def metadata(
        self,
    ) -> Dict[str, Any]:
        """
        Return storage metadata.
        """

        return {
            "storage_path": str(
                self.storage_path
            ),
            "writer": self.__class__.__name__,
        }
