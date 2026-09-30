<#
    modules\reporting\Word.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Microsoft Word reporting module.

.DESCRIPTION
    Provides Word document generation capabilities for
    compliance assessments, audit deliverables, evidence
    packages, and executive reporting.

    Responsibilities:

    - Generate Word reports
    - Create structured documents
    - Add headings and tables
    - Export assessment documents
    - Support audit documentation

.NOTES
    GRC Engineering Platform
    Version 1.0.0

    Optional Dependency:

        Microsoft Word
        Microsoft.Office.Interop.Word
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Configuration

$script:WordApplication = "Microsoft Word"

#endregion

#region Document Creation

function New-GRCWordDocument {
    <#
    .SYNOPSIS
        Creates a new Word document.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Title,

        [string]$Author = "GRC Engineering Platform"
    )

    [PSCustomObject]@{
        Title    = $Title
        Author   = $Author
        Created  = (Get-Date).ToUniversalTime()
        Sections = @()
    }
}

function Add-WordSection {
    <#
    .SYNOPSIS
        Adds document section.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Document,

        [Parameter(Mandatory)]
        [string]$Title,

        [Parameter(Mandatory)]
        [string]$Content
    )

    $Document.Sections += [PSCustomObject]@{
        Title   = $Title
        Content = $Content
    }

    return $Document
}

#endregion

#region Tables

function Add-WordTable {
    <#
    .SYNOPSIS
        Adds table data to document.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Document,

        [Parameter(Mandatory)]
        [object[]]$Data,

        [string]$Title = "Table"
    )

    $Document.Sections += [PSCustomObject]@{
        Title = $Title
        Type  = "Table"
        Data  = $Data
    }

    return $Document
}

function ConvertTo-WordTableData {
    <#
    .SYNOPSIS
        Converts objects into Word table format.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Data
    )

    $Data |
    Select-Object *
}

#endregion

#region Export

function Export-GRCWordReport {
    <#
    .SYNOPSIS
        Exports Word document.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Document,

        [Parameter(Mandatory)]
        [string]$Path
    )

    $word =
    New-Object `
        -ComObject Word.Application `
        -ErrorAction Stop

    try {

        $doc =
        $word.Documents.Add()

        $selection =
        $word.Selection

        $selection.Style = "Title"

        $selection.TypeText(
            $Document.Title
        )

        foreach ($section in $Document.Sections) {

            $selection.TypeParagraph()

            $selection.Style = "Heading 1"

            $selection.TypeText(
                $section.Title
            )

            $selection.TypeParagraph()

            if ($section.Type -eq "Table") {

                $selection.TypeText(
                    ($section.Data | Out-String)
                )

            }
            else {

                $selection.TypeText(
                    $section.Content
                )

            }
        }

        $doc.SaveAs(
            $Path
        )

        $doc.Close()

    }
    finally {

        $word.Quit()

    }

    Get-Item $Path
}

#endregion

#region Compliance Reports

function Export-ComplianceWordReport {
    <#
    .SYNOPSIS
        Creates compliance Word report.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Framework,

        [Parameter(Mandatory)]
        [object[]]$Controls,

        [Parameter(Mandatory)]
        [string]$Path
    )

    $document =
    New-GRCWordDocument `
        -Title "$Framework Compliance Report"

    Add-WordTable `
        -Document $document `
        -Title "Control Assessment" `
        -Data $Controls

    Export-GRCWordReport `
        -Document $document `
        -Path $Path
}

function Export-AuditWordPackage {
    <#
    .SYNOPSIS
        Creates audit documentation package.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Title,

        [Parameter(Mandatory)]
        [string]$Content,

        [Parameter(Mandatory)]
        [string]$Path
    )

    $document =
    New-GRCWordDocument `
        -Title $Title

    Add-WordSection `
        -Document $document `
        -Title "Audit Documentation" `
        -Content $Content

    Export-GRCWordReport `
        -Document $document `
        -Path $Path
}

#endregion

#region Metadata

function Get-WordReportMetadata {
    <#
    .SYNOPSIS
        Returns Word report metadata.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    if (-not (Test-Path $Path)) {

        throw "Word document not found: $Path"

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

function Test-WordReportingHealth {
    <#
    .SYNOPSIS
        Performs Word reporting health check.
    #>

    [CmdletBinding()]
    param()

    $word =
    Get-Command `
        winword.exe `
        -ErrorAction SilentlyContinue

    [PSCustomObject]@{
        Status = if ($word) {
            "Healthy"
        }
        else {
            "Unavailable"
        }
        Module = "Word"
        Engine = $script:WordApplication
    }
}

#endregion

Export-ModuleMember -Function @(
    "New-GRCWordDocument"
    "Add-WordSection"
    "Add-WordTable"
    "ConvertTo-WordTableData"
    "Export-GRCWordReport"
    "Export-ComplianceWordReport"
    "Export-AuditWordPackage"
    "Get-WordReportMetadata"
    "Test-WordReportingHealth"
)
