# engine\reporting\export.py

"""
Export Engine

Exports generated reports to multiple formats.

Supported formats:

- JSON
- YAML
- CSV
- Markdown
- HTML
- Excel
- PDF

Responsibilities:

- General-purpose report exports
- Export orchestration
- Output directory management
- Export manifest generation

Dedicated exporters:

- Excel -> export_excel.py
- PDF -> export_pdf.py
"""

from __future__ import annotations

import csv
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .report_generator import ReportDocument

# ==============================================================================
# Export Manager
# ==============================================================================


class ReportExporter:
    """
    Export report documents into multiple formats.

    General-purpose formats are implemented directly in this class.

    Excel and PDF are delegated to their dedicated exporter classes.
    """

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
    # Export All
    # ------------------------------------------------------------------

    def export_all(
        self,
        report: ReportDocument,
        base_name: str,
    ) -> dict[str, Path]:
        """
        Export the report into every supported format.

        Supported exports:

        - JSON
        - YAML
        - CSV
        - Markdown
        - HTML
        - Excel
        - PDF
        """

        exports: dict[str, Path] = {}

        # --------------------------------------------------------------
        # General-purpose formats
        # --------------------------------------------------------------

        exports["json"] = self.export_json(
            report,
            base_name,
        )

        exports["yaml"] = self.export_yaml(
            report,
            base_name,
        )

        exports["csv"] = self.export_csv(
            report,
            base_name,
        )

        exports["markdown"] = self.export_markdown(
            report,
            base_name,
        )

        exports["html"] = self.export_html(
            report,
            base_name,
        )

        # --------------------------------------------------------------
        # Excel
        # --------------------------------------------------------------

        from .export_excel import ExcelReportExporter

        excel_exporter = ExcelReportExporter(self.output_directory)

        exports["excel"] = excel_exporter.export(
            report=report,
            base_name=base_name,
        )

        # --------------------------------------------------------------
        # PDF
        # --------------------------------------------------------------

        from .export_pdf import PDFReportExporter

        pdf_exporter = PDFReportExporter(self.output_directory)

        exports["pdf"] = pdf_exporter.export(
            report=report,
            base_name=base_name,
        )

        # --------------------------------------------------------------
        # Manifest
        # --------------------------------------------------------------

        self.export_manifest(
            base_name=base_name,
            exports=exports,
        )

        return exports

    # ------------------------------------------------------------------
    # JSON
    # ------------------------------------------------------------------

    def export_json(
        self,
        report: ReportDocument,
        base_name: str,
    ) -> Path:
        """
        Export report as JSON.
        """

        file = self.output_directory / f"{base_name}.json"

        with file.open(
            "w",
            encoding="utf-8",
        ) as fp:
            json.dump(
                self._serialise(report),
                fp,
                indent=2,
                ensure_ascii=False,
                default=str,
            )

        return file

    # ------------------------------------------------------------------
    # YAML
    # ------------------------------------------------------------------

    def export_yaml(
        self,
        report: ReportDocument,
        base_name: str,
    ) -> Path:
        """
        Export report as YAML.
        """

        file = self.output_directory / f"{base_name}.yml"

        with file.open(
            "w",
            encoding="utf-8",
        ) as fp:
            yaml.safe_dump(
                self._serialise(report),
                fp,
                sort_keys=False,
                allow_unicode=True,
            )

        return file

    # ------------------------------------------------------------------
    # CSV
    # ------------------------------------------------------------------

    def export_csv(
        self,
        report: ReportDocument,
        base_name: str,
    ) -> Path:
        """
        Export report sections as CSV.
        """

        file = self.output_directory / f"{base_name}.csv"

        with file.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as fp:
            writer = csv.writer(fp)

            writer.writerow(
                [
                    "Section",
                    "Content",
                ]
            )

            for section in report.sections:
                writer.writerow(
                    [
                        section.title,
                        json.dumps(
                            section.content,
                            default=str,
                        ),
                    ]
                )

        return file

    # ------------------------------------------------------------------
    # Markdown
    # ------------------------------------------------------------------

    def export_markdown(
        self,
        report: ReportDocument,
        base_name: str,
    ) -> Path:
        """
        Export report as Markdown.
        """

        file = self.output_directory / f"{base_name}.md"

        with file.open(
            "w",
            encoding="utf-8",
        ) as fp:
            fp.write(f"# {report.metadata.title}\n\n")

            fp.write(f"Tenant: {report.metadata.tenant}\n\n")

            fp.write(f"Generated: " f"{report.metadata.generated_at}\n\n")

            for section in report.sections:
                fp.write(f"## {section.title}\n\n")

                fp.write("```json\n")

                fp.write(
                    json.dumps(
                        section.content,
                        indent=2,
                        default=str,
                    )
                )

                fp.write("\n```\n\n")

        return file

    # ------------------------------------------------------------------
    # HTML
    # ------------------------------------------------------------------

    def export_html(
        self,
        report: ReportDocument,
        base_name: str,
    ) -> Path:
        """
        Export report as HTML.
        """

        file = self.output_directory / f"{base_name}.html"

        with file.open(
            "w",
            encoding="utf-8",
        ) as fp:
            fp.write("<!DOCTYPE html>\n")

            fp.write("<html>\n<head>\n")

            fp.write(f"<title>" f"{html.escape(report.metadata.title)}" f"</title>\n")

            fp.write('<meta charset="utf-8">\n')

            fp.write("</head>\n<body>\n")

            fp.write(f"<h1>" f"{html.escape(report.metadata.title)}" f"</h1>\n")

            fp.write(
                "<p><strong>Tenant:</strong> "
                f"{html.escape(str(report.metadata.tenant))}"
                "</p>\n"
            )

            fp.write(
                "<p><strong>Generated:</strong> "
                f"{html.escape(str(report.metadata.generated_at))}"
                "</p>\n"
            )

            for section in report.sections:
                fp.write(f"<h2>" f"{html.escape(section.title)}" f"</h2>\n")

                fp.write("<pre>")

                fp.write(
                    html.escape(
                        json.dumps(
                            section.content,
                            indent=2,
                            default=str,
                        )
                    )
                )

                fp.write("</pre>\n")

            fp.write("</body></html>")

        return file

    # ------------------------------------------------------------------
    # Manifest
    # ------------------------------------------------------------------

    def export_manifest(
        self,
        base_name: str,
        exports: dict[str, Path],
    ) -> Path:
        """
        Generate an export manifest containing all generated files.
        """

        manifest = {
            "generated": datetime.now(timezone.utc).isoformat(),
            "report": base_name,
            "files": {key: str(value) for key, value in exports.items()},
        }

        file = self.output_directory / f"{base_name}.manifest.json"

        with file.open(
            "w",
            encoding="utf-8",
        ) as fp:
            json.dump(
                manifest,
                fp,
                indent=2,
            )

        return file

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    @classmethod
    def _serialise(
        cls,
        obj: Any,
    ) -> Any:
        """
        Convert dataclass instances into dictionaries recursively.

        This deliberately avoids passing the result of is_dataclass()
        directly into asdict(), because static type checkers such as
        Pylance can represent is_dataclass() as accepting either a
        dataclass instance or a dataclass class.

        Dataclass fields are therefore collected explicitly after
        confirming that the supplied object is not a class.

        Nested dictionaries, lists, tuples, and sets are also
        recursively serialised.
        """

        if obj is None:
            return None

        if isinstance(
            obj,
            (
                str,
                int,
                float,
                bool,
            ),
        ):
            return obj

        if isinstance(
            obj,
            dict,
        ):
            return {str(key): cls._serialise(value) for key, value in obj.items()}

        if isinstance(
            obj,
            (list, tuple, set),
        ):
            return [cls._serialise(value) for value in obj]

        #
        # Dataclass instance.
        #
        # Do not call asdict(obj) directly here. Pylance can retain
        # the possibility that obj is a dataclass class even after
        # is_dataclass(obj) has returned True.
        #
        try:
            from dataclasses import fields, is_dataclass

            if not isinstance(obj, type) and is_dataclass(obj):
                return {
                    field.name: cls._serialise(
                        getattr(
                            obj,
                            field.name,
                        )
                    )
                    for field in fields(obj)
                }

        except Exception:
            pass

        #
        # Preserve datetime values as ISO strings for exporters that
        # consume the serialised representation.
        #
        if isinstance(
            obj,
            datetime,
        ):
            return obj.isoformat()

        #
        # Preserve enum-like values through their underlying value
        # where available.
        #
        enum_value = getattr(
            obj,
            "value",
            None,
        )

        if enum_value is not None:
            return cls._serialise(enum_value)

        #
        # Support Pydantic-style model_dump() objects without requiring
        # Pydantic as a dependency of the export engine.
        #
        model_dump = getattr(
            obj,
            "model_dump",
            None,
        )

        if callable(model_dump):

            try:
                return cls._serialise(model_dump())
            except Exception:
                pass

        #
        # Support older Pydantic-style dict() objects.
        #
        dictionary = getattr(
            obj,
            "dict",
            None,
        )

        if callable(dictionary):

            try:
                return cls._serialise(dictionary())
            except Exception:
                pass

        #
        # Last-resort support for normal Python objects exposing
        # instance attributes.
        #
        try:
            values = vars(obj)

            if isinstance(
                values,
                dict,
            ):
                return {
                    str(key): cls._serialise(value) for key, value in values.items()
                }

        except TypeError:
            pass

        #
        # JSON/YAML exporters already use default=str as a final
        # fallback. Returning the string here also keeps the
        # serialised structure safe for YAML.
        #
        return str(obj)


# ==============================================================================
# Convenience API
# ==============================================================================


def export_report(
    report: ReportDocument,
    output_directory: Path,
    base_name: str | None = None,
) -> dict[str, Path]:
    """
    Export a report into all supported formats.

    Returns paths for:

    - json
    - yaml
    - csv
    - markdown
    - html
    - excel
    - pdf
    """

    exporter = ReportExporter(output_directory)

    if base_name is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        base_name = f"assessment_{timestamp}"

    return exporter.export_all(
        report,
        base_name,
    )
