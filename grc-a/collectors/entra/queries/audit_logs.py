# collectors\entra\queries\audit_logs.py


"""
Microsoft Entra audit logs query.

Provides Microsoft Graph query definitions
for collecting directory audit log evidence.
"""

from __future__ import annotations

from typing import Any, Dict


NAME = "audit_logs"

METHOD = "GET"

ENDPOINT = "/auditLogs/directoryAudits"


SELECT_FIELDS = [
    "id",
    "activityDisplayName",
    "category",
    "operationType",
    "result",
    "resultReason",
    "loggedByService",
    "initiatedBy",
    "targetResources",
    "correlationId",
    "activityDateTime",
]

EXPAND_FIELDS: list[str] = []

FILTER: str | None = None

ORDER_BY = "activityDateTime desc"

TOP: int | None = None

PERMISSIONS = [
    "AuditLog.Read.All",
]


def build_params() -> Dict[str, Any]:
    """
    Build Microsoft Graph query parameters.
    """

    params: Dict[str, Any] = {}

    if SELECT_FIELDS:
        params["$select"] = ",".join(
            SELECT_FIELDS
        )

    if EXPAND_FIELDS:
        params["$expand"] = ",".join(
            EXPAND_FIELDS
        )

    if FILTER:
        params["$filter"] = FILTER

    if ORDER_BY:
        params["$orderby"] = ORDER_BY

    if TOP:
        params["$top"] = TOP

    return params


def query() -> Dict[str, Any]:
    """
    Return audit logs query definition.
    """

    return {
        "name": NAME,
        "endpoint": ENDPOINT,
        "method": METHOD,
        "params": build_params(),
    }


def endpoint() -> str:
    """
    Return Microsoft Graph endpoint.
    """

    return ENDPOINT


def select_fields() -> list[str]:
    """
    Return selected fields.
    """

    return SELECT_FIELDS


def permissions() -> list[str]:
    """
    Return required Microsoft Graph
    application permissions.
    """

    return PERMISSIONS


def method() -> str:
    """
    Return HTTP method.
    """

    return METHOD
