<#
    modules\authentication\Connect-Entra.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Microsoft Entra ID authentication module.

.DESCRIPTION
    Provides reusable authentication functions for Microsoft Graph
    using the Microsoft Graph PowerShell SDK.

    Supported authentication methods:

    - Interactive
    - Device Code
    - Service Principal (Certificate)
    - Managed Identity

.NOTES
    GRC Engineering Platform
    Version: 1.0.0

    Required Modules:
      Microsoft.Graph.Authentication
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"



#region Dependencies

Import-Module Microsoft.Graph.Authentication -ErrorAction Stop

#endregion



#region Connection


function Connect-EntraTenant {

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
        $ClientId,


        [Parameter(ParameterSetName = "Certificate")]
        [string]
        $CertificateThumbprint,


        [string[]]
        $Scopes = @(
            "Directory.Read.All",
            "User.Read.All",
            "Group.Read.All"
        )

    )


    switch ($PSCmdlet.ParameterSetName) {

        "Interactive" {

            Connect-MgGraph `
                -Scopes $Scopes `
                -NoWelcome

        }

        "DeviceCode" {

            Connect-MgGraph `
                -Scopes $Scopes `
                -UseDeviceCode `
                -NoWelcome

        }

        "ManagedIdentity" {

            Connect-MgGraph `
                -Identity `
                -NoWelcome

        }

        "Certificate" {

            Connect-MgGraph `
                -TenantId $TenantId `
                -ClientId $ClientId `
                -CertificateThumbprint $CertificateThumbprint `
                -NoWelcome

        }

    }

    return Get-EntraTenantContext

}



function Disconnect-EntraTenant {

    [CmdletBinding()]

    param()

    Disconnect-MgGraph

}



#endregion



#region Context


function Get-EntraTenantContext {

    [CmdletBinding()]

    param()

    $context =
        Get-MgContext

    if ($null -eq $context) {

        return $null

    }

    [PSCustomObject]@{

        TenantId =
        $context.TenantId

        ClientId =
        $context.ClientId

        Account =
        $context.Account

        Environment =
        $context.Environment

        Scopes =
        $context.Scopes

    }

}



function Test-EntraConnection {

    [CmdletBinding()]

    param()

    try {

        $null =
            Get-MgContext

        return $true

    }

    catch {

        return $false

    }

}



#endregion



#region Tokens


function Get-EntraAccessToken {

    [CmdletBinding()]

    param()

    $context =
        Get-MgContext

    if ($null -eq $context) {

        throw "Not connected to Microsoft Graph."

    }

    try {

        $token =
            Get-MgContext

        return $token

    }

    catch {

        throw $_

    }

}



#endregion



#region Permissions


function Get-EntraScopes {

    [CmdletBinding()]

    param()

    $context =
        Get-MgContext

    if ($null -eq $context) {

        return @()

    }

    return $context.Scopes

}



#endregion



Export-ModuleMember `
    -Function `
        Connect-EntraTenant,
        Disconnect-EntraTenant,
        Get-EntraTenantContext,
        Test-EntraConnection,
        Get-EntraAccessToken,
        Get-EntraScopes
