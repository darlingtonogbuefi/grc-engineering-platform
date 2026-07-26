"""
Base Evidence Normalizer.

Defines the interface for converting
vendor-specific data into standard evidence objects.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List

import logging

from .models import EvidenceRecord
from .exceptions import ValidationError


logger = logging.getLogger(__name__)


class BaseNormalizer(ABC):
    """Abstract evidence normalization provider."""

    def __init__(
        self,
        source: str,
    ):
        self.source = source

    @abstractmethod
    def normalize(
        self,
        data: Any,
    ) -> List[EvidenceRecord]:
        """
        Convert raw source data into evidence records.
        """
        pass

    def create_record(
        self,
        resource_type: str,
        resource_id: str,
        data: Dict[str, Any],
        metadata: Dict[str, Any] | None = None,
    ) -> EvidenceRecord:
        """
        Create standard evidence record.
        """

        return EvidenceRecord(
            source=self.source,
            resource_type=resource_type,
            resource_id=resource_id,
            data=data,
            collected_at=datetime.now(
                timezone.utc
            ),
            metadata=metadata or {},
        )

    def validate(
        self,
        records: List[EvidenceRecord],
    ) -> bool:
        """
        Validate normalized evidence.
        """

        for record in records:
            if not record.resource_id:
                raise ValidationError(
                    "Evidence record missing resource id"
                )

            if not record.resource_type:
                raise ValidationError(
                    "Evidence record missing resource type"
                )

        return True

    def metadata(self) -> Dict[str, Any]:
        """
        Return normalizer metadata.
        """

        return {
            "normalizer": self.__class__.__name__,
            "source": self.source,
        }
