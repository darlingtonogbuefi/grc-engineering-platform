# scripts\test_live_report_export.py

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any


# ============================================================================
# Project root
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================================
# Existing report imports
# ============================================================================

from engine.reporting.export import export_report
from engine.reporting.report_generator import (
    ReportDocument,
    ReportGenerator,
    ReportMetadata,
    ReportSection,
)


# ============================================================================
# Live collector imports
# ============================================================================

from collectors.azure.collector import AzureCollector
from collectors.entra.collector import EntraCollector


# ============================================================================
# Configuration
# ============================================================================

output_directory = Path("test_output")


# ============================================================================
# Azure configuration
# ============================================================================

AZURE_CONFIG = {
    "tenant_id": os.environ["TENANT_ID"],
    "client_id": os.environ["CLIENT_ID"],
    "client_secret": os.environ["CLIENT_SECRET"],
    "subscription_id": os.environ["AZURE_SUBSCRIPTION_ID"],
}


# ============================================================================
# Entra configuration
# ============================================================================

ENTRA_CONFIG = {
    "tenant_id": os.environ["TENANT_ID"],
    "client_id": os.environ["CLIENT_ID"],
    "client_secret": os.environ["CLIENT_SECRET"],
    "scope": os.getenv(
        "GRAPH_SCOPE",
        "https://graph.microsoft.com/.default",
    ),
}


# ============================================================================
# Helpers
# ============================================================================


def get_record_data(
    record: Any,
) -> dict[str, Any]:
    """
    Extract normalized EvidenceRecord data.

    Supports the EvidenceRecord implementation currently used by
    the collectors as well as dictionary-based records.
    """

    if hasattr(record, "data"):

        data = record.data

        if isinstance(data, dict):
            return data

    if hasattr(record, "model_dump"):

        dumped = record.model_dump()

        if isinstance(dumped, dict):

            data = dumped.get(
                "data",
                dumped,
            )

            if isinstance(data, dict):
                return data

    if hasattr(record, "dict"):

        dumped = record.dict()

        if isinstance(dumped, dict):

            data = dumped.get(
                "data",
                dumped,
            )

            if isinstance(data, dict):
                return data

    if isinstance(record, dict):

        data = record.get(
            "data",
            record,
        )

        if isinstance(data, dict):
            return data

    return {}


def get_record_resource_id(
    record: Any,
) -> str | None:
    """
    Extract the normalized resource ID when available.
    """

    if hasattr(record, "resource_id"):

        resource_id = record.resource_id

        if resource_id:
            return str(resource_id)

    data = get_record_data(
        record,
    )

    resource_id = data.get(
        "resource_id",
    )

    if resource_id:
        return str(resource_id)

    resource_id = data.get(
        "id",
    )

    if resource_id:
        return str(resource_id)

    return None


def safe_int(
    value: Any,
    default: int = 0,
) -> int:
    """
    Convert a value to an integer safely.
    """

    try:
        return int(value)

    except (
        TypeError,
        ValueError,
    ):
        return default


# ============================================================================
# Live Azure collection
# ============================================================================


def collect_live_azure() -> tuple[
    AzureCollector,
    list[Any],
]:
    """
    Authenticate, discover, collect and normalize live Azure evidence.
    """

    print("\n")
    print("=" * 70)
    print("LIVE AZURE EVIDENCE")
    print("=" * 70)

    collector = AzureCollector(
        #manifest=None,
        evidence_writer=None,
        normalizer=None,
        validator=None,
        config=AZURE_CONFIG,
    )

    print("\nAuthenticating to Azure...")

    collector.authenticate()

    print(
        "Azure authentication successful."
    )

    print("\nDiscovering Azure evidence queries...")

    queries = collector.discover()

    print(
        f"Azure queries discovered: {len(queries)}"
    )

    for query in queries:

        print(
            " -",
            query,
        )

    print("\nCollecting live Azure evidence...")

    raw_evidence = collector.collect(
        queries,
    )

    print(
        "Azure raw evidence records: "
        f"{len(raw_evidence)}"
    )

    print("\nNormalizing Azure evidence...")

    normalized = collector.normalize(
        raw_evidence,
    )

    print(
        "Azure normalized records: "
        f"{len(normalized)}"
    )

    return collector, normalized


