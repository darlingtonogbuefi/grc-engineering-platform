#  collectors\azure\__init__.py

"""
Azure evidence collector.

Provides authentication, API client,
and collector implementations for
Microsoft Azure (Azure Resource Manager).
"""

from .auth import AzureAuthenticator
from .client import AzureClient
from .collector import AzureCollector

__version__ = "1.0.0"

__all__ = [
    "AzureAuthenticator",
    "AzureClient",
    "AzureCollector",
]
