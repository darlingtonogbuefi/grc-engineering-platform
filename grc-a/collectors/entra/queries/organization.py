#collectors\entra\queries\organization.py


"""
Microsoft Entra organization query.

Provides Microsoft Graph query definitions
for collecting tenant organization evidence.
"""

from __future__ import annotations

from typing import Any, Dict


NAME = "organization"

METHOD = "GET"

ENDPOINT = "/organization"


SELECT_FIELDS = [
    "id",
    "displayName",
    "verifiedDomains",
    "tenantType",
    "defaultUsageLocation",
    "businessPhones",
    "countryLetterCode",
    "country",
    "city",
    "technicalNotificationMails",
    "securityComplianceNotificationMails",
]


EXPAND_FIELDS: list[str] = []

FILTER: str | None = None

ORDER_BY: str | None = None

TOP: int | None = None

PERMISSIONS = [
    "Organization.Read.All",
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
    Return organization query definition.
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
