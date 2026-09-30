<#
    modules\storage\EvidenceStore.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Evidence storage module.

.DESCRIPTION
    Provides storage operations for compliance evidence
    collected from IT infrastructure.

    Responsibilities:

    - Store collected evidence
    - Retrieve evidence
    - Search evidence
    - Manage evidence metadata
    - Maintain evidence lifecycle

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Configuration

$script:EvidenceRoot =
Join-Path `
    -Path (Get-Location) `
    -ChildPath "evidence"

$script:EvidenceFolders = @(
    "raw"
    "processed"
    "runs"
    "archive"
)

#endregion

#region Initialisation

function Initialize-EvidenceStore {
    <#
    .SYNOPSIS
        Creates evidence storage structure.
    #>

    [CmdletBinding()]
    param(
        [string]$RootPath = $script:EvidenceRoot
    )

    foreach ($folder in $script:EvidenceFolders) {

        $path =
        Join-Path `
            -Path $RootPath `
            -ChildPath $folder

        if (-not (Test-Path $path)) {

            New-Item `
                -Path $path `
                -ItemType Directory `
                -Force |
            Out-Null

        }
    }

    Resolve-Path $RootPath
}

#endregion

#region Evidence Storage

function Save-Evidence {
    <#
    .SYNOPSIS
        Saves evidence object.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence,

        [string]$Name = "evidence",

        [ValidateSet(
            "raw",
            "processed",
            "runs",
            "archive"
        )]
        [string]$Stage = "raw"
    )

    $folder =
    Join-Path `
        -Path $script:EvidenceRoot `
        -ChildPath $Stage

    Initialize-EvidenceStore |
    Out-Null

    $timestamp =
    Get-Date `
        -Format "yyyyMMdd-HHmmss"

    $file =
    Join-Path `
        -Path $folder `
        -ChildPath "$Name-$timestamp.json"

    $Evidence |
    ConvertTo-Json `
        -Depth 50 |
    Out-File `
        -FilePath $file `
        -Encoding UTF8

    Get-Item $file
}

function Get-Evidence {
    <#
    .SYNOPSIS
        Retrieves stored evidence.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    if (-not (Test-Path $Path)) {

        throw "Evidence file not found: $Path"

    }

    Get-Content `
        -Path $Path `
        -Raw |
    ConvertFrom-Json
}

#endregion

#region Search

function Find-Evidence {
    <#
    .SYNOPSIS
        Searches evidence files.
    #>

    [CmdletBinding()]
    param(
        [string]$Pattern = "*.json",

        [string]$Stage = "raw"
    )

    $path =
    Join-Path `
        -Path $script:EvidenceRoot `
        -ChildPath $Stage

    if (-not (Test-Path $path)) {

        return @()

    }

    Get-ChildItem `
        -Path $path `
        -Filter $Pattern `
        -File
}

#endregion

#region Metadata

function Get-EvidenceMetadata {
    <#
    .SYNOPSIS
        Returns evidence metadata.
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

function Remove-Evidence {
    <#
    .SYNOPSIS
        Removes evidence file.
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

function Test-EvidenceStoreHealth {
    <#
    .SYNOPSIS
        Performs evidence store health check.
    #>

    [CmdletBinding()]
    param()

    [PSCustomObject]@{
        Status    = "Healthy"
        Module    = "EvidenceStore"
        Root      = $script:EvidenceRoot
        Available = Test-Path $script:EvidenceRoot
    }
}

#endregion

Export-ModuleMember -Function @(
    "Initialize-EvidenceStore"
    "Save-Evidence"
    "Get-Evidence"
    "Find-Evidence"
    "Get-EvidenceMetadata"
    "Remove-Evidence"
    "Test-EvidenceStoreHealth"
)
