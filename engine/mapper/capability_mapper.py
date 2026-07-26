

# engine\mapper\capability_mapper.py


"""
Capability Mapper

Maps framework controls into security capabilities.

Capabilities represent higher-level security domains used
for reporting, maturity scoring and cross-framework mapping.

Supported capabilities include:

- Identity
- Endpoint
- Cloud
- Networking
- Monitoring
- Logging
- Backup
- Vulnerability
- Microsoft 365
- DevOps
- Business Applications
"""

from __future__ import annotations

from dataclasses import dataclass, field

from typing import Any


from .control_mapper import (
    ControlMapping,
)


# ==============================================================================
# Capability Model
# ==============================================================================


@dataclass(slots=True)
class Capability:
    """
    Represents a security capability.
    """

    id: str

    name: str

    description: str

    controls: list[ControlMapping] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Capability Result
# ==============================================================================


@dataclass(slots=True)
class CapabilityResult:
    """
    Result produced for a capability after mapping.

    Scoring is performed later by the scoring engine.
    """

    capability: Capability

    evidence_count: int = 0

    mapped_controls: int = 0

    maturity: float = 0.0

    score: float = 0.0

    findings: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ==============================================================================
# Capability Registry
# ==============================================================================


class CapabilityRegistry:
    """
    Registry of supported capabilities.

    This provides a single source of truth for capability
    definitions across the platform.
    """

    DEFAULT_CAPABILITIES: dict[str, tuple[str, str]] = {

        "identity": (

            "Identity",

            "Identity and access management.",

        ),

        "endpoint": (

            "Endpoint",

            "Endpoint security and device management.",

        ),

        "cloud": (

            "Cloud",

            "Cloud platform governance and security.",

        ),

        "networking": (

            "Networking",

            "Network security controls.",

        ),

        "monitoring": (

            "Monitoring",

            "Monitoring and alerting.",

        ),

        "logging": (

            "Logging",

            "Audit logging and event collection.",

        ),

        "backup": (

            "Backup",

            "Backup, restore and recovery.",

        ),

        "vulnerability": (

            "Vulnerability",

            "Vulnerability and patch management.",

        ),

        "m365": (

            "Microsoft 365",

            "Microsoft 365 security capabilities.",

        ),

        "devops": (

            "DevOps",

            "DevOps and CI/CD security.",

        ),

        "business-apps": (

            "Business Applications",

            "Business application governance.",

        ),

    }

    def __init__(self) -> None:

        self._capabilities: dict[str, Capability] = {}

        self.load_defaults()

    # ------------------------------------------------------------------

    def load_defaults(self) -> None:
        """
        Load built-in capabilities.
        """

        self._capabilities.clear()

        for capability_id, values in (
            self.DEFAULT_CAPABILITIES.items()
        ):

            name, description = values

            self._capabilities[capability_id] = Capability(

                id=capability_id,

                name=name,

                description=description,

            )

    # ------------------------------------------------------------------

    def register(
        self,
        capability: Capability,
    ) -> None:
        """
        Register or replace a capability.
        """

        self._capabilities[
            capability.id
        ] = capability

    # ------------------------------------------------------------------

    def get(
        self,
        capability_id: str,
    ) -> Capability | None:
        """
        Retrieve a capability by identifier.
        """

        return self._capabilities.get(
            capability_id
        )

    # ------------------------------------------------------------------

    def all(
        self,
    ) -> list[Capability]:
        """
        Return all registered capabilities.
        """

        return sorted(

            self._capabilities.values(),

            key=lambda c: c.name,

        )

    # ------------------------------------------------------------------

    def identifiers(
        self,
    ) -> list[str]:
        """
        Return capability identifiers.
        """

        return sorted(
            self._capabilities.keys()
        )




# ==============================================================================
# Capability Mapper
# ==============================================================================


class CapabilityMapper:
    """
    Maps ControlMappings into security capabilities.

    Pipeline

        ControlMappings
              |
              v
        Capability Registry
              |
              v
        Capability Results
              |
              v
        Maturity
              |
              v
        Summary
    """

    def __init__(
        self,
        registry: CapabilityRegistry | None = None,
    ) -> None:

        self.registry = registry or CapabilityRegistry()

    # ------------------------------------------------------------------

    def map_controls(
        self,
        mappings: list[ControlMapping],
    ) -> list[CapabilityResult]:
        """
        Convert mapped controls into capability results.
        """

        results: dict[str, CapabilityResult] = {}

        for mapping in mappings:

            capability_id = (
                mapping.capability or "uncategorised"
            ).lower()

            capability = self.registry.get(
                capability_id
            )

            if capability is None:

                capability = Capability(

                    id=capability_id,

                    name=capability_id.replace(
                        "-",
                        " "
                    ).title(),

                    description="Custom capability",

                )

                self.registry.register(
                    capability
                )

            if capability.id not in results:

                results[capability.id] = CapabilityResult(
                    capability=capability
                )

            result = results[capability.id]

            result.capability.controls.append(
                mapping
            )

            result.mapped_controls += 1

            result.evidence_count += len(
                mapping.evidence
            )

        for result in results.values():

            result.score = self.calculate_score(
                result
            )

            result.maturity = (
                self.calculate_maturity(
                    result
                )
            )

        return sorted(

            results.values(),

            key=lambda item:
                item.capability.name,

        )

    # ------------------------------------------------------------------

    @staticmethod
    def calculate_score(
        result: CapabilityResult,
    ) -> float:
        """
        Basic capability score.

        Future versions will use weighted
        evidence confidence.
        """

        if result.mapped_controls == 0:

            return 0.0

        evidence_ratio = (
            result.evidence_count /
            result.mapped_controls
        )

        score = min(
            evidence_ratio * 20.0,
            100.0,
        )

        return round(
            score,
            2,
        )

    # ------------------------------------------------------------------

    @staticmethod
    def calculate_maturity(
        result: CapabilityResult,
    ) -> float:
        """
        Convert score into maturity level.

        0.0–5.0 scale.
        """

        return round(
            (result.score / 100.0) * 5.0,
            2,
        )

    # ------------------------------------------------------------------

    @staticmethod
    def summary(
        results: list[CapabilityResult],
    ) -> dict[str, Any]:
        """
        Produce summary statistics.
        """

        if not results:

            return {

                "capabilities": 0,

                "average_score": 0.0,

                "average_maturity": 0.0,

                "mapped_controls": 0,

                "evidence": 0,

            }

        capability_count = len(
            results
        )

        total_score = sum(
            item.score
            for item in results
        )

        total_maturity = sum(
            item.maturity
            for item in results
        )

        mapped_controls = sum(
            item.mapped_controls
            for item in results
        )

        evidence = sum(
            item.evidence_count
            for item in results
        )

        return {

            "capabilities":
                capability_count,

            "average_score":
                round(
                    total_score /
                    capability_count,
                    2,
                ),

            "average_maturity":
                round(
                    total_maturity /
                    capability_count,
                    2,
                ),

            "mapped_controls":
                mapped_controls,

            "evidence":
                evidence,

        }


# ==============================================================================
# Public API
# ==============================================================================


def map_capabilities(
    mappings: list[ControlMapping],
) -> list[CapabilityResult]:
    """
    Convenience function.

    Example

        capability_results = map_capabilities(
            control_results.mappings
        )
    """

    mapper = CapabilityMapper()

    return mapper.map_controls(
        mappings
    )
