#collectors\entra\normalizers\users.py


"""
Microsoft Entra user normalizer.

Normalizes Microsoft Graph user objects
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
    user: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Normalize a Microsoft Graph user object.

    Parameters
    ----------
    user:
        Raw Microsoft Graph user object.

    Returns
    -------
    Dict[str, Any]
        Normalized user evidence.
    """

    return remove_empty_values(
        {
            "id": user.get(
                "id"
            ),
            "type": "user",
            "provider": "entra",
            "display_name": user.get(
                "displayName"
            ),
            "upn": user.get(
                "userPrincipalName"
            ),
            "user_principal_name": user.get(
                "userPrincipalName"
            ),
            "mail": user.get(
                "mail"
            ),
            "given_name": user.get(
                "givenName"
            ),
            "surname": user.get(
                "surname"
            ),
            "job_title": user.get(
                "jobTitle"
            ),
            "department": user.get(
                "department"
            ),
            "company_name": user.get(
                "companyName"
            ),
            "employee_id": user.get(
                "employeeId"
            ),
            "employee_type": user.get(
                "employeeType"
            ),
            "enabled": normalize_boolean(
                user.get(
                    "accountEnabled"
                )
            ),
            "account_enabled": normalize_boolean(
                user.get(
                    "accountEnabled"
                )
            ),
            "user_type": user.get(
                "userType"
            ),
            "usage_location": user.get(
                "usageLocation"
            ),
            "office_location": user.get(
                "officeLocation"
            ),
            "city": user.get(
                "city"
            ),
            "state": user.get(
                "state"
            ),
            "country": user.get(
                "country"
            ),
            "created_date_time": normalize_datetime(
                user.get(
                    "createdDateTime"
                )
            ),
            "last_sign_in": normalize_sign_in(
                user
            ),
            "licenses": normalize_licenses(
                user.get(
                    "assignedLicenses",
                    [],
                )
            ),
            "assigned_licenses": normalize_licenses(
                user.get(
                    "assignedLicenses",
                    [],
                )
            ),
            "service_plans": normalize_plans(
                user.get(
                    "assignedPlans",
                    [],
                )
            ),
            "assigned_plans": normalize_plans(
                user.get(
                    "assignedPlans",
                    [],
                )
            ),
            "authentication_methods": normalize_methods(
                user.get(
                    "authenticationMethods",
                    [],
                )
            ),
        }
    )


def normalize_sign_in(
    user: Dict[str, Any],
) -> Dict[str, Any] | None:
    """
    Normalize sign-in activity.
    """

    activity = user.get(
        "signInActivity"
    )

    if not activity:
        return None

    return remove_empty_values(
        {
            "last_sign_in_date_time": normalize_datetime(
                activity.get(
                    "lastSignInDateTime"
                )
            ),
            "last_non_interactive_sign_in_date_time": normalize_datetime(
                activity.get(
                    "lastNonInteractiveSignInDateTime"
                )
            ),
        }
    )


def normalize_licenses(
    licenses: list[Dict[str, Any]],
) -> list[Dict[str, Any]]:
    """
    Normalize assigned licenses.
    """

    return [
        remove_empty_values(
            {
                "sku_id": license.get(
                    "skuId"
                ),
                "disabled_plans": license.get(
                    "disabledPlans",
                    [],
                ),
            }
        )
        for license in licenses
    ]


def normalize_plans(
    plans: list[Dict[str, Any]],
) -> list[Dict[str, Any]]:
    """
    Normalize assigned service plans.
    """

    return [
        remove_empty_values(
            {
                "service": plan.get(
                    "service"
                ),
                "service_plan_id": plan.get(
                    "servicePlanId"
                ),
                "capability_status": plan.get(
                    "capabilityStatus"
                ),
            }
        )
        for plan in plans
    ]


def normalize_methods(
    methods: list[Dict[str, Any]],
) -> list[Dict[str, Any]]:
    """
    Normalize authentication methods.
    """

    return [
        remove_empty_values(
            {
                "id": method.get(
                    "id"
                ),
                "method": normalize_method_type(
                    method.get(
                        "@odata.type"
                    )
                ),
                "type": normalize_method_type(
                    method.get(
                        "@odata.type"
                    )
                ),
                "display_name": method.get(
                    "displayName"
                ),
            }
        )
        for method in methods
    ]


def normalize_method_type(
    method_type: str | None,
) -> str | None:
    """
    Normalize Microsoft Graph authentication
    method types into platform-friendly values.
    """

    if not method_type:
        return None

    mapping = {
        "#microsoft.graph.passwordAuthenticationMethod": "password",
        "#microsoft.graph.microsoftAuthenticatorAuthenticationMethod": "microsoft_authenticator",
        "#microsoft.graph.fido2AuthenticationMethod": "fido2",
        "#microsoft.graph.phoneAuthenticationMethod": "phone",
        "#microsoft.graph.emailAuthenticationMethod": "email",
        "#microsoft.graph.softwareOathAuthenticationMethod": "software_oath",
        "#microsoft.graph.temporaryAccessPassAuthenticationMethod": "temporary_access_pass",
        "#microsoft.graph.windowsHelloForBusinessAuthenticationMethod": "windows_hello_for_business",
    }

    return mapping.get(
        method_type,
        method_type.rsplit(
            ".",
            1,
        )[-1].removesuffix(
            "AuthenticationMethod"
        ).lower(),
    )
