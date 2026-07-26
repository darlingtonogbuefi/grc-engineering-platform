"""
Base Evidence Validator.

Defines validation rules for collected evidence.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List

import logging

from .exceptions import ValidationError
from .models import EvidenceRecord


logger = logging.getLogger(__name__)


class BaseValidator(ABC):
    """Abstract evidence validator."""

    def validate(
        self,
        evidence: Any,
    ) -> bool:
        """
        Validate collected evidence.
        """

        if evidence is None:
            raise ValidationError(
                "Evidence cannot be empty"
            )

        records = self.prepare(
            evidence
        )

        self.validate_records(
            records
        )

        self.validate_custom(
            records
        )

        return True

    def prepare(
        self,
        evidence: Any,
    ) -> List[Any]:
        """
        Prepare evidence for validation.
        """

        if isinstance(
            evidence,
            list,
        ):
            return evidence

        return [evidence]

    def validate_records(
        self,
        records: List[Any],
    ) -> None:
        """
        Validate standard evidence fields.
        """

        for record in records:

            if isinstance(
                record,
                EvidenceRecord,
            ):
                if not record.resource_id:
                    raise ValidationError(
                        "Missing resource id"
                    )

                if not record.resource_type:
                    raise ValidationError(
                        "Missing resource type"
                    )

            elif not isinstance(
                record,
                dict,
            ):
                raise ValidationError(
                    "Invalid evidence format"
                )

    def validate_custom(
        self,
        records: List[Any],
    ) -> None:
        """
        Override for collector-specific validation.
        """

        return None

    def metadata(
        self,
    ) -> Dict[str, str]:
        """
        Return validator metadata.
        """

        return {
            "validator": self.__class__.__name__,
        }
