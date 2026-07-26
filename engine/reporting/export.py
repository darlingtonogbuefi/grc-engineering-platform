"""
Export Engine

Exports generated reports to multiple formats.

Supported formats:

- JSON
- YAML
- CSV
- Markdown
- HTML

Features:

- Output directory management
- Timestamped filenames
- Report packaging
- Export manifest generation
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import yaml
from _typeshed import DataclassInstance

from .report_generator import ReportDocument


# ==============================================================================
# Export Manager
# ==============================================================================


class ReportExporter:
    """
    Export report documents into multiple formats.
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

    def export_all(
        self,
        report: ReportDocument,
        base_name: str,
    ) -> dict[str, Path]:
        """
        Export every supported format.
        """

        exports = {

            "json":
                self.export_json(
                    report,
                    base_name,
                ),

            "yaml":
                self.export_yaml(
                    report,
                    base_name,
                ),

            "csv":
                self.export_csv(
                    report,
                    base_name,
                ),

            "markdown":
                self.export_markdown(
                    report,
                    base_name,
                ),

            "html":
                self.export_html(
                    report,
                    base_name,
                ),

        }

        self.export_manifest(
            base_name,
            exports,
        )

        return exports

    # ------------------------------------------------------------------

    def export_json(
        self,
        report: ReportDocument,
        base_name: str,
    ) -> Path:

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

    def export_yaml(
        self,
        report: ReportDocument,
        base_name: str,
    ) -> Path:

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

    def export_csv(
        self,
        report: ReportDocument,
        base_name: str,
    ) -> Path:

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

    def export_markdown(
        self,
        report: ReportDocument,
        base_name: str,
    ) -> Path:

        file = self.output_directory / f"{base_name}.md"

        with file.open(
            "w",
            encoding="utf-8",
        ) as fp:

            fp.write(
                f"# {report.metadata.title}\n\n"
            )

            fp.write(
                f"Tenant: {report.metadata.tenant}\n\n"
            )

            fp.write(
                f"Generated: {report.metadata.generated_at}\n\n"
            )

            for section in report.sections:

                fp.write(
                    f"## {section.title}\n\n"
                )

                fp.write(
                    "```json\n"
                )

                fp.write(

                    json.dumps(

                        section.content,

                        indent=2,

                        default=str,

                    )

                )

                fp.write(
                    "\n```\n\n"
                )

        return file

    # ------------------------------------------------------------------

    def export_html(
        self,
        report: ReportDocument,
        base_name: str,
    ) -> Path:

        file = self.output_directory / f"{base_name}.html"

        with file.open(
            "w",
            encoding="utf-8",
        ) as fp:

            fp.write(
                "<!DOCTYPE html>\n"
            )

            fp.write(
                "<html>\n<head>\n"
            )

            fp.write(
                f"<title>{report.metadata.title}</title>\n"
            )

            fp.write(
                "<meta charset=\"utf-8\">\n"
            )

            fp.write(
                "</head>\n<body>\n"
            )

            fp.write(
                f"<h1>{report.metadata.title}</h1>\n"
            )

            fp.write(
                f"<p><strong>Tenant:</strong> "
                f"{report.metadata.tenant}</p>\n"
            )

            fp.write(
                f"<p><strong>Generated:</strong> "
                f"{report.metadata.generated_at}</p>\n"
            )

            for section in report.sections:

                fp.write(
                    f"<h2>{section.title}</h2>\n"
                )

                fp.write("<pre>")

                fp.write(

                    json.dumps(

                        section.content,

                        indent=2,

                        default=str,

                    )

                )

                fp.write("</pre>\n")

            fp.write("</body></html>")

        return file

    # ------------------------------------------------------------------

    def export_manifest(
        self,
        base_name: str,
        exports: dict[str, Path],
    ) -> Path:

        manifest = {

            "generated":

                datetime.now(
                    timezone.utc
                ).isoformat(),

            "report":

                base_name,

            "files": {

                key: str(value)

                for key, value in exports.items()

            },

        }

        file = (
            self.output_directory
            /
            f"{base_name}.manifest.json"
        )

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

    @staticmethod
    def _serialise(
        obj: Any,
    ) -> Any:
        """
        Convert dataclass instances into dictionaries recursively.
        """

        # is_dataclass() returns True for both dataclass classes
        # and dataclass instances. asdict() only accepts instances.
        if is_dataclass(obj) and not isinstance(obj, type):

            return asdict(
                cast(
                    DataclassInstance,
                    obj,
                )
            )

        return obj

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
    """

    exporter = ReportExporter(
        output_directory
    )

    if base_name is None:

        timestamp = datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%d_%H%M%S"
        )

        base_name = (
            f"assessment_{timestamp}"
        )

    return exporter.export_all(
        report,
        base_name,
    )
