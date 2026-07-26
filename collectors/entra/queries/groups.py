#collectors\entra\queries\groups.py


"""
Microsoft Entra groups query.

Provides Microsoft Graph query definitions
for collecting group evidence.
"""

from __future__ import annotations

from typing import Any, Dict


NAME = "groups"

METHOD = "GET"

ENDPOINT = "/groups"


SELECT_FIELDS = [
    "id",
    "displayName",
    "description",
    "mail",
    "mailEnabled",
    "securityEnabled",
    "groupTypes",
    "membershipRule",
    "membershipRuleProcessingState",
    "visibility",
    "createdDateTime",
    "deletedDateTime",
]


EXPAND_FIELDS = [
    "members",
    "owners",
]

FILTER: str | None = None

ORDER_BY: str | None = None

TOP: int | None = None

PERMISSIONS = [
    "Group.Read.All",
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
    Return groups query definition.
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
