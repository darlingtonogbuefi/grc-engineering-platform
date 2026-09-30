# collectors\entra\normalizers\logs.py

"""
Microsoft Entra log normalizer.

Normalizes Microsoft Graph audit and sign-in
log objects into a consistent evidence format.
"""

from __future__ import annotations

from typing import Any, Dict

from .common import (
    normalize_boolean,
    normalize_datetime,
    remove_empty_values,
)


def normalize(
    log: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Normalize a Microsoft Graph log object.

    Supports:
        - Audit logs
        - Sign-in logs

    Parameters
    ----------
    log:
        Raw Microsoft Graph log object.

    Returns
    -------
    Dict[str, Any]
        Normalized log evidence.
    """

    return remove_empty_values(
        {
            "id": log.get(
                "id"
            ),
            "type": "log",
            "provider": "entra",
            "created_date_time": normalize_datetime(
                log.get(
                    "createdDateTime"
                )
            ),
            "activity_display_name": log.get(
                "activityDisplayName"
            ),
            "category": log.get(
                "category"
            ),
            "operation_type": log.get(
                "operationType"
            ),
            "event_type": (
                log.get(
                    "category"
                )
                or log.get(
                    "operationType"
                )
            ),
            "result": log.get(
                "result"
            ),
            "result_reason": log.get(
                "resultReason"
            ),
            "correlation_id": log.get(
                "correlationId"
            ),
            "logged_by_service": log.get(
                "loggedByService"
            ),
            "initiated_by": normalize_initiated_by(
                log.get(
                    "initiatedBy"
                )
            ),
            "target_resources": normalize_targets(
                log.get(
                    "targetResources",
                    [],
                )
            ),
            "upn": extract_user(
                log
            ),
            "user_principal_name": extract_user(
                log
            ),
            "ip_address": log.get(
                "ipAddress"
            ),
            "client_app_used": log.get(
                "clientAppUsed"
            ),
            "conditional_access_status": log.get(
                "conditionalAccessStatus"
            ),
            "authentication_requirement": log.get(
                "authenticationRequirement"
            ),
            "risk_level": (
                log.get(
                    "riskLevelAggregated"
                )
                or log.get(
                    "riskLevelDuringSignIn"
                )
            ),
            "risk_state": log.get(
                "riskState"
            ),
            "location": normalize_location(
                log.get(
                    "location"
                )
            ),
            "device_detail": normalize_device(
                log.get(
                    "deviceDetail"
                )
            ),
        }
    )


def normalize_audit_logs(
    logs: list[Dict[str, Any]],
) -> list[Dict[str, Any]]:
    """
    Normalize a collection of Microsoft Entra audit logs.

    Parameters
    ----------
    logs:
        List of raw Microsoft Graph audit log objects.

    Returns
    -------
    list[Dict[str, Any]]
        Normalized audit log evidence records.
    """

    return [normalize(log) for log in logs if log]


def normalize_sign_ins(
    logs: list[Dict[str, Any]],
) -> list[Dict[str, Any]]:
    """
    Normalize a collection of Microsoft Entra sign-in logs.

    Parameters
    ----------
    logs:
        List of raw Microsoft Graph sign-in log objects.

    Returns
    -------
    list[Dict[str, Any]]
        Normalized sign-in log evidence records.
    """

    return [normalize(log) for log in logs if log]


def normalize_initiated_by(
    initiated_by: Dict[str, Any] | None,
) -> Dict[str, Any] | None:
    """
    Normalize audit log initiator.
    """

    if not initiated_by:
        return None

    return remove_empty_values(
        {
            "user": normalize_identity(
                initiated_by.get(
                    "user"
                )
            ),
            "app": normalize_identity(
                initiated_by.get(
                    "app"
                )
            ),
        }
    )


def normalize_identity(
    identity: Dict[str, Any] | None,
) -> Dict[str, Any] | None:
    """
    Normalize user/application identity.
    """

    if not identity:
        return None

    return remove_empty_values(
        {
            "id": identity.get(
                "id"
            ),
            "display_name": identity.get(
                "displayName"
            ),
            "upn": identity.get(
                "userPrincipalName"
            ),
            "user_principal_name": identity.get(
                "userPrincipalName"
            ),
            "app_id": identity.get(
                "appId"
            ),
        }
    )


def normalize_targets(
    targets: list[Dict[str, Any]],
) -> list[Dict[str, Any]]:
    """
    Normalize audit target resources.
    """

    return [
        remove_empty_values(
            {
                "id": target.get(
                    "id"
                ),
                "display_name": target.get(
                    "displayName"
                ),
                "type": target.get(
                    "type"
                ),
            }
        )
        for target in targets
    ]


def normalize_location(
    location: Dict[str, Any] | None,
) -> Dict[str, Any] | None:
    """
    Normalize sign-in location.
    """

    if not location:
        return None

    return remove_empty_values(
        {
            "city": location.get(
                "city"
            ),
            "state": location.get(
                "state"
            ),
            "country_or_region": location.get(
                "countryOrRegion"
            ),
            "geo_coordinates": location.get(
                "geoCoordinates"
            ),
        }
    )


def normalize_device(
    device: Dict[str, Any] | None,
) -> Dict[str, Any] | None:
    """
    Normalize sign-in device details.
    """

    if not device:
        return None

    return remove_empty_values(
        {
            "device_id": device.get(
                "deviceId"
            ),
            "display_name": device.get(
                "displayName"
            ),
            "operating_system": device.get(
                "operatingSystem"
            ),
            "browser": device.get(
                "browser"
            ),
            "is_compliant": normalize_boolean(
                device.get(
                    "isCompliant"
                )
            ),
            "is_managed": normalize_boolean(
                device.get(
                    "isManaged"
                )
            ),
        }
    )


def extract_user(
    log: Dict[str, Any],
) -> str | None:
    """
    Extract user principal name from
    audit or sign-in logs.

    Audit logs may be initiated by either
    a user or an application. Handle both
    safely.
    """

    #
    # Sign-in logs expose the UPN directly.
    #
    if log.get("userPrincipalName"):
        return log.get("userPrincipalName")

    initiated_by = log.get("initiatedBy") or {}

    user = initiated_by.get("user") or {}

    return user.get("userPrincipalName")
