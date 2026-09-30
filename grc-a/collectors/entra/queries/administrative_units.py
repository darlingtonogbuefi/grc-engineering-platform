# collectors\entra\queries\administrative_units.py


"""
Microsoft Entra administrative units query.

Provides Microsoft Graph query definitions
for collecting administrative unit evidence.
"""

from __future__ import annotations

from typing import Any, Dict


NAME = "administrative_units"

METHOD = "GET"

ENDPOINT = "/administrativeUnits"


SELECT_FIELDS = [
    "id",
    "displayName",
    "description",
    "visibility",
    "isMemberManagementRestricted",
    "createdDateTime",
]

EXPAND_FIELDS: list[str] = []

FILTER: str | None = None

ORDER_BY: str | None = None

TOP: int | None = None

PERMISSIONS = [
    "AdministrativeUnit.Read.All",
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
    Return administrative units query definition.

    Returns
    -------
    Dict[str, Any]
        Microsoft Graph query configuration.
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
    Return fields requested from Graph.
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
