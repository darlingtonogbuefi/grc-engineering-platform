# collectors\azure\normalizers\__init__.py

"""
Azure evidence normalizer.

Coordinates normalization of Azure Resource Manager
resources into a standard evidence format.
"""

from __future__ import annotations

from typing import Any, Dict, List

from collectors.base.normalizer import BaseNormalizer
from collectors.base.models import EvidenceRecord

from .subscription import SubscriptionNormalizer
from .resource import ResourceNormalizer
from .iam import IAMNormalizer
from .policy import PolicyNormalizer
from .network import NetworkNormalizer
from .logging import LoggingNormalizer
from .storage import StorageNormalizer
from .compute import ComputeNormalizer
from .security import SecurityNormalizer


class AzureNormalizer(BaseNormalizer):
    """Azure evidence normalizer."""

    def __init__(self):
        super().__init__("azure")

        self.normalizers = {
            "subscriptions": SubscriptionNormalizer(),
            "resources": ResourceNormalizer(),
            "role_assignments": IAMNormalizer(),
            "role_definitions": IAMNormalizer(),
            "policy_assignments": PolicyNormalizer(),
            "security_settings": SecurityNormalizer(),
            "policy_definitions": PolicyNormalizer(),
            "virtual_networks": NetworkNormalizer(),
            "network_security_groups": NetworkNormalizer(),
            "firewalls": NetworkNormalizer(),
            "activity_logs": LoggingNormalizer(),
            "diagnostic_settings": LoggingNormalizer(),
            "storage_accounts": StorageNormalizer(),
            "virtual_machines": ComputeNormalizer(),
            "backup_vaults": SecurityNormalizer(),
            "defender_settings": SecurityNormalizer(),
            "key_vaults": SecurityNormalizer(),
            "sql_databases": ResourceNormalizer(),
            "resource_groups": ResourceNormalizer(),
        }

    def normalize(
        self,
        data: Dict[str, Any],
    ) -> List[EvidenceRecord]:
        """
        Normalize Azure evidence into standard
        EvidenceRecord objects.
        """

        records: List[EvidenceRecord] = []

        for resource, items in data.items():

            normalizer = self.normalizers.get(resource)

            if normalizer is None:
                continue

            if items is None:
                continue

            normalized = normalizer.normalize(items)

            if not normalized:
                continue

            #
            # Child Azure normalizers already return
            # standard EvidenceRecord objects.
            #
            # Do not convert them again using
            # create_record(), because they are not
            # dictionaries.
            #
            records.extend(normalized)

        self.validate(records)

        return records


__all__ = [
    "AzureNormalizer",
    "SubscriptionNormalizer",
    "ResourceNormalizer",
    "IAMNormalizer",
    "PolicyNormalizer",
    "NetworkNormalizer",
    "LoggingNormalizer",
    "StorageNormalizer",
    "ComputeNormalizer",
    "SecurityNormalizer",
]
