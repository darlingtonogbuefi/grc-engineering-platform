#collectors\entra\queries\enterprise_apps.py



"""
Microsoft Entra enterprise applications query.

Provides Microsoft Graph query definitions
for collecting enterprise application
(service principal) evidence.
"""

from __future__ import annotations

from typing import Any, Dict


NAME = "enterprise_apps"

METHOD = "GET"

ENDPOINT = "/servicePrincipals"


SELECT_FIELDS = [
    "id",
    "appId",
    "displayName",
    "servicePrincipalType",
    "accountEnabled",
    "appDisplayName",
    "appOwnerOrganizationId",
    "publisherName",
    "homepage",
    "loginUrl",
    "preferredSingleSignOnMode",
    "preferredTokenSigningKeyThumbprint",
    "tags",
]


EXPAND_FIELDS = [
    "owners",
]

FILTER: str | None = None

ORDER_BY: str | None = None

TOP: int | None = None

PERMISSIONS = [
    "Application.Read.All",
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
    Return enterprise applications query definition.
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
