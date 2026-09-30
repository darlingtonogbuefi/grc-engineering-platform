# engine\reporting\export_excel.py

"""
Excel Report Exporter

Exports ReportDocument instances to Excel.

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

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from .report_generator import ReportDocument


class ExcelReportExporter:
    """
    Export ReportDocument instances to Excel.

    Generic report sections retain the existing rendering behaviour.

    The standard "Live Control Evidence" section receives a dedicated
    worksheet renderer so that every report containing control evidence
    automatically gets a structured control-evidence table.
    """

    def __init__(self, output_directory: Path) -> None:
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
        Export a ReportDocument to Excel.

        Every report section is still exported to its own worksheet.

        The standard "Live Control Evidence" section is rendered using
        the dedicated control-evidence renderer. All other sections
        continue through the existing generic renderer.
        """

        file = self.output_directory / f"{base_name}.xlsx"

        workbook = Workbook()

        summary_sheet = workbook.active

        if summary_sheet is None:
            raise RuntimeError(
                "Failed to create the Excel Summary worksheet."
            )

        summary_sheet.title = "Summary"

        header_fill = PatternFill(
            fill_type="solid",
            fgColor="1F4E78",
        )

        section_fill = PatternFill(
            fill_type="solid",
            fgColor="D9EAF7",
        )

        control_header_fill = PatternFill(
            fill_type="solid",
            fgColor="1F4E78",
        )

        control_subheader_fill = PatternFill(
            fill_type="solid",
            fgColor="5B9BD5",
        )

        pass_fill = PatternFill(
            fill_type="solid",
            fgColor="E2F0D9",
        )

        fail_fill = PatternFill(
            fill_type="solid",
            fgColor="FCE4D6",
        )

        header_font = Font(
            bold=True,
            color="FFFFFF",
        )

        bold_font = Font(
            bold=True,
        )

        self._write_summary(
            sheet=summary_sheet,
            report=report,
            bold_font=bold_font,
        )

        for section in report.sections:
            sheet_name = self._sheet_name(
                section.title,
                workbook.sheetnames,
            )

            sheet = workbook.create_sheet(
                sheet_name
            )

            sheet["A1"] = section.title
            sheet["A1"].font = Font(
                bold=True,
                size=14,
                color="FFFFFF",
            )
            sheet["A1"].fill = header_fill

            sheet.merge_cells(
                start_row=1,
                start_column=1,
                end_row=1,
                end_column=5,
            )

            #
            # Dedicated renderer for the standard control evidence
            # section produced by ReportGenerator.
            #
            if self._is_control_evidence_section(
                title=section.title,
                content=section.content,
            ):
                self._write_control_evidence_content(
                    sheet=sheet,
                    content=section.content,
                    header_fill=control_header_fill,
                    header_font=header_font,
                    subheader_fill=control_subheader_fill,
                    pass_fill=pass_fill,
                    fail_fill=fail_fill,
                )

            else:
                #
                # Preserve the existing generic rendering behaviour
                # for every other report section.
                #
                self._write_content(
                    sheet=sheet,
                    content=section.content,
                    start_row=3,
                    header_fill=header_fill,
                    header_font=header_font,
                    section_fill=section_fill,
                )

            sheet.freeze_panes = "A3"

            for column in (
                "A",
                "B",
                "C",
                "D",
                "E",
            ):
                sheet.column_dimensions[
                    column
                ].width = 24

        workbook.save(file)

        return file

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    @staticmethod
    def _write_summary(
        sheet: Any,
        report: ReportDocument,
        bold_font: Font,
    ) -> None:
        """
        Write the report metadata summary worksheet.

        Existing summary behaviour is preserved.
        """

        rows = [
            (
                "Report",
                report.metadata.title,
            ),
            (
                "Tenant",
                report.metadata.tenant,
            ),
            (
                "Generated",
                str(
                    report.metadata.generated_at
                ),
            ),
            (
                "Version",
                str(
                    report.metadata.version
                ),
            ),
            (
                "Frameworks",
                ", ".join(
                    report.metadata.frameworks
                ),
            ),
        ]

        for row_number, (
            label,
            value,
        ) in enumerate(
            rows,
            start=1,
        ):
            sheet.cell(
                row=row_number,
                column=1,
                value=label,
            ).font = bold_font

            sheet.cell(
                row=row_number,
                column=2,
                value=value,
            )

        sheet.column_dimensions[
            "A"
        ].width = 24

        sheet.column_dimensions[
            "B"
        ].width = 80

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
    # Control Evidence Content
    # ------------------------------------------------------------------

    @classmethod
    def _write_control_evidence_content(
        cls,
        sheet: Worksheet,
        content: dict[str, Any],
        header_fill: PatternFill,
        header_font: Font,
        subheader_fill: PatternFill,
        pass_fill: PatternFill,
        fail_fill: PatternFill,
    ) -> int:
        """
        Render the standard Live Control Evidence section.

        The expected structure comes from ReportGenerator:

            {
                "assessment_type": "...",
                "controls": [
                    {
                        "framework": "ISO27001",
                        "control_id": "A.8.2",
                        "title": "Privileged access rights",
                        "status": "PASS",
                        "evidence_source": "Microsoft Entra ID / Microsoft Graph",
                        "observed_evidence": [
                            "2 high-privilege roles",
                            "2 assignments",
                            "Global Administrator -> user",
                            "User Administrator -> user"
                        ]
                    }
                ]
            }

        The values are consumed from the assessment pipeline and are
        not generated by this exporter.
        """

        row = 3

        assessment_type = content.get(
            "assessment_type"
        )

        if assessment_type is not None:
            sheet.cell(
                row=row,
                column=1,
                value="Assessment Type",
            ).fill = subheader_fill

            sheet.cell(
                row=row,
                column=1,
            ).font = header_font

            sheet.cell(
                row=row,
                column=2,
                value=cls._excel_value(
                    assessment_type
                ),
            )

            row += 2

        controls = content.get(
            "controls",
            [],
        )

        if not isinstance(
            controls,
            list,
        ):
            return row

        if not controls:
            sheet.cell(
                row=row,
                column=1,
                value=(
                    "No control-level evidence was "
                    "supplied by the assessment pipeline."
                ),
            )

            return row + 1

        for index, control in enumerate(
            controls
        ):
            if not isinstance(
                control,
                dict,
            ):
                continue

            row = cls._write_control_evidence_table(
                sheet=sheet,
                control=control,
                start_row=row,
                header_fill=header_fill,
                header_font=header_font,
                subheader_fill=subheader_fill,
                pass_fill=pass_fill,
                fail_fill=fail_fill,
            )

            if index < len(controls) - 1:
                row += 2

        return row

    # ------------------------------------------------------------------
    # Control Evidence Table
    # ------------------------------------------------------------------

    @classmethod
    def _write_control_evidence_table(
        cls,
        sheet: Worksheet,
        control: dict[str, Any],
        start_row: int,
        header_fill: PatternFill,
        header_font: Font,
        subheader_fill: PatternFill,
        pass_fill: PatternFill,
        fail_fill: PatternFill,
    ) -> int:
        """
        Render one normalized control-evidence record.

        Standard fields:

        - framework
        - control_id
        - title
        - status
        - evidence_source
        - observed_evidence

        Optional assessment fields are also preserved:

        - score
        - coverage
        - reason

        Additional evidence-related fields are not discarded. They
        are rendered after the standard fields where supplied.
        """

        row = start_row

        #
        # Control fields supplied by the assessment pipeline.
        #
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
        # --------------------------------------------------------------
        # Primary control information
        # --------------------------------------------------------------
        #

        headers = [
            "Framework",
            "Control ID",
            "Requirement",
            "Status",
            "Evidence Source",
        ]

        for column, header in enumerate(
            headers,
            start=1,
        ):
            cell = sheet.cell(
                row=row,
                column=column,
                value=header,
            )

            cell.fill = header_fill
            cell.font = header_font

        row += 1

        values = [
            framework,
            control_id,
            title,
            status,
            evidence_source,
        ]

        for column, value in enumerate(
            values,
            start=1,
        ):
            cell = sheet.cell(
                row=row,
                column=column,
                value=cls._excel_value(
                    value
                ),
            )

            if column == 4:
                cls._apply_status_style(
                    cell=cell,
                    status=status,
                    pass_fill=pass_fill,
                    fail_fill=fail_fill,
                )

        row += 2

        #
        # --------------------------------------------------------------
        # Optional assessment details
        # --------------------------------------------------------------
        #

        if score is not None or coverage is not None:

            assessment_headers = [
                "Score",
                "Coverage",
                "Assessment Reason",
            ]

            for column, header in enumerate(
                assessment_headers,
                start=1,
            ):
                cell = sheet.cell(
                    row=row,
                    column=column,
                    value=header,
                )

                cell.fill = subheader_fill
                cell.font = header_font

            row += 1

            assessment_values = [
                score,
                coverage,
                reason,
            ]

            for column, value in enumerate(
                assessment_values,
                start=1,
            ):
                sheet.cell(
                    row=row,
                    column=column,
                    value=cls._excel_value(
                        value
                    ),
                )

            row += 2

        #
        # --------------------------------------------------------------
        # Observed Evidence
        # --------------------------------------------------------------
        #

        sheet.cell(
            row=row,
            column=1,
            value="Observed Evidence",
        ).fill = subheader_fill

        sheet.cell(
            row=row,
            column=1,
        ).font = header_font

        sheet.merge_cells(
            start_row=row,
            start_column=1,
            end_row=row,
            end_column=5,
        )

        row += 1

        if observed_evidence:

            for evidence_item in observed_evidence:

                #
                # Dictionary evidence is retained as structured JSON
                # in the Excel cell rather than being discarded.
                #
                if isinstance(
                    evidence_item,
                    dict,
                ):
                    value = json.dumps(
                        evidence_item,
                        default=str,
                        ensure_ascii=False,
                    )

                elif isinstance(
                    evidence_item,
                    (list, tuple, set),
                ):
                    value = json.dumps(
                        list(evidence_item),
                        default=str,
                        ensure_ascii=False,
                    )

                else:
                    value = cls._excel_value(
                        evidence_item
                    )

                sheet.cell(
                    row=row,
                    column=1,
                    value=value,
                )

                sheet.merge_cells(
                    start_row=row,
                    start_column=1,
                    end_row=row,
                    end_column=5,
                )

                row += 1

        else:
            sheet.cell(
                row=row,
                column=1,
                value=(
                    "No observed evidence was supplied "
                    "by the assessment pipeline."
                ),
            )

            sheet.merge_cells(
                start_row=row,
                start_column=1,
                end_row=row,
                end_column=5,
            )

            row += 1

        #
        # --------------------------------------------------------------
        # Additional evidence-related fields
        # --------------------------------------------------------------
        #

        additional_fields = (
            "evidence_ids",
            "evidence_count",
            "assignment_count",
            "members",
            "roles",
            "findings",
        )

        additional_values: list[
            tuple[str, Any]
        ] = []

        for field_name in additional_fields:

            if field_name not in control:
                continue

            additional_values.append(
                (
                    field_name,
                    control[field_name],
                )
            )

        if additional_values:

            row += 1

            sheet.cell(
                row=row,
                column=1,
                value="Additional Evidence Details",
            ).fill = subheader_fill

            sheet.cell(
                row=row,
                column=1,
            ).font = header_font

            sheet.merge_cells(
                start_row=row,
                start_column=1,
                end_row=row,
                end_column=5,
            )

            row += 1

            for field_name, value in additional_values:

                sheet.cell(
                    row=row,
                    column=1,
                    value=cls._format_key(
                        field_name
                    ),
                ).font = Font(
                    bold=True
                )

                sheet.cell(
                    row=row,
                    column=2,
                    value=cls._excel_value(
                        value
                    ),
                )

                sheet.merge_cells(
                    start_row=row,
                    start_column=2,
                    end_row=row,
                    end_column=5,
                )

                row += 1

        #
        # Add a bottom border to the rendered control area.
        #
        for column in range(
            1,
            6,
        ):
            sheet.cell(
                row=row,
                column=column,
            )

        return row

    # ------------------------------------------------------------------
    # Control Status Styling
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_status_style(
        cell: Any,
        status: Any,
        pass_fill: PatternFill,
        fail_fill: PatternFill,
    ) -> None:
        """
        Apply presentation-only formatting to a control status.

        The status value itself is never changed.
        """

        status_value = str(
            status
        ).upper()

        if status_value == "PASS":
            cell.fill = pass_fill
            cell.font = Font(
                bold=True,
                color="006100",
            )

        elif status_value in {
            "FAIL",
            "FAILED",
        }:
            cell.fill = fail_fill
            cell.font = Font(
                bold=True,
                color="9C0006",
            )

    # ------------------------------------------------------------------
    # Generic Content Renderer
    # ------------------------------------------------------------------

    @classmethod
    def _write_content(
        cls,
        sheet: Any,
        content: Any,
        start_row: int,
        header_fill: PatternFill,
        header_font: Font,
        section_fill: PatternFill,
    ) -> int:
        """
        Generic report-content renderer.

        This preserves the existing behaviour for all sections other
        than Live Control Evidence.
        """

        if isinstance(
            content,
            dict,
        ):
            row = start_row

            simple_items = []
            complex_items = []

            for key, value in content.items():
                if cls._is_simple(
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

            if simple_items:
                sheet.cell(
                    row=row,
                    column=1,
                    value="Metric",
                )

                sheet.cell(
                    row=row,
                    column=2,
                    value="Value",
                )

                for column in (
                    1,
                    2,
                ):
                    cell = sheet.cell(
                        row=row,
                        column=column,
                    )

                    cell.fill = header_fill
                    cell.font = header_font

                row += 1

                for key, value in simple_items:
                    sheet.cell(
                        row=row,
                        column=1,
                        value=key,
                    ).font = Font(
                        bold=True
                    )

                    sheet.cell(
                        row=row,
                        column=2,
                        value=cls._excel_value(
                            value
                        ),
                    )

                    row += 1

                row += 1

            for key, value in complex_items:
                cell = sheet.cell(
                    row=row,
                    column=1,
                    value=key,
                )

                cell.fill = section_fill
                cell.font = Font(
                    bold=True
                )

                row += 1

                row = cls._write_content(
                    sheet=sheet,
                    content=value,
                    start_row=row,
                    header_fill=header_fill,
                    header_font=header_font,
                    section_fill=section_fill,
                )

                row += 1

            return row

        if isinstance(
            content,
            list,
        ):
            if not content:
                sheet.cell(
                    row=start_row,
                    column=1,
                    value="No records",
                )

                return start_row + 1

            if all(
                isinstance(
                    item,
                    dict,
                )
                for item in content
            ):
                keys: list[str] = []

                for item in content:
                    for key in item:
                        key = str(key)

                        if key not in keys:
                            keys.append(
                                key
                            )

                row = start_row

                for column, key in enumerate(
                    keys,
                    start=1,
                ):
                    cell = sheet.cell(
                        row=row,
                        column=column,
                        value=key.replace(
                            "_",
                            " ",
                        ).title(),
                    )

                    cell.fill = header_fill
                    cell.font = header_font

                row += 1

                for item in content:
                    for column, key in enumerate(
                        keys,
                        start=1,
                    ):
                        sheet.cell(
                            row=row,
                            column=column,
                            value=cls._excel_value(
                                item.get(
                                    key
                                )
                            ),
                        )

                    row += 1

                return row

            sheet.cell(
                row=start_row,
                column=1,
                value="Value",
            ).fill = header_fill

            sheet.cell(
                row=start_row,
                column=1,
            ).font = header_font

            row = start_row + 1

            for item in content:
                sheet.cell(
                    row=row,
                    column=1,
                    value=cls._excel_value(
                        item
                    ),
                )

                row += 1

            return row

        sheet.cell(
            row=start_row,
            column=1,
            value=cls._excel_value(
                content
            ),
        )

        return start_row + 1

    # ------------------------------------------------------------------
    # Value Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_simple(
        value: Any,
    ) -> bool:
        """
        Determine whether a value can be written directly to Excel.
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
    def _excel_value(
        value: Any,
    ) -> Any:
        """
        Convert Python values into Excel-compatible values.
        """

        if value is None:
            return ""

        if isinstance(
            value,
            (
                str,
                int,
                float,
                bool,
            ),
        ):
            return value

        if isinstance(
            value,
            datetime,
        ):
            return value.isoformat()

        return json.dumps(
            value,
            default=str,
            ensure_ascii=False,
        )

    @staticmethod
    def _format_key(
        key: str,
    ) -> str:
        """
        Convert snake_case field names into readable labels.
        """

        return (
            str(key)
            .replace(
                "_",
                " ",
            )
            .title()
        )

    # ------------------------------------------------------------------
    # Worksheet Naming
    # ------------------------------------------------------------------

    @staticmethod
    def _sheet_name(
        title: str,
        existing_names: list[str],
    ) -> str:
        """
        Create a valid and unique Excel worksheet name.

        Existing behaviour is preserved, including Excel's 31-character
        worksheet-name limit and invalid-character handling.
        """

        invalid_characters = (
            "\\",
            "/",
            "*",
            "?",
            ":",
            "[",
            "]",
        )

        name = title

        for character in invalid_characters:
            name = name.replace(
                character,
                "_",
            )

        name = name[:31] or "Section"

        original = name
        counter = 1

        while name in existing_names:
            suffix = f"_{counter}"

            name = (
                original[
                    : 31 - len(suffix)
                ]
                + suffix
            )

            counter += 1

        return name
