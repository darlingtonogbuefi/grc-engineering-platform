<#
    modules\authentication\Connect-Azure.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Azure Resource Manager authentication module.

.DESCRIPTION
    Provides reusable authentication functions for Azure Resource
    Manager using the Az PowerShell modules.

    Supported authentication methods:

    - Interactive
    - Device Code
    - Managed Identity
    - Service Principal (Certificate)
    - Service Principal (Secret)

.NOTES
    GRC Engineering Platform
    Version: 1.0.0

    Required Modules:
      Az.Accounts
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"



#region Dependencies

Import-Module Az.Accounts -ErrorAction Stop

#endregion



#region Connection


function Connect-AzureTenant {

    [CmdletBinding(DefaultParameterSetName = "Interactive")]

    param(

        [Parameter(ParameterSetName = "Interactive")]
        [switch]
        $Interactive,


        [Parameter(ParameterSetName = "DeviceCode")]
        [switch]
        $DeviceCode,


        [Parameter(ParameterSetName = "ManagedIdentity")]
        [switch]
        $ManagedIdentity,


        [Parameter(ParameterSetName = "Certificate")]
        [string]
        $TenantId,


        [Parameter(ParameterSetName = "Certificate")]
        [string]
        $ApplicationId,


        [Parameter(ParameterSetName = "Certificate")]
        [string]
        $CertificateThumbprint,


        [Parameter(ParameterSetName = "Secret")]
        [string]
        $ClientSecret,


        [Parameter(ParameterSetName = "Secret")]
        [pscredential]
        $Credential,


        [string]
        $SubscriptionId

    )


    switch ($PSCmdlet.ParameterSetName) {

        "Interactive" {

            Connect-AzAccount

        }

        "DeviceCode" {

            Connect-AzAccount `
                -UseDeviceAuthentication

        }

        "ManagedIdentity" {

            Connect-AzAccount `
                -Identity

        }

        "Certificate" {

            Connect-AzAccount `
                -ServicePrincipal `
                -Tenant $TenantId `
                -ApplicationId $ApplicationId `
                -CertificateThumbprint $CertificateThumbprint

        }

        "Secret" {

            Connect-AzAccount `
                -ServicePrincipal `
                -Tenant $TenantId `
                -Credential $Credential

        }

    }


    if ($SubscriptionId) {

        Set-AzureSubscription `
            -SubscriptionId $SubscriptionId

    }


    return Get-AzureContext

}



function Disconnect-AzureTenant {

    [CmdletBinding()]

    param()

    Disconnect-AzAccount `
        -ErrorAction SilentlyContinue

    Clear-AzContext `
        -Force `
        -ErrorAction SilentlyContinue

}



#endregion



#region Context


function Get-AzureContext {

    [CmdletBinding()]

    param()

    $context =
        Get-AzContext

    if ($null -eq $context) {

        return $null

    }


    [PSCustomObject]@{

        TenantId =
        $context.Tenant.Id

        SubscriptionId =
        $context.Subscription.Id

        SubscriptionName =
        $context.Subscription.Name

        Account =
        $context.Account.Id

        Environment =
        $context.Environment.Name

    }

}



function Test-AzureConnection {

    [CmdletBinding()]

    param()

    try {

        $null =
            Get-AzContext

        return $true

    }

    catch {

        return $false

    }

}



#endregion



#region Subscription


function Set-AzureSubscription {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $SubscriptionId

    )

    Set-AzContext `
        -SubscriptionId $SubscriptionId |
    Out-Null

}



function Get-AzureSubscriptions {

    [CmdletBinding()]

    param()

    Get-AzSubscription |
    Sort-Object Name

}



#endregion



#region Tenant


function Get-AzureTenants {

    [CmdletBinding()]

    param()

    Get-AzTenant |
    Sort-Object Name

}



#endregion



#region Validation


function Test-AzureSubscription {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $SubscriptionId

    )


    return (

        Get-AzSubscription |
        Where-Object {

            $_.Id -eq $SubscriptionId

        }

    ) -ne $null

}



#endregion



Export-ModuleMember `
    -Function `
        Connect-AzureTenant,
        Disconnect-AzureTenant,
        Get-AzureContext,
        Test-AzureConnection,
        Set-AzureSubscription,
        Get-AzureSubscriptions,
        Get-AzureTenants,
        Test-AzureSubscription
