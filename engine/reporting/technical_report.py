"""
Technical Report Generator

Produces detailed operational reports for:

- Security Engineers
- GRC Teams
- Auditors
- Compliance Managers

Includes:

- Evidence inventory
- Control assessment
- Capability assessment
- Framework assessment
- Risk register
- Validation findings
- Recommendations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..scoring.scoring_engine import AssessmentScore
from .report_generator import (
    ReportDocument,
    ReportGenerator,
    ReportSection,
)


# ==============================================================================
# Technical Report Models
# ==============================================================================


@dataclass(slots=True)
class TechnicalStatistic:
    """
    Technical reporting statistic.
    """

    name: str
    value: Any


@dataclass(slots=True)
class TechnicalReport:
    """
    Complete technical report.
    """

    report: ReportDocument

    statistics: list[TechnicalStatistic] = field(
        default_factory=list
    )


# ==============================================================================
# Technical Report Generator
# ==============================================================================


class TechnicalReportGenerator:
    """
    Generates detailed assessment reports.
    """

    def __init__(self) -> None:

        self.generator = ReportGenerator()

    # ------------------------------------------------------------------

    def generate(
        self,
        assessment: AssessmentScore,
        tenant: str = "default",
    ) -> TechnicalReport:

        report = self.generator.generate(
            assessment,
            tenant,
        )

        report.sections.extend(

            [

                self.evidence_section(
                    assessment
                ),

                self.control_section(
                    assessment
                ),

                self.capability_section(
                    assessment
                ),

                self.framework_section(
                    assessment
                ),

                self.risk_section(
                    assessment
                ),

                self.validation_section(
                    assessment
                ),

                self.recommendation_section(
                    assessment
                ),

            ]

        )

        return TechnicalReport(

            report=report,

            statistics=self.statistics(
                assessment
            ),

        )

    # ------------------------------------------------------------------

    @staticmethod
    def statistics(
        assessment: AssessmentScore,
    ) -> list[TechnicalStatistic]:

        return [

            TechnicalStatistic(
                "Evidence Items",
                len(
                    assessment.evidence_scores
                ),
            ),

            TechnicalStatistic(
                "Controls",
                len(
                    assessment.control_scores
                ),
            ),

            TechnicalStatistic(
                "Capabilities",
                len(
                    assessment.capability_scores
                ),
            ),

            TechnicalStatistic(
                "Frameworks",
                len(
                    assessment.framework_scores
                ),
            ),

            TechnicalStatistic(
                "Risks",
                len(
                    assessment.risks
                ),
            ),

        ]

    # ------------------------------------------------------------------

    @staticmethod
    def evidence_section(
        assessment: AssessmentScore,
    ) -> ReportSection:

        return ReportSection(

            title="Evidence",

            content={

                "evidence": [

                    {

                        "id": evidence.evidence_id,

                        "score": evidence.score,

                        "confidence": evidence.confidence,

                        "findings": evidence.findings,

                    }

                    for evidence in assessment.evidence_scores

                ]

            },

        )

    # ------------------------------------------------------------------

    @staticmethod
    def control_section(
        assessment: AssessmentScore,
    ) -> ReportSection:

        return ReportSection(

            title="Controls",

            content={

                "controls": [

                    {

                        "id": control.control_id,

                        "score": control.score,

                        "evidence_count": control.evidence_count,

                        "findings": control.findings,

                    }

                    for control in assessment.control_scores

                ]

            },

        )

    # ------------------------------------------------------------------

    @staticmethod
    def capability_section(
        assessment: AssessmentScore,
    ) -> ReportSection:

        return ReportSection(

            title="Capabilities",

            content={

                "capabilities": [

                    {

                        "name":
                            capability.capability.name,

                        "score":
                            capability.score,

                        "maturity":
                            capability.maturity,

                    }

                    for capability in assessment.capability_scores

                ]

            },

        )

    # ------------------------------------------------------------------

    @staticmethod
    def framework_section(
        assessment: AssessmentScore,
    ) -> ReportSection:

        return ReportSection(

            title="Framework Assessment",

            content={

                "frameworks": [

                    {

                        "id":
                            framework.framework.id,

                        "name":
                            framework.framework.name,

                        "version":
                            framework.framework.version,

                        "coverage":
                            framework.coverage,

                        "score":
                            framework.score,

                        "mapped_controls":
                            len(
                                framework.mapped_controls
                            ),

                    }

                    for framework in assessment.framework_scores

                ]

            },

        )

    # ------------------------------------------------------------------

    @staticmethod
    def risk_section(
        assessment: AssessmentScore,
    ) -> ReportSection:

        return ReportSection(

            title="Risk Register",

            content={

                "risks": [

                    {

                        "id":
                            result.risk.id,

                        "title":
                            result.risk.title,

                        "score":
                            result.score,

                        "level":
                            result.level.value,

                        "priority":
                            result.priority.value,

                        "owner":
                            result.risk.owner,

                        "framework":
                            result.risk.framework,

                    }

                    for result in assessment.risks

                ]

            },

        )

    # ------------------------------------------------------------------

    @staticmethod
    def validation_section(
        assessment: AssessmentScore,
    ) -> ReportSection:

        findings: list[str] = []

        for evidence in assessment.evidence_scores:

            findings.extend(
                evidence.findings
            )

        return ReportSection(

            title="Validation Findings",

            content={

                "count": len(findings),

                "findings": findings,

            },

        )

    # ------------------------------------------------------------------

    @staticmethod
    def recommendation_section(
        assessment: AssessmentScore,
    ) -> ReportSection:

        recommendations: list[str] = []

        for risk in assessment.risks:

            recommendations.extend(
                risk.recommendations
            )

        recommendations = sorted(
            set(recommendations)
        )

        return ReportSection(

            title="Technical Recommendations",

            content={

                "recommendations":
                    recommendations

            },

        )


# ==============================================================================
# Public API
# ==============================================================================


def generate_technical_report(
    assessment: AssessmentScore,
    tenant: str = "default",
) -> TechnicalReport:
    """
    Generate a technical report.
    """

    generator = TechnicalReportGenerator()

    return generator.generate(
        assessment,
        tenant,
    )
