"""
Base Authentication Provider.

Defines the authentication interface used by collectors.

Vendor-specific implementations should inherit from BaseAuthenticator.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import logging

from .exceptions import AuthenticationError

logger = logging.getLogger(__name__)


class BaseAuthenticator(ABC):
    """Abstract authentication provider."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._token: Optional[str] = None
        self._expires_at: Optional[datetime] = None

    def authenticate(self) -> str:
        """Authenticate and return access token."""
        try:
            token = self.acquire_token()

            if not token:
                raise AuthenticationError(
                    "Authentication returned empty token"
                )

            self._token = token
            self._expires_at = self.token_expiry()

            logger.info("Authentication successful")

            return token

        except Exception as exc:
            logger.exception("Authentication failed")
            raise AuthenticationError(
                "Unable to authenticate"
            ) from exc

    @abstractmethod
    def acquire_token(self) -> str:
        """
        Acquire authentication token.

        Implemented by provider-specific authenticators.
        """
        pass

    def get_token(self) -> str:
        """Return cached token or refresh when expired."""
        if not self._token or self.is_expired():
            return self.authenticate()

        return self._token

    def is_expired(self) -> bool:
        """Check whether token has expired."""
        if not self._expires_at:
            return True

        return datetime.now(timezone.utc) >= self._expires_at

    def token_expiry(self) -> Optional[datetime]:
        """
        Return token expiry timestamp.

        Override when provider supplies expiry information.
        """
        return None

    def validate(self) -> bool:
        """Validate authentication availability."""
        try:
            self.get_token()
            return True
        except Exception:
            return False

    def metadata(self) -> Dict[str, Any]:
        """Return authentication metadata for evidence runs."""
        return {
            "authenticated": self._token is not None,
            "expires_at": (
                self._expires_at.isoformat()
                if self._expires_at
                else None
            ),
        }
