# scripts\test_live_report_export.py

from pathlib import Path

from engine.reporting.export import export_report
from engine.reporting.report_generator import (
    ReportDocument,
    ReportMetadata,
    ReportSection,
)


def main() -> None:
    output_directory = Path("test_output")

    report = ReportDocument(
        metadata=ReportMetadata(
            title="Live GRC Assessment Test",
            tenant="test-tenant",
            frameworks=[
                "ISO27001",
                "SOC2",
            ],
        ),
        sections=[
            ReportSection(
                title="Executive Summary",
                content={
                    "security_score": 78,
                    "maturity_level": 3,
                    "maturity_name": "Defined",
                    "frameworks_assessed": 2,
                    "risks_identified": 3,
                    "critical_risks": 1,
                },
            ),
            ReportSection(
                title="Framework Assessment",
                content={
                    "frameworks": [
                        {
                            "framework": "ISO27001",
                            "version": "2022",
                            "score": 82,
                            "coverage": 0.85,
                        },
                        {
                            "framework": "SOC2",
                            "version": "2022",
                            "score": 74,
                            "coverage": 0.76,
                        },
                    ]
                },
            ),
            ReportSection(
                title="Risk Register",
                content={
                    "risks": [
                        {
                            "id": "RISK-001",
                            "title": "Missing MFA",
                            "score": 20,
                            "level": "Critical",
                            "priority": "Urgent",
                        },
                        {
                            "id": "RISK-002",
                            "title": "Incomplete logging",
                            "score": 12,
                            "level": "High",
                            "priority": "High",
                        },
                    ]
                },
            ),
        ],
    )

    exports = export_report(
        report=report,
        output_directory=output_directory,
        base_name="live_assessment",
    )

    print("\nExport completed.\n")

    for format_name, path in exports.items():
        print(f"{format_name:10} -> {path.resolve()}")

    print("\nExpected files:")
    print((output_directory / "live_assessment.xlsx").resolve())
    print((output_directory / "live_assessment.pdf").resolve())


if __name__ == "__main__":
    main()