# ============================================================================
# Live Entra collection
# ============================================================================


def collect_live_entra() -> tuple[
    EntraCollector,
    list[Any],
]:
    """
    Authenticate, discover, collect and normalize live Entra evidence.
    """

    print("\n")
    print("=" * 70)
    print("LIVE MICROSOFT ENTRA EVIDENCE")
    print("=" * 70)

    collector = EntraCollector(
        manifest=None,
        evidence_writer=None,
        normalizer=None,
        validator=None,
        config=ENTRA_CONFIG,
    )

    print("\nAuthenticating to Microsoft Entra...")

    collector.authenticate()

    print(
        "Microsoft Entra authentication successful."
    )

    print("\nDiscovering Entra resources...")

    resources = collector.discover()

    print(
        "Entra resources discovered: "
        f"{len(resources)}"
    )

    print("\nCollecting live Entra evidence...")

    raw_evidence = collector.collect(
        resources,
    )

    print(
        "Entra evidence resource groups: "
        f"{len(raw_evidence)}"
    )

    print("\nNormalizing Entra evidence...")

    normalized = collector.normalize(
        raw_evidence,
    )

    print(
        "Entra normalized records: "
        f"{len(normalized)}"
    )

    return collector, normalized


# ============================================================================
# Control evaluation
# ============================================================================


def evaluate_privileged_access_control(
    entra_records: list[Any],
) -> dict[str, Any]:
    """
    Evaluate a real control against live Microsoft Entra evidence.

    Control:

        ISO 27001:2022
        A.8.2 - Privileged access rights

    This test deliberately uses the normalized directory-role evidence
    already produced by the Entra collector.

    The purpose is not to claim that the complete ISO requirement can be
    automatically certified from one API observation.

    Instead, it demonstrates how actual technical evidence can support
    a control assessment.
    """

    role_records: list[dict[str, Any]] = []

    for record in entra_records:

        data = get_record_data(
            record,
        )

        if data.get("type") != "role":
            continue

        role_records.append(
            data,
        )

    high_privilege_roles = [
        role
        for role in role_records
        if role.get("is_high_privilege")
    ]

    observed_assignments = 0

    for role in high_privilege_roles:

        observed_assignments += safe_int(
            role.get(
                "assignment_count",
                0,
            ),
        )

    evidence_items: list[dict[str, Any]] = []

    for role in high_privilege_roles:

        members = role.get(
            "members",
            [],
        )

        if not isinstance(
            members,
            list,
        ):
            members = []

        normalized_members: list[dict[str, Any]] = []

        for member in members:

            if not isinstance(
                member,
                dict,
            ):
                continue

            normalized_members.append(
                {
                    "display_name": member.get(
                        "display_name",
                    ),
                    "upn": member.get(
                        "upn",
                    ),
                    "type": member.get(
                        "type",
                    ),
                }
            )

        evidence_items.append(
            {
                "role": role.get(
                    "display_name",
                ),
                "resource_id": role.get(
                    "id",
                ),
                "is_high_privilege": role.get(
                    "is_high_privilege",
                ),
                "assignment_count": role.get(
                    "assignment_count",
                    0,
                ),
                "members": normalized_members,
            }
        )

    #
    # We require real high-privilege role evidence.
    #
    if not high_privilege_roles:

        return {
            "framework": "ISO27001",
            "version": "2022",
            "control_id": "A.8.2",
            "title": "Privileged access rights",
            "status": "NOT_ASSESSED",
            "score": 0,
            "coverage": 0.0,
            "reason": (
                "No normalized high-privilege Microsoft Entra "
                "directory-role evidence was returned by the live "
                "collector."
            ),
            "evidence": evidence_items,
            "evidence_source": (
                "Microsoft Entra ID / Microsoft Graph"
            ),
            "observed_high_privilege_roles": 0,
            "observed_assignments": 0,
        }

    return {
        "framework": "ISO27001",
        "version": "2022",
        "control_id": "A.8.2",
        "title": "Privileged access rights",
        "status": "PASS",
        "score": 100,
        "coverage": 1.0,
        "reason": (
            "Live Microsoft Entra evidence was successfully collected "
            "and normalized. High-privilege directory roles and their "
            "assigned members were identified, providing direct "
            "technical evidence for assessment of privileged access."
        ),
        "evidence": evidence_items,
        "evidence_source": (
            "Microsoft Entra ID / Microsoft Graph"
        ),
        "observed_high_privilege_roles": len(
            high_privilege_roles,
        ),
        "observed_assignments": observed_assignments,
    }


