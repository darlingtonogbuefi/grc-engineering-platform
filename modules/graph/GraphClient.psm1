<#
    modules\graph\GraphClient.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Microsoft Graph client management module.

.DESCRIPTION
    Provides common Microsoft Graph client operations used by
    GRC collectors.

    Responsibilities:

    - Initialise Graph sessions
    - Validate Graph connectivity
    - Retrieve Graph context
    - Manage Graph connection lifecycle
    - Provide tenant and scope information

    Authentication is handled by:

    modules\authentication\Connect-Entra.psm1

.NOTES
    GRC Engineering Platform
    Version: 1.0.0

    Required Modules:
      Microsoft.Graph.Authentication
#>


Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"



#region Dependencies


if (-not (Get-Module -ListAvailable Microsoft.Graph.Authentication)) {

    throw @"
Microsoft.Graph.Authentication module is required.

Install:

Install-Module Microsoft.Graph.Authentication -Scope CurrentUser

"@

}


Import-Module `
    Microsoft.Graph.Authentication `
    -ErrorAction Stop



#endregion



#region Graph Context


function Get-GraphContext {

    <#
    .SYNOPSIS
        Returns the current Microsoft Graph context.
    #>


    [CmdletBinding()]

    param()



    $context =
    Get-MgContext



    if ($null -eq $context) {

        return $null

    }



    return [PSCustomObject]@{

        TenantId =
        $context.TenantId


        ClientId =
        $context.ClientId


        Account =
        $context.Account


        AuthType =
        $context.AuthType


        Environment =
        $context.Environment


        Scopes =
        $context.Scopes


        CertificateThumbprint =
        $context.CertificateThumbprint

    }

}



function Test-GraphConnection {

    <#
    .SYNOPSIS
        Tests whether a Graph session exists.
    #>


    [CmdletBinding()]

    param()



    try {

        return (
            $null -ne (Get-MgContext)
        )

    }

    catch {

        return $false

    }

}



#endregion



#region Client Lifecycle


function Initialize-GraphClient {

    <#
    .SYNOPSIS
        Creates a Microsoft Graph connection.

    .PARAMETER Scopes
        Microsoft Graph delegated permissions.
    #>


    [CmdletBinding()]

    param(

        [string[]]
        $Scopes = @(

            "Directory.Read.All"

        )

    )



    if (Test-GraphConnection) {

        return Get-GraphContext

    }



    Connect-MgGraph `

        -Scopes $Scopes `

        -NoWelcome



    return Get-GraphContext

}



function Disconnect-GraphClient {

    <#
    .SYNOPSIS
        Disconnects Microsoft Graph session.
    #>


    [CmdletBinding()]

    param()



    if (Test-GraphConnection) {

        Disconnect-MgGraph

    }

}



#endregion



#region Graph Information


function Get-GraphTenantId {

    [CmdletBinding()]

    param()



    $context =
    Get-MgContext



    if ($null -eq $context) {

        throw "Microsoft Graph connection not established."

    }



    return $context.TenantId

}



function Get-GraphScopes {

    [CmdletBinding()]

    param()



    $context =
    Get-MgContext



    if ($null -eq $context) {

        return @()

    }



    return $context.Scopes

}



function Get-GraphEnvironment {

    [CmdletBinding()]

    param()



    $context =
    Get-MgContext



    if ($null -eq $context) {

        return $null

    }



    return $context.Environment

}



#endregion



#region Health Check


function Test-GraphHealth {

    <#
    .SYNOPSIS
        Performs a Graph API health check.
    #>


    [CmdletBinding()]

    param()



    try {


        if (-not (Test-GraphConnection)) {

            return [PSCustomObject]@{

                Connected = $false

                Status = "Disconnected"

            }

        }



        $organization =

            Get-MgOrganization `

                -Top 1



        return [PSCustomObject]@{

            Connected = $true

            Status = "Healthy"

            TenantId =
            (
                Get-MgContext
            ).TenantId

            Organization =
            $organization.DisplayName

        }


    }

    catch {


        return [PSCustomObject]@{

            Connected = $false

            Status = "Failed"

            Error =
            $_.Exception.Message

        }

    }

}



#endregion



Export-ModuleMember -Function @(
    "Get-GraphContext"
    "Test-GraphConnection"
    "Initialize-GraphClient"
    "Disconnect-GraphClient"
    "Get-GraphTenantId"
    "Get-GraphScopes"
    "Get-GraphEnvironment"
    "Test-GraphHealth"
)
