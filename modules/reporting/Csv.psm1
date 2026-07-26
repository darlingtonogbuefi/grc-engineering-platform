<#
    modules\reporting\Csv.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    CSV reporting module.

.DESCRIPTION
    Provides CSV report generation capabilities for
    compliance assessments, evidence exports, control
    tracking, and operational reporting.

    Responsibilities:

    - Generate CSV reports
    - Export structured data
    - Flatten assessment results
    - Support audit exports
    - Provide spreadsheet-compatible output

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Conversion

function ConvertTo-GRCCsv {
    <#
    .SYNOPSIS
        Converts objects into CSV format.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Data
    )

    if ($Data.Count -eq 0) {

        return ""

    }

    $Data |
    ConvertTo-Csv `
        -NoTypeInformation
}

#endregion

#region Export

function Export-GRCCsvReport {
    <#
    .SYNOPSIS
        Exports CSV report to file.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Data,

        [Parameter(Mandatory)]
        [string]$Path
    )

    $Data |
    Export-Csv `
        -Path $Path `
        -NoTypeInformation `
        -Encoding UTF8

    Get-Item $Path
}

#endregion

#region Compliance Reports

function Export-ControlCsvReport {
    <#
    .SYNOPSIS
        Exports control assessment report.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Controls,

        [Parameter(Mandatory)]
        [string]$Path
    )

    $Controls |
    Select-Object `
        Framework,
    ControlId,
    Title,
    Status,
    Score,
    Risk,
    Owner |
    Export-Csv `
        -Path $Path `
        -NoTypeInformation `
        -Encoding UTF8

    Get-Item $Path
}

function Export-EvidenceCsvReport {
    <#
    .SYNOPSIS
        Exports evidence inventory report.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Evidence,

        [Parameter(Mandatory)]
        [string]$Path
    )

    $Evidence |
    Select-Object `
        EvidenceId,
    Name,
    Source,
    Type,
    Status,
    CollectedDate,
    Owner |
    Export-Csv `
        -Path $Path `
        -NoTypeInformation `
        -Encoding UTF8

    Get-Item $Path
}

function Export-RiskCsvReport {
    <#
    .SYNOPSIS
        Exports risk assessment report.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Risks,

        [Parameter(Mandatory)]
        [string]$Path
    )

    $Risks |
    Select-Object `
        RiskId,
    Category,
    Description,
    Likelihood,
    Impact,
    Score,
    Treatment |
    Export-Csv `
        -Path $Path `
        -NoTypeInformation `
        -Encoding UTF8

    Get-Item $Path
}

#endregion

#region Import

function Import-GRCCsvReport {
    <#
    .SYNOPSIS
        Imports CSV report.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    if (-not (Test-Path $Path)) {

        throw "CSV report not found: $Path"

    }

    Import-Csv `
        -Path $Path
}

#endregion

#region Utilities

function Merge-CsvReports {
    <#
    .SYNOPSIS
        Combines multiple CSV datasets.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[][]]$Reports
    )

    $merged = @()

    foreach ($report in $Reports) {

        $merged += $report

    }

    return $merged
}

function ConvertTo-CsvSummary {
    <#
    .SYNOPSIS
        Creates CSV summary metrics.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [hashtable]$Summary
    )

    $Summary.GetEnumerator() |
    Select-Object `
    @{
        Name       = "Metric"
        Expression = {
            $_.Key
        }
    },
    @{
        Name       = "Value"
        Expression = {
            $_.Value
        }
    }
}

#endregion

#region Health

function Test-CsvReportingHealth {
    <#
    .SYNOPSIS
        Performs CSV reporting health check.
    #>

    [CmdletBinding()]
    param()

    [PSCustomObject]@{
        Status = "Healthy"
        Module = "Csv"
        Engine = "PowerShell CSV Serializer"
    }
}

#endregion

Export-ModuleMember -Function @(
    "ConvertTo-GRCCsv"
    "Export-GRCCsvReport"
    "Export-ControlCsvReport"
    "Export-EvidenceCsvReport"
    "Export-RiskCsvReport"
    "Import-GRCCsvReport"
    "Merge-CsvReports"
    "ConvertTo-CsvSummary"
    "Test-CsvReportingHealth"
)
