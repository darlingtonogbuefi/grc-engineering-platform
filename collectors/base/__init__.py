"""
Base classes and interfaces for all evidence collectors.

Every collector (Entra, Azure, Intune, GitHub, VMware, etc.)
inherits from the classes exported by this package.

Example:
    from collectors.base import BaseCollector

    class EntraCollector(BaseCollector):
        ...
"""

from .collector import BaseCollector
from .auth import BaseAuthenticator
from .client import BaseClient
from .evidence import BaseEvidenceWriter
from .normalizer import BaseNormalizer
from .validator import BaseValidator
from .manifest import CollectorManifest
from .registry import CollectorRegistry

__version__ = "1.0.0"

__all__ = [
    "BaseCollector",
    "BaseAuthenticator",
    "BaseClient",
    "BaseEvidenceWriter",
    "BaseNormalizer",
    "BaseValidator",
    "CollectorManifest",
    "CollectorRegistry",
]
