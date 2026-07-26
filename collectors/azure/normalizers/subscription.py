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

from datetime import datetime, timezone
from typing import Any

from collectors.base.normalizer import BaseNormalizer
from collectors.base.models import EvidenceRecord


class SubscriptionNormalizer(BaseNormalizer):
    """Normalize Azure subscription resources."""

    RESOURCE_TYPE = "azure.subscription"

    def normalize(
        self,
        data: dict[str, Any],
    ) -> list[EvidenceRecord]:
        """
        Normalize Azure subscription response.
        """

        records: list[EvidenceRecord] = []

        collected_at = datetime.now(
            timezone.utc
        )

        for subscription in data.get(
            "value",
            [],
        ):
            subscription_id = subscription.get(
                "subscriptionId",
                "",
            )

            records.append(
                EvidenceRecord(
                    source="azure",
                    resource_type=self.RESOURCE_TYPE,
                    resource_id=subscription_id,
                    data={
                        "name": subscription.get(
                            "displayName",
                            "",
                        ),
                        "provider": "azure",
                        "service": "subscriptions",
                        "subscription_id": subscription_id,
                        "state": subscription.get(
                            "state"
                        ),
                        "tenant_id": subscription.get(
                            "tenantId"
                        ),
                        "authorization_source": subscription.get(
                            "authorizationSource"
                        ),
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
                    collected_at=collected_at,
                    metadata={
                        "collector": "azure",
                        "normalizer": "subscription",
                    },
                )
            )

        return records
