# collectors\azure\auth.py


"""
Azure Authentication Provider.

Implements Azure identity authentication
for Azure evidence collectors.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from azure.identity import ClientSecretCredential

from collectors.base.auth import BaseAuthenticator
from collectors.base.exceptions import AuthenticationError

logger = logging.getLogger(__name__)


class AzureAuthenticator(BaseAuthenticator):
    """Azure authentication provider."""

    def __init__(
        self,
        config: Dict[str, Any],
    ):
        if not config:
            raise AuthenticationError("Azure authentication configuration is required")

        super().__init__(
            config,
        )

        tenant_id = config.get(
            "tenant_id",
        )

        client_id = config.get(
            "client_id",
        )

        client_secret = config.get(
            "client_secret",
        )

        if not isinstance(tenant_id, str):
            raise AuthenticationError(
                "Missing tenant_id configuration",
            )

        if not isinstance(client_id, str):
            raise AuthenticationError(
                "Missing client_id configuration",
            )

        if not isinstance(client_secret, str):
            raise AuthenticationError(
                "Missing client_secret configuration",
            )

        self.tenant_id = tenant_id

        self.client_id = client_id

        self.client_secret = client_secret

        self.scope = config.get(
            "scope",
            "https://management.azure.com/.default",
        )

        self._token: Optional[str] = None

        self._token_expiry: Optional[datetime] = None

    def acquire_token(self) -> str:
        """
        Acquire Azure Resource Manager access token.
        """

        try:
            credential = ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret,
            )

            access_token = credential.get_token(
                self.scope,
            )

            self._token = access_token.token

            self._token_expiry = datetime.fromtimestamp(
                access_token.expires_on,
                tz=timezone.utc,
            )

            return self._token

        except Exception as exc:
            logger.exception(
                "Azure authentication failed",
            )

            raise AuthenticationError(
                "Azure token acquisition failed",
            ) from exc

    def get_token(self) -> str:
        """
        Return current token.

        Required by BaseClient.
        """

        if not self._token:
            return self.acquire_token()

        if self._token_expiry and datetime.now(timezone.utc) >= self._token_expiry:
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
        Acquire Azure Resource Manager access token.

        Uses Azure client secret authentication.
        """

        if not self.tenant_id:
            raise AuthenticationError(
                "Missing tenant_id configuration",
            )

        if not self.client_id:
            raise AuthenticationError(
                "Missing client_id configuration",
            )

        if not self.client_secret:
            raise AuthenticationError(
                "Missing client_secret configuration",
            )

        credential = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        token = credential.get_token(
            self.scope,
        )

        return token.token

    def token_expiry(self) -> Optional[datetime]:
        """
        Return Azure token expiry.
        """

        return self._token_expiry

    def metadata(self) -> Dict[str, Any]:
        """
        Return authentication metadata.
        """

        data = super().metadata()

        data.update(
            {
                "provider": "azure",
                "tenant_id": self.tenant_id,
                "scope": self.scope,
            }
        )

        return data
