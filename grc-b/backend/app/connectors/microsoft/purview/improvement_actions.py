# grc-b\backend\app\connectors\microsoft\purview\improvement_actions.py

"""
Microsoft Purview Compliance Manager improvement action collector.

Collects improvement action data associated with Microsoft Purview
Compliance Manager assessments.

Improvement actions are kept separate from assessments because they
represent the actionable requirements associated with a Compliance
Manager assessment/control.

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


class PurviewImprovementActionCollector:
    """
    Collect Microsoft Purview Compliance Manager improvement actions.

    The collector provides the authenticated Microsoft Graph client
    boundary while keeping Purview-specific API details isolated.

    Specific Improvement Action endpoints should only be added after
    confirming that the endpoint is supported by Microsoft for the
    tenant and API version being used.
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

        Purview-specific resource paths should only be supplied after
        confirming that the corresponding Microsoft API is supported.
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
                "Microsoft Graph improvement action request failed: %s",
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
        Entry point for Improvement Action collection.

        The actual Purview Improvement Action API/query is deliberately
        not hard-coded here until its supported Microsoft interface has
        been confirmed.
        """

        logger.info(
            "Purview Improvement Action collection requested",
        )

        return {
            "provider": "microsoft",
            "service": "purview",
            "component": "improvement_actions",
            "api_version": self.api_version,
            "status": "api_endpoint_pending",
            "data": [],
        }