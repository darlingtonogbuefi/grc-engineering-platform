"""
Azure Evidence Collector.

Provides Azure resource collection capabilities
for the GRC evidence engineering platform.
"""

from .collector import AzureCollector
from .auth import AzureAuthenticator
from .client import AzureClient

__version__ = "1.0.0"

__all__ = [
    "AzureCollector",
    "AzureAuthenticator",
    "AzureClient",
]
