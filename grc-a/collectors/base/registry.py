"""
Collector Registry.

Maintains available evidence collectors.
"""

from __future__ import annotations

from typing import Dict, Type

import logging

from .collector import BaseCollector
from .exceptions import CollectorError


logger = logging.getLogger(__name__)


class CollectorRegistry:
    """Registry for collector implementations."""

    def __init__(self):
        self._collectors: Dict[str, Type[BaseCollector]] = {}

    def register(
        self,
        name: str,
        collector: Type[BaseCollector],
    ) -> None:
        """
        Register a collector class.
        """

        if not issubclass(
            collector,
            BaseCollector,
        ):
            raise CollectorError(
                f"{name} is not a valid collector"
            )

        if name in self._collectors:
            raise CollectorError(
                f"Collector already registered: {name}"
            )

        self._collectors[name] = collector

        logger.info(
            "Collector registered",
            extra={
                "collector": name,
            },
        )

    def get(
        self,
        name: str,
    ) -> Type[BaseCollector]:
        """
        Retrieve collector by name.
        """

        if name not in self._collectors:
            raise CollectorError(
                f"Collector not found: {name}"
            )

        return self._collectors[name]

    def exists(
        self,
        name: str,
    ) -> bool:
        """
        Check collector availability.
        """

        return name in self._collectors

    def list(
        self,
    ) -> Dict[str, Type[BaseCollector]]:
        """
        Return registered collectors.
        """

        return self._collectors.copy()

    def remove(
        self,
        name: str,
    ) -> None:
        """
        Remove collector registration.
        """

        if name in self._collectors:
            del self._collectors[name]
