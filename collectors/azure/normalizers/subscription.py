# collectors\azure\normalizers\subscription.py

"""
Azure Subscription Normalizer.

Converts Azure subscription API responses into the platform's
standard evidence format.

Does not perform:
- Compliance evaluation
- Subscription governance checks
- Framework mappings
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from collectors.base.normalizer import BaseNormalizer
from collectors.base.models import EvidenceRecord


class SubscriptionNormalizer(BaseNormalizer):
    """Normalize Azure subscription resources."""

    RESOURCE_TYPE = "azure.subscription"

    def __init__(self):
        super().__init__("azure")

    def normalize(
        self,
        data: dict[str, Any],
    ) -> list[EvidenceRecord]:
        """
        Normalize Azure subscription response.
        """

        records: list[EvidenceRecord] = []

        #
        # Generate one UTC timestamp for the entire
        # normalization run.
        #
        # This represents when the Azure Subscription
        # evidence batch was observed/normalized.
        #
        collection_timestamp = datetime.now(
            UTC,
        ).isoformat()

        for subscription in data.get(
            "value",
            [],
        ):
            if not isinstance(subscription, dict):
                continue

            subscription_id = subscription.get(
                "subscriptionId",
                "",
            )

            records.append(
                self.create_record(
                    resource_type=self.RESOURCE_TYPE,
                    resource_id=subscription_id,
                    data={
                        #
                        # Collection timestamp.
                        #
                        # This is the UTC timestamp for the
                        # live Azure Subscription evidence
                        # normalization run. Every record from
                        # this collection run receives the same
                        # timestamp.
                        #
                        "timestamp": collection_timestamp,
                        "name": subscription.get(
                            "displayName",
                            "",
                        ),
                        "provider": "azure",
                        "service": "subscriptions",
                        "subscription_id": subscription_id,
                        "state": subscription.get("state"),
                        "tenant_id": subscription.get("tenantId"),
                        "authorization_source": subscription.get("authorizationSource"),
                        "managed_by_tenants": subscription.get(
                            "managedByTenants",
                            [],
                        ),
                        "subscription_policies": subscription.get(
                            "subscriptionPolicies",
                            {},
                        ),
                        "tags": subscription.get(
                            "tags",
                            {},
                        ),
                        "raw": subscription,
                    },
                    metadata={
                        "collector": "azure",
                        "normalizer": "subscription",
                    },
                )
            )

        self.validate(records)

        return records
