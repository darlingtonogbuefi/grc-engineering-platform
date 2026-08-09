# collectors\azure\validator.py

"""
Azure evidence validator.

Provides validation rules for Azure
evidence collected from Azure Resource Manager.
"""

from __future__ import annotations

from typing import Any, Dict, List

from collectors.base.validator import BaseValidator
from collectors.base.exceptions import ValidationError


class AzureValidator(BaseValidator):
    """Azure evidence validator."""

    def validate(
        self,
        evidence: Dict[str, Any] | None,
    ) -> bool:
        """
        Validate Azure evidence.

        Supports:

        1. Single normalized evidence record

        {
            "collector": "azure",
            "provider": "azure",
            "resource_id": "...",
            "data": {}
        }

        2. Collector evidence envelope

        {
            "collector": "azure",
            "run_id": "...",
            "evidence": [
                {
                    "source": "azure",
                    "resource_id": "...",
                    "data": {}
                }
            ]
        }
        """

        try:
            if evidence is None:
                return False

            if not isinstance(
                evidence,
                dict,
            ):
                return False

            #
            # Pipeline evidence envelope validation
            #
            if "evidence" in evidence:

                records = evidence.get(
                    "evidence",
                )

                if not isinstance(
                    records,
                    list,
                ):
                    return False

                if not records:
                    return False

                for record in records:

                    if not isinstance(
                        record,
                        dict,
                    ):
                        return False

                    required_fields = [
                        "source",
                        "resource_type",
                        "resource_id",
                        "data",
                    ]

                    for field in required_fields:

                        if field not in record:
                            return False

                    if (
                        record.get(
                            "source",
                        )
                        != "azure"
                    ):
                        return False

                    if not record.get(
                        "resource_id",
                    ):
                        return False

                    if not isinstance(
                        record.get("data"),
                        dict,
                    ):
                        return False

                return True

            #
            # Existing single evidence record validation
            #
            required_fields = [
                "collector",
                "provider",
                "resource_id",
                "data",
            ]

            for field in required_fields:

                if field not in evidence:
                    return False

            if (
                evidence.get(
                    "provider",
                )
                != "azure"
            ):
                return False

            if not evidence.get(
                "resource_id",
            ):
                return False

            if not isinstance(
                evidence.get("data"),
                dict,
            ):
                return False

            self.validate_custom(
                [
                    evidence,
                ]
            )

            return True

        except ValidationError:
            return False

        except Exception:
            return False

    def validate_custom(
        self,
        records: List[Any],
    ) -> None:
        """
        Perform Azure-specific validation.

        Ensures Azure evidence records contain
        supported data structures.
        """

        for record in records:

            if record is None:
                raise ValidationError("Collected evidence cannot be None.")

            if not isinstance(
                record,
                dict,
            ):
                raise ValidationError("Collected evidence must be a dictionary.")

            for resource, value in record.items():

                if value is None:
                    raise ValidationError(f"Resource '{resource}' returned no data.")

                if resource in (
                    "collector",
                    "provider",
                    "resource_id",
                    "run_id",
                ):

                    if not isinstance(
                        value,
                        str,
                    ):
                        raise ValidationError(
                            f"Resource '{resource}' must be a string."
                        )

                elif resource == "data":

                    if not isinstance(
                        value,
                        dict,
                    ):
                        raise ValidationError("Evidence data must be a dictionary.")

                elif not isinstance(
                    value,
                    (list, dict),
                ):
                    raise ValidationError(
                        f"Resource '{resource}' returned an unsupported data type."
                    )
