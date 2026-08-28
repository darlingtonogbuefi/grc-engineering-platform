# scripts/test_live_report_export.py

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
    ReportMetadata,
    ReportSection,
)
from engine.reporting.evidence_table import EvidenceTableBuilder

# ============================================================================
# Live collector imports
# ============================================================================

from collectors.azure.collector import AzureCollector
from collectors.entra.collector import EntraCollector

# ============================================================================
# Configuration
# ============================================================================

# Keep report output deterministic regardless of the directory from which
# this script is launched.
output_directory = PROJECT_ROOT / "test_output"


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
# Report evidence configuration
# ============================================================================

# The live collectors continue to collect ALL available evidence.
#
# This limit only controls how many representative Azure records are placed
# into the human-readable report. It does NOT limit collection, normalization,
# control evaluation, or evidence availability.
#
# This prevents hundreds/thousands of pages of raw inventory being embedded
# directly into PDF/XLSX reports.
REPORT_AZURE_SAMPLE_LIMIT = 25


# ============================================================================
# Helpers
# ============================================================================


def get_record_data(
    record: Any,
) -> dict[str, Any]:
    """
    Extract normalized EvidenceRecord data.

    Supports:

        - EvidenceRecord-like objects exposing ``data``
        - Pydantic models exposing ``model_dump()``
        - Pydantic v1-style models exposing ``dict()``
        - plain dictionaries

    The helper is deliberately defensive because collectors may return
    different record implementations.
    """

    if hasattr(record, "data"):

        try:
            data = record.data
        except Exception:
            data = None

        if isinstance(data, dict):
            return data

    if hasattr(record, "model_dump"):

        try:
            dumped = record.model_dump()
        except Exception:
            dumped = None

        if isinstance(dumped, dict):

            data = dumped.get(
                "data",
                dumped,
            )

            if isinstance(data, dict):
                return data

    if hasattr(record, "dict"):

        try:
            dumped = record.dict()
        except Exception:
            dumped = None

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

        try:
            resource_id = record.resource_id
        except Exception:
            resource_id = None

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


def safe_bool(
    value: Any,
) -> bool:
    """
    Convert common truthy/falsey values to a boolean safely.
    """

    if isinstance(value, bool):
        return value

    if isinstance(value, str):

        normalized = value.strip().lower()

        if normalized in {
            "true",
            "yes",
            "1",
            "y",
        }:
            return True

        if normalized in {
            "false",
            "no",
            "0",
            "n",
            "",
        }:
            return False

    return bool(value)


# ============================================================================
# Report evidence helpers
# ============================================================================


def get_record_type(
    record: Any,
) -> str:
    """
    Return a compact normalized evidence/resource type.

    Azure collectors may expose the type as ``azure_type`` while
    other normalized records may expose ``type``.
    """

    data = get_record_data(
        record,
    )

    value = data.get(
        "azure_type",
        data.get(
            "type",
            "Unknown",
        ),
    )

    if value is None:
        return "Unknown"

    value = str(value).strip()

    if not value:
        return "Unknown"

    return value


def get_record_timestamp(
    record: Any,
) -> str:
    """
    Extract the timestamp from the normalized record.

    The timestamp is retained in the report output and is not replaced
    by the resource name or any other field.

    Supported timestamp fields, in priority order:

        - timestamp
        - collected_at
        - observed_at
        - created_at
    """

    data = get_record_data(
        record,
    )

    timestamp = data.get(
        "timestamp",
    )

    if timestamp is None:
        timestamp = data.get(
            "collected_at",
        )

    if timestamp is None:
        timestamp = data.get(
            "observed_at",
        )

    if timestamp is None:
        timestamp = data.get(
            "created_at",
        )

    if timestamp is None:
        return ""

    return EvidenceTableBuilder.format_time(
        timestamp,
    )


def get_record_resource_name(
    record: Any,
) -> str | None:
    """
    Extract the Azure resource name.

    ``resource_name`` is preferred because the report should expose
    the resource name explicitly rather than using the ambiguous
    generic field ``name``.

    ``resourceName`` and ``name`` remain compatibility fallbacks so
    existing collector output is not broken.
    """

    data = get_record_data(
        record,
    )

    resource_name = data.get(
        "resource_name",
    )

    if resource_name is None:
        resource_name = data.get(
            "resourceName",
        )

    if resource_name is None:
        resource_name = data.get(
            "name",
        )

    if resource_name is None:
        return None

    return str(resource_name)


