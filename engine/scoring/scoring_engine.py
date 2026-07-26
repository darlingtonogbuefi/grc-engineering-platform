"""
Scoring Engine

Central scoring orchestration layer.

Combines:

- Evidence scoring
- Control scoring
- Capability scoring
- Framework scoring
- Risk calculations
- Executive summaries

Pipeline:

Evidence
    |
    v
Evidence Score
    |
    v
Control Score
    |
    v
Capability Score
    |
    v
Framework Score
    |
    v
Risk Assessment
    |
    v
Executive Summary
"""

from __future__ import annotations


from dataclasses import dataclass, field


from typing import Any


from .maturity_model import (
    MaturityModel,
    MaturityResult,
)


from .risk_calculator import (
    Risk,
    RiskCalculator,
    RiskResult,
)


from ..mapper.control_mapper import (
    ControlMapping,
)


from ..mapper.capability_mapper import (
    CapabilityResult,
)


from ..mapper.framework_mapper import (
    FrameworkResult,
)



# ==============================================================================
# Score Models
# ==============================================================================


@dataclass(slots=True)
class EvidenceScore:
    """
    Evidence quality score.
    """

    evidence_id: str

    score: float

    confidence: float = 1.0

    findings: list[str] = field(
        default_factory=list
    )



@dataclass(slots=True)
class ControlScore:
    """
    Control effectiveness score.
    """

    control_id: str

    score: float

    evidence_count: int

    findings: list[str] = field(
        default_factory=list
    )



@dataclass(slots=True)
class AssessmentScore:
    """
    Complete assessment scoring result.
    """

    evidence_scores: list[EvidenceScore]

    control_scores: list[ControlScore]

    capability_scores: list[CapabilityResult]

    framework_scores: list[FrameworkResult]

    risks: list[RiskResult]

    maturity: MaturityResult

    executive_summary: dict[str, Any]



# ==============================================================================
# Scoring Engine
# ==============================================================================


class ScoringEngine:
    """
    Main scoring coordinator.
    """

    def __init__(
        self,
    ) -> None:

        self.maturity_model = (
            MaturityModel()
        )

        self.risk_calculator = (
            RiskCalculator()
        )


    # ------------------------------------------------------------------
    # Evidence Scoring
    # ------------------------------------------------------------------

    def score_evidence(
        self,
        evidence: list[dict[str, Any]],
    ) -> list[EvidenceScore]:
        """
        Score evidence quality.
        """

        results: list[EvidenceScore] = []


        for item in evidence:

            evidence_id = item.get(
                "evidence_id",
                "unknown",
            )


            confidence = float(
                item.get(
                    "confidence",
                    1.0,
                )
            )


            score = confidence * 100


            findings = []


            if confidence < 0.5:

                findings.append(
                    "Low confidence evidence."
                )


            results.append(

                EvidenceScore(

                    evidence_id=evidence_id,

                    score=round(
                        score,
                        2,
                    ),

                    confidence=confidence,

                    findings=findings,

                )

            )


        return results



    # ------------------------------------------------------------------
    # Control Scoring
    # ------------------------------------------------------------------

    def score_controls(
        self,
        mappings: list[ControlMapping],
    ) -> list[ControlScore]:
        """
        Score control effectiveness.
        """

        results: dict[str, ControlScore] = {}


        for mapping in mappings:

            control_id = (
                mapping.control_id
            )


            score = min(

                len(
                    mapping.evidence
                )
                *
                25,

                100,

            )


            results[control_id] = ControlScore(

                control_id=control_id,

                score=score,

                evidence_count=len(
                    mapping.evidence
                ),

            )


        return list(
            results.values()
        )



    # ------------------------------------------------------------------
    # Capability Scoring
    # ------------------------------------------------------------------

    def score_capabilities(
        self,
        capabilities: list[CapabilityResult],
    ) -> list[CapabilityResult]:
        """
        Normalise capability scores.
        """

        for capability in capabilities:

            capability.score = min(

                capability.score,

                100,

            )


            capability.maturity = (

                capability.score /

                20

            )


        return capabilities



    # ------------------------------------------------------------------
    # Framework Scoring
    # ------------------------------------------------------------------

    def score_frameworks(
        self,
        frameworks: list[FrameworkResult],
    ) -> list[FrameworkResult]:
        """
        Calculate framework maturity scores.
        """

        for framework in frameworks:

            framework.score = min(

                framework.score,

                100,

            )


        return frameworks



    # ------------------------------------------------------------------
    # Risk Integration
    # ------------------------------------------------------------------

    def calculate_risks(
        self,
        risks: list[Risk],
    ) -> list[RiskResult]:
        """
        Calculate risk results.
        """

        return [

            self.risk_calculator.calculate(
                risk
            )

            for risk in risks

        ]



    # ------------------------------------------------------------------
    # Complete Assessment
    # ------------------------------------------------------------------

    def assess(
        self,
        evidence: list[dict[str, Any]],
        controls: list[ControlMapping],
        capabilities: list[CapabilityResult],
        frameworks: list[FrameworkResult],
        risks: list[Risk] | None = None,
    ) -> AssessmentScore:
        """
        Execute complete scoring process.
        """

        evidence_scores = (
            self.score_evidence(
                evidence
            )
        )


        control_scores = (
            self.score_controls(
                controls
            )
        )


        capability_scores = (
            self.score_capabilities(
                capabilities
            )
        )


        framework_scores = (
            self.score_frameworks(
                frameworks
            )
        )


        risk_results = (

            self.calculate_risks(
                risks or []
            )

        )


        overall_score = (
            self.calculate_overall_score(
                framework_scores
            )
        )


        maturity = (
            self.maturity_model.calculate(
                overall_score
            )
        )


        summary = (
            self.executive_summary(
                overall_score,
                maturity,
                framework_scores,
                risk_results,
            )
        )


        return AssessmentScore(

            evidence_scores=evidence_scores,

            control_scores=control_scores,

            capability_scores=capability_scores,

            framework_scores=framework_scores,

            risks=risk_results,

            maturity=maturity,

            executive_summary=summary,

        )



    # ------------------------------------------------------------------
    # Overall Score
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_overall_score(
        frameworks: list[FrameworkResult],
    ) -> float:
        """
        Calculate enterprise security score.
        """

        if not frameworks:

            return 0.0


        return round(

            sum(
                item.score
                for item in frameworks
            )
            /
            len(frameworks),

            2,

        )



    # ------------------------------------------------------------------
    # Executive Summary
    # ------------------------------------------------------------------

    @staticmethod
    def executive_summary(
        score: float,
        maturity: MaturityResult,
        frameworks: list[FrameworkResult],
        risks: list[RiskResult],
    ) -> dict[str, Any]:
        """
        Generate executive reporting data.
        """

        return {

            "security_score":
                score,


            "maturity_level":
                maturity.level,


            "maturity_name":
                maturity.name,


            "frameworks_assessed":
                len(frameworks),


            "risks_identified":
                len(risks),


            "critical_risks":
                len(

                    [

                        risk

                        for risk in risks

                        if risk.level.value
                        ==
                        "Critical"

                    ]

                ),

        }



# ==============================================================================
# Public API
# ==============================================================================


def run_scoring(
    evidence: list[dict[str, Any]],
    controls: list[ControlMapping],
    capabilities: list[CapabilityResult],
    frameworks: list[FrameworkResult],
    risks: list[Risk] | None = None,
) -> AssessmentScore:
    """
    Convenience scoring API.
    """

    engine = ScoringEngine()

    return engine.assess(

        evidence,

        controls,

        capabilities,

        frameworks,

        risks,

    )
