# grc-b\backend\app\connectors\microsoft\defender\assessments.py

"""
Microsoft Defender for Cloud assessment collector.

Collects security assessment records from Azure Resource Graph.

The collector intentionally preserves the raw Microsoft response.
Interpretation, evidence planning, and framework/control mapping are
handled by later stages of the compliance evidence pipeline.
"""

from __future__ import annotations

import logging
from typing import Any

import requests

from collectors.base.exceptions import AuthenticationError
from collectors.microsoft.auth import MicrosoftAuthenticator

logger = logging.getLogger(__name__)


RESOURCE_GRAPH_SCOPE = "https://management.azure.com/.default"

RESOURCE_GRAPH_ENDPOINT = (
    "https://management.azure.com/providers/"
    "Microsoft.ResourceGraph/resources"
)

API_VERSION = "2022-10-01"


class DefenderAssessmentCollector:
    """Collect Microsoft Defender for Cloud assessments."""

    def __init__(
        self,
        config: dict[str, Any],
    ) -> None:
        if not config:
            raise AuthenticationError(
                "Defender authentication configuration is required",
            )

        self.config = config

        self.authenticator = MicrosoftAuthenticator(
            config,
        )

        self.subscription_ids = self._get_subscription_ids(
            config,
        )

        self.timeout = int(
            config.get(
                "timeout",
                60,
            ),
        )

    @staticmethod
    def _get_subscription_ids(
        config: dict[str, Any],
    ) -> list[str]:
        """
        Get subscription IDs from configuration.

        The Resource Graph query requires the subscriptions that
        should be searched.
        """

        subscription_ids = config.get(
            "subscription_ids",
            [],
        )

        if isinstance(subscription_ids, str):
            subscription_ids = [
                subscription_ids,
            ]

        if not isinstance(subscription_ids, list):
            raise ValueError(
                "subscription_ids must be a list of strings",
            )

        if not all(
            isinstance(subscription_id, str)
            for subscription_id in subscription_ids
        ):
            raise ValueError(
                "subscription_ids must contain only strings",
            )

        if not subscription_ids:
            raise ValueError(
                "At least one subscription_id is required",
            )

        return subscription_ids

    def collect(
        self,
    ) -> dict[str, Any]:
        """
        Collect Defender for Cloud assessment records.

        Returns the complete Resource Graph response so that the
        ingestion layer can preserve the original Microsoft data.
        """

        token = self.authenticator.get_token_for_scope(
            RESOURCE_GRAPH_SCOPE,
        )

        query = """
        SecurityResources
        | where type =~ 'microsoft.security/assessments'
        | project
            id,
            name,
            type,
            subscriptionId,
            resourceGroup,
            tenantId,
            location,
            properties
        """

        payload = {
            "subscriptions": self.subscription_ids,
            "query": query,
            "options": {
                "resultFormat": "objectArray",
            },
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        logger.info(
            "Collecting Defender for Cloud assessments",
        )

        response = requests.post(
            RESOURCE_GRAPH_ENDPOINT,
            params={
                "api-version": API_VERSION,
            },
            headers=headers,
            json=payload,
            timeout=self.timeout,
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            logger.exception(
                "Defender for Cloud assessment request failed",
            )

            raise RuntimeError(
                "Failed to collect Defender for Cloud assessments",
            ) from exc

        data = response.json()

        logger.info(
            "Collected %s Defender for Cloud assessment records",
            len(
                data.get(
                    "data",
                    [],
                ),
            ),
        )

        return data