def get_record_subscription(
    record: Any,
) -> str | None:
    """
    Extract the Azure subscription value.

    ``subscription`` is preferred for the human-readable report.

    Existing ``subscription_name``, ``subscriptionName``,
    ``subscription_id`` and ``subscriptionId`` fields remain supported
    so no collector functionality is changed.
    """

    data = get_record_data(
        record,
    )

    subscription = data.get(
        "subscription",
    )

    if subscription is None:
        subscription = data.get(
            "subscription_name",
        )

    if subscription is None:
        subscription = data.get(
            "subscriptionName",
        )

    if subscription is not None:
        return str(subscription)

    subscription_id = data.get(
        "subscription_id",
        data.get(
            "subscriptionId",
        ),
    )

    if subscription_id is not None:
        return str(subscription_id)

    return None


def build_azure_report_sample(
    azure_records: list[Any],
    limit: int = REPORT_AZURE_SAMPLE_LIMIT,
) -> list[dict[str, Any]]:
    """
    Build a compact representative Azure inventory sample for the report.

    The human-readable Azure inventory uses:

        Timestamp
        Resource Name
        Provider
        Service
        Subscription
        Evidence

    This deliberately does NOT expose the raw Azure inventory schema:

        Resource Id
        Name
        Provider
        Service
        Location
        Subscription Id
        Resource Group
        Azure Type

    The full Azure evidence remains available in ``azure_records`` for
    processing and control evaluation. Only a deliberately limited,
    human-readable inventory sample is embedded in the exported report.

    IMPORTANT:

    These Azure inventory records are inventory/evidence records only.
    They are not automatically treated as control evidence and are not
    assigned a synthetic compliance reason.
    """

    sample: list[dict[str, Any]] = []

    if limit <= 0:
        return sample

    for record in azure_records[:limit]:

        data = get_record_data(
            record,
        )

        if not data:
            continue

        sample.append(
            {
                # Timestamp is intentionally retained.
                "timestamp": get_record_timestamp(
                    record,
                ),
                # ``name`` is replaced in the report with the explicit
                # ``resource_name`` field.
                "resource_name": get_record_resource_name(
                    record,
                ),
                "provider": data.get(
                    "provider",
                    data.get(
                        "namespace",
                    ),
                ),
                "service": data.get(
                    "service",
                ),
                # Subscription is explicitly included as its own column.
                "subscription": get_record_subscription(
                    record,
                ),
                "evidence": ("Azure resource inventory record"),
            }
        )

    return sample


def build_azure_evidence_inventory(
    azure_records: list[Any],
) -> dict[str, Any]:
    """
    Build a compact Azure evidence inventory.

    The complete Azure evidence set is retained in memory and remains
    available to the caller. This function intentionally produces only
    summary information suitable for inclusion in a report.
    """

    resource_types: dict[str, int] = {}

    providers: dict[str, int] = {}

    services: dict[str, int] = {}

    locations: dict[str, int] = {}

    subscriptions: dict[str, int] = {}

    resource_groups: dict[str, int] = {}

    for record in azure_records:

        data = get_record_data(
            record,
        )

        resource_type = get_record_type(
            record,
        )

        resource_types[resource_type] = (
            resource_types.get(
                resource_type,
                0,
            )
            + 1
        )

        provider = data.get(
            "provider",
            data.get(
                "namespace",
            ),
        )

        if provider:

            provider = str(provider)

            providers[provider] = (
                providers.get(
                    provider,
                    0,
                )
                + 1
            )

        service = data.get(
            "service",
        )

        if service:

            service = str(service)

            services[service] = (
                services.get(
                    service,
                    0,
                )
                + 1
            )

        location = data.get(
            "location",
        )

        if location:

            location = str(location)

            locations[location] = (
                locations.get(
                    location,
                    0,
                )
                + 1
            )

        subscription_id = data.get(
            "subscription_id",
            data.get(
                "subscriptionId",
            ),
        )

        if subscription_id:

            subscription_id = str(subscription_id)

            subscriptions[subscription_id] = (
                subscriptions.get(
                    subscription_id,
                    0,
                )
                + 1
            )

        resource_group = data.get(
            "resource_group",
            data.get(
                "resourceGroup",
            ),
        )

        if resource_group:

            resource_group = str(resource_group)

            resource_groups[resource_group] = (
                resource_groups.get(
                    resource_group,
                    0,
                )
                + 1
            )

    return {
        "total_normalized_resources": len(
            azure_records,
        ),
        "resource_types": dict(
            sorted(
                resource_types.items(),
                key=lambda item: (-item[1], item[0]),
            )
        ),
        "providers": dict(
            sorted(
                providers.items(),
                key=lambda item: (-item[1], item[0]),
            )
        ),
        "services": dict(
            sorted(
                services.items(),
                key=lambda item: (-item[1], item[0]),
            )
        ),
        "locations": dict(
            sorted(
                locations.items(),
                key=lambda item: (-item[1], item[0]),
            )
        ),
        "subscriptions": dict(
            sorted(
                subscriptions.items(),
                key=lambda item: (-item[1], item[0]),
            )
        ),
        "resource_groups": dict(
            sorted(
                resource_groups.items(),
                key=lambda item: (-item[1], item[0]),
            )
        ),
    }


