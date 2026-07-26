# collectors\entra\normalizers\applications.py

"""
Microsoft Entra application normalizer.

Normalizes Microsoft Graph application
objects into a consistent evidence format.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .common import (
    normalize_datetime,
    remove_empty_values,
)


def normalize(
    application: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Normalize an Entra application object.

    Parameters
    ----------
    application:
        Raw Microsoft Graph application object.

    Returns
    -------
    Dict[str, Any]
        Normalized application evidence.
    """

    return remove_empty_values(
        {
            "id": application.get(
                "id"
            ),
            "type": "application",
            "provider": "entra",
            "display_name": application.get(
                "displayName"
            ),
            "application_id": application.get(
                "appId"
            ),
            "app_id": application.get(
                "appId"
            ),
            "publisher_domain": application.get(
                "publisherDomain"
            ),
            "created_date_time": normalize_datetime(
                application.get(
                    "createdDateTime"
                )
            ),
            "sign_in_audience": application.get(
                "signInAudience"
            ),
            "tags": application.get(
                "tags",
                [],
            ),
            "verified_publisher": normalize_publisher(
                application.get(
                    "verifiedPublisher"
                )
            ),
            "required_resource_access": application.get(
                "requiredResourceAccess",
                [],
            ),
            "owners": normalize_collection(
                application.get(
                    "owners",
                    [],
                )
            ),
        }
    )


def normalize_publisher(
    publisher: Dict[str, Any] | None,
) -> Dict[str, Any] | None:
    """
    Normalize verified publisher details.
    """

    if not publisher:
        return None

    return remove_empty_values(
        {
            "display_name": publisher.get(
                "displayName"
            ),
            "verified_id": publisher.get(
                "verifiedId"
            ),
            "added_date_time": normalize_datetime(
                publisher.get(
                    "addedDateTime"
                )
            ),
        }
    )


def normalize_collection(
    items: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Normalize Graph collections.
    """

    return [
        remove_empty_values(
            {
                "id": item.get(
                    "id"
                ),
                "display_name": item.get(
                    "displayName"
                ),
            }
        )
        for item in items
    ]
