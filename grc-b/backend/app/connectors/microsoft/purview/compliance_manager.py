#grc-b\backend\app\connectors\microsoft\purview\compliance_manager.py


"""
Microsoft Purview Compliance Manager collector.

Provides the integration boundary for Microsoft Purview Compliance
Manager data.

Compliance Manager contains assessments, controls, regulations, and
improvement actions. Unlike Defender for Cloud, its data model is
not exposed through the same Azure Resource Graph SecurityResources
interface.

This collector therefore keeps the Purview API interaction isolated
from the rest of the evidence platform.

Raw Microsoft responses should be preserved by the ingestion layer.
"""

from __future__ import annotations

import logging
from typing import Any

import requests

from collectors.base.exceptions import AuthenticationError
from collectors.microsoft.auth import MicrosoftAuthenticator

logger = logging.getLogger(__name__)


MICROSOFT_GRAPH_SCOPE = "https://graph.microsoft.com/.default"

MICROSOFT_GRAPH_ENDPOINT = "https://graph.microsoft.com"

GRAPH_API_VERSION = "v1.0"


class PurviewComplianceManagerCollector:
    """
    Collect Microsoft Purview Compliance Manager data.

    The collector currently provides the authenticated HTTP client
    boundary. Specific Compliance Manager endpoints should only be
    added once they are confirmed to be supported for the tenant/API
    version being used.
    """

    def __init__(
        self,
        config: dict[str, Any],
    ) -> None:
        if not config:
            raise AuthenticationError(
                "Purview authentication configuration is required",
            )

        self.config = config

        self.authenticator = MicrosoftAuthenticator(
            config,
        )

        self.timeout = int(
            config.get(
                "timeout",
                60,
            ),
        )

        self.api_version = config.get(
            "graph_api_version",
            GRAPH_API_VERSION,
        )

    def _get_headers(self) -> dict[str, str]:
        """
        Build authenticated Microsoft Graph request headers.
        """

        token = self.authenticator.get_token_for_scope(
            MICROSOFT_GRAPH_SCOPE,
        )

        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

    def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute an authenticated Microsoft Graph GET request.

        This method is intentionally generic. Purview-specific
        resource paths should be added only after the corresponding
        Microsoft API has been confirmed.
        """

        normalized_path = path.lstrip(
            "/",
        )

        url = (
            f"{MICROSOFT_GRAPH_ENDPOINT}/"
            f"{self.api_version}/"
            f"{normalized_path}"
        )

        logger.info(
            "Requesting Microsoft Graph resource: %s",
            path,
        )

        response = requests.get(
            url,
            headers=self._get_headers(),
            params=params,
            timeout=self.timeout,
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            logger.exception(
                "Microsoft Graph request failed: %s",
                path,
            )

            raise RuntimeError(
                f"Microsoft Graph request failed: {path}",
            ) from exc

        return response.json()

    def collect(
        self,
    ) -> dict[str, Any]:
        """
        Entry point for Compliance Manager collection.

        Compliance Manager-specific API discovery is kept separate
        from the generic Microsoft Graph client so unsupported or
        preview APIs are not accidentally treated as stable APIs.
        """

        logger.info(
            "Purview Compliance Manager collection requested",
        )

        return {
            "provider": "microsoft",
            "service": "purview",
            "component": "compliance_manager",
            "api_version": self.api_version,
            "status": "api_endpoint_pending",
            "data": [],
        }