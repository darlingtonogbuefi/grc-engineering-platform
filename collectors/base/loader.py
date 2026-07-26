"""
Collector Loader.

Dynamically loads collector implementations.
"""

from __future__ import annotations

import importlib
import logging
from typing import Type

from .collector import BaseCollector
from .exceptions import CollectorError

logger = logging.getLogger(__name__)


class CollectorLoader:
    """Loads collector implementations dynamically."""

    def __init__(self, package: str = "collectors"):
        self.package = package

    def load(
        self,
        name: str,
    ) -> Type[BaseCollector]:
        """
        Load collector class by name.

        Example:
            entra
            azure
            github
        """

        try:
            module_path = (
                f"{self.package}.{name}.collector"
            )

            module = importlib.import_module(
                module_path
            )

            collector = self._find_collector(
                module
            )

            return collector

        except Exception as exc:
            logger.exception(
                "Collector loading failed",
                extra={"collector": name},
            )

            raise CollectorError(
                f"Unable to load collector: {name}"
            ) from exc

    def _find_collector(
        self,
        module,
    ) -> Type[BaseCollector]:
        """
        Find BaseCollector implementation.
        """

        for item in module.__dict__.values():

            if (
                isinstance(item, type)
                and issubclass(item, BaseCollector)
                and item is not BaseCollector
            ):
                return item

        raise CollectorError(
            "No collector implementation found"
        )
