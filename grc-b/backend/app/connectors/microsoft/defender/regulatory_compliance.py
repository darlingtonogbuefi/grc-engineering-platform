#grc-b\backend\app\connectors\microsoft\purview\compliance_manager.py

"""
Microsoft Defender for Cloud regulatory compliance collector.

Collects regulatory compliance standards, controls, and assessment
state from Azure Resource Graph.

The collector preserves the raw Microsoft response. Interpretation,
evidence planning, and control/evidence relationships are handled
by later stages of the compliance evidence pipeline.
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


class DefenderRegulatoryComplianceCollector:
    """Collect Microsoft Defender regulatory compliance data."""

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
        Collect regulatory compliance assessment records.

        The query returns the relationship between:

            compliance standard
                ↓
            compliance control
                ↓
            compliance assessment
                ↓
            assessment state/resource counts

        The complete Resource Graph response is returned unchanged.
        """

        token = self.authenticator.get_token_for_scope(
            RESOURCE_GRAPH_SCOPE,
        )

        query = """
        SecurityResources
        | where type =~
            'microsoft.security/regulatorycompliancestandards/'
            'regulatorycompliancecontrols/regulatorycomplianceassessments'
        | extend
            assessmentName = tostring(properties.description),
            complianceStandard = extract(
                @'/regulatoryComplianceStandards/(.+)/regulatoryComplianceControls',
                1,
                id
            ),
            complianceControl = extract(
                @'/regulatoryComplianceControls/(.+)/regulatoryComplianceAssessments',
                1,
                id
            ),
            skippedResources = properties.skippedResources,
            passedResources = properties.passedResources,
            failedResources = properties.failedResources,
            state = tostring(properties.state)
        | project
            tenantId,
            subscriptionId,
            id,
            name,
            type,
            resourceGroup,
            location,
            complianceStandard,
            complianceControl,
            assessmentName,
            state,
            skippedResources,
            passedResources,
            failedResources,
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
            "Collecting Defender regulatory compliance assessments",
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
                "Defender regulatory compliance request failed",
            )

            raise RuntimeError(
                "Failed to collect Defender regulatory compliance data",
            ) from exc

        data = response.json()

        logger.info(
            "Collected %s Defender regulatory compliance records",
            len(
                data.get(
                    "data",
                    [],
                ),
            ),
        )

        return data