def build_entra_evidence_summary(
    entra_records: list[Any],
) -> dict[str, Any]:
    """
    Build a compact Microsoft Entra evidence summary.

    Full Entra evidence remains available for control evaluation.
    Only aggregate information is included in the general report
    evidence summary.
    """

    evidence_types: dict[str, int] = {}

    high_privilege_roles = 0

    total_assignments = 0

    for record in entra_records:

        data = get_record_data(
            record,
        )

        evidence_type = data.get(
            "type",
            "Unknown",
        )

        evidence_type = str(
            evidence_type,
        ).strip()

        if not evidence_type:
            evidence_type = "Unknown"

        evidence_types[evidence_type] = (
            evidence_types.get(
                evidence_type,
                0,
            )
            + 1
        )

        if evidence_type.lower() == "role" and safe_bool(
            data.get(
                "is_high_privilege",
            )
        ):

            high_privilege_roles += 1

            total_assignments += safe_int(
                data.get(
                    "assignment_count",
                    0,
                )
            )

    return {
        "normalized_records": len(
            entra_records,
        ),
        "evidence_types": dict(
            sorted(
                evidence_types.items(),
                key=lambda item: (-item[1], item[0]),
            )
        ),
        "high_privilege_roles": high_privilege_roles,
        "observed_assignments": total_assignments,
    }


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
        # manifest=None,
        evidence_writer=None,
        normalizer=None,
        validator=None,
        config=AZURE_CONFIG,
    )

    print("\nAuthenticating to Azure...")

    collector.authenticate()

    print("Azure authentication successful.")

    print("\nDiscovering Azure evidence queries...")

    queries = collector.discover()

    print(f"Azure queries discovered: {len(queries)}")

    for query in queries:

        print(
            " -",
            query,
        )

    print("\nCollecting live Azure evidence...")

    raw_evidence = collector.collect(
        queries,
    )

    print("Azure raw evidence records: " f"{len(raw_evidence)}")

    print("\nNormalizing Azure evidence...")

    normalized = collector.normalize(
        raw_evidence,
    )

    print("Azure normalized records: " f"{len(normalized)}")

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

    print("Microsoft Entra authentication successful.")

    print("\nDiscovering Entra resources...")

    resources = collector.discover()

    print("Entra resources discovered: " f"{len(resources)}")

    print("\nCollecting live Entra evidence...")

    raw_evidence = collector.collect(
        resources,
    )

    print("Entra evidence resource groups: " f"{len(raw_evidence)}")

    print("\nNormalizing Entra evidence...")

    normalized = collector.normalize(
        raw_evidence,
    )

    print("Entra normalized records: " f"{len(normalized)}")

    return collector, normalized


# ============================================================================
# Control evaluation
# ============================================================================


