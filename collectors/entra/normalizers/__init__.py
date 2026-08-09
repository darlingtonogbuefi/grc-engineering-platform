# collectors\entra\normalizers\__init__.py


"""
Microsoft Entra evidence normalizer.

Coordinates normalization of Microsoft Graph
resources into a standard evidence format.
"""

from __future__ import annotations

from typing import Any, Dict, List

from collectors.base.normalizer import BaseNormalizer
from collectors.base.models import EvidenceRecord

from .applications import normalize_applications
from .devices import normalize_devices
from .groups import normalize_groups
from .logs import (
    normalize_audit_logs,
    normalize_sign_ins,
)
from .policies import normalize_conditional_access
from .roles import normalize_directory_roles
from .users import normalize_users


class EntraNormalizer(BaseNormalizer):
    """Microsoft Entra evidence normalizer."""

    def __init__(self):
        super().__init__("entra")

    def normalize(
        self,
        data: Dict[str, Any],
    ) -> List[EvidenceRecord]:
        """
        Normalize Microsoft Entra evidence into
        standard EvidenceRecord objects.
        """

        records: List[EvidenceRecord] = []

        normalizers = {
            "users": normalize_users,
            "groups": normalize_groups,
            "applications": normalize_applications,
            "devices": normalize_devices,
            "directory_roles": normalize_directory_roles,
            "conditional_access": normalize_conditional_access,
            "audit_logs": normalize_audit_logs,
            "sign_ins": normalize_sign_ins,
        }

        for resource, items in data.items():

            normalizer = normalizers.get(resource)

            if normalizer is None:
                continue

            if items is None:
                continue

            normalized = normalizer(items)

            if not normalized:
                continue

            #
            # Convert provider-specific normalized
            # dictionaries into standard EvidenceRecord
            # objects required by BaseNormalizer.
            #
            for item in normalized:

                resource_id = item.get("id")

                if not resource_id:
                    continue

                record = self.create_record(
                    resource_type=resource,
                    resource_id=resource_id,
                    data=item,
                )

                records.append(record)

        self.validate(records)

        return records


__all__ = [
    "EntraNormalizer",
]
