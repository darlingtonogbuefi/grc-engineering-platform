<#
    modules\dashboards\PowerBI.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Microsoft Power BI client module.

.DESCRIPTION
    Provides reusable Power BI REST API operations used by
    dashboard publishing and reporting components.

    Responsibilities

    - Validate Power BI connectivity
    - Discover workspaces
    - Discover reports
    - Discover datasets
    - Refresh datasets
    - Retrieve dashboards
    - Execute Power BI REST requests

.NOTES
    GRC Engineering Platform
    Version 1.0.0

    Requires:
        MicrosoftPowerBIMgmt.Profile
        MicrosoftPowerBIMgmt.Workspaces
        MicrosoftPowerBIMgmt.Reports
        MicrosoftPowerBIMgmt.Data
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Dependencies

$RequiredModules = @(
    "MicrosoftPowerBIMgmt.Profile"
    "MicrosoftPowerBIMgmt.Workspaces"
)

foreach ($Module in $RequiredModules) {
    if (-not (Get-Module -ListAvailable $Module)) {
        throw @"
Required PowerShell module missing.

Install:

Install-Module $Module -Scope CurrentUser
"@
    }

    Import-Module $Module -ErrorAction Stop
}

#endregion

#region Connection

function Test-PowerBIConnection {
    <#
    .SYNOPSIS
        Tests the current Power BI connection.
    #>

    [CmdletBinding()]
    param()

    try {
        $null = Get-PowerBIWorkspace -Scope Organization -First 1
        return $true
    }
    catch {
        return $false
    }
}

#endregion

#region REST

function Invoke-PowerBIRestRequest {
    <#
    .SYNOPSIS
        Executes a Power BI REST request.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [ValidateSet("GET", "POST", "PUT", "DELETE", "PATCH")]
        [string]$Method,

        [Parameter(Mandatory)]
        [string]$Uri,

        [object]$Body
    )

    try {
        $parameters = @{
            Url    = $Uri
            Method = $Method
        }

        if ($PSBoundParameters.ContainsKey("Body")) {
            $parameters.Body = $Body | ConvertTo-Json -Depth 20
        }

        Invoke-PowerBIRestMethod @parameters
    }
    catch {
        throw
    }
}

#endregion

#region Workspaces

function Get-PowerBIWorkspaceList {
    <#
    .SYNOPSIS
        Returns all Power BI workspaces.
    #>

    [CmdletBinding()]
    param()

    Get-PowerBIWorkspace -Scope Organization
}

#endregion

#region Reports

function Get-PowerBIReportList {
    <#
    .SYNOPSIS
        Returns reports from a workspace.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [guid]$WorkspaceId
    )

    Invoke-PowerBIRestRequest `
        -Method GET `
        -Uri "groups/$WorkspaceId/reports"
}

#endregion

#region Dashboards

function Get-PowerBIDashboardList {
    <#
    .SYNOPSIS
        Returns dashboards within a workspace.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [guid]$WorkspaceId
    )

    Invoke-PowerBIRestRequest `
        -Method GET `
        -Uri "groups/$WorkspaceId/dashboards"
}

#endregion

#region Datasets

function Get-PowerBIDatasetList {
    <#
    .SYNOPSIS
        Returns datasets.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [guid]$WorkspaceId
    )

    Invoke-PowerBIRestRequest `
        -Method GET `
        -Uri "groups/$WorkspaceId/datasets"
}

function Start-PowerBIDatasetRefresh {
    <#
    .SYNOPSIS
        Starts a dataset refresh.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [guid]$WorkspaceId,

        [Parameter(Mandatory)]
        [guid]$DatasetId
    )

    Invoke-PowerBIRestRequest `
        -Method POST `
        -Uri "groups/$WorkspaceId/datasets/$DatasetId/refreshes"
}

#endregion

#region Health

function Test-PowerBIHealth {
    <#
    .SYNOPSIS
        Performs a health check.
    #>

    [CmdletBinding()]
    param()

    try {
        $workspace = Get-PowerBIWorkspace -First 1

        [PSCustomObject]@{
            Connected = $true
            Status    = "Healthy"
            Workspace = $workspace.Name
        }
    }
    catch {
        [PSCustomObject]@{
            Connected = $false
            Status    = "Failed"
            Error     = $_.Exception.Message
        }
    }
}

#endregion

Export-ModuleMember -Function @(
    "Invoke-PowerBIRestRequest"
    "Test-PowerBIConnection"
    "Get-PowerBIWorkspaceList"
    "Get-PowerBIReportList"
    "Get-PowerBIDashboardList"
    "Get-PowerBIDatasetList"
    "Start-PowerBIDatasetRefresh"
    "Test-PowerBIHealth"
)
