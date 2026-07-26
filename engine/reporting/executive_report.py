"""
Executive Report Generator

Produces executive-level reporting suitable for:

- CIO
- CISO
- Executive Leadership Team
- Board reporting
- Audit Committees

Focuses on:

- Overall security posture
- Framework compliance
- Risk exposure
- Maturity
- Strategic recommendations
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
# Executive Report Models
# ==============================================================================


@dataclass(slots=True)
class ExecutiveMetric:
    """
    Executive KPI.
    """

    name: str
    value: Any
    status: str


@dataclass(slots=True)
class ExecutiveReport:
    """
    Executive report wrapper.
    """

    report: ReportDocument

    metrics: list[ExecutiveMetric] = field(
        default_factory=list
    )

    recommendations: list[str] = field(
        default_factory=list
    )


# ==============================================================================
# Executive Report Generator
# ==============================================================================


class ExecutiveReportGenerator:
    """
    Produces executive reporting.
    """

    def __init__(self) -> None:

        self.report_generator = ReportGenerator()

    # ------------------------------------------------------------------

    def generate(
        self,
        assessment: AssessmentScore,
        tenant: str = "default",
    ) -> ExecutiveReport:

        report = self.report_generator.generate(
            assessment,
            tenant,
        )

        metrics = self.build_metrics(
            assessment
        )

        recommendations = self.build_recommendations(
            assessment
        )

        report.sections.append(
            self.metric_section(
                metrics
            )
        )

        report.sections.append(
            self.recommendation_section(
                recommendations
            )
        )

        return ExecutiveReport(
            report=report,
            metrics=metrics,
            recommendations=recommendations,
        )

    # ------------------------------------------------------------------

    @staticmethod
    def build_metrics(
        assessment: AssessmentScore,
    ) -> list[ExecutiveMetric]:

        summary = assessment.executive_summary

        return [

            ExecutiveMetric(
                "Security Score",
                summary.get("security_score", 0),
                "Good"
                if summary.get("security_score", 0) >= 80
                else "Needs Improvement",
            ),

            ExecutiveMetric(
                "Frameworks Assessed",
                summary.get("frameworks_assessed", 0),
                "Complete",
            ),

            ExecutiveMetric(
                "Critical Risks",
                summary.get("critical_risks", 0),
                "Attention"
                if summary.get("critical_risks", 0) > 0
                else "Healthy",
            ),

            ExecutiveMetric(
                "Maturity",
                summary.get("maturity_name", "Unknown"),
                "Current",
            ),

        ]

    # ------------------------------------------------------------------

    @staticmethod
    def build_recommendations(
        assessment: AssessmentScore,
    ) -> list[str]:

        recommendations: list[str] = []

        summary = assessment.executive_summary

        if summary.get("security_score", 0) < 80:

            recommendations.append(
                "Increase implementation of security controls across assessed frameworks."
            )

        if summary.get("critical_risks", 0) > 0:

            recommendations.append(
                "Prioritise remediation of all Critical risks."
            )

        if summary.get("maturity_level", 0) < 4:

            recommendations.append(
                "Improve governance processes to achieve Managed maturity."
            )

        if not recommendations:

            recommendations.append(
                "Maintain current security posture through continuous monitoring."
            )

        return recommendations

    # ------------------------------------------------------------------

    @staticmethod
    def metric_section(
        metrics: list[ExecutiveMetric],
    ) -> ReportSection:

        return ReportSection(
            title="Executive Metrics",
            content={
                "metrics": [
                    {
                        "name": metric.name,
                        "value": metric.value,
                        "status": metric.status,
                    }
                    for metric in metrics
                ]
            },
        )

    # ------------------------------------------------------------------

    @staticmethod
    def recommendation_section(
        recommendations: list[str],
    ) -> ReportSection:

        return ReportSection(
            title="Executive Recommendations",
            content={
                "recommendations": recommendations
            },
        )


# ==============================================================================
# Public API
# ==============================================================================


def generate_executive_report(
    assessment: AssessmentScore,
    tenant: str = "default",
) -> ExecutiveReport:
    """
    Generate an executive report.
    """

    generator = ExecutiveReportGenerator()

    return generator.generate(
        assessment,
        tenant,
    )
