#collectors\entra\normalizers\devices.py#

"""
Microsoft Entra device normalizer.

Normalizes Microsoft Graph device objects
into a consistent evidence format.
"""

from __future__ import annotations

from typing import Any, Dict

from .common import (
    normalize_boolean,
    normalize_collection,
    normalize_datetime,
    remove_empty_values,
)


def normalize(
    device: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Normalize a Microsoft Graph device object.

    Parameters
    ----------
    device:
        Raw Microsoft Graph device object.

    Returns
    -------
    Dict[str, Any]
        Normalized device evidence.
    """

    return remove_empty_values(
        {
            "id": device.get(
                "id"
            ),
            "type": "device",
            "provider": "entra",
            "display_name": device.get(
                "displayName"
            ),
            "device_id": device.get(
                "deviceId"
            ),
            "operating_system": device.get(
                "operatingSystem"
            ),
            "operating_system_version": device.get(
                "operatingSystemVersion"
            ),
            "trust_type": device.get(
                "trustType"
            ),
            "enabled": normalize_boolean(
                device.get(
                    "accountEnabled"
                )
            ),
            "account_enabled": normalize_boolean(
                device.get(
                    "accountEnabled"
                )
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
            "management_type": device.get(
                "managementType"
            ),
            "manufacturer": device.get(
                "manufacturer"
            ),
            "model": device.get(
                "model"
            ),
            "serial_number": device.get(
                "serialNumber"
            ),
            "physical_ids": device.get(
                "physicalIds",
                [],
            ),
            "registered_owners": normalize_collection(
                device.get(
                    "registeredOwners",
                    [],
                )
            ),
            "registered_users": normalize_collection(
                device.get(
                    "registeredUsers",
                    [],
                )
            ),
            "approximate_last_sign_in": normalize_datetime(
                device.get(
                    "approximateLastSignInDateTime"
                )
            ),
            "created_date_time": normalize_datetime(
                device.get(
                    "createdDateTime"
                )
            ),
            "alternative_security_ids": device.get(
                "alternativeSecurityIds",
                [],
            ),
        }
    )
