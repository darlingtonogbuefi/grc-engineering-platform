"""
Azure evidence normalizers.

Normalizers transform Azure-specific API responses into the
platform's standard EvidenceRecord model.

Responsibilities:
- Validate Azure API responses
- Transform Azure resources
- Produce normalized evidence

Not responsible for:
- Compliance evaluation
- Framework mappings
- Risk scoring
- Report generation
"""

from .subscription import SubscriptionNormalizer
from .resource import ResourceNormalizer
from .iam import IAMNormalizer
from .policy import PolicyNormalizer
from .network import NetworkNormalizer
from .logging import LoggingNormalizer
from .storage import StorageNormalizer
from .compute import ComputeNormalizer
from .security import SecurityNormalizer

__all__ = [
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
