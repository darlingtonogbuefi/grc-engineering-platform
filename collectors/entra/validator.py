"""
Microsoft Entra evidence validator.

Provides validation rules for Microsoft Entra
evidence collected from Microsoft Graph.
"""

from __future__ import annotations

from typing import Any, List

from collectors.base.validator import BaseValidator
from collectors.base.exceptions import ValidationError


class EntraValidator(BaseValidator):
    """Microsoft Entra evidence validator."""

    def validate_custom(
        self,
        records: List[Any],
    ) -> None:
        """
        Perform Microsoft Entra-specific validation.

        This extends the default validation provided
        by BaseValidator. Currently it ensures that
        evidence is present and each collected resource
        contains data in an expected format.
        """

        for record in records:

            if record is None:
                raise ValidationError(
                    "Collected evidence cannot be None."
                )

            if isinstance(record, dict):

                for resource, value in record.items():

                    if value is None:
                        raise ValidationError(
                            f"Resource '{resource}' returned no data."
                        )

                    if not isinstance(
                        value,
                        (list, dict),
                    ):
                        raise ValidationError(
                            f"Resource '{resource}' returned an unsupported data type."
                        )

            elif not isinstance(
                record,
                (list, dict),
            ):
                raise ValidationError(
                    "Collected evidence must be a list or dictionary."
                )
