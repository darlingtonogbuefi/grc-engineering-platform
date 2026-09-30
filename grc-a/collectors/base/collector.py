# collectors\base\collector.py

"""
Base Evidence Collector.

Defines the common lifecycle for all evidence collectors.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import logging
import uuid

from .exceptions import CollectorError
from .models import CollectionResult
from .manifest import CollectorManifest

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """Abstract base class for evidence collectors."""

    def __init__(
        self,
        manifest: CollectorManifest,
        client: Any,
        evidence_writer: Any,
        normalizer: Any,
        validator: Any,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.manifest = manifest
        self.client = client
        self.evidence_writer = evidence_writer
        self.normalizer = normalizer
        self.validator = validator
        self.config = config or {}

        self.run_id = str(uuid.uuid4())
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def execute(self) -> CollectionResult:
        """Execute collector lifecycle."""

        self.started_at = datetime.now(timezone.utc)

        logger.info(
            "Starting collector",
            extra={
                "collector": self.manifest.name,
                "run_id": self.run_id,
            },
        )

        try:
            self.authenticate()
            self.validate()

            discovered = self.discover()
            raw_evidence = self.collect(discovered)

            if not self.validator.validate(raw_evidence):
                raise CollectorError(
                    "Evidence validation failed"
                )

            normalized = self.normalize(raw_evidence)
            evidence_path = self.save(normalized)

            self.completed_at = datetime.now(timezone.utc)

            return CollectionResult(
                collector=self.manifest.name,
                run_id=self.run_id,
                started_at=self.started_at,
                completed_at=self.completed_at,
                records=len(normalized),
                evidence_path=evidence_path,
                status="success",
            )

        except Exception as exc:
            logger.exception(
                "Collector failed",
                extra={
                    "collector": self.manifest.name,
                    "run_id": self.run_id,
                },
            )

            raise CollectorError(
                f"{self.manifest.name} failed"
            ) from exc

    def authenticate(self):
        """Establish collector authentication."""

        if hasattr(self.client, "authenticate"):
            self.client.authenticate()

    def validate(self) -> bool:
        """Validate collector prerequisites."""

        return True

    @abstractmethod
    def discover(self):
        """
        Discover available resources.

        Example:
            Entra:
                users, groups, policies

            Azure:
                subscriptions, resources
        """
        pass

    @abstractmethod
    def collect(self, discovered: Any):
        """
        Collect raw evidence from source system.
        """
        pass

    def normalize(self, evidence: Any):
        """Convert raw evidence into standard format."""

        return self.normalizer.normalize(evidence)

    def save(self, evidence: Any) -> str:
        """Persist evidence artifact."""

        return self.evidence_writer.write(
            collector=self.manifest.name,
            run_id=self.run_id,
            evidence=evidence,
        )

    def metadata(self) -> Dict[str, Any]:
        """Return collector execution metadata."""

        return {
            "collector": self.manifest.name,
            "version": self.manifest.version,
            "provider": self.manifest.provider,
            "run_id": self.run_id,
            "started_at": (
                self.started_at.isoformat()
                if self.started_at
                else None
            ),
            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at
                else None
            ),
        }
