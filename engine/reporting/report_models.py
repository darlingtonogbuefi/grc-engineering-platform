# engine/reporting/report_models.py

"""
Reporting Models

Defines the structured report representation used by the reporting layer.

The models in this module are framework-agnostic. They support:

- ISO 27001
- SOC 2
- CAF
- Cyber Essentials
- GovAssure
- and future frameworks

The models represent report data only. They do not calculate scores,
determine compliance, or invent assessment results.

This module also preserves the original ReportSection and ReportDocument
models used by the existing reporting API.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# ==============================================================================
# Requirement Report
# ==============================================================================


@dataclass(slots=True)
class RequirementReport:
    """
    Report representation of a single framework requirement/control.

    The reporting layer consumes the result produced by the assessment
    pipeline. It does not determine whether a requirement is met.
    """

    requirement_id: str

    title: str | None = None

    status: str | None = None
    confidence: str | None = None
    score: float | None = None

    finding: str | None = None

    evidence: list[Any] = field(default_factory=list)


# ==============================================================================
# Framework Report
# ==============================================================================


@dataclass(slots=True)
class FrameworkReport:
    """
    Complete report representation for one framework.

    The same model is used for ISO 27001, SOC 2, CAF,
    Cyber Essentials, GovAssure, and future frameworks.

    A single assessment can therefore contain multiple FrameworkReport
    instances without requiring framework-specific report classes.
    """

    framework: str

    version: str | None = None

    score: float | None = None
    status: str | None = None

    total_requirements: int = 0

    met: int = 0

    partially_met: int = 0

    not_met: int = 0

    not_applicable: int = 0

    requirements: list[RequirementReport] = field(default_factory=list)


# ==============================================================================
# Executive Summary
# ==============================================================================


@dataclass(slots=True)
class ExecutiveSummary:
    """
    Executive-level assessment summary.

    Values are supplied by the assessment/scoring pipeline.
    The reporting layer does not calculate compliance values.
    """

    overall_compliance: float | None = None

    controls_assessed: int = 0

    evidence_items_used: int = 0

    high_risk_gaps: int = 0

    narrative: str | None = None


# ==============================================================================
# Report Metadata
# ==============================================================================


@dataclass(slots=True)
class ReportMetadata:
    """
    Metadata describing the generated assessment report.

    ``generated_at`` is retained for compatibility with the original
    ReportGenerator implementation.

    ``assessment_date`` is optional so existing callers that only provide
    generated_at continue to work while newer report formats can expose
    a dedicated assessment date.
    """

    title: str

    tenant: str

    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    frameworks: list[str] = field(default_factory=list)

    version: str = "1.0"

    assessment_date: str | None = None


# ==============================================================================
# Report Section
# ==============================================================================


@dataclass(slots=True)
class ReportSection:
    """
    Individual report section.

    This is retained from the original reporting implementation so
    existing consumers of ReportDocument continue to work.

    The content remains intentionally generic because different report
    sections contain different structures.
    """

    title: str

    content: dict[str, Any]


# ==============================================================================
# Report Document
# ==============================================================================


@dataclass(slots=True)
class ReportDocument:
    """
    Complete legacy-compatible report document.

    The existing ReportGenerator produces this representation.

    Sections can contain:

    - Executive Summary
    - Evidence Summary
    - Live Control Evidence
    - Framework Summary
    - Capability Summary
    - Risk Summary

    The structured FrameworkReport and RequirementReport models above
    provide a stronger representation for framework-oriented exporters
    without breaking the existing ReportDocument API.
    """

    metadata: ReportMetadata

    sections: list[ReportSection] = field(default_factory=list)


# ==============================================================================
# Complete Assessment Report
# ==============================================================================


@dataclass(slots=True)
class AssessmentReport:
    """
    Structured assessment report.

    This representation is intended for framework-oriented reporting
    and future exporters.

    A single assessment can contain any number of frameworks:

        ISO 27001
        SOC 2
        CAF
        Cyber Essentials
        GovAssure
        etc.
    """

    metadata: ReportMetadata

    executive_summary: ExecutiveSummary

    frameworks: list[FrameworkReport] = field(default_factory=list)
