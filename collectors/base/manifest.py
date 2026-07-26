"""
Collector Manifest.

Defines metadata and capabilities for evidence collectors.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from .exceptions import ManifestError


@dataclass
class CollectorManifest:
    """Collector metadata definition."""

    name: str
    version: str
    provider: str

    description: str = ""

    authentication: List[str] = field(
        default_factory=list
    )

    profiles: List[str] = field(
        default_factory=list
    )

    capabilities: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "CollectorManifest":
        """
        Create manifest from YAML/JSON data.
        """

        required = [
            "name",
            "version",
            "provider",
        ]

        missing = [
            item
            for item in required
            if item not in data
        ]

        if missing:
            raise ManifestError(
                f"Missing manifest fields: {missing}"
            )

        return cls(
            name=data["name"],
            version=data["version"],
            provider=data["provider"],
            description=data.get(
                "description",
                "",
            ),
            authentication=data.get(
                "authentication",
                [],
            ),
            profiles=data.get(
                "profiles",
                [],
            ),
            capabilities=data.get(
                "capabilities",
                [],
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )

    def supports_profile(
        self,
        profile: str,
    ) -> bool:
        """
        Check if collector supports evidence profile.
        """

        return profile in self.profiles

    def supports_capability(
        self,
        capability: str,
    ) -> bool:
        """
        Check collector capability.
        """

        return capability in self.capabilities

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize manifest.
        """

        return {
            "name": self.name,
            "version": self.version,
            "provider": self.provider,
            "description": self.description,
            "authentication": self.authentication,
            "profiles": self.profiles,
            "capabilities": self.capabilities,
            "metadata": self.metadata,
        }
