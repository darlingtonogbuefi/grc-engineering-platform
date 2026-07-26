"""
Microsoft Entra group normalizer.

Normalizes Microsoft Graph group objects
into a consistent evidence format.
"""

from __future__ import annotations

from typing import Any, Dict

from .common import (
    normalize_boolean,
    normalize_datetime,
    remove_empty_values,
)


def normalize(
    group: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Normalize a Microsoft Graph group object.

    Parameters
    ----------
    group:
        Raw Microsoft Graph group object.

    Returns
    -------
    Dict[str, Any]
        Normalized group evidence.
    """

    return remove_empty_values(
        {
            "id": group.get(
                "id"
            ),
            "type": "group",
            "provider": "entra",
            "display_name": group.get(
                "displayName"
            ),
            "description": group.get(
                "description"
            ),
            "group_types": group.get(
                "groupTypes",
                [],
            ),
            "mail": group.get(
                "mail"
            ),
            "mail_enabled": normalize_boolean(
                group.get(
                    "mailEnabled"
                )
            ),
            "mail_nickname": group.get(
                "mailNickname"
            ),
            "security_enabled": normalize_boolean(
                group.get(
                    "securityEnabled"
                )
            ),
            "visibility": group.get(
                "visibility"
            ),
            "membership_rule": group.get(
                "membershipRule"
            ),
            "membership_rule_processing_state": group.get(
                "membershipRuleProcessingState"
            ),
            "is_assignable_to_role": normalize_boolean(
                group.get(
                    "isAssignableToRole"
                )
            ),
            "created_date_time": normalize_datetime(
                group.get(
                    "createdDateTime"
                )
            ),
            "expiration_date_time": normalize_datetime(
                group.get(
                    "expirationDateTime"
                )
            ),
            "renewed_date_time": normalize_datetime(
                group.get(
                    "renewedDateTime"
                )
            ),
            "resource_behavior_options": group.get(
                "resourceBehaviorOptions",
                [],
            ),
            "resource_provisioning_options": group.get(
                "resourceProvisioningOptions",
                [],
            ),
            "owners": normalize_members(
                group.get(
                    "owners",
                    [],
                )
            ),
            "members": normalize_members(
                group.get(
                    "members",
                    [],
                )
            ),
        }
    )


def normalize_members(
    members: list[Dict[str, Any]],
) -> list[Dict[str, Any]]:
    """
    Normalize group members and owners.
    """

    return [
        remove_empty_values(
            {
                "id": member.get(
                    "id"
                ),
                "display_name": member.get(
                    "displayName"
                ),
                "upn": member.get(
                    "userPrincipalName"
                ),
                "user_principal_name": member.get(
                    "userPrincipalName"
                ),
                "type": normalize_object_type(
                    member.get(
                        "@odata.type"
                    )
                ),
                "object_type": member.get(
                    "@odata.type"
                ),
            }
        )
        for member in members
    ]


def normalize_object_type(
    object_type: str | None,
) -> str | None:
    """
    Normalize Microsoft Graph object types
    into platform-friendly values.
    """

    if not object_type:
        return None

    mapping = {
        "#microsoft.graph.user": "user",
        "#microsoft.graph.group": "group",
        "#microsoft.graph.device": "device",
        "#microsoft.graph.servicePrincipal": "service_principal",
        "#microsoft.graph.orgContact": "contact",
    }

    return mapping.get(
        object_type,
        object_type.rsplit(
            ".",
            1,
        )[-1],
    )

