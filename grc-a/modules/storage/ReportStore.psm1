<#
    modules\storage\ReportStore.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Report storage module.

.DESCRIPTION
    Provides storage operations for generated compliance
    reports and assessment outputs.

    Responsibilities:

    - Store generated reports
    - Retrieve reports
    - Track report metadata
    - Maintain report history
    - Support audit traceability

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Configuration

$script:ReportRoot =
Join-Path `
    -Path (Get-Location) `
    -ChildPath "reports"

$script:ReportFormats = @(
    "html"
    "markdown"
    "json"
    "csv"
    "pdf"
    "word"
)

#endregion

#region Initialisation

function Initialize-ReportStore {
    <#
    .SYNOPSIS
        Creates report storage structure.
    #>

    [CmdletBinding()]
    param(
        [string]$Path = $script:ReportRoot
    )

    foreach ($format in $script:ReportFormats) {

        $folder =
        Join-Path `
            -Path $Path `
            -ChildPath $format

        if (-not (Test-Path $folder)) {

            New-Item `
                -Path $folder `
                -ItemType Directory `
                -Force |
            Out-Null

        }

    }

    Resolve-Path $Path
}

#endregion

#region Report Storage

function Save-GRCReport {
    <#
    .SYNOPSIS
        Stores a generated report.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Content,

        [Parameter(Mandatory)]
        [ValidateSet(
            "html",
            "markdown",
            "json",
            "csv",
            "pdf",
            "word"
        )]
        [string]$Format,

        [Parameter(Mandatory)]
        [string]$Name,

        [string]$Framework
    )

    Initialize-ReportStore |
    Out-Null

    $folder =
    Join-Path `
        -Path $script:ReportRoot `
        -ChildPath $Format

    if ($Framework) {

        $folder =
        Join-Path `
            -Path $folder `
            -ChildPath $Framework

        if (-not (Test-Path $folder)) {

            New-Item `
                -Path $folder `
                -ItemType Directory `
                -Force |
            Out-Null

        }

    }

    $timestamp =
    Get-Date `
        -Format "yyyyMMdd-HHmmss"

    $extension =
    switch ($Format) {
        "html" { "html" }
        "markdown" { "md" }
        "json" { "json" }
        "csv" { "csv" }
        "pdf" { "pdf" }
        "word" { "docx" }
    }

    $file =
    Join-Path `
        -Path $folder `
        -ChildPath "$Name-$timestamp.$extension"

    $Content |
    Out-File `
        -FilePath $file `
        -Encoding UTF8

    Get-ReportMetadata `
        -Path $file
}

#endregion

#region Retrieval

function Get-GRCReport {
    <#
    .SYNOPSIS
        Retrieves report content.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    if (-not (Test-Path $Path)) {

        throw "Report not found: $Path"

    }

    Get-Content `
        -Path $Path `
        -Raw
}

function Get-GRCReports {
    <#
    .SYNOPSIS
        Lists stored reports.
    #>

    [CmdletBinding()]
    param(
        [string]$Format
    )

    Initialize-ReportStore |
    Out-Null

    $path =
    if ($Format) {

        Join-Path `
            -Path $script:ReportRoot `
            -ChildPath $Format

    }
    else {

        $script:ReportRoot

    }

    Get-ChildItem `
        -Path $path `
        -File `
        -Recurse

}

#endregion

#region Metadata

function Get-ReportMetadata {
    <#
    .SYNOPSIS
        Returns report metadata.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    $file =
    Get-Item `
        -Path $Path

    [PSCustomObject]@{
        Name     = $file.Name
        Path     = $file.FullName
        Size     = $file.Length
        Created  = $file.CreationTimeUtc
        Modified = $file.LastWriteTimeUtc
        Hash     = (
            Get-FileHash `
                -Path $Path `
                -Algorithm SHA256
        ).Hash
    }
}

#endregion

#region Lifecycle

function Remove-GRCReport {
    <#
    .SYNOPSIS
        Removes a stored report.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    Remove-Item `
        -Path $Path `
        -Force
}

#endregion

#region Health

function Test-ReportStoreHealth {
    <#
    .SYNOPSIS
        Performs report store health check.
    #>

    [CmdletBinding()]
    param()

    [PSCustomObject]@{
        Status    = "Healthy"
        Module    = "ReportStore"
        Root      = $script:ReportRoot
        Available = Test-Path $script:ReportRoot
    }
}

#endregion

Export-ModuleMember -Function @(
    "Initialize-ReportStore"
    "Save-GRCReport"
    "Get-GRCReport"
    "Get-GRCReports"
    "Get-ReportMetadata"
    "Remove-GRCReport"
    "Test-ReportStoreHealth"
)
