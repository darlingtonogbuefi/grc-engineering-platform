"""
Collector Loader.

Dynamically loads collector implementations
and collector manifests.
"""

from __future__ import annotations

import importlib
import logging
from pathlib import Path
from typing import Type

import yaml

from .collector import BaseCollector
from .exceptions import CollectorError, ManifestError
from .manifest import CollectorManifest

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
            module_path = f"{self.package}.{name}.collector"

            module = importlib.import_module(module_path)

            collector = self._find_collector(module)

            return collector

        except Exception as exc:
            logger.exception(
                "Collector loading failed",
                extra={"collector": name},
            )

            raise CollectorError(f"Unable to load collector: {name}") from exc

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

        raise CollectorError("No collector implementation found")


def load_collector_manifest(
    manifest_path: str | Path,
) -> CollectorManifest:
    """
    Load a collector manifest from a YAML file.

    Args:
        manifest_path:
            Path to a collector manifest.yml file.

    Returns:
        CollectorManifest instance.
    """

    manifest_path = Path(manifest_path)

    if not manifest_path.is_absolute():
        project_root = Path(__file__).resolve().parents[2]
        manifest_path = project_root / manifest_path

    if not manifest_path.exists():
        raise ManifestError(f"Collector manifest not found: {manifest_path}")

    try:
        with manifest_path.open(
            "r",
            encoding="utf-8",
        ) as stream:
            data = yaml.safe_load(stream) or {}

        return CollectorManifest.from_dict(data)

    except Exception as exc:
        logger.exception(
            "Failed to load collector manifest",
            extra={"manifest": str(manifest_path)},
        )

        raise ManifestError(f"Unable to load manifest: {manifest_path}") from exc