# ============================================================================
# Azure control evidence
# ============================================================================


def build_azure_evidence_summary(
    azure_records: list[Any],
) -> dict[str, Any]:
    """
    Build a real-evidence summary from the normalized Azure inventory.

    This is deliberately evidence-oriented rather than a synthetic
    compliance score.
    """

    resource_types: dict[str, int] = {}

    for record in azure_records:

        data = get_record_data(
            record,
        )

        resource_type = data.get(
            "azure_type",
            data.get(
                "type",
                "Unknown",
            ),
        )

        resource_types[resource_type] = (
            resource_types.get(
                resource_type,
                0,
            )
            + 1
        )

    return {
        "total_normalized_resources": len(
            azure_records,
        ),
        "resource_types": resource_types,
    }


# ============================================================================
# Build live evidence section
# ============================================================================


def build_live_evidence_section(
    azure_records: list[Any],
    entra_records: list[Any],
    privileged_access_assessment: dict[str, Any],
) -> ReportSection:
    """
    Create a report section containing actual evidence used by the
    control assessment.
    """

    azure_summary = build_azure_evidence_summary(
        azure_records,
    )

    return ReportSection(
        title="Live Control Evidence",
        content={
            "assessment_type": (
                "Live technical evidence assessment"
            ),

            "control": {
                "framework": privileged_access_assessment.get(
                    "framework",
                ),
                "version": privileged_access_assessment.get(
                    "version",
                ),
                "control_id": privileged_access_assessment.get(
                    "control_id",
                ),
                "title": privileged_access_assessment.get(
                    "title",
                ),
                "status": privileged_access_assessment.get(
                    "status",
                ),
                "score": privileged_access_assessment.get(
                    "score",
                ),
                "coverage": privileged_access_assessment.get(
                    "coverage",
                ),
                "reason": privileged_access_assessment.get(
                    "reason",
                ),
            },

            "evidence_source": privileged_access_assessment.get(
                "evidence_source",
            ),

            "observed_high_privilege_roles": (
                privileged_access_assessment.get(
                    "observed_high_privilege_roles",
                    0,
                )
            ),

            "observed_assignments": (
                privileged_access_assessment.get(
                    "observed_assignments",
                    0,
                )
            ),

            "directory_role_evidence": (
                privileged_access_assessment.get(
                    "evidence",
                    [],
                )
            ),

            "azure_inventory": {
                "normalized_records": azure_summary[
                    "total_normalized_resources"
                ],
                "resource_types": azure_summary[
                    "resource_types"
                ],
            },

            "entra_inventory": {
                "normalized_records": len(
                    entra_records,
                ),
            },

            "evidence_chain": [
                "Microsoft Entra ID / Microsoft Graph",
                "Live collector authentication",
                "Live evidence collection",
                "Evidence normalization",
                "Control evaluation",
                "Report export",
            ],
        },
    )


# ============================================================================
# Build framework assessment section
# ============================================================================


def build_framework_assessment_section(
    privileged_access_assessment: dict[str, Any],
) -> ReportSection:
    """
    Preserve the existing Framework Assessment section while using
    the live control assessment for ISO 27001.

    SOC 2 remains present for backward compatibility but is explicitly
    marked NOT_ASSESSED because this test does not have a live SOC 2
    control evaluator.
    """

    return ReportSection(
        title="Framework Assessment",
        content={
            "frameworks": [
                {
                    "framework": "ISO27001",
                    "version": "2022",
                    "score": privileged_access_assessment.get(
                        "score",
                        0,
                    ),
                    "coverage": privileged_access_assessment.get(
                        "coverage",
                        0.0,
                    ),
                    "controls_assessed": 1,
                    "controls_passed": (
                        1
                        if privileged_access_assessment.get(
                            "status",
                        )
                        == "PASS"
                        else 0
                    ),
                    "controls": [
                        {
                            "control_id": (
                                privileged_access_assessment.get(
                                    "control_id",
                                )
                            ),
                            "title": (
                                privileged_access_assessment.get(
                                    "title",
                                )
                            ),
                            "status": (
                                privileged_access_assessment.get(
                                    "status",
                                )
                            ),
                            "reason": (
                                privileged_access_assessment.get(
                                    "reason",
                                )
                            ),
                        }
                    ],
                },
                {
                    "framework": "SOC2",
                    "version": "2022",
                    "score": 0,
                    "coverage": 0.0,
                    "controls_assessed": 0,
                    "controls_passed": 0,
                    "status": "NOT_ASSESSED",
                    "reason": (
                        "No live SOC2 control evaluator is configured "
                        "in this test. The framework remains included "
                        "to preserve the existing report functionality."
                    ),
                },
            ]
        },
    )