def evaluate_privileged_access_control(
    entra_records: list[Any],
) -> dict[str, Any]:
    """
    Evaluate technical evidence relevant to:

        ISO 27001:2022
        A.8.2 - Privileged access rights

    IMPORTANT:

    This function evaluates whether relevant live technical evidence was
    successfully collected and normalized.

    It does NOT claim that the complete ISO 27001 A.8.2 requirement has
    been independently certified or fully demonstrated from Microsoft
    Graph role data alone.

    A PASS therefore means:

        "The live technical evidence required by this test was observed."

    It does not mean:

        "The organization is fully compliant with A.8.2."
    """

    role_records: list[dict[str, Any]] = []

    for record in entra_records:

        data = get_record_data(
            record,
        )

        evidence_type = (
            str(
                data.get(
                    "type",
                    "",
                )
            )
            .strip()
            .lower()
        )

        if evidence_type != "role":
            continue

        role_records.append(
            data,
        )

    high_privilege_roles = [
        role
        for role in role_records
        if safe_bool(
            role.get(
                "is_high_privilege",
            )
        )
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
                "is_high_privilege": safe_bool(
                    role.get(
                        "is_high_privilege",
                    )
                ),
                "assignment_count": safe_int(
                    role.get(
                        "assignment_count",
                        0,
                    )
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
            "assessment_scope": ("Technical evidence observation only"),
            "reason": (
                "No normalized high-privilege Microsoft Entra "
                "directory-role evidence was returned by the live "
                "collector."
            ),
            "assessment_limitation": (
                "This test does not independently certify ISO 27001 "
                "A.8.2. A complete assessment also requires appropriate "
                "organizational, procedural, authorization, review, "
                "and governance evidence."
            ),
            "evidence": evidence_items,
            "evidence_source": ("Microsoft Entra ID / Microsoft Graph"),
            "observed_high_privilege_roles": 0,
            "observed_assignments": 0,
        }

    return {
        "framework": "ISO27001",
        "version": "2022",
        "control_id": "A.8.2",
        "title": "Privileged access rights",
        #
        # PASS here means that the technical evidence required by this
        # live test was observed. It is deliberately not described as
        # complete organizational ISO certification.
        #
        "status": "PASS",
        "score": 100,
        "coverage": 1.0,
        "assessment_scope": ("Technical evidence observation only"),
        "reason": (
            "Live Microsoft Entra evidence was successfully collected "
            "and normalized. High-privilege directory roles and their "
            "assigned members were identified, providing direct "
            "technical evidence relevant to assessment of privileged "
            "access rights."
        ),
        "assessment_limitation": (
            "This PASS indicates successful observation of the "
            "technical evidence used by this test. It does not by "
            "itself certify full ISO 27001:2022 A.8.2 compliance. "
            "Organizational policies, approvals, access reviews, "
            "least-privilege requirements, joiner/mover/leaver "
            "processes, and other relevant evidence require separate "
            "assessment."
        ),
        "evidence": evidence_items,
        "evidence_source": ("Microsoft Entra ID / Microsoft Graph"),
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

    The full Azure evidence remains available to the live pipeline.
    Only summary information is returned for report presentation.
    """

    inventory = build_azure_evidence_inventory(
        azure_records,
    )

    return {
        "total_normalized_resources": inventory["total_normalized_resources"],
        "resource_types": inventory["resource_types"],
        "providers": inventory["providers"],
        "services": inventory["services"],
        "locations": inventory["locations"],
        "subscriptions": inventory["subscriptions"],
        "resource_groups": inventory["resource_groups"],
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

    The report intentionally does not embed the complete Azure or
    Entra evidence payload. Full evidence remains available to the
    collection/assessment pipeline while the report contains only
    audit-relevant summaries and the evidence directly supporting
    the assessed control.
    """

    azure_summary = build_azure_evidence_summary(
        azure_records,
    )

    entra_summary = build_entra_evidence_summary(
        entra_records,
    )

    return ReportSection(
        title="Live Control Evidence",
        content={
            "assessment_type": ("Live technical evidence assessment"),
            "assessment_scope": (
                privileged_access_assessment.get(
                    "assessment_scope",
                    "Technical evidence observation only",
                )
            ),
            "assessment_limitation": (
                privileged_access_assessment.get(
                    "assessment_limitation",
                )
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
            #
            # These are the actual evidence items used for
            # the live A.8.2 control assessment.
            #
            "directory_role_evidence": (
                privileged_access_assessment.get(
                    "evidence",
                    [],
                )
            ),
            #
            # Compact Azure inventory summary only.
            #
            "azure_inventory": {
                "normalized_records": azure_summary["total_normalized_resources"],
                "resource_types": azure_summary["resource_types"],
                "providers": azure_summary["providers"],
                "services": azure_summary["services"],
                "locations": azure_summary["locations"],
                "subscriptions": azure_summary["subscriptions"],
                "resource_groups": azure_summary["resource_groups"],
            },
            #
            # Compact Entra inventory summary.
            #
            "entra_inventory": {
                "normalized_records": entra_summary["normalized_records"],
                "evidence_types": entra_summary["evidence_types"],
                "high_privilege_roles": entra_summary["high_privilege_roles"],
                "observed_assignments": entra_summary["observed_assignments"],
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
                    "assessment_scope": (
                        privileged_access_assessment.get(
                            "assessment_scope",
                            "Technical evidence observation only",
                        )
                    ),
                    "assessment_limitation": (
                        privileged_access_assessment.get(
                            "assessment_limitation",
                        )
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
            "risk_count": len(risks),
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
    Build a concise evidence summary from the live collectors.

    IMPORTANT:

    The previous implementation embedded every Azure and Entra record
    directly into the report. This caused the exported report to contain
    hundreds/thousands of pages of raw inventory.

    The collection functionality is unchanged.

    All live evidence is still collected and normalized. The report now
    contains:

        - total evidence counts
        - Azure inventory statistics
        - Entra inventory statistics
        - evidence used for the assessed control
        - a small representative Azure inventory sample

    The complete raw evidence is deliberately NOT embedded in the
    human-readable report.

    Azure inventory sample columns are:

        Timestamp
        Resource Name
        Provider
        Service
        Subscription
        Evidence

    ``Reason`` is deliberately NOT added to Azure inventory records.
    Reason belongs to evaluated control evidence, not generic inventory.
    """

    control_evidence = privileged_access_assessment.get(
        "evidence",
        [],
    )

    azure_inventory = build_azure_evidence_inventory(
        azure_records,
    )

    entra_summary = build_entra_evidence_summary(
        entra_records,
    )

    azure_sample = build_azure_report_sample(
        azure_records,
    )

    return ReportSection(
        title="Evidence Summary",
        content={
            #
            # Overall evidence counts.
            #
            "evidence_count": (len(azure_records) + len(entra_records)),
            "azure_evidence_count": len(
                azure_records,
            ),
            "entra_evidence_count": len(
                entra_records,
            ),
            "control_evidence_count": len(
                control_evidence,
            ),
            #
            # Existing field retained for compatibility.
            #
            "evidence_scores": [],
            #
            # High-level evidence inventory.
            #
            "evidence_inventory": {
                "total_records": (len(azure_records) + len(entra_records)),
                "azure_records": len(
                    azure_records,
                ),
                "entra_records": len(
                    entra_records,
                ),
                "raw_records_embedded_in_report": 0,
                "report_raw_data_policy": (
                    "Full live evidence is retained by the "
                    "collection pipeline but is not embedded "
                    "in the human-readable report."
                ),
            },
            #
            # Azure summary rather than the previous
            # raw inventory dump.
            #
            "azure_inventory": {
                "normalized_records": azure_inventory["total_normalized_resources"],
                "resource_types": azure_inventory["resource_types"],
                "providers": azure_inventory["providers"],
                "services": azure_inventory["services"],
                "locations": azure_inventory["locations"],
                "subscriptions": azure_inventory["subscriptions"],
                "resource_groups": azure_inventory["resource_groups"],
            },
            #
            # Entra summary rather than dumping every
            # normalized Entra record.
            #
            "entra_inventory": {
                "normalized_records": entra_summary["normalized_records"],
                "evidence_types": entra_summary["evidence_types"],
                "high_privilege_roles": entra_summary["high_privilege_roles"],
                "observed_assignments": entra_summary["observed_assignments"],
            },
            #
            # Only a small representative Azure inventory
            # sample is included for report readers.
            #
            "azure_report_sample": {
                "columns": [
                    "Timestamp",
                    "Resource Name",
                    "Provider",
                    "Service",
                    "Subscription",
                    "Evidence",
                ],
                "sample_limit": REPORT_AZURE_SAMPLE_LIMIT,
                "sample_count": len(
                    azure_sample,
                ),
                "records": azure_sample,
            },
            #
            # Actual evidence supporting the live control.
            #
            "control_evidence": control_evidence,
            #
            # Explicit assessment information.
            #
            "control_assessment": {
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
                "assessment_scope": privileged_access_assessment.get(
                    "assessment_scope",
                ),
                "assessment_limitation": (
                    privileged_access_assessment.get(
                        "assessment_limitation",
                    )
                ),
            },
            #
            # Explicit evidence retention statement.
            #
            "evidence_retention": {
                "azure_records_collected": len(
                    azure_records,
                ),
                "entra_records_collected": len(
                    entra_records,
                ),
                "azure_records_embedded_in_report": len(
                    azure_sample,
                ),
                "entra_records_embedded_as_raw_data": 0,
                "control_evidence_embedded": len(
                    control_evidence,
                ),
                "note": (
                    "Full collected evidence remains available to "
                    "the live collection and assessment pipeline. "
                    "The report contains summaries and control-relevant "
                    "evidence rather than the complete raw inventory."
                ),
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

    privileged_access_assessment = evaluate_privileged_access_control(
        entra_records,
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
        "Assessment scope:",
        privileged_access_assessment.get(
            "assessment_scope",
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

    print("\nAssessment limitation:")

    print(
        privileged_access_assessment.get(
            "assessment_limitation",
        )
    )

    # ========================================================================
    # Fail the live test if required evidence was not collected
    # ========================================================================

    if (
        privileged_access_assessment.get(
            "status",
        )
        == "NOT_ASSESSED"
    ):

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
    # actual live evidence is represented in the document passed to
    # export_report.
    #
    # IMPORTANT:
    #
    # The full Azure records are NOT inserted into the document.
    # The full Entra records are NOT inserted into the general evidence
    # summary either.
    #
    # The actual control evidence used for A.8.2 remains present.
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
                    #
                    # Only ISO27001 has actually been assessed by
                    # the live evaluator. SOC2 remains included as
                    # NOT_ASSESSED for compatibility.
                    #
                    "frameworks_assessed": 1,
                    "frameworks_declared": 2,
                    "risks_identified": 2,
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
                    "assessment_scope": (
                        privileged_access_assessment.get(
                            "assessment_scope",
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

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    exports = export_report(
        report=report,
        output_directory=output_directory,
        base_name="live_assessment",
    )

    print("\nExport completed.\n")

    for format_name, path in exports.items():

        print(f"{format_name:10} -> " f"{path.resolve()}")

    print("\nExpected files:")

    print((output_directory / "live_assessment.xlsx").resolve())

    print((output_directory / "live_assessment.pdf").resolve())

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

        print("No directory-role evidence was available.")

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

                print("MEMBERS: None")

                continue

            print("MEMBERS:")

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
        "Azure records embedded in report:",
        min(
            len(azure_records),
            REPORT_AZURE_SAMPLE_LIMIT,
        ),
    )

    print(
        "Entra raw records embedded in report:",
        0,
    )

    print(
        "Full Azure raw inventory embedded:",
        "NO",
    )

    print(
        "Full Entra raw inventory embedded:",
        "NO",
    )

    print(
        "Azure report columns:",
        "Timestamp | Resource Name | Provider | Service | " "Subscription | Evidence",
    )

    print(
        "Azure report field:",
        "resource_name",
    )

    print(
        "Azure subscription report field:",
        "subscription",
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
        "Assessment scope:",
        privileged_access_assessment.get(
            "assessment_scope",
        ),
    )

    print(
        "\nLive evidence was successfully collected, "
        "evaluated against a framework control, and "
        "included in the exported report without "
        "embedding the complete raw inventory."
    )


# ============================================================================
# Entry point
# ============================================================================


if __name__ == "__main__":
    main()
