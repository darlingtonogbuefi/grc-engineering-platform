#collectors\entra\queries\privileged_identity_management.py


"""
Microsoft Entra Privileged Identity Management query.

Provides Microsoft Graph query definitions
for collecting privileged access management
evidence.
"""

from __future__ import annotations

from typing import Any, Dict


NAME = "privileged_identity_management"

METHOD = "GET"

ENDPOINT = "/roleManagement"


ROLE_ASSIGNMENTS_ENDPOINT = (
    "/roleManagement/directory/"
    "roleAssignments"
)

ROLE_ELIGIBILITY_ENDPOINT = (
    "/roleManagement/directory/"
    "roleEligibilitySchedules"
)

ROLE_SCHEDULES_ENDPOINT = (
    "/roleManagement/directory/"
    "roleAssignmentSchedules"
)


SELECT_FIELDS = [
    "id",
    "principalId",
    "roleDefinitionId",
    "directoryScopeId",
    "status",
    "createdDateTime",
    "modifiedDateTime",
]


EXPAND_FIELDS: list[str] = []

FILTER: str | None = None

ORDER_BY: str | None = None

TOP: int | None = None

PERMISSIONS = [
    "RoleManagement.Read.Directory",
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
    Return privileged identity management
    query definition.
    """

    return {
        "name": NAME,
        "endpoint": ROLE_ASSIGNMENTS_ENDPOINT,
        "method": METHOD,
        "params": build_params(),
    }


def endpoint() -> str:
    """
    Return base Graph endpoint.
    """

    return ENDPOINT


def role_assignments_endpoint() -> str:
    """
    Return active role assignments endpoint.
    """

    return ROLE_ASSIGNMENTS_ENDPOINT


def role_eligibility_endpoint() -> str:
    """
    Return eligible role assignments endpoint.
    """

    return ROLE_ELIGIBILITY_ENDPOINT


def role_schedules_endpoint() -> str:
    """
    Return scheduled role assignments endpoint.
    """

    return ROLE_SCHEDULES_ENDPOINT


def select_fields() -> list[str]:
    """
    Return selected fields.
    """

    return SELECT_FIELDS


def expand_fields() -> list[str]:
    """
    Return expanded relationships.
    """

    return EXPAND_FIELDS


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
