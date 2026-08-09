# collectors\entra\normalizers\policies.py


"""
Microsoft Entra policy normalizer.

Normalizes Microsoft Graph policy objects
into a consistent evidence format.

Supports:
    - Conditional Access policies
    - Authentication policies
    - Directory policies
"""

from __future__ import annotations

from typing import Any, Dict

from .common import (
    normalize_boolean,
    normalize_datetime,
    remove_empty_values,
)


def normalize(
    policy: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Normalize a Microsoft Graph policy object.

    Parameters
    ----------
    policy:
        Raw Microsoft Graph policy object.

    Returns
    -------
    Dict[str, Any]
        Normalized policy evidence.
    """

    return remove_empty_values(
        {
            "id": policy.get(
                "id"
            ),
            "type": "policy",
            "provider": "entra",
            "policy_type": detect_policy_type(
                policy
            ),
            "display_name": policy.get(
                "displayName"
            ),
            "description": policy.get(
                "description"
            ),
            "created_date_time": normalize_datetime(
                policy.get(
                    "createdDateTime"
                )
            ),
            "modified_date_time": normalize_datetime(
                policy.get(
                    "modifiedDateTime"
                )
            ),
            "state": policy.get(
                "state"
            ),
            "enabled": normalize_boolean(
                policy.get(
                    "isEnabled"
                )
            ),
            "is_enabled": normalize_boolean(
                policy.get(
                    "isEnabled"
                )
            ),
            "conditions": normalize_conditions(
                policy.get(
                    "conditions"
                )
            ),
            "grant_controls": normalize_controls(
                policy.get(
                    "grantControls"
                )
            ),
            "session_controls": normalize_controls(
                policy.get(
                    "sessionControls"
                )
            ),
            "included_users": extract_include(
                policy,
                "users",
            ),
            "included_groups": extract_include(
                policy,
                "groups",
            ),
            "excluded_users": extract_exclude(
                policy,
                "users",
            ),
            "excluded_groups": extract_exclude(
                policy,
                "groups",
            ),
        }
    )


def normalize_conditional_access(
    policies: list[Dict[str, Any]],
) -> list[Dict[str, Any]]:
    """
    Normalize a collection of Microsoft Entra Conditional Access policies.

    Parameters
    ----------
    policies:
        List of raw Microsoft Graph Conditional Access policy objects.

    Returns
    -------
    list[Dict[str, Any]]
        Normalized Conditional Access policy evidence records.
    """

    return [normalize(policy) for policy in policies if policy]


def detect_policy_type(
    policy: Dict[str, Any],
) -> str:
    """
    Detect Microsoft Entra policy category.
    """

    policy_name = (
        policy.get(
            "displayName"
        )
        or ""
    ).lower()

    if (
        "conditional"
        in policy_name
    ):
        return "conditional_access"

    if (
        "authentication"
        in policy_name
    ):
        return "authentication"

    if (
        "directory"
        in policy_name
    ):
        return "directory"

    if (
        "conditions"
        in policy
        or "grantControls"
        in policy
    ):
        return "conditional_access"

    return "unknown"


def normalize_conditions(
    conditions: Dict[str, Any] | None,
) -> Dict[str, Any] | None:
    """
    Normalize Conditional Access conditions.
    """

    if not conditions:
        return None

    return remove_empty_values(
        {
            "users": conditions.get(
                "users"
            ),
            "applications": conditions.get(
                "applications"
            ),
            "platforms": conditions.get(
                "platforms"
            ),
            "locations": conditions.get(
                "locations"
            ),
            "client_app_types": conditions.get(
                "clientAppTypes"
            ),
            "devices": conditions.get(
                "devices"
            ),
            "risk_levels": (
                conditions.get(
                    "signInRiskLevels"
                )
                or conditions.get(
                    "userRiskLevels"
                )
            ),
        }
    )


def normalize_controls(
    controls: Dict[str, Any] | None,
) -> Dict[str, Any] | None:
    """
    Normalize policy control settings.
    """

    if not controls:
        return None

    return remove_empty_values(
        {
            "operator": controls.get(
                "operator"
            ),
            "built_in_controls": controls.get(
                "builtInControls",
                [],
            ),
            "custom_authentication_factors": controls.get(
                "customAuthenticationFactors",
                [],
            ),
            "terms_of_use": controls.get(
                "termsOfUse",
                [],
            ),
            "authentication_strength": controls.get(
                "authenticationStrength"
            ),
        }
    )


def extract_include(
    policy: Dict[str, Any],
    resource: str,
) -> list[str]:
    """
    Extract included policy assignments.
    """

    return (
        policy.get(
            "conditions",
            {},
        )
        .get(
            "users",
            {},
        )
        .get(
            f"include{resource.title()}",
            [],
        )
    )


def extract_exclude(
    policy: Dict[str, Any],
    resource: str,
) -> list[str]:
    """
    Extract excluded policy assignments.
    """

    return (
        policy.get(
            "conditions",
            {},
        )
        .get(
            "users",
            {},
        )
        .get(
            f"exclude{resource.title()}",
            [],
        )
    )
