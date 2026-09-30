<#
    modules\graph\GraphRequest.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Microsoft Graph request execution module.

.DESCRIPTION
    Provides standardised Microsoft Graph API request handling.

    Responsibilities:
    - Execute Graph REST requests
    - Standardise headers
    - Handle request bodies
    - Support API versions
    - Provide consistent response handling

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

Import-Module Microsoft.Graph.Authentication `
    -ErrorAction Stop

#endregion

#region Graph Request Helpers

function Invoke-GraphRequest {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]
        $Uri,

        [ValidateSet(
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE"
        )]
        [string]
        $Method = "GET",

        [object]
        $Body,

        [ValidateSet(
            "v1.0",
            "beta"
        )]
        [string]
        $ApiVersion = "v1.0",

        [hashtable]
        $Headers
    )

    if ($Uri -notmatch "^https://") {
        $Uri = "https://graph.microsoft.com/$ApiVersion$Uri"
    }

    $request = @{
        Uri    = $Uri
        Method = $Method
    }

    if ($Headers) {
        $request.Headers = $Headers
    }

    if ($null -ne $Body) {
        $request.Body = $Body | ConvertTo-Json -Depth 20
        $request.ContentType = "application/json"
    }

    Invoke-MgGraphRequest @request
}

#endregion

#region Common Requests

function Get-GraphResource {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]
        $Resource,

        [string]
        $ApiVersion = "v1.0"
    )

    Invoke-GraphRequest `
        -Uri $Resource `
        -Method GET `
        -ApiVersion $ApiVersion
}


function New-GraphResource {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]
        $Resource,

        [Parameter(Mandatory)]
        [object]
        $Body,

        [string]
        $ApiVersion = "v1.0"
    )

    Invoke-GraphRequest `
        -Uri $Resource `
        -Method POST `
        -Body $Body `
        -ApiVersion $ApiVersion
}


function Update-GraphResource {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]
        $Resource,

        [Parameter(Mandatory)]
        [object]
        $Body,

        [string]
        $ApiVersion = "v1.0"
    )

    Invoke-GraphRequest `
        -Uri $Resource `
        -Method PATCH `
        -Body $Body `
        -ApiVersion $ApiVersion
}


function Remove-GraphResource {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]
        $Resource,

        [string]
        $ApiVersion = "v1.0"
    )

    Invoke-GraphRequest `
        -Uri $Resource `
        -Method DELETE `
        -ApiVersion $ApiVersion
}

#endregion

#region Response Helpers

function Test-GraphResponse {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        $Response
    )

    return $null -ne $Response
}


function Get-GraphValue {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        $Response
    )

    if ($Response.value) {
        return $Response.value
    }

    return $Response
}

#endregion

Export-ModuleMember -Function @(
    "Invoke-GraphRequest"
    "Get-GraphResource"
    "New-GraphResource"
    "Update-GraphResource"
    "Remove-GraphResource"
    "Test-GraphResponse"
    "Get-GraphValue"
)
