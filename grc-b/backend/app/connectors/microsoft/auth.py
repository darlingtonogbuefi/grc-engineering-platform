# grc-b\backend\app\connectors\microsoft\auth.py

"""
Microsoft Authentication Provider.

Provides authentication for Microsoft and Azure APIs used by
Defender for Cloud, Microsoft Purview, Microsoft Graph, and
Azure Resource Manager evidence collectors.
"""

from __future__ import annotations
from typing import Any
from azure.identity import ClientSecretCredential
from collectors.azure.auth import AzureAuthenticator


class MicrosoftAuthenticator(AzureAuthenticator):
    """
    Microsoft authentication provider.

    Extends the existing AzureAuthenticator so all Microsoft
    collectors use the same authentication and token lifecycle.
    """

    def __init__(
        self,
        config: dict[str, Any],
    ):
        super().__init__(
            config,
        )

    def get_token_for_scope(
        self,
        scope: str,
    ) -> str:
        """
        Acquire an access token for a specific Microsoft API scope.

        Examples:

            Azure Resource Manager:
            https://management.azure.com/.default

            Microsoft Graph:
            https://graph.microsoft.com/.default
        """

        credential = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        access_token = credential.get_token(
            scope,
        )

        return access_token.token

    def metadata(self) -> dict[str, Any]:
        """
        Return Microsoft authentication metadata.
        """

        data = super().metadata()

        data.update(
            {
                "provider": "microsoft",
            }
        )

        return data