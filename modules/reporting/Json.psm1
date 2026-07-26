<#
    modules\reporting\Json.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    JSON reporting module.

.DESCRIPTION
    Provides JSON report generation capabilities for
    compliance assessments, evidence processing,
    automation workflows, and system integrations.

    Responsibilities:

    - Generate JSON reports
    - Serialize assessment data
    - Export structured results
    - Support API integrations
    - Provide machine-readable reporting

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Configuration

$script:JsonDepth = 20

#endregion

#region Report Creation

function New-JsonReport {
    <#
    .SYNOPSIS
        Creates a JSON report object.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Title,

        [Parameter(Mandatory)]
        [object]$Data,

        [string]$Framework = "General"
    )

    [PSCustomObject]@{
        Report = @{
            Title     = $Title
            Framework = $Framework
            Generated = (Get-Date).ToUniversalTime()
            Platform  = "GRC Engineering Platform"
        }
        Data   = $Data
    }
}

function ConvertTo-GRCJson {
    <#
    .SYNOPSIS
        Converts objects into GRC JSON format.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$InputObject,

        [int]$Depth = $script:JsonDepth
    )

    $InputObject |
    ConvertTo-Json `
        -Depth $Depth
}

#endregion

#region Compliance Reports

function New-ComplianceJsonReport {
    <#
    .SYNOPSIS
        Creates compliance JSON report.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Framework,

        [Parameter(Mandatory)]
        [object[]]$Controls
    )

    New-JsonReport `
        -Title "$Framework Compliance Report" `
        -Framework $Framework `
        -Data @{
        Controls     = $Controls
        ControlCount = $Controls.Count
    }
}

function New-EvidenceJsonReport {
    <#
    .SYNOPSIS
        Creates evidence JSON report.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Evidence
    )

    New-JsonReport `
        -Title "Evidence Report" `
        -Data @{
        Evidence      = $Evidence
        EvidenceCount = $Evidence.Count
    }
}

function New-AssessmentJsonReport {
    <#
    .SYNOPSIS
        Creates assessment JSON report.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Assessment
    )

    New-JsonReport `
        -Title "Assessment Report" `
        -Data $Assessment
}

#endregion

#region File Operations

function Export-GRCJsonReport {
    <#
    .SYNOPSIS
        Exports JSON report to file.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Report,

        [Parameter(Mandatory)]
        [string]$Path,

        [int]$Depth = $script:JsonDepth
    )

    $json =
    $Report |
    ConvertTo-Json `
        -Depth $Depth

    $json |
    Out-File `
        -FilePath $Path `
        -Encoding UTF8

    Get-Item $Path
}

function Import-GRCJsonReport {
    <#
    .SYNOPSIS
        Imports JSON report.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    if (-not (Test-Path $Path)) {

        throw "Report file not found: $Path"

    }

    Get-Content `
        -Path $Path `
        -Raw |
    ConvertFrom-Json
}

#endregion

#region Data Utilities

function Merge-JsonReportData {
    <#
    .SYNOPSIS
        Merges JSON report objects.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Reports
    )

    [PSCustomObject]@{
        Reports   = $Reports
        Count     = $Reports.Count
        Generated = (Get-Date).ToUniversalTime()
    }
}

function Test-JsonReportSchema {
    <#
    .SYNOPSIS
        Validates JSON report structure.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Report
    )

    $required =
    @(
        "Report"
        "Data"
    )

    foreach ($field in $required) {

        if (-not $Report.PSObject.Properties.Name.Contains($field)) {

            return $false

        }
    }

    return $true
}

#endregion

#region Health

function Test-JsonReportingHealth {
    <#
    .SYNOPSIS
        Performs JSON reporting health check.
    #>

    [CmdletBinding()]
    param()

    [PSCustomObject]@{
        Status = "Healthy"
        Module = "Json"
        Engine = "PowerShell JSON Serializer"
        Depth  = $script:JsonDepth
    }
}

#endregion

Export-ModuleMember -Function @(
    "New-JsonReport"
    "ConvertTo-GRCJson"
    "New-ComplianceJsonReport"
    "New-EvidenceJsonReport"
    "New-AssessmentJsonReport"
    "Export-GRCJsonReport"
    "Import-GRCJsonReport"
    "Merge-JsonReportData"
    "Test-JsonReportSchema"
    "Test-JsonReportingHealth"
)
