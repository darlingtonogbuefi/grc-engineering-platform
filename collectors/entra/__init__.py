"""
Microsoft Entra evidence collector.

Provides authentication, API client,
and collector implementations for
Microsoft Entra ID (Microsoft Graph).
"""

from .auth import EntraAuthenticator
from .client import EntraClient
from .collector import EntraCollector

__all__ = [
    "EntraAuthenticator",
    "EntraClient",
    "EntraCollector",
]
