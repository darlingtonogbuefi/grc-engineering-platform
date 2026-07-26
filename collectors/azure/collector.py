"""
Azure Evidence Collector.

Collects Azure platform evidence based on
configured collection profiles.
"""

from __future__ import annotations

from typing import Any, Dict, List

import logging

from collectors.base import BaseCollector
from collectors.base.models import EvidenceRecord

from .client import AzureClient
from .auth import AzureAuthenticator


logger = logging.getLogger(__name__)


class AzureCollector(BaseCollector):
    """Azure evidence collector."""

    def __init__(
        self,
        manifest,
        client: AzureClient,
        evidence_writer,
        normalizer,
        validator,
        config: Dict[str, Any] | None = None,
    ):
        super().__init__(
            manifest=manifest,
            client=client,
            evidence_writer=evidence_writer,
            normalizer=normalizer,
            validator=validator,
            config=config,
        )

        self.profile = (
            self.config.get(
                "profile",
                "default",
            )
        )

    def discover(self) -> List[str]:
        """
        Load enabled Azure queries
        from collection profile.
        """

        return self.client.load_profile(
            self.profile
        )

    def collect(
        self,
        discovered: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Execute Azure evidence queries.
        """

        evidence = []

        for query in discovered:

            logger.info(
                "Collecting Azure evidence",
                extra={
                    "query": query,
                    "run_id": self.run_id,
                },
            )

            result = self.client.execute_query(
                query
            )

            evidence.extend(
                result
            )

        return evidence

    def normalize(
        self,
        evidence: List[Dict[str, Any]],
    ) -> List[EvidenceRecord]:
        """
        Convert Azure responses into
        standard evidence records.
        """

        return self.normalizer.normalize(
            evidence
        )