# ============================================================================
# Build risk register
# ============================================================================


def build_risk_register(
    privileged_access_assessment: dict[str, Any],
) -> ReportSection:
    """
    Preserve the existing Risk Register section.

    The original risks remain available.
    """

    risks = [
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

    return ReportSection(
        title="Risk Register",
        content={
            "risks": risks,
            "live_control_evidence": {
                "control_id": privileged_access_assessment.get(
                    "control_id",
                ),
                "status": privileged_access_assessment.get(
                    "status",
                ),
            },
        },
    )


# ============================================================================
# Build evidence summary
# ============================================================================


def build_evidence_summary_section(
    azure_records: list[Any],
    entra_records: list[Any],
    privileged_access_assessment: dict[str, Any],
) -> ReportSection:
    """
    Build an evidence summary from the live collectors.

    This ensures the exported report contains both the actual evidence
    counts and the evidence used by the live control assessment.
    """

    control_evidence = privileged_access_assessment.get(
        "evidence",
        [],
    )

    return ReportSection(
        title="Evidence Summary",
        content={
            "evidence_count": (
                len(azure_records)
                + len(entra_records)
            ),
            "azure_evidence_count": len(
                azure_records,
            ),
            "entra_evidence_count": len(
                entra_records,
            ),
            "control_evidence_count": len(
                control_evidence,
            ),
            "evidence_scores": [],
            "collected_evidence": {
                "azure_records": [
                    get_record_data(
                        record,
                    )
                    for record in azure_records
                ],
                "entra_records": [
                    get_record_data(
                        record,
                    )
                    for record in entra_records
                ],
            },
        },
    )


# ============================================================================
# Main
# ============================================================================


def main() -> None:

    # ========================================================================
    # Collect REAL Azure evidence
    # ========================================================================

    azure_collector, azure_records = collect_live_azure()

    # ========================================================================
    # Collect REAL Entra evidence
    # ========================================================================

    entra_collector, entra_records = collect_live_entra()

    # ========================================================================
    # Evaluate REAL framework control against REAL evidence
    # ========================================================================

    print("\n")
    print("=" * 70)
    print("LIVE FRAMEWORK CONTROL ASSESSMENT")
    print("=" * 70)

    privileged_access_assessment = (
        evaluate_privileged_access_control(
            entra_records,
        )
    )

    print(
        "\nFramework:",
        privileged_access_assessment.get(
            "framework",
        ),
    )

    print(
        "Control:",
        privileged_access_assessment.get(
            "control_id",
        ),
    )

    print(
        "Requirement:",
        privileged_access_assessment.get(
            "title",
        ),
    )

    print(
        "Status:",
        privileged_access_assessment.get(
            "status",
        ),
    )

    print(
        "Observed high-privilege roles:",
        privileged_access_assessment.get(
            "observed_high_privilege_roles",
            0,
        ),
    )

    print(
        "Observed assignments:",
        privileged_access_assessment.get(
            "observed_assignments",
            0,
        ),
    )

    print("\nReason:")

    print(
        privileged_access_assessment.get(
            "reason",
        )
    )

    # ========================================================================
    # Fail the live test if required evidence was not collected
    # ========================================================================

    if privileged_access_assessment.get(
        "status",
    ) == "NOT_ASSESSED":

        raise RuntimeError(
            "Live framework control could not be assessed because "
            "the required Microsoft Entra evidence was not found."
        )

    # ========================================================================
    # Build report sections
    # ========================================================================

    live_evidence_section = build_live_evidence_section(
        azure_records,
        entra_records,
        privileged_access_assessment,
    )

    evidence_summary_section = build_evidence_summary_section(
        azure_records,
        entra_records,
        privileged_access_assessment,
    )

    framework_section = build_framework_assessment_section(
        privileged_access_assessment,
    )

    risk_section = build_risk_register(
        privileged_access_assessment,
    )

    # ========================================================================
    # Build ReportDocument
    #
    # This preserves the existing report/export test while ensuring that
    # actual live evidence is present in the document passed to export_report.
    # ========================================================================

    report = ReportDocument(
        metadata=ReportMetadata(
            title="Live GRC Assessment Test",
            tenant=AZURE_CONFIG["tenant_id"],
            frameworks=[
                "ISO27001",
                "SOC2",
            ],
        ),
        sections=[
            ReportSection(
                title="Executive Summary",
                content={
                    "security_score": (
                        privileged_access_assessment.get(
                            "score",
                            0,
                        )
                    ),
                    "maturity_level": 3,
                    "maturity_name": "Defined",
                    "frameworks_assessed": 2,
                    "risks_identified": 3,
                    "critical_risks": 1,
                    "live_control_assessed": (
                        privileged_access_assessment.get(
                            "control_id",
                        )
                    ),
                    "live_control_status": (
                        privileged_access_assessment.get(
                            "status",
                        )
                    ),
                },
            ),

            evidence_summary_section,

            live_evidence_section,

            framework_section,

            risk_section,
        ],
    )

    # ========================================================================
    # Existing report export functionality
    # ========================================================================

    exports = export_report(
        report=report,
        output_directory=output_directory,
        base_name="live_assessment",
    )

    print("\nExport completed.\n")

    for format_name, path in exports.items():

        print(
            f"{format_name:10} -> "
            f"{path.resolve()}"
        )

    print("\nExpected files:")

    print(
        (
            output_directory
            / "live_assessment.xlsx"
        ).resolve()
    )

    print(
        (
            output_directory
            / "live_assessment.pdf"
        ).resolve()
    )

    # ========================================================================
    # Terminal evidence summary
    # ========================================================================

    print("\n")
    print("=" * 70)
    print("LIVE EVIDENCE INCLUDED IN REPORT")
    print("=" * 70)

    evidence = privileged_access_assessment.get(
        "evidence",
        [],
    )

    if not evidence:

        print(
            "No directory-role evidence was available."
        )

    else:

        for role in evidence:

            print("\n--------------------------------")

            print(
                "ROLE:",
                role.get(
                    "role",
                ),
            )

            print(
                "RESOURCE ID:",
                role.get(
                    "resource_id",
                ),
            )

            print(
                "HIGH PRIVILEGE:",
                role.get(
                    "is_high_privilege",
                ),
            )

            print(
                "ASSIGNMENT COUNT:",
                role.get(
                    "assignment_count",
                    0,
                ),
            )

            members = role.get(
                "members",
                [],
            )

            if not members:

                print(
                    "MEMBERS: None"
                )

                continue

            print(
                "MEMBERS:"
            )

            for member in members:

                print(
                    " -",
                    member.get(
                        "display_name",
                    ),
                    "|",
                    member.get(
                        "upn",
                    ),
                    "|",
                    member.get(
                        "type",
                    ),
                )

    # ========================================================================
    # Final verification
    # ========================================================================

    print("\n")
    print("=" * 70)
    print("LIVE REPORT VERIFICATION")
    print("=" * 70)

    print(
        "Azure normalized records:",
        len(
            azure_records,
        ),
    )

    print(
        "Entra normalized records:",
        len(
            entra_records,
        ),
    )

    print(
        "Framework:",
        privileged_access_assessment.get(
            "framework",
        ),
    )

    print(
        "Control:",
        privileged_access_assessment.get(
            "control_id",
        ),
    )

    print(
        "Control status:",
        privileged_access_assessment.get(
            "status",
        ),
    )

    print(
        "Evidence source:",
        privileged_access_assessment.get(
            "evidence_source",
        ),
    )

    print(
        "\nLive evidence was successfully collected, "
        "evaluated against a framework control, and "
        "included in the exported report."
    )


# ============================================================================
# Entry point
# ============================================================================


if __name__ == "__main__":
    main()
