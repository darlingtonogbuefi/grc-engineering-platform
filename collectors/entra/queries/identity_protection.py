#collectors\entra\queries\identity_protection.py

"""
Microsoft Entra Identity Protection query.

Provides Microsoft Graph query definitions
for collecting risky user and identity risk
evidence.
"""

from __future__ import annotations

from typing import Any, Dict


NAME = "identity_protection"

METHOD = "GET"

ENDPOINT = "/identityProtection/riskyUsers"


SELECT_FIELDS = [
    "id",
    "userDisplayName",
    "userPrincipalName",
    "riskLevel",
    "riskState",
    "riskDetail",
    "riskLastUpdatedDateTime",
    "isDeleted",
    "userId",
]


EXPAND_FIELDS: list[str] = []

FILTER: str | None = None

ORDER_BY = "riskLastUpdatedDateTime desc"

TOP: int | None = None

PERMISSIONS = [
    "IdentityRiskyUser.Read.All",
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
    Return Identity Protection query definition.
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
