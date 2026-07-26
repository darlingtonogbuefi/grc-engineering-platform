"""
Report Generator

Creates reporting objects from completed assessments.

Supports:

- Executive reporting
- Technical reporting
- Framework reporting
- Compliance summaries
- Risk summaries
"""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime, timezone

from typing import Any

from ..scoring.scoring_engine import AssessmentScore



# ==============================================================================
# Report Models
# ==============================================================================


@dataclass(slots=True)
class ReportMetadata:
    """
    Report metadata.
    """

    title: str

    tenant: str

    generated_at: datetime = field(
        default_factory=lambda:
        datetime.now(timezone.utc)
    )

    frameworks: list[str] = field(
        default_factory=list
    )

    version: str = "1.0"



@dataclass(slots=True)
class ReportSection:
    """
    Individual report section.
    """

    title: str

    content: dict[str, Any]



@dataclass(slots=True)
class ReportDocument:
    """
    Complete report.
    """

    metadata: ReportMetadata

    sections: list[ReportSection] = field(
        default_factory=list
    )



# ==============================================================================
# Report Generator
# ==============================================================================


class ReportGenerator:
    """
    Generates report objects from assessment results.
    """

    def __init__(self) -> None:

        pass


    # ------------------------------------------------------------------

    def generate(
        self,
        assessment: AssessmentScore,
        tenant: str = "default",
    ) -> ReportDocument:
        """
        Generate complete report.
        """

        metadata = ReportMetadata(

            title="Compliance Assessment",

            tenant=tenant,

            frameworks=[

                framework.framework.id

                for framework in assessment.framework_scores

            ],

        )


        report = ReportDocument(
            metadata=metadata
        )


        report.sections.extend(

            [

                self.executive_summary(
                    assessment
                ),

                self.framework_summary(
                    assessment
                ),

                self.capability_summary(
                    assessment
                ),

                self.risk_summary(
                    assessment
                ),

            ]

        )


        return report



    # ------------------------------------------------------------------

    @staticmethod
    def executive_summary(
        assessment: AssessmentScore,
    ) -> ReportSection:
        """
        Executive overview.
        """

        return ReportSection(

            title="Executive Summary",

            content=assessment.executive_summary,

        )


    # ------------------------------------------------------------------

    @staticmethod
    def framework_summary(
        assessment: AssessmentScore,
    ) -> ReportSection:
        """
        Framework assessment summary.
        """

        frameworks = [

            {

                "framework":

                    framework.framework.name,

                "version":

                    framework.framework.version,

                "score":

                    framework.score,

                "coverage":

                    framework.coverage,

            }

            for framework in assessment.framework_scores

        ]


        return ReportSection(

            title="Framework Summary",

            content={

                "frameworks":

                    frameworks

            },

        )


    # ------------------------------------------------------------------

    @staticmethod
    def capability_summary(
        assessment: AssessmentScore,
    ) -> ReportSection:
        """
        Capability maturity summary.
        """

        capabilities = [

            {

                "capability":

                    capability.capability.name,

                "score":

                    capability.score,

                "maturity":

                    capability.maturity,

            }

            for capability in assessment.capability_scores

        ]


        return ReportSection(

            title="Capability Summary",

            content={

                "capabilities":

                    capabilities

            },

        )


    # ------------------------------------------------------------------

    @staticmethod
    def risk_summary(
        assessment: AssessmentScore,
    ) -> ReportSection:
        """
        Risk overview.
        """

        risks = [

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

            }

            for result in assessment.risks

        ]


        return ReportSection(

            title="Risk Summary",

            content={

                "risks":

                    risks

            },

        )



# ==============================================================================
# Public API
# ==============================================================================


def generate_report(
    assessment: AssessmentScore,
    tenant: str = "default",
) -> ReportDocument:
    """
    Convenience API for report generation.
    """

    generator = ReportGenerator()

    return generator.generate(
        assessment=assessment,
        tenant=tenant,
    )
