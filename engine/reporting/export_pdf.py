# engine\reporting\export_pdf.py

"""
PDF Report Exporter

Exports ReportDocument instances to PDF.

Supports the standard report structure produced by
engine.reporting.report_generator.

In addition to generic report content rendering, this exporter
provides a dedicated renderer for the standard:

    Live Control Evidence

section.

The control-evidence renderer consumes evidence already produced
by the assessment pipeline. It does not create or infer control
assessment results.
"""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .report_generator import ReportDocument


class PDFReportExporter:
    """
    Export ReportDocument instances to PDF.
    """

    # ------------------------------------------------------------------
    # PDF Layout Safety Limits
    # ------------------------------------------------------------------

    #
    # Generic list-of-dictionaries tables can contain a large number
    # of fields, particularly when live Microsoft Graph / Entra
    # evidence is present.
    #
    # Keeping the number of columns bounded prevents ReportLab from
    # attempting to construct extremely wide and unstable tables.
    #
    MAX_TABLE_COLUMNS = 8

    #
    # Long unbroken values can otherwise cause ReportLab Paragraph
    # layout calculations to produce pathological row heights.
    #
    # This does NOT truncate evidence. It only inserts invisible
    # soft-break opportunities into long runs.
    #
    SOFT_BREAK_INTERVAL = 80

    #
    # ReportLab Paragraph uses a small HTML-like markup language.
    # The exporter deliberately permits only the markup it creates
    # itself, primarily <b> and <br/>.
    #
    # This expression is used only as a final fallback when malformed
    # externally supplied markup reaches _safe_paragraph().
    #
    HTML_TAG_RE = re.compile(
        r"<[^>]*>"
    )

    def __init__(
        self,
        output_directory: Path,
    ) -> None:
        self.output_directory = output_directory

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ------------------------------------------------------------------
    # Public Export API
    # ------------------------------------------------------------------

    def export(
        self,
        report: ReportDocument,
        base_name: str,
    ) -> Path:
        """
        Export a report to PDF.
        """

        file = self.output_directory / f"{base_name}.pdf"

        document = SimpleDocTemplate(
            str(file),
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
            title=report.metadata.title,
            author="GRC Engineering Platform",
        )

        styles = getSampleStyleSheet()

        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["BodyText"],
            fontSize=9,
            leading=12,
            alignment=TA_LEFT,
        )

        table_header_style = ParagraphStyle(
            "ReportTableHeader",
            parent=body_style,
            fontName="Helvetica-Bold",
            textColor=colors.white,
        )

        control_header_style = ParagraphStyle(
            "ControlEvidenceHeader",
            parent=table_header_style,
            fontSize=8,
            leading=10,
        )

        control_body_style = ParagraphStyle(
            "ControlEvidenceBody",
            parent=body_style,
            fontSize=8,
            leading=10,
        )

        story: list[Any] = []

        # --------------------------------------------------------------
        # Title
        # --------------------------------------------------------------

        story.append(
            Paragraph(
                self._escape(report.metadata.title),
                styles["Title"],
            )
        )

        story.append(
            Spacer(
                1,
                12,
            )
        )

        # --------------------------------------------------------------
        # Metadata
        # --------------------------------------------------------------

        story.append(
            self._metadata_table(
                report,
                body_style,
            )
        )

        story.append(
            Spacer(
                1,
                18,
            )
        )

        # --------------------------------------------------------------
        # Report Sections
        # --------------------------------------------------------------

        for section in report.sections:

            story.append(
                Paragraph(
                    self._escape(section.title),
                    styles["Heading2"],
                )
            )

            story.append(
                Spacer(
                    1,
                    6,
                )
            )

            #
            # Dedicated renderer for the standard control evidence
            # section produced by ReportGenerator.
            #
            if self._is_control_evidence_section(
                section.title,
                section.content,
            ):
                story.extend(
                    self._build_control_evidence_content(
                        content=section.content,
                        body_style=control_body_style,
                        table_header_style=control_header_style,
                    )
                )

            else:
                #
                # Preserve the existing generic rendering behaviour
                # for every other report section.
                #
                story.extend(
                    self._build_content(
                        content=section.content,
                        body_style=body_style,
                        table_header_style=table_header_style,
                    )
                )

            story.append(
                Spacer(
                    1,
                    14,
                )
            )

        document.build(story)

        return file

    # ------------------------------------------------------------------
    # Metadata Table
    # ------------------------------------------------------------------

    @classmethod
    def _metadata_table(
        cls,
        report: ReportDocument,
        body_style: ParagraphStyle,
    ) -> Table:
        """
        Build the report metadata table.
        """

        rows = [
            [
                Paragraph(
                    "<b>Tenant</b>",
                    body_style,
                ),
                cls._safe_paragraph(
                    report.metadata.tenant,
                    body_style,
                ),
            ],
            [
                Paragraph(
                    "<b>Generated</b>",
                    body_style,
                ),
                cls._safe_paragraph(
                    str(report.metadata.generated_at),
                    body_style,
                ),
            ],
            [
                Paragraph(
                    "<b>Version</b>",
                    body_style,
                ),
                cls._safe_paragraph(
                    str(report.metadata.version),
                    body_style,
                ),
            ],
            [
                Paragraph(
                    "<b>Frameworks</b>",
                    body_style,
                ),
                cls._safe_paragraph(
                    ", ".join(
                        report.metadata.frameworks
                    ),
                    body_style,
                ),
            ],
        ]

        table = Table(
            rows,
            colWidths=[
                35 * mm,
                135 * mm,
            ],
            splitByRow=1,
            splitInRow=1,
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.lightgrey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        colors.HexColor("#EAF2F8"),
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                ]
            )
        )

        return table

    # ------------------------------------------------------------------
    # Control Evidence Detection
    # ------------------------------------------------------------------

    @staticmethod
    def _is_control_evidence_section(
        title: str,
        content: Any,
    ) -> bool:
        """
        Determine whether a report section uses the standard
        control-evidence structure.

        The preferred indicator is the section title generated by
        ReportGenerator:

            Live Control Evidence

        The content must also contain a controls collection.

        This prevents arbitrary sections from accidentally being
        rendered as control evidence.
        """

        if title.strip().lower() != "live control evidence":
            return False

        if not isinstance(
            content,
            dict,
        ):
            return False

        controls = content.get(
            "controls"
        )

        return isinstance(
            controls,
            list,
        )

    # ------------------------------------------------------------------
    # Control Evidence Content Builder
    # ------------------------------------------------------------------

    @classmethod
    def _build_control_evidence_content(
        cls,
        content: dict[str, Any],
        body_style: ParagraphStyle,
        table_header_style: ParagraphStyle,
    ) -> list[Any]:
        """
        Render the standard Live Control Evidence section.

        The standard representation comes from ReportGenerator:

            {
                "assessment_type": "...",
                "controls": [
                    {
                        "framework": "...",
                        "control_id": "...",
                        "title": "...",
                        "status": "...",
                        "evidence_source": "...",
                        "observed_evidence": [...]
                    }
                ]
            }

        Each control is rendered as a structured evidence table.

        No control status, score, or evidence is generated here.
        """

        flowables: list[Any] = []

        assessment_type = content.get(
            "assessment_type"
        )

        if assessment_type is not None:

            flowables.append(
                cls._safe_paragraph(
                    assessment_type,
                    body_style,
                )
            )

            flowables.append(
                Spacer(
                    1,
                    8,
                )
            )

        controls = content.get(
            "controls",
            [],
        )

        if not isinstance(
            controls,
            list,
        ):
            return flowables

        if not controls:

            flowables.append(
                cls._safe_paragraph(
                    "No control-level evidence was supplied by the assessment pipeline.",
                    body_style,
                )
            )

            return flowables

        rendered_controls = 0

        for control in controls:

            if not isinstance(
                control,
                dict,
            ):
                continue

            table = cls._build_control_evidence_table(
                control=control,
                body_style=body_style,
                table_header_style=table_header_style,
            )

            if table is not None:

                if rendered_controls > 0:
                    flowables.append(
                        Spacer(
                            1,
                            12,
                        )
                    )

                flowables.append(
                    table
                )

                rendered_controls += 1

        return flowables

    # ------------------------------------------------------------------
    # Control Evidence Table
    # ------------------------------------------------------------------

    @classmethod
    def _build_control_evidence_table(
        cls,
        control: dict[str, Any],
        body_style: ParagraphStyle,
        table_header_style: ParagraphStyle,
    ) -> Table | None:
        """
        Build the standard control-evidence table.

        The table presents the control in the following form:

            Framework | Control ID | Requirement | Status | Evidence Source
            ISO27001  | A.8.2     | ...         | PASS   | Microsoft Graph

            Score | Coverage | Assessment Reason

            Observed Evidence
            - 2 high-privilege roles
            - 2 assignments
            - Global Administrator -> user
            - User Administrator -> user

        This is deliberately a presentation concern. The values are
        taken directly from the normalized report content.
        """

        framework = control.get(
            "framework"
        )

        control_id = control.get(
            "control_id"
        )

        title = control.get(
            "title"
        )

        status = control.get(
            "status"
        )

        evidence_source = control.get(
            "evidence_source"
        )

        score = control.get(
            "score"
        )

        coverage = control.get(
            "coverage"
        )

        reason = control.get(
            "reason"
        )

        observed_evidence = control.get(
            "observed_evidence",
            [],
        )

        if not isinstance(
            observed_evidence,
            list,
        ):
            observed_evidence = [
                observed_evidence
            ]

        #
        # Primary control identity/evaluation table.
        #
        rows: list[list[Any]] = [
            [
                Paragraph(
                    "Framework",
                    table_header_style,
                ),
                Paragraph(
                    "Control ID",
                    table_header_style,
                ),
                Paragraph(
                    "Requirement",
                    table_header_style,
                ),
                Paragraph(
                    "Status",
                    table_header_style,
                ),
                Paragraph(
                    "Evidence Source",
                    table_header_style,
                ),
            ],
            [
                cls._safe_paragraph(
                    framework,
                    body_style,
                ),
                cls._safe_paragraph(
                    control_id,
                    body_style,
                ),
                cls._safe_paragraph(
                    title,
                    body_style,
                ),
                cls._safe_paragraph(
                    status,
                    cls._status_style(
                        status,
                        body_style,
                    ),
                ),
                cls._safe_paragraph(
                    evidence_source,
                    body_style,
                ),
            ],
        ]

        #
        # Add score and coverage when supplied by the real
        # assessment pipeline.
        #
        score_section_present = (
            score is not None
            or coverage is not None
            or reason is not None
        )

        score_header_row: int | None = None
        score_value_row: int | None = None

        if score_section_present:

            score_header_row = len(rows)

            rows.append(
                [
                    Paragraph(
                        "Score",
                        table_header_style,
                    ),
                    Paragraph(
                        "Coverage",
                        table_header_style,
                    ),
                    Paragraph(
                        "Assessment Reason",
                        table_header_style,
                    ),
                    Paragraph(
                        "",
                        table_header_style,
                    ),
                    Paragraph(
                        "",
                        table_header_style,
                    ),
                ]
            )

            score_value_row = len(rows)

            rows.append(
                [
                    cls._safe_paragraph(
                        score,
                        body_style,
                    ),
                    cls._safe_paragraph(
                        coverage,
                        body_style,
                    ),
                    cls._safe_paragraph(
                        reason,
                        body_style,
                    ),
                    Paragraph(
                        "",
                        body_style,
                    ),
                    Paragraph(
                        "",
                        body_style,
                    ),
                ]
            )

        #
        # Observed evidence is deliberately rendered separately from
        # the control metadata so the reader can clearly see what was
        # actually observed.
        #
        observed_header_row = len(rows)

        rows.append(
            [
                Paragraph(
                    "Observed Evidence",
                    table_header_style,
                ),
                Paragraph(
                    "",
                    table_header_style,
                ),
                Paragraph(
                    "",
                    table_header_style,
                ),
                Paragraph(
                    "",
                    table_header_style,
                ),
                Paragraph(
                    "",
                    table_header_style,
                ),
            ]
        )

        if observed_evidence:

            evidence_flowables = (
                cls._format_observed_evidence_flowables(
                    observed_evidence,
                    body_style,
                )
            )

        else:

            evidence_flowables = [
                cls._safe_paragraph(
                    "No observed evidence was supplied "
                    "by the assessment pipeline.",
                    body_style,
                )
            ]

        observed_value_row = len(rows)

        #
        # A table cell can contain a list of flowables. Using multiple
        # Paragraphs rather than one enormous Paragraph allows
        # ReportLab to split the content safely across pages.
        #
        rows.append(
            [
                evidence_flowables,
                [],
                [],
                [],
                [],
            ]
        )

        table = Table(
            rows,
            colWidths=[
                28 * mm,
                24 * mm,
                38 * mm,
                20 * mm,
                60 * mm,
            ],
            repeatRows=1,
            splitByRow=1,
            splitInRow=1,
        )

        #
        # Base styling.
        #
        style_commands: list[tuple[Any, ...]] = [
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1F4E78"),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#B7C9D6"),
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP",
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5,
            ),
            (
                "BACKGROUND",
                (0, 1),
                (-1, 1),
                colors.white,
            ),
        ]

        #
        # Score / coverage / reason section.
        #
        if (
            score_header_row is not None
            and score_value_row is not None
        ):

            style_commands.extend(
                [
                    (
                        "BACKGROUND",
                        (0, score_header_row),
                        (-1, score_header_row),
                        colors.HexColor("#5B9BD5"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, score_header_row),
                        (-1, score_header_row),
                        colors.white,
                    ),
                    (
                        "BACKGROUND",
                        (0, score_value_row),
                        (-1, score_value_row),
                        colors.white,
                    ),
                    #
                    # Assessment Reason occupies the remaining three
                    # columns so the reason is readable without
                    # creating another unrelated table.
                    #
                    (
                        "SPAN",
                        (2, score_header_row),
                        (4, score_header_row),
                    ),
                    (
                        "SPAN",
                        (2, score_value_row),
                        (4, score_value_row),
                    ),
                ]
            )

        #
        # Merge the observed-evidence rows across the full table.
        #
        style_commands.extend(
            [
                (
                    "SPAN",
                    (0, observed_header_row),
                    (-1, observed_header_row),
                ),
                (
                    "SPAN",
                    (0, observed_value_row),
                    (-1, observed_value_row),
                ),
                (
                    "BACKGROUND",
                    (0, observed_header_row),
                    (-1, observed_header_row),
                    colors.HexColor("#5B9BD5"),
                ),
                (
                    "TEXTCOLOR",
                    (0, observed_header_row),
                    (-1, observed_header_row),
                    colors.white,
                ),
                (
                    "BACKGROUND",
                    (0, observed_value_row),
                    (-1, observed_value_row),
                    colors.HexColor("#F4F7F9"),
                ),
            ]
        )

        #
        # Highlight PASS / FAIL without changing the underlying
        # assessment result.
        #
        status_value = str(
            status
        ).upper()

        if status_value == "PASS":

            style_commands.append(
                (
                    "BACKGROUND",
                    (3, 1),
                    (3, 1),
                    colors.HexColor("#E2F0D9"),
                )
            )

            style_commands.append(
                (
                    "TEXTCOLOR",
                    (3, 1),
                    (3, 1),
                    colors.HexColor("#006100"),
                )
            )

        elif status_value in {
            "FAIL",
            "FAILED",
        }:

            style_commands.append(
                (
                    "BACKGROUND",
                    (3, 1),
                    (3, 1),
                    colors.HexColor("#FCE4D6"),
                )
            )

            style_commands.append(
                (
                    "TEXTCOLOR",
                    (3, 1),
                    (3, 1),
                    colors.HexColor("#9C0006"),
                )
            )

        table.setStyle(
            TableStyle(
                style_commands
            )
        )

        return table

    # ------------------------------------------------------------------
    # Observed Evidence Formatting
    # ------------------------------------------------------------------

    @classmethod
    def _format_observed_evidence(
        cls,
        evidence: list[Any],
    ) -> str:
        """
        Convert observed evidence into readable PDF text.

        Simple values become bullet points.

        Dictionary evidence is rendered as key/value observations.

        Nested lists and dictionaries are converted recursively.

        The method does not discard the supplied evidence.

        This method is retained for compatibility with the existing
        renderer and any callers that use it directly. The control
        evidence PDF renderer uses _format_observed_evidence_flowables()
        to allow ReportLab to split large evidence across pages.
        """

        lines: list[str] = []

        for item in evidence:

            if isinstance(
                item,
                dict,
            ):

                dictionary_lines: list[str] = []

                for key, value in item.items():

                    #
                    # Keep dictionary evidence readable while
                    # preserving the actual supplied values.
                    #
                    display_value = cls._display_value(
                        value
                    )

                    dictionary_lines.append(
                        (
                            f"<b>{cls._escape(cls._format_key(str(key)))}</b>: "
                            f"{cls._escape(display_value)}"
                        )
                    )

                if dictionary_lines:

                    lines.append(
                        "• "
                        + "<br/>".join(
                            dictionary_lines
                        )
                    )

                continue

            if isinstance(
                item,
                (list, tuple, set),
            ):

                nested = cls._format_observed_evidence(
                    list(item)
                )

                if nested:
                    lines.append(
                        nested
                    )

                continue

            lines.append(
                "• "
                + cls._escape(
                    cls._display_value(item)
                )
            )

        if not lines:
            return ""

        return "<br/>".join(
            lines
        )

    # ------------------------------------------------------------------
    # Observed Evidence Flowables
    # ------------------------------------------------------------------

    @classmethod
    def _format_observed_evidence_flowables(
        cls,
        evidence: list[Any],
        body_style: ParagraphStyle,
    ) -> list[Paragraph]:
        """
        Convert observed evidence into multiple ReportLab Paragraph
        flowables.

        This is intentionally separate from
        _format_observed_evidence().

        The original method produces one HTML string, which is useful
        for compatibility but can become a single enormous Paragraph
        when large live evidence collections are supplied.

        Returning separate Paragraphs allows ReportLab to split the
        evidence row across pages instead of calculating one
        pathological cell height.
        """

        flowables: list[Paragraph] = []

        for item in evidence:

            if isinstance(
                item,
                dict,
            ):

                for key, value in item.items():

                    label = cls._escape(
                        cls._format_key(
                            str(key)
                        )
                    )

                    display_value = cls._escape(
                        cls._display_value(
                            value
                        )
                    )

                    flowables.append(
                        cls._safe_paragraph(
                            f"<b>{label}:</b> {display_value}",
                            body_style,
                            assume_html=True,
                        )
                    )

                continue

            if isinstance(
                item,
                (list, tuple, set),
            ):

                flowables.extend(
                    cls._format_observed_evidence_flowables(
                        list(item),
                        body_style,
                    )
                )

                continue

            flowables.append(
                cls._safe_paragraph(
                    "• "
                    + cls._display_value(item),
                    body_style,
                )
            )

        if not flowables:

            flowables.append(
                cls._safe_paragraph(
                    "No observed evidence was supplied "
                    "by the assessment pipeline.",
                    body_style,
                )
            )

        return flowables

    # ------------------------------------------------------------------
    # Status Style
    # ------------------------------------------------------------------

    @staticmethod
    def _status_style(
        status: Any,
        body_style: ParagraphStyle,
    ) -> ParagraphStyle:
        """
        Return a status-specific paragraph style.

        This is presentation-only. The assessment status itself is
        never modified.
        """

        status_value = str(
            status
        ).upper()

        if status_value == "PASS":

            return ParagraphStyle(
                "ControlPass",
                parent=body_style,
                textColor=colors.HexColor(
                    "#006100"
                ),
                fontName="Helvetica-Bold",
            )

        if status_value in {
            "FAIL",
            "FAILED",
        }:

            return ParagraphStyle(
                "ControlFail",
                parent=body_style,
                textColor=colors.HexColor(
                    "#9C0006"
                ),
                fontName="Helvetica-Bold",
            )

        return body_style

    # ------------------------------------------------------------------
    # Generic PDF Content Builder
    # ------------------------------------------------------------------

    @classmethod
    def _build_content(
        cls,
        content: Any,
        body_style: ParagraphStyle,
        table_header_style: ParagraphStyle,
    ) -> list[Any]:
        """
        Convert structured report content into ReportLab flowables.

        Supports:

        - dictionaries
        - lists of dictionaries
        - lists of simple values
        - scalar values

        This is the existing generic renderer. Control evidence is
        handled separately by _build_control_evidence_content().
        """

        flowables: list[Any] = []

        # --------------------------------------------------------------
        # Dictionary
        # --------------------------------------------------------------

        if isinstance(
            content,
            dict,
        ):

            simple_items: list[tuple[str, Any]] = []

            complex_items: list[tuple[str, Any]] = []

            for key, value in content.items():

                if cls._is_simple_value(
                    value
                ):
                    simple_items.append(
                        (
                            str(key),
                            value,
                        )
                    )
                else:
                    complex_items.append(
                        (
                            str(key),
                            value,
                        )
                    )

            # ----------------------------------------------------------
            # Simple dictionary values
            # ----------------------------------------------------------

            if simple_items:

                rows = [
                    [
                        Paragraph(
                            "Metric",
                            table_header_style,
                        ),
                        Paragraph(
                            "Value",
                            table_header_style,
                        ),
                    ]
                ]

                for key, value in simple_items:

                    rows.append(
                        [
                            cls._safe_paragraph(
                                cls._format_key(
                                    key
                                ),
                                body_style,
                            ),
                            cls._safe_paragraph(
                                value,
                                body_style,
                            ),
                        ]
                    )

                table = Table(
                    rows,
                    colWidths=[
                        65 * mm,
                        105 * mm,
                    ],
                    repeatRows=1,
                    splitByRow=1,
                    splitInRow=1,
                )

                table.setStyle(
                    cls._table_style()
                )

                flowables.append(
                    table
                )

                flowables.append(
                    Spacer(
                        1,
                        8,
                    )
                )

            # ----------------------------------------------------------
            # Nested dictionary/list values
            # ----------------------------------------------------------

            for key, value in complex_items:

                flowables.append(
                    cls._safe_paragraph(
                        cls._format_key(
                            key
                        ),
                        body_style,
                    )
                )

                flowables.append(
                    Spacer(
                        1,
                        4,
                    )
                )

                flowables.extend(
                    cls._build_content(
                        content=value,
                        body_style=body_style,
                        table_header_style=table_header_style,
                    )
                )

                flowables.append(
                    Spacer(
                        1,
                        8,
                    )
                )

            return flowables

        # --------------------------------------------------------------
        # List
        # --------------------------------------------------------------

        if isinstance(
            content,
            list,
        ):

            if not content:

                flowables.append(
                    cls._safe_paragraph(
                        "No records",
                        body_style,
                    )
                )

                return flowables

            # ----------------------------------------------------------
            # List of dictionaries
            # ----------------------------------------------------------

            if all(
                isinstance(
                    item,
                    dict,
                )
                for item in content
            ):

                #
                # Preserve the existing list-of-dictionaries
                # functionality, but render wide datasets as multiple
                # manageable tables instead of creating a pathological
                # 20+ column ReportLab table.
                #
                flowables.extend(
                    cls._build_dictionary_list_tables(
                        content=content,
                        body_style=body_style,
                        table_header_style=table_header_style,
                    )
                )

                return flowables

            # ----------------------------------------------------------
            # List of simple values
            # ----------------------------------------------------------

            rows = [
                [
                    Paragraph(
                        "Value",
                        table_header_style,
                    )
                ]
            ]

            for item in content:

                rows.append(
                    [
                        cls._safe_paragraph(
                            item,
                            body_style,
                        )
                    ]
                )

            table = Table(
                rows,
                colWidths=[
                    170 * mm
                ],
                repeatRows=1,
                splitByRow=1,
                splitInRow=1,
            )

            table.setStyle(
                cls._table_style()
            )

            flowables.append(
                table
            )

            return flowables

        # --------------------------------------------------------------
        # Scalar
        # --------------------------------------------------------------

        flowables.append(
            cls._safe_paragraph(
                content,
                body_style,
            )
        )

        return flowables

    # ------------------------------------------------------------------
    # Generic Dictionary List Tables
    # ------------------------------------------------------------------

    @classmethod
    def _build_dictionary_list_tables(
        cls,
        content: list[dict[str, Any]],
        body_style: ParagraphStyle,
        table_header_style: ParagraphStyle,
    ) -> list[Any]:
        """
        Render a list of dictionaries as one or more manageable PDF
        tables.

        The previous implementation created one table containing every
        discovered key. Live Microsoft Entra / Microsoft Graph records
        can contain many fields, resulting in tables such as:

            950 rows x 24 columns

        That layout is technically valid data, but it is not a safe
        PDF representation.

        The evidence itself is not discarded. Columns are simply
        partitioned into groups so ReportLab can lay out each table
        reliably.
        """

        keys: list[str] = []

        for item in content:

            for key in item:

                key_string = str(
                    key
                )

                if key_string not in keys:
                    keys.append(
                        key_string
                    )

        if not keys:

            return [
                cls._safe_paragraph(
                    "No records",
                    body_style,
                )
            ]

        flowables: list[Any] = []

        #
        # Partition columns into manageable groups.
        #
        for start in range(
            0,
            len(keys),
            cls.MAX_TABLE_COLUMNS,
        ):

            column_keys = keys[
                start:start + cls.MAX_TABLE_COLUMNS
            ]

            rows: list[list[Any]] = [
                [
                    Paragraph(
                        cls._format_key(
                            key
                        ),
                        table_header_style,
                    )
                    for key in column_keys
                ]
            ]

            for item in content:

                rows.append(
                    [
                        cls._safe_paragraph(
                            item.get(key),
                            body_style,
                        )
                        for key in column_keys
                    ]
                )

            column_width = (
                170 * mm
            ) / max(
                len(column_keys),
                1,
            )

            table = Table(
                rows,
                colWidths=[
                    column_width
                    for _ in column_keys
                ],
                repeatRows=1,
                splitByRow=1,
                splitInRow=1,
            )

            table.setStyle(
                cls._table_style()
            )

            flowables.append(
                table
            )

            #
            # Separate each column group visually while preserving
            # the complete dataset.
            #
            if (
                start + cls.MAX_TABLE_COLUMNS
                < len(keys)
            ):

                flowables.append(
                    Spacer(
                        1,
                        10,
                    )
                )

        return flowables

    # ------------------------------------------------------------------
    # Table Styling
    # ------------------------------------------------------------------

    @staticmethod
    def _table_style() -> TableStyle:
        """
        Consistent styling for PDF tables.
        """

        return TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1F4E78"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#B7C9D6"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#F4F7F9"),
                    ],
                ),
            ]
        )

    # ------------------------------------------------------------------
    # Value Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_simple_value(
        value: Any,
    ) -> bool:
        """
        Determine whether a value can be displayed directly.
        """

        return value is None or isinstance(
            value,
            (
                str,
                int,
                float,
                bool,
            ),
        )

    @staticmethod
    def _format_key(
        key: str,
    ) -> str:
        """
        Convert snake_case keys into readable labels.
        """

        return (
            str(key)
            .replace(
                "_",
                " ",
            )
            .title()
        )

    @staticmethod
    def _display_value(
        value: Any,
    ) -> str:
        """
        Convert Python values into readable PDF text.

        Existing scalar, dictionary, and collection display semantics
        are preserved.
        """

        if value is None:
            return ""

        if isinstance(
            value,
            bool,
        ):
            return "Yes" if value else "No"

        if isinstance(
            value,
            float,
        ):
            if 0 <= value <= 1:
                return f"{value * 100:.0f}%"

        if isinstance(
            value,
            dict,
        ):
            parts: list[str] = []

            for key, item in value.items():
                parts.append(
                    f"{key}: {item}"
                )

            return "; ".join(parts)

        if isinstance(
            value,
            (list, tuple, set),
        ):
            return ", ".join(
                str(item)
                for item in value
            )

        return str(value)

    # ------------------------------------------------------------------
    # Safe Paragraph Construction
    # ------------------------------------------------------------------

    @classmethod
    def _safe_paragraph(
        cls,
        value: Any,
        style: ParagraphStyle,
        assume_html: bool = False,
    ) -> Paragraph:
        """
        Create a ReportLab Paragraph safely.

        The method does not truncate or discard supplied evidence.

        Ordinary values are HTML-escaped before being passed to
        ReportLab.

        Marked-up values generated internally by the exporter are
        accepted when assume_html=True.

        If malformed ReportLab markup is encountered, the method
        automatically falls back to escaped plain text rather than
        allowing the entire PDF export to fail.

        This is important for live Microsoft Graph / Entra evidence,
        because externally sourced values can contain characters such
        as '<', '>', '&', serialized objects, URLs, or other text that
        ReportLab's Paragraph parser may interpret as markup.
        """

        if assume_html:

            text = cls._prepare_html_for_pdf(
                str(value)
            )

            try:
                return Paragraph(
                    text,
                    style,
                )

            except (
                ValueError,
                TypeError,
            ):
                #
                # The caller supplied markup, but ReportLab rejected
                # it. Do not allow malformed evidence markup to abort
                # the complete PDF export.
                #
                fallback_text = cls._html_to_plain_text(
                    str(value)
                )

                return Paragraph(
                    cls._prepare_text_for_pdf(
                        fallback_text
                    ),
                    style,
                )

        text = cls._prepare_text_for_pdf(
            cls._display_value(value)
        )

        try:
            return Paragraph(
                text,
                style,
            )

        except (
            ValueError,
            TypeError,
        ):
            #
            # _prepare_text_for_pdf() already escapes ordinary text,
            # so this is an additional defensive fallback for unusual
            # values or ReportLab parser behaviour.
            #
            fallback_text = html.escape(
                str(
                    cls._display_value(
                        value
                    )
                ),
                quote=False,
            )

            return Paragraph(
                cls._insert_soft_breaks(
                    fallback_text
                ),
                style,
            )

    @classmethod
    def _prepare_text_for_pdf(
        cls,
        value: str,
    ) -> str:
        """
        Escape ordinary text and add invisible soft-break
        opportunities to long runs.
        """

        escaped = cls._escape(
            value
        )

        return cls._insert_soft_breaks(
            escaped
        )

    @classmethod
    def _prepare_html_for_pdf(
        cls,
        value: str,
    ) -> str:
        """
        Prepare already-marked-up Paragraph content.

        Existing ReportLab HTML-style markup is preserved.

        Soft-break opportunities are inserted only into text outside
        markup tags. This prevents zero-width spaces from being
        inserted into tags such as:

            <b>
            </b>
            <br/>

        which could otherwise corrupt valid markup and cause
        ReportLab's parser to report unclosed tags.
        """

        if not value:
            return ""

        output: list[str] = []

        #
        # Split the input into HTML tags and ordinary text.
        #
        # Only ordinary text receives soft-break opportunities.
        #
        parts = re.split(
            r"(<[^>]*>)",
            value,
        )

        for part in parts:

            if not part:
                continue

            if (
                part.startswith("<")
                and part.endswith(">")
            ):
                #
                # Preserve ReportLab markup exactly as supplied.
                #
                output.append(
                    part
                )

            else:

                output.append(
                    cls._insert_soft_breaks(
                        part
                    )
                )

        return "".join(
            output
        )

    @classmethod
    def _html_to_plain_text(
        cls,
        value: str,
    ) -> str:
        """
        Convert malformed/unsupported Paragraph markup into plain
        text for the final safe fallback.

        This method does not intentionally discard evidence content.
        It removes only markup syntax that ReportLab cannot safely
        parse and converts the remaining HTML entities back into their
        visible text representation.
        """

        text = cls.HTML_TAG_RE.sub(
            "",
            value,
        )

        text = text.replace(
            "<br/>",
            "\n",
        )

        text = text.replace(
            "<br>",
            "\n",
        )

        text = text.replace(
            "<br />",
            "\n",
        )

        return html.unescape(
            text
        )

    @classmethod
    def _insert_soft_breaks(
        cls,
        value: str,
    ) -> str:
        """
        Add zero-width spaces to long runs of characters.

        The zero-width space is invisible in the resulting PDF but
        gives ReportLab a safe opportunity to wrap long machine-
        generated values.

        Existing newlines and normal whitespace remain untouched.
        """

        interval = cls.SOFT_BREAK_INTERVAL

        if interval <= 0:
            return value

        output: list[str] = []

        run: list[str] = []

        def flush_run() -> None:
            if not run:
                return

            text = "".join(
                run
            )

            #
            # Only add soft breaks to genuinely long runs.
            #
            if len(text) > interval:

                chunks = [
                    text[index:index + interval]
                    for index in range(
                        0,
                        len(text),
                        interval,
                    )
                ]

                output.append(
                    "\u200b".join(
                        chunks
                    )
                )

            else:

                output.append(
                    text
                )

            run.clear()

        for character in value:

            if character.isspace():

                flush_run()
                output.append(
                    character
                )

            else:

                run.append(
                    character
                )

        flush_run()

        return "".join(
            output
        )

    # ------------------------------------------------------------------
    # HTML Escaping
    # ------------------------------------------------------------------

    @staticmethod
    def _escape(
        value: str,
    ) -> str:
        """
        Escape text before inserting it into ReportLab Paragraphs.
        """

        return html.escape(
            str(value)
        )
