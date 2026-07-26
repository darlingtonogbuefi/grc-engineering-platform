"""
Framework Mapper

Maps security capability results and control mappings
across multiple compliance frameworks.

Supported frameworks:

- CAF
- ISO27001
- SOC2
- GovAssure
- CyberEssentials

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


from typing import Any


from .control_mapper import (
    ControlMapping,
)


from .capability_mapper import (
    CapabilityResult,
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

    controls: list[dict[str, Any]] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )



# ==============================================================================
# Framework Result
# ==============================================================================


@dataclass(slots=True)
class FrameworkResult:
    """
    Result of framework mapping.
    """

    framework: Framework


    mapped_controls: list[ControlMapping] = field(
        default_factory=list
    )


    capabilities: list[CapabilityResult] = field(
        default_factory=list
    )


    coverage: float = 0.0


    score: float = 0.0


    findings: list[str] = field(
        default_factory=list
    )


    metadata: dict[str, Any] = field(
        default_factory=dict
    )



# ==============================================================================
# Framework Registry
# ==============================================================================


class FrameworkRegistry:
    """
    Registry containing supported compliance frameworks.
    """

    DEFAULT_FRAMEWORKS = {

        "CAF": {

            "name": "Cyber Assessment Framework",

            "version": "3.2",

            "description":
                "UK NCSC Cyber Assessment Framework",

        },


        "ISO27001": {

            "name":
                "ISO/IEC 27001",

            "version":
                "2022",

            "description":
                "Information Security Management System standard",

        },


        "SOC2": {

            "name":
                "SOC 2",

            "version":
                "2017",

            "description":
                "Service Organization Control framework",

        },


        "GovAssure": {

            "name":
                "GovAssure",

            "version":
                "current",

            "description":
                "UK Government cyber assurance framework",

        },


        "CyberEssentials": {

            "name":
                "Cyber Essentials",

            "version":
                "2025",

            "description":
                "UK baseline cyber security certification",

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
        Load built-in framework metadata.
        """

        self._frameworks.clear()


        for framework_id, data in (
            self.DEFAULT_FRAMEWORKS.items()
        ):

            self._frameworks[framework_id] = Framework(

                id=framework_id,

                name=data["name"],

                version=data["version"],

                description=data["description"],

            )



    # ------------------------------------------------------------------

    def register(
        self,
        framework: Framework,
    ) -> None:
        """
        Register custom framework.
        """

        self._frameworks[
            framework.id
        ] = framework



    # ------------------------------------------------------------------

    def get(
        self,
        framework_id: str,
    ) -> Framework | None:
        """
        Retrieve framework.
        """

        return self._frameworks.get(
            framework_id
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

            key=lambda item:
                item.name,

        )



    # ------------------------------------------------------------------

    def identifiers(
        self,
    ) -> list[str]:
        """
        Return framework identifiers.
        """

        return sorted(
            self._frameworks.keys()
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

        self.registry = (
            registry or FrameworkRegistry()
        )


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

        framework = self.registry.get(
            framework_id
        )

        if framework is None:

            raise ValueError(
                f"Framework not registered: {framework_id}"
            )


        matched_controls = [

            control

            for control in controls

            if control.framework == framework_id

        ]


        result = FrameworkResult(

            framework=framework,

            mapped_controls=matched_controls,

            capabilities=capabilities or [],

        )


        result.coverage = (
            self.calculate_coverage(
                result
            )
        )


        result.score = (
            self.calculate_score(
                result
            )
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

            CAF
            ISO27001
            GovAssure

        """

        results: list[FrameworkResult] = []


        for framework_id in framework_ids:

            result = self.map_framework(

                framework_id,

                controls,

                capabilities,

            )

            results.append(
                result
            )


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
                result.mapped_controls
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


        result.score = (
            FrameworkMapper.calculate_score(
                result
            )
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

        Future versions may compare against
        full framework control catalogues.
        """

        total_controls = len(
            result.framework.controls
        )


        if total_controls == 0:

            return 0.0


        return round(

            (
                len(result.mapped_controls)
                /
                total_controls
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

                total /
                len(result.capabilities),

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



        framework_count = len(
            results
        )


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
                results
            )

        )


        return {

            "frameworks":
                framework_count,


            "average_score":
                round(

                    total_score /
                    framework_count,

                    2,

                ),


            "average_coverage":
                round(

                    total_coverage /
                    framework_count,

                    2,

                ),


            "controls":
                total_controls,

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

            "summary":
                FrameworkMapper.cross_framework_summary(
                    results
                ),


            "frameworks": [

                {

                    "id":
                        item.framework.id,


                    "name":
                        item.framework.name,


                    "version":
                        item.framework.version,


                    "score":
                        item.score,


                    "coverage":
                        item.coverage,


                    "controls":
                        len(
                            item.mapped_controls
                        ),

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
                "CAF",
                "ISO27001",
                "GovAssure",
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
