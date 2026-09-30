# collectors\entra\auth.py

"""
Microsoft Entra Authentication Provider.

Implements Microsoft Graph authentication
for Entra evidence collectors.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional

import logging

from collectors.base.auth import BaseAuthenticator
from collectors.base.exceptions import AuthenticationError


logger = logging.getLogger(__name__)


class EntraAuthenticator(BaseAuthenticator):
    """Microsoft Entra authentication provider."""

    def __init__(
        self,
        config: Dict[str, Any],
    ):
        super().__init__(config)

        self.tenant_id = config.get(
            "tenant_id"
        )

        self.client_id = config.get(
            "client_id"
        )

        self.client_secret = config.get(
            "client_secret"
        )

        self.scope = config.get(
            "scope",
            "https://graph.microsoft.com/.default",
        )

        self._token: Optional[str] = None

        self._token_expiry: Optional[datetime] = None

    def acquire_token(self) -> str:
        """
        Acquire Microsoft Graph access token.
        """

        try:
            self._token = self._get_token()

            self._token_expiry = (
                datetime.now(timezone.utc)
                + timedelta(hours=1)
            )

            return self._token

        except Exception as exc:
            logger.exception(
                "Entra authentication failed"
            )

            raise AuthenticationError(
                "Microsoft Graph token acquisition failed"
            ) from exc

    def get_token(self) -> str:
        """
        Return current token.

        Required by BaseClient.
        """

        if not self._token:
            return self.acquire_token()

        return self._token

    @property
    def token(self) -> Optional[str]:
        """
        Return current access token.
        """

        return self._token

    def _get_token(self) -> str:
        """
        Acquire Microsoft Graph access token.

        Uses Azure client secret authentication.
        """

        from azure.identity import ClientSecretCredential

        if not self.tenant_id:
            raise AuthenticationError(
                "Missing tenant_id configuration"
            )

        if not self.client_id:
            raise AuthenticationError(
                "Missing client_id configuration"
            )

        if not self.client_secret:
            raise AuthenticationError(
                "Missing client_secret configuration"
            )

        credential = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        token = credential.get_token(
            self.scope
        )

        return token.token

    def token_expiry(self) -> Optional[datetime]:
        """
        Return token expiry.
        """

        return self._token_expiry

    def metadata(self) -> Dict[str, Any]:
        """
        Return authentication metadata.
        """

        data = super().metadata()

        data.update(
            {
                "provider": "entra",
                "tenant_id": self.tenant_id,
                "scope": self.scope,
            }
        )

        return data
