# engine/reporting/report_generator.py

"""
Report Generator

Creates reporting objects from completed assessments.

This module is the orchestration layer for reporting.

Responsibilities:

- Create report metadata
- Coordinate executive reporting
- Coordinate evidence reporting
- Coordinate framework reporting
- Coordinate capability reporting
- Coordinate risk reporting

Detailed evidence/framework/helper logic lives in:

    report_models.py
    report_evidence.py
    report_frameworks.py
    report_helpers.py

The reporting layer consumes assessment results and evidence produced by
the assessment pipeline. It does not invent control results or evidence.

Evidence reporting is delegated entirely to report_evidence.py so that
EvidenceTableBuilder remains the single implementation for the standard
framework/provider-independent evidence table.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..scoring.scoring_engine import AssessmentScore
from . import report_frameworks
from .report_evidence import EvidenceReporter
from .report_helpers import (
    enum_value,
    first_value,
    framework_name,
    object_name,
    object_to_dict,
    serialise_value,
)
from .report_models import (
    ReportDocument,
    ReportMetadata,
    ReportSection,
)

# ==============================================================================
# Report Generator
# ==============================================================================


class ReportGenerator:
    """
    Generates report objects from assessment results.

    The generator is intentionally kept as an orchestration layer.

    It does not perform detailed evidence normalization, framework
    processing, or object serialization itself. Those responsibilities
    are delegated to the reporting modules.

    Control-level evidence is taken from the completed assessment object.
    The reporting layer does not manufacture control results, statuses,
    scores, or evidence.

    Standard evidence-table construction is delegated to
    EvidenceReporter, which in turn uses EvidenceTableBuilder.
    """

    def __init__(self) -> None:
        pass

    # ------------------------------------------------------------------
    # Report Generation
    # ------------------------------------------------------------------

    def generate(
        self,
        assessment: AssessmentScore,
        tenant: str = "default",
    ) -> ReportDocument:
        """
        Generate complete report.

        The report contains:

        - Executive Summary
        - Evidence Summary
        - Live Control Evidence
        - Standard Evidence Table
        - Framework Summary
        - Capability Summary
        - Risk Summary

        Detailed construction of evidence and framework sections is
        delegated to their respective reporting modules.

        Evidence does not bypass report_evidence.py. All evidence-related
        report sections are produced by EvidenceReporter.
        """

        framework_scores = getattr(
            assessment,
            "framework_scores",
            [],
        )

        metadata = ReportMetadata(
            title="Compliance Assessment",
            tenant=tenant,
            generated_at=datetime.now(timezone.utc),
            frameworks=[
                self.framework_identifier(framework) for framework in framework_scores
            ],
        )

        report = ReportDocument(
            metadata=metadata,
        )

        # ------------------------------------------------------------------
        # Evidence reporting
        #
        # All evidence-related sections are deliberately delegated to
        # EvidenceReporter.
        #
        # EvidenceReporter.evidence_table() uses EvidenceTableBuilder,
        # ensuring that the standard evidence representation is built in
        # one place and remains provider/framework independent.
        # ------------------------------------------------------------------

        evidence_summary = EvidenceReporter.evidence_summary(
            assessment,
        )

        control_evidence_summary = EvidenceReporter.control_evidence_summary(
            assessment,
        )

        evidence_table = EvidenceReporter.evidence_table(
            assessment,
        )

        # ------------------------------------------------------------------
        # Assemble the complete report.
        #
        # Existing report sections remain in their original order, with
        # the standard evidence table added immediately after the live
        # control evidence section.
        # ------------------------------------------------------------------

        report.sections.extend(
            [
                self.executive_summary(
                    assessment,
                ),
                evidence_summary,
                control_evidence_summary,
                evidence_table,
                self.framework_summary(
                    assessment,
                ),
                self.capability_summary(
                    assessment,
                ),
                self.risk_summary(
                    assessment,
                ),
            ]
        )

        return report

    # ------------------------------------------------------------------
    # Executive Summary
    # ------------------------------------------------------------------

    @staticmethod
    def executive_summary(
        assessment: AssessmentScore,
    ) -> ReportSection:
        """
        Executive overview.

        The executive summary is consumed directly from the assessment
        scoring result. No compliance result is calculated here.
        """

        return ReportSection(
            title="Executive Summary",
            content=dict(assessment.executive_summary),
        )

    # ------------------------------------------------------------------
    # Framework Summary
    # ------------------------------------------------------------------

    @staticmethod
    def framework_identifier(
        framework: Any,
    ) -> str:
        """
        Return the identifier/name of a framework.

        This method is intentionally retained as a compatibility API for
        existing callers that may already use:

            ReportGenerator.framework_identifier(...)

        The implementation uses the shared reporting helper rather than
        referencing a non-existent function in report_frameworks.py.
        """

        name = framework_name(framework)

        if name is not None:
            return str(
                serialise_value(
                    name,
                )
            )

        return str(
            serialise_value(
                framework,
            )
        )

    @classmethod
    def framework_summary(
        cls,
        assessment: AssessmentScore,
    ) -> ReportSection:
        """
        Framework summary compatibility layer.

        The detailed framework processing is performed by
        FrameworkReportBuilder in report_frameworks.py.

        The resulting FrameworkReport objects are converted into the
        existing ReportSection representation so existing consumers of
        ReportGenerator continue to work.
        """

        framework_reports = report_frameworks.build_framework_reports(
            assessment,
        )

        frameworks: list[dict[str, Any]] = []

        for framework_report in framework_reports:
            item: dict[str, Any] = {
                "framework": framework_report.framework,
            }

            if framework_report.version is not None:
                item["version"] = framework_report.version

            if framework_report.score is not None:
                item["score"] = framework_report.score

            if framework_report.status is not None:
                item["status"] = framework_report.status

            item["total_requirements"] = framework_report.total_requirements

            item["met"] = framework_report.met

            item["partially_met"] = framework_report.partially_met

            item["not_met"] = framework_report.not_met

            item["not_applicable"] = framework_report.not_applicable

            item["requirements"] = [
                {
                    "requirement_id": requirement.requirement_id,
                    "title": requirement.title,
                    "status": requirement.status,
                    "confidence": requirement.confidence,
                    "score": requirement.score,
                    "finding": requirement.finding,
                    "evidence": list(
                        requirement.evidence,
                    ),
                }
                for requirement in framework_report.requirements
            ]

            frameworks.append(
                item,
            )

        return ReportSection(
            title="Framework Summary",
            content={
                "frameworks": frameworks,
            },
        )

    # ------------------------------------------------------------------
    # Capability Summary
    # ------------------------------------------------------------------

    @classmethod
    def capability_summary(
        cls,
        assessment: AssessmentScore,
    ) -> ReportSection:
        """
        Capability maturity summary.

        This remains in the generator because it is a high-level
        reporting operation and does not require the detailed evidence
        or framework normalization machinery.
        """

        capabilities: list[dict[str, Any]] = []

        for capability in assessment.capability_scores:
            capability_data = cls._object_to_dict(
                capability,
            )

            capability_object = capability_data.get(
                "capability",
                getattr(
                    capability,
                    "capability",
                    None,
                ),
            )

            capability_object_data = cls._object_to_dict(
                capability_object,
            )

            name = cls._first_value(
                capability_object_data,
                (
                    "name",
                    "id",
                ),
            )

            score = cls._first_value(
                capability_data,
                ("score",),
            )

            maturity = cls._first_value(
                capability_data,
                ("maturity",),
            )

            item: dict[str, Any] = {}

            if name is not None:
                item["capability"] = cls._serialise_value(
                    name,
                )

            elif capability_object is not None:
                item["capability"] = cls._serialise_value(
                    cls._object_name(
                        capability_object,
                    ),
                )

            if score is not None:
                item["score"] = cls._serialise_value(
                    score,
                )

            if maturity is not None:
                item["maturity"] = cls._serialise_value(
                    maturity,
                )

            if item:
                capabilities.append(
                    item,
                )

        return ReportSection(
            title="Capability Summary",
            content={
                "capabilities": capabilities,
            },
        )

    # ------------------------------------------------------------------
    # Risk Summary
    # ------------------------------------------------------------------

    @classmethod
    def risk_summary(
        cls,
        assessment: AssessmentScore,
    ) -> ReportSection:
        """
        Risk overview.

        Risk values are consumed from the completed assessment.
        The reporting layer does not calculate risk.
        """

        risks: list[dict[str, Any]] = []

        for result in assessment.risks:
            result_data = cls._object_to_dict(
                result,
            )

            risk = result_data.get(
                "risk",
                getattr(
                    result,
                    "risk",
                    None,
                ),
            )

            risk_data = cls._object_to_dict(
                risk,
            )

            risk_id = cls._first_value(
                risk_data,
                ("id",),
            )

            title = cls._first_value(
                risk_data,
                (
                    "title",
                    "name",
                ),
            )

            score = cls._first_value(
                result_data,
                ("score",),
            )

            level = cls._enum_value(
                cls._first_value(
                    result_data,
                    ("level",),
                ),
            )

            priority = cls._enum_value(
                cls._first_value(
                    result_data,
                    ("priority",),
                ),
            )

            item: dict[str, Any] = {}

            if risk_id is not None:
                item["id"] = cls._serialise_value(
                    risk_id,
                )

            if title is not None:
                item["title"] = cls._serialise_value(
                    title,
                )

            if score is not None:
                item["score"] = cls._serialise_value(
                    score,
                )

            if level is not None:
                item["level"] = cls._serialise_value(
                    level,
                )

            if priority is not None:
                item["priority"] = cls._serialise_value(
                    priority,
                )

            if item:
                risks.append(
                    item,
                )

        return ReportSection(
            title="Risk Summary",
            content={
                "risks": risks,
            },
        )

    # ------------------------------------------------------------------
    # Compatibility Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _object_to_dict(
        value: Any,
    ) -> dict[str, Any]:
        """
        Compatibility wrapper for report_helpers.object_to_dict().
        """

        return object_to_dict(
            value,
        )

    @staticmethod
    def _first_value(
        data: dict[str, Any],
        names: tuple[str, ...],
    ) -> Any:
        """
        Compatibility wrapper for report_helpers.first_value().
        """

        return first_value(
            data,
            names,
        )

    @staticmethod
    def _object_name(
        value: Any,
    ) -> Any:
        """
        Compatibility wrapper for report_helpers.object_name().
        """

        return object_name(
            value,
        )

    @staticmethod
    def _enum_value(
        value: Any,
    ) -> Any:
        """
        Compatibility wrapper for report_helpers.enum_value().
        """

        return enum_value(
            value,
        )

    @staticmethod
    def _serialise_value(
        value: Any,
    ) -> Any:
        """
        Compatibility wrapper for report_helpers.serialise_value().
        """

        return serialise_value(
            value,
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

    Existing callers can continue to use:

        generate_report(
            assessment,
            tenant="tenant-id",
        )

    without needing to know about the internal reporting modules.
    """

    generator = ReportGenerator()

    return generator.generate(
        assessment=assessment,
        tenant=tenant,
    )
