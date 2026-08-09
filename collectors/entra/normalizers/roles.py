# collectors\entra\normalizers\roles.py


"""
Microsoft Entra role normalizer.

Normalizes Microsoft Graph directory role
objects into a consistent evidence format.
"""

from __future__ import annotations

from typing import Any, Dict

from .common import (
    normalize_datetime,
    remove_empty_values,
)

#
# Directory roles that represent elevated
# administrative privileges in Microsoft Entra ID.
#
# Used for GRC classification and reporting.
#
HIGH_PRIVILEGE_DIRECTORY_ROLES = {
    "Global Administrator",
    "Privileged Role Administrator",
    "Security Administrator",
    "Conditional Access Administrator",
    "Exchange Administrator",
    "SharePoint Administrator",
    "User Administrator",
    "Authentication Administrator",
    "Application Administrator",
    "Cloud Application Administrator",
}


def normalize(
    role: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Normalize a Microsoft Graph directory role.

    Parameters
    ----------
    role:
        Raw Microsoft Graph directory role object.

    Returns
    -------
    Dict[str, Any]
        Normalized role evidence.
    """

    return remove_empty_values(
        {
            "id": role.get("id"),
            "type": "role",
            "provider": "entra",
            "name": role.get("displayName"),
            "display_name": role.get("displayName"),
            #
            # GRC classification flag.
            #
            # Identifies roles requiring privileged
            # access monitoring and review.
            #
            "is_high_privilege": (
                role.get("displayName") in HIGH_PRIVILEGE_DIRECTORY_ROLES
            ),
            "description": role.get("description"),
            "role_template_id": role.get("roleTemplateId"),
            "deleted_date_time": normalize_datetime(role.get("deletedDateTime")),
            "members": normalize_members(
                role.get(
                    "members",
                    [],
                )
            ),
            "assignment_count": len(
                role.get(
                    "members",
                    [],
                )
            ),
        }
    )


def normalize_directory_roles(
    roles: list[Dict[str, Any]],
) -> list[Dict[str, Any]]:
    """
    Normalize a collection of Microsoft Entra directory roles.

    Parameters
    ----------
    roles:
        List of raw Microsoft Graph directory role objects.

    Returns
    -------
    list[Dict[str, Any]]
        Normalized directory role evidence records.
    """

    return [normalize(role) for role in roles if role]


def normalize_members(
    members: list[Dict[str, Any]],
) -> list[Dict[str, Any]]:
    """
    Normalize role members.

    Directory role members may be:
        - Users
        - Groups
        - Service principals
    """

    return [
        remove_empty_values(
            {
                "id": member.get("id"),
                "display_name": member.get("displayName"),
                "upn": member.get("userPrincipalName"),
                "user_principal_name": member.get("userPrincipalName"),
                "app_id": member.get("appId"),
                "type": resolve_type(member),
                "object_type": member.get("@odata.type"),
                "role_member_type": resolve_type(member),
            }
        )
        for member in members
    ]


def resolve_type(
    member: Dict[str, Any],
) -> str | None:
    """
    Resolve directory role member type.
    """

    object_type = member.get("@odata.type")

    if not object_type:
        return None

    mapping = {
        "#microsoft.graph.user": "user",
        "#microsoft.graph.group": "group",
        "#microsoft.graph.servicePrincipal": "service_principal",
        "#microsoft.graph.device": "device",
    }

    if object_type in mapping:
        return mapping[object_type]

    return object_type.replace(
        "#microsoft.graph.",
        "",
    ).lower()
