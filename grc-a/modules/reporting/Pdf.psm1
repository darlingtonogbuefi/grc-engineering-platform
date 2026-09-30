<#
    modules\reporting\Pdf.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    PDF reporting module.

.DESCRIPTION
    Provides PDF report generation capabilities for
    compliance assessments, executive reporting,
    evidence packages, and audit deliverables.

    Responsibilities:

    - Generate PDF reports
    - Convert HTML reports to PDF
    - Export assessment packages
    - Create audit-ready documents
    - Manage PDF metadata

.NOTES
    GRC Engineering Platform
    Version 1.0.0

    Optional Dependencies:

        Microsoft Edge
        wkhtmltopdf
        Chromium based PDF renderer
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Configuration

$script:PdfEngine = "Edge"

#endregion

#region HTML Conversion

function ConvertTo-PdfFromHtml {
    <#
    .SYNOPSIS
        Converts HTML content into PDF.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Html,

        [Parameter(Mandatory)]
        [string]$Path
    )

    $tempFile =
    Join-Path `
        -Path $env:TEMP `
        -ChildPath (
        "grc-report-{0}.html" -f (
            [guid]::NewGuid()
        )
    )

    $Html |
    Out-File `
        -FilePath $tempFile `
        -Encoding UTF8

    try {

        Convert-HtmlToPdf `
            -HtmlPath $tempFile `
            -OutputPath $Path

    }
    finally {

        Remove-Item `
            -Path $tempFile `
            -Force `
            -ErrorAction SilentlyContinue

    }

    Get-Item $Path
}

#endregion

#region PDF Engine

function Convert-HtmlToPdf {
    <#
    .SYNOPSIS
        Converts HTML file using available renderer.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$HtmlPath,

        [Parameter(Mandatory)]
        [string]$OutputPath
    )

    $edge =
    Get-Command `
        msedge.exe `
        -ErrorAction SilentlyContinue

    if ($null -eq $edge) {

        throw @"
Microsoft Edge PDF renderer not available.

Install Microsoft Edge or configure
an alternative PDF rendering engine.
"@

    }

    & $edge.Source `
        --headless `
        --disable-gpu `
        --print-to-pdf="$OutputPath" `
        "$HtmlPath"

}

#endregion

#region Report Generation

function New-GRCPdfReport {
    <#
    .SYNOPSIS
        Creates PDF compliance report.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Title,

        [Parameter(Mandatory)]
        [string]$HtmlContent,

        [Parameter(Mandatory)]
        [string]$Path
    )

    ConvertTo-PdfFromHtml `
        -Html $HtmlContent `
        -Path $Path
}

function Export-GRCPdfReport {
    <#
    .SYNOPSIS
        Exports PDF report package.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Content,

        [Parameter(Mandatory)]
        [string]$Path
    )

    New-GRCPdfReport `
        -Title "GRC Report" `
        -HtmlContent $Content `
        -Path $Path
}

#endregion

#region Compliance Reports

function Export-CompliancePdfReport {
    <#
    .SYNOPSIS
        Exports compliance assessment PDF.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Framework,

        [Parameter(Mandatory)]
        [string]$HtmlContent,

        [Parameter(Mandatory)]
        [string]$Path
    )

    New-GRCPdfReport `
        -Title "$Framework Compliance Report" `
        -HtmlContent $HtmlContent `
        -Path $Path
}

function Export-EvidencePdfPackage {
    <#
    .SYNOPSIS
        Creates evidence PDF package.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$HtmlContent,

        [Parameter(Mandatory)]
        [string]$Path
    )

    New-GRCPdfReport `
        -Title "Evidence Package" `
        -HtmlContent $HtmlContent `
        -Path $Path
}

#endregion

#region Metadata

function Get-PdfMetadata {
    <#
    .SYNOPSIS
        Returns PDF report metadata.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    if (-not (Test-Path $Path)) {

        throw "PDF file not found: $Path"

    }

    $file =
    Get-Item $Path

    [PSCustomObject]@{
        Name     = $file.Name
        Size     = $file.Length
        Created  = $file.CreationTimeUtc
        Modified = $file.LastWriteTimeUtc
    }
}

#endregion

#region Health

function Test-PdfReportingHealth {
    <#
    .SYNOPSIS
        Performs PDF reporting health check.
    #>

    [CmdletBinding()]
    param()

    $renderer =
    Get-Command `
        msedge.exe `
        -ErrorAction SilentlyContinue

    [PSCustomObject]@{
        Status = if ($renderer) {
            "Healthy"
        }
        else {
            "Unavailable"
        }
        Module = "Pdf"
        Engine = $script:PdfEngine
    }
}

#endregion

Export-ModuleMember -Function @(
    "ConvertTo-PdfFromHtml"
    "Convert-HtmlToPdf"
    "New-GRCPdfReport"
    "Export-GRCPdfReport"
    "Export-CompliancePdfReport"
    "Export-EvidencePdfPackage"
    "Get-PdfMetadata"
    "Test-PdfReportingHealth"
)
