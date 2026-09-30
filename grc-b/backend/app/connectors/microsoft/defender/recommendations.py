# grc-b\backend\app\connectors\microsoft\defender\recommendations.py

"""
Microsoft Defender for Cloud recommendation collector.

Collects recommendation records from Azure Resource Graph.

The collector preserves the raw Microsoft response. Interpretation
and evidence planning are handled by later stages of the platform.
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


class DefenderRecommendationCollector:
    """Collect Microsoft Defender for Cloud recommendations."""

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
        Collect Defender for Cloud recommendation records.

        Returns the complete Azure Resource Graph response.
        """

        token = self.authenticator.get_token_for_scope(
            RESOURCE_GRAPH_SCOPE,
        )

        query = """
        SecurityResources
        | where type =~ 'microsoft.security/assessments'
        | extend
            assessmentName = tostring(name),
            displayName = tostring(properties.displayName),
            description = tostring(properties.description),
            status = properties.status,
            resourceDetails = properties.resourceDetails,
            metadata = properties.metadata
        | project
            id,
            name,
            type,
            subscriptionId,
            resourceGroup,
            tenantId,
            location,
            assessmentName,
            displayName,
            description,
            status,
            resourceDetails,
            metadata,
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
            "Collecting Defender for Cloud recommendations",
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
                "Defender for Cloud recommendation request failed",
            )

            raise RuntimeError(
                "Failed to collect Defender for Cloud recommendations",
            ) from exc

        data = response.json()

        logger.info(
            "Collected %s Defender for Cloud recommendation records",
            len(
                data.get(
                    "data",
                    [],
                ),
            ),
        )

        return data