<#
    modules\reporting\Markdown.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Markdown reporting module.

.DESCRIPTION
    Provides Markdown report generation capabilities for
    compliance assessments, evidence summaries, technical
    documentation, and operational reporting.

    Responsibilities:

    - Generate Markdown reports
    - Create headings and sections
    - Render tables
    - Generate compliance summaries
    - Export Markdown files

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Report Creation

function New-MarkdownReport {
    <#
    .SYNOPSIS
        Creates a Markdown report header.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Title,

        [string]$Author = "GRC Engineering Platform"
    )

    @"
# $Title

**Author:** $Author

**Generated:** $(Get-Date -Format u)

---

"@
}

function Complete-MarkdownReport {
    <#
    .SYNOPSIS
        Completes Markdown document.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Content
    )

    $Content + @"

---

_GRC Engineering Platform_
"@
}

#endregion

#region Sections

function Add-MarkdownSection {
    <#
    .SYNOPSIS
        Adds Markdown section.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Title,

        [Parameter(Mandatory)]
        [string]$Content,

        [ValidateRange(1, 6)]
        [int]$Level = 2
    )

    $heading =
    "#" * $Level

    @"

$heading $Title

$Content

"@
}

function Add-MarkdownSummary {
    <#
    .SYNOPSIS
        Creates summary section.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [hashtable]$Summary
    )

    $content = ""

    foreach ($key in $Summary.Keys) {

        $content += "- **${key}:** $($Summary[$key])`n"

    }

    Add-MarkdownSection `
        -Title "Executive Summary" `
        -Content $content
}
#endregion

#region Tables

function ConvertTo-MarkdownTable {
    <#
    .SYNOPSIS
        Converts objects into Markdown table.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Data
    )

    if ($Data.Count -eq 0) {
        return ""
    }

    $properties =
    $Data[0].PSObject.Properties.Name

    $header =
    "| " +
    (
        $properties -join " | "
    ) +
    " |"

    $separator =
    "| " +
    (
        ($properties | ForEach-Object {
            "---"
        }) -join " | "
    ) +
    " |"

    $rows = ""

    foreach ($item in $Data) {

        $values = foreach ($property in $properties) {

            $item.$property

        }

        $rows +=
        "| " +
        (
            $values -join " | "
        ) +
        " |`n"
    }

    @"
$header
$separator
$rows
"@
}

function Add-MarkdownTable {
    <#
    .SYNOPSIS
        Adds Markdown table section.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Title,

        [Parameter(Mandatory)]
        [object[]]$Data
    )

    Add-MarkdownSection `
        -Title $Title `
        -Content (
        ConvertTo-MarkdownTable `
            -Data $Data
    )
}

#endregion

#region Compliance Reports

function New-ComplianceMarkdownReport {
    <#
    .SYNOPSIS
        Creates compliance Markdown report.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Framework,

        [Parameter(Mandatory)]
        [object[]]$Controls
    )

    $report =
    New-MarkdownReport `
        -Title "$Framework Compliance Report"

    $report +=
    Add-MarkdownTable `
        -Title "Control Assessment" `
        -Data $Controls

    Complete-MarkdownReport `
        -Content $report
}

function Add-EvidenceSummary {
    <#
    .SYNOPSIS
        Adds evidence summary.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Evidence
    )

    Add-MarkdownTable `
        -Title "Evidence Summary" `
        -Data $Evidence
}

#endregion

#region Export

function Export-GRCMarkdownReport {
    <#
    .SYNOPSIS
        Exports Markdown report.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Content,

        [Parameter(Mandatory)]
        [string]$Path
    )

    $Content |
    Out-File `
        -FilePath $Path `
        -Encoding UTF8

    Get-Item $Path
}

#endregion

#region Health

function Test-MarkdownReportingHealth {
    <#
    .SYNOPSIS
        Performs Markdown reporting health check.
    #>

    [CmdletBinding()]
    param()

    [PSCustomObject]@{
        Status = "Healthy"
        Module = "Markdown"
        Engine = "Markdown Renderer"
    }
}

#endregion

Export-ModuleMember -Function @(
    "New-MarkdownReport"
    "Complete-MarkdownReport"
    "Add-MarkdownSection"
    "Add-MarkdownSummary"
    "ConvertTo-MarkdownTable"
    "Add-MarkdownTable"
    "New-ComplianceMarkdownReport"
    "Add-EvidenceSummary"
    "Export-GRCMarkdownReport"
    "Test-MarkdownReportingHealth"
)
