<#
    modules\dashboards\Grafana.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Grafana REST API client module.

.DESCRIPTION
    Provides reusable Grafana REST API operations used by
    dashboard publishing and monitoring components.

    Responsibilities

    - Validate Grafana connectivity
    - Execute Grafana REST requests
    - Retrieve dashboards
    - Retrieve folders
    - Retrieve data sources
    - Retrieve organizations
    - Perform service health checks

.NOTES
    GRC Engineering Platform
    Version 1.0.0

    Authentication is provided using a Grafana API token.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Configuration

$script:GrafanaUri = $null
$script:GrafanaToken = $null

#endregion

#region Connection

function Initialize-GrafanaClient {
    <#
    .SYNOPSIS
        Initializes the Grafana client.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$BaseUri,

        [Parameter(Mandatory)]
        [string]$ApiToken
    )

    $script:GrafanaUri = $BaseUri.TrimEnd("/")
    $script:GrafanaToken = $ApiToken
}

function Test-GrafanaConnection {
    <#
    .SYNOPSIS
        Tests the Grafana connection.
    #>

    [CmdletBinding()]
    param()

    try {
        $null = Invoke-GrafanaRequest -Method GET -Path "/api/health"
        return $true
    }
    catch {
        return $false
    }
}

#endregion

#region REST

function Invoke-GrafanaRequest {
    <#
    .SYNOPSIS
        Executes a Grafana REST API request.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [ValidateSet("GET", "POST", "PUT", "PATCH", "DELETE")]
        [string]$Method,

        [Parameter(Mandatory)]
        [string]$Path,

        [object]$Body
    )

    if ([string]::IsNullOrWhiteSpace($script:GrafanaUri)) {
        throw "Grafana client has not been initialized."
    }

    $headers = @{
        Authorization = "Bearer $($script:GrafanaToken)"
        Accept        = "application/json"
    }

    $parameters = @{
        Uri         = "$($script:GrafanaUri)$Path"
        Method      = $Method
        Headers     = $headers
        ContentType = "application/json"
    }

    if ($PSBoundParameters.ContainsKey("Body")) {
        $parameters.Body = $Body | ConvertTo-Json -Depth 20
    }

    Invoke-RestMethod @parameters
}

#endregion

#region Dashboards

function Get-GrafanaDashboards {
    <#
    .SYNOPSIS
        Returns Grafana dashboards.
    #>

    [CmdletBinding()]
    param()

    Invoke-GrafanaRequest `
        -Method GET `
        -Path "/api/search?type=dash-db"
}

#endregion

#region Folders

function Get-GrafanaFolders {
    <#
    .SYNOPSIS
        Returns Grafana folders.
    #>

    [CmdletBinding()]
    param()

    Invoke-GrafanaRequest `
        -Method GET `
        -Path "/api/folders"
}

#endregion

#region Data Sources

function Get-GrafanaDataSources {
    <#
    .SYNOPSIS
        Returns Grafana data sources.
    #>

    [CmdletBinding()]
    param()

    Invoke-GrafanaRequest `
        -Method GET `
        -Path "/api/datasources"
}

#endregion

#region Organizations

function Get-GrafanaOrganizations {
    <#
    .SYNOPSIS
        Returns Grafana organizations.
    #>

    [CmdletBinding()]
    param()

    Invoke-GrafanaRequest `
        -Method GET `
        -Path "/api/orgs"
}

#endregion

#region Health

function Test-GrafanaHealth {
    <#
    .SYNOPSIS
        Performs a Grafana health check.
    #>

    [CmdletBinding()]
    param()

    try {
        $health = Invoke-GrafanaRequest `
            -Method GET `
            -Path "/api/health"

        [PSCustomObject]@{
            Connected = $true
            Status    = $health.database
            Version   = $health.version
            Commit    = $health.commit
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
    "Initialize-GrafanaClient"
    "Invoke-GrafanaRequest"
    "Test-GrafanaConnection"
    "Get-GrafanaDashboards"
    "Get-GrafanaFolders"
    "Get-GrafanaDataSources"
    "Get-GrafanaOrganizations"
    "Test-GrafanaHealth"
)
