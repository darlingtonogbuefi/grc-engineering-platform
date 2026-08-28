# engine\mapper\framework_mapper.py

"""
Framework Mapper

Maps security capability results and control mappings
across multiple compliance frameworks.

Supported frameworks:

- NCSC CAF
- ISO 42001
- ISO 27001
- SOC 2
- Cyber Essentials
- Government Assurance

Purpose:

Evidence
|
v
Controls
|
v
Capabilities
|
v
Framework Assessment
|
v
Reports
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .control_mapper import ControlMapping
from .capability_mapper import CapabilityResult


# ==============================================================================
# Supported Frameworks
# ==============================================================================


SUPPORTED_FRAMEWORKS = (
    "NCSC_CAF",
    "ISO_42001",
    "ISO_27001",
    "SOC_2",
    "CYBER_ESSENTIALS",
    "GOV_ASSURANCE",
)


# ==============================================================================
# Framework Identifier Normalisation
# ==============================================================================


FRAMEWORK_ID_ALIASES = {
    "ISO27001": "ISO_27001",
    "ISO_42001": "ISO_42001",
    "NCSC_CAF": "NCSC_CAF",
    "SOC_2": "SOC_2",
    "CYBER_ESSENTIALS": "CYBER_ESSENTIALS",
    "GOV_ASSURANCE": "GOV_ASSURANCE",
}


def normalize_framework_id(framework_id: str) -> str:
    """
    Normalize framework identifiers to the canonical registry ID.

    This allows source framework definitions to use identifiers such as
    ``ISO27001`` while the application registry consistently uses
    ``ISO_27001``.
    """

    if not isinstance(framework_id, str):
        raise TypeError("Framework identifier must be a string.")

    normalized = framework_id.strip()

    return FRAMEWORK_ID_ALIASES.get(
        normalized,
        normalized,
    )


# ==============================================================================
# Framework Model
# ==============================================================================


@dataclass(slots=True)
class Framework:
    """
    Represents a compliance framework.
    """

    id: str

    name: str

    version: str

    description: str

    controls: list[dict[str, Any]] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)


# ==============================================================================
# Framework Result
# ==============================================================================


@dataclass(slots=True)
class FrameworkResult:
    """
    Result of framework mapping.
    """

    framework: Framework

    mapped_controls: list[ControlMapping] = field(default_factory=list)

    capabilities: list[CapabilityResult] = field(default_factory=list)

    coverage: float = 0.0

    score: float = 0.0

    findings: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)


# ==============================================================================
# Framework Registry
# ==============================================================================


class FrameworkRegistry:
    """
    Registry containing supported compliance frameworks.

    Framework metadata is defined in ``DEFAULT_FRAMEWORKS``.

    Where a framework catalogue exists under:

        frameworks/<framework-directory>/controls.yml

    the control definitions are loaded into ``Framework.controls``.
    """

    DEFAULT_FRAMEWORKS = {
        "NCSC_CAF": {
            "name": "NCSC Cyber Assessment Framework",
            "version": "current",
            "description": "UK NCSC Cyber Assessment Framework",
        },
        "ISO_42001": {
            "name": "ISO/IEC 42001",
            "version": "2023",
            "description": "Artificial intelligence management system standard",
        },
        "ISO_27001": {
            "name": "ISO/IEC 27001",
            "version": "2022",
            "description": "Information security management system standard",
        },
        "SOC_2": {
            "name": "SOC 2",
            "version": "2017",
            "description": "Service Organization Control framework",
        },
        "GOV_ASSURANCE": {
            "name": "Government Assurance",
            "version": "current",
            "description": "UK Government cyber assurance framework",
        },
        "CYBER_ESSENTIALS": {
            "name": "Cyber Essentials",
            "version": "current",
            "description": "UK baseline cyber security certification scheme",
        },
    }

    def __init__(self) -> None:
        self._frameworks: dict[str, Framework] = {}

        self.load_defaults()

    # ------------------------------------------------------------------

    def load_defaults(
        self,
    ) -> None:
        """
        Load built-in framework metadata and available control catalogues.
        """

        self._frameworks.clear()

        for framework_id, data in self.DEFAULT_FRAMEWORKS.items():

            controls = self._load_controls(
                framework_id,
            )

            self._frameworks[framework_id] = Framework(
                id=framework_id,
                name=data["name"],
                version=data["version"],
                description=data["description"],
                controls=controls,
                metadata={
                    "id": framework_id,
                },
            )

    # ------------------------------------------------------------------

    @staticmethod
    def _framework_directory(
        framework_id: str,
    ) -> str:
        """
        Return the framework directory name used by the source catalogues.

        Application identifiers use underscores in places such as
        ``ISO_27001``, while the source catalogue currently uses
        ``ISO27001``.
        """

        directory_aliases = {
            "ISO_27001": "ISO27001",
            "ISO_42001": "ISO42001",
            "NCSC_CAF": "NCSC_CAF",
            "SOC_2": "SOC2",
            "CYBER_ESSENTIALS": "CYBER_ESSENTIALS",
            "GOV_ASSURANCE": "GOV_ASSURANCE",
        }

        return directory_aliases.get(
            framework_id,
            framework_id,
        )

    # ------------------------------------------------------------------

    @classmethod
    def _load_controls(
        cls,
        framework_id: str,
    ) -> list[dict[str, Any]]:
        """
        Load controls from the framework's controls.yml file.

        Missing catalogues return an empty list so that framework
        registration remains backwards compatible for frameworks
        whose YAML catalogue has not yet been added.
        """

        canonical_id = normalize_framework_id(
            framework_id,
        )

        project_root = Path(__file__).resolve().parents[2]

        framework_directory = cls._framework_directory(
            canonical_id,
        )

        controls_path = (
            project_root
            / "frameworks"
            / framework_directory
            / "controls.yml"
        )

        if not controls_path.exists():
            return []

        try:
            with controls_path.open(
                "r",
                encoding="utf-8",
            ) as handle:

                data = yaml.safe_load(handle) or {}

        except (OSError, yaml.YAMLError):
            return []

        if not isinstance(data, dict):
            return []

        controls = data.get(
            "controls",
            [],
        )

        if not isinstance(controls, list):
            return []

        return [
            control
            for control in controls
            if isinstance(control, dict)
            and control.get("id")
        ]

    # ------------------------------------------------------------------

    def register(
        self,
        framework: Framework,
    ) -> None:
        """
        Register custom framework.
        """

        framework.id = normalize_framework_id(
            framework.id,
        )

        self._frameworks[framework.id] = framework

    # ------------------------------------------------------------------

    def get(
        self,
        framework_id: str,
    ) -> Framework | None:
        """
        Retrieve framework using its canonical identifier.
        """

        canonical_id = normalize_framework_id(
            framework_id,
        )

        return self._frameworks.get(
            canonical_id,
        )

    # ------------------------------------------------------------------

    def all(
        self,
    ) -> list[Framework]:
        """
        Return all frameworks.
        """

        return sorted(
            self._frameworks.values(),
            key=lambda item: item.name,
        )

    # ------------------------------------------------------------------

    def identifiers(
        self,
    ) -> list[str]:
        """
        Return framework identifiers.
        """

        return sorted(
            self._frameworks.keys(),
        )


# ==============================================================================
# Framework Mapper
# ==============================================================================


class FrameworkMapper:
    """
    Orchestrates framework-level assessments.

    Combines:

    - Control mappings
    - Capability results
    - Framework definitions

    Produces:

    - Framework coverage
    - Framework scores
    - Cross-framework summaries
    """

    def __init__(
        self,
        registry: FrameworkRegistry | None = None,
    ) -> None:

        self.registry = registry or FrameworkRegistry()

    # ------------------------------------------------------------------
    # Single Framework Mapping
    # ------------------------------------------------------------------

    def map_framework(
        self,
        framework_id: str,
        controls: list[ControlMapping],
        capabilities: list[CapabilityResult] | None = None,
    ) -> FrameworkResult:
        """
        Map controls and capabilities into a framework.
        """

        canonical_framework_id = normalize_framework_id(
            framework_id,
        )

        framework = self.registry.get(
            canonical_framework_id,
        )

        if framework is None:

            raise ValueError(
                f"Framework not registered: {framework_id}"
            )

        matched_controls = [
            control
            for control in controls
            if normalize_framework_id(control.framework)
            == canonical_framework_id
        ]

        result = FrameworkResult(
            framework=framework,
            mapped_controls=matched_controls,
            capabilities=capabilities or [],
        )

        result.coverage = self.calculate_coverage(
            result,
        )

        result.score = self.calculate_score(
            result,
        )

        return result

    # ------------------------------------------------------------------
    # Multi Framework Mapping
    # ------------------------------------------------------------------

    def map_frameworks(
        self,
        framework_ids: list[str],
        controls: list[ControlMapping],
        capabilities: list[CapabilityResult] | None = None,
    ) -> list[FrameworkResult]:
        """
        Run mapping across multiple frameworks.

        Example:

            NCSC_CAF
            ISO_27001
            GOV_ASSURANCE
        """

        results: list[FrameworkResult] = []

        for framework_id in framework_ids:

            result = self.map_framework(
                framework_id,
                controls,
                capabilities,
            )

            results.append(result)

        return results

    # ------------------------------------------------------------------
    # Control Aggregation
    # ------------------------------------------------------------------

    @staticmethod
    def aggregate_controls(
        results: list[FrameworkResult],
    ) -> list[ControlMapping]:
        """
        Combine controls from multiple frameworks.
        """

        controls: list[ControlMapping] = []

        for result in results:

            controls.extend(
                result.mapped_controls,
            )

        return controls

    # ------------------------------------------------------------------
    # Capability Integration
    # ------------------------------------------------------------------

    @staticmethod
    def attach_capabilities(
        result: FrameworkResult,
        capabilities: list[CapabilityResult],
    ) -> FrameworkResult:
        """
        Attach capability assessments.
        """

        result.capabilities = capabilities

        result.score = FrameworkMapper.calculate_score(
            result,
        )

        return result

    # ------------------------------------------------------------------
    # Coverage Calculation
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_coverage(
        result: FrameworkResult,
    ) -> float:
        """
        Calculate framework control coverage.

        Coverage is based on unique mapped control IDs divided by
        the total number of controls in the framework catalogue.
        """

        total_controls = len(
            result.framework.controls,
        )

        if total_controls == 0:
            return 0.0

        mapped_control_ids = {
            control.control_id
            for control in result.mapped_controls
        }

        return round(
            (
                len(mapped_control_ids)
                / total_controls
            )
            * 100,
            2,
        )

    # ------------------------------------------------------------------
    # Framework Scoring
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_score(
        result: FrameworkResult,
    ) -> float:
        """
        Calculate framework score.

        Uses capability scores when available.
        """

        if result.capabilities:

            total = sum(
                capability.score
                for capability in result.capabilities
            )

            return round(
                total / len(result.capabilities),
                2,
            )

        return result.coverage

    # ------------------------------------------------------------------
    # Cross Framework Summary
    # ------------------------------------------------------------------

    @staticmethod
    def cross_framework_summary(
        results: list[FrameworkResult],
    ) -> dict[str, Any]:
        """
        Produce enterprise-wide compliance summary.
        """

        if not results:

            return {
                "frameworks": 0,
                "average_score": 0.0,
                "average_coverage": 0.0,
                "controls": 0,
            }

        framework_count = len(results)

        total_score = sum(
            item.score
            for item in results
        )

        total_coverage = sum(
            item.coverage
            for item in results
        )

        total_controls = len(
            FrameworkMapper.aggregate_controls(
                results,
            )
        )

        return {
            "frameworks": framework_count,
            "average_score": round(
                total_score / framework_count,
                2,
            ),
            "average_coverage": round(
                total_coverage / framework_count,
                2,
            ),
            "controls": total_controls,
        }

    # ------------------------------------------------------------------
    # Reporting Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def reporting_payload(
        results: list[FrameworkResult],
    ) -> dict[str, Any]:
        """
        Generate reporting-ready data.

        Used by:

        - HTML reports
        - Power BI exports
        - Executive dashboards
        """

        return {
            "summary": FrameworkMapper.cross_framework_summary(
                results,
            ),
            "frameworks": [
                {
                    "id": item.framework.id,
                    "name": item.framework.name,
                    "version": item.framework.version,
                    "score": item.score,
                    "coverage": item.coverage,
                    "controls": len(item.mapped_controls),
                }
                for item in results
            ],
        }


# ==============================================================================
# Public API
# ==============================================================================


def map_frameworks(
    framework_ids: list[str],
    controls: list[ControlMapping],
    capabilities: list[CapabilityResult] | None = None,
) -> list[FrameworkResult]:
    """
    Convenience API.

    Example:

        results = map_frameworks(
            [
                "NCSC_CAF",
                "ISO_27001",
                "GOV_ASSURANCE",
            ],
            controls,
            capabilities,
        )
    """

    mapper = FrameworkMapper()

    return mapper.map_frameworks(
        framework_ids,
        controls,
        capabilities,
    )
