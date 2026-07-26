"""
Azure Authentication Provider.

Implements Azure identity authentication
for Azure evidence collectors.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional

import logging

from collectors.base.auth import BaseAuthenticator
from collectors.base.exceptions import AuthenticationError


logger = logging.getLogger(__name__)


class AzureAuthenticator(BaseAuthenticator):
    """Azure authentication provider."""

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
            "https://management.azure.com/.default",
        )

        self._token_expiry: Optional[datetime] = None

    def acquire_token(self) -> str:
        """
        Acquire Azure access token.

        Uses Azure Identity implementation
        in production.
        """

        try:
            token = self._get_token()

            self._token_expiry = (
                datetime.now(timezone.utc)
                + timedelta(hours=1)
            )

            return token

        except Exception as exc:
            logger.exception(
                "Azure authentication failed"
            )

            raise AuthenticationError(
                "Azure token acquisition failed"
            ) from exc

    def _get_token(self) -> str:
        """
        Azure identity implementation.

        Replace with:
            azure.identity.ClientSecretCredential
            azure.identity.ManagedIdentityCredential
            azure.identity.CertificateCredential
        """

        raise NotImplementedError(
            "Azure identity provider not configured"
        )

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
