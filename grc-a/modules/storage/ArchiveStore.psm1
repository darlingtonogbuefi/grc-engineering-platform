<#
    modules\storage\ArchiveStore.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Evidence and report archive storage module.

.DESCRIPTION
    Provides long-term archival operations for compliance
    evidence, assessment runs and generated reports.

    Responsibilities:

    - Archive assessment data
    - Preserve audit history
    - Retrieve archived items
    - Manage retention lifecycle
    - Maintain archive metadata

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Configuration

$script:ArchiveRoot =
Join-Path `
    -Path (Get-Location) `
    -ChildPath "evidence\archive"

$script:RetentionYears = 7

#endregion

#region Initialisation

function Initialize-ArchiveStore {
    <#
    .SYNOPSIS
        Creates archive storage directory.
    #>

    [CmdletBinding()]
    param(
        [string]$Path = $script:ArchiveRoot
    )

    if (-not (Test-Path $Path)) {

        New-Item `
            -Path $Path `
            -ItemType Directory `
            -Force |
        Out-Null

    }

    Resolve-Path $Path
}

#endregion

#region Archive Operations

function Archive-GRCItem {
    <#
    .SYNOPSIS
        Archives a file or directory.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Path,

        [string]$Category = "general"
    )

    if (-not (Test-Path $Path)) {

        throw "Archive source not found: $Path"

    }

    Initialize-ArchiveStore |
    Out-Null

    $categoryPath =
    Join-Path `
        -Path $script:ArchiveRoot `
        -ChildPath $Category

    if (-not (Test-Path $categoryPath)) {

        New-Item `
            -Path $categoryPath `
            -ItemType Directory `
            -Force |
        Out-Null

    }

    $timestamp =
    Get-Date `
        -Format "yyyyMMdd-HHmmss"

    $name =
    Split-Path `
        -Path $Path `
        -Leaf

    $destination =
    Join-Path `
        -Path $categoryPath `
        -ChildPath "$timestamp-$name"

    Copy-Item `
        -Path $Path `
        -Destination $destination `
        -Recurse `
        -Force

    Get-ArchiveMetadata `
        -Path $destination
}

function Get-ArchivedItem {
    <#
    .SYNOPSIS
        Retrieves archived content.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    if (-not (Test-Path $Path)) {

        throw "Archived item not found: $Path"

    }

    Get-Item $Path
}

#endregion

#region Discovery

function Get-ArchiveItems {
    <#
    .SYNOPSIS
        Lists archived items.
    #>

    [CmdletBinding()]
    param(
        [string]$Category
    )

    Initialize-ArchiveStore |
    Out-Null

    $path =
    if ($Category) {

        Join-Path `
            -Path $script:ArchiveRoot `
            -ChildPath $Category

    }
    else {

        $script:ArchiveRoot

    }

    Get-ChildItem `
        -Path $path `
        -Recurse
}

#endregion

#region Metadata

function Get-ArchiveMetadata {
    <#
    .SYNOPSIS
        Returns archive metadata.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    $item =
    Get-Item `
        -Path $Path

    [PSCustomObject]@{
        Name           = $item.Name
        Path           = $item.FullName
        Size           = $item.Length
        Archived       = (Get-Date).ToUniversalTime()
        RetentionYears = $script:RetentionYears
        Hash           = if ($item.PSIsContainer -eq $false) {
            (
                Get-FileHash `
                    -Path $Path `
                    -Algorithm SHA256
            ).Hash
        }
        else {
            $null
        }
    }
}

#endregion

#region Retention

function Remove-ExpiredArchiveItems {
    <#
    .SYNOPSIS
        Removes expired archive items.
    #>

    [CmdletBinding()]
    param(
        [int]$RetentionYears = $script:RetentionYears
    )

    $expiry =
    (Get-Date).AddYears(
        - $RetentionYears
    )

    Get-ChildItem `
        -Path $script:ArchiveRoot `
        -Recurse |
    Where-Object {
        $_.CreationTime -lt $expiry
    } |
    Remove-Item `
        -Force `
        -Recurse
}

#endregion

#region Health

function Test-ArchiveStoreHealth {
    <#
    .SYNOPSIS
        Performs archive store health check.
    #>

    [CmdletBinding()]
    param()

    [PSCustomObject]@{
        Status         = "Healthy"
        Module         = "ArchiveStore"
        Root           = $script:ArchiveRoot
        Available      = Test-Path $script:ArchiveRoot
        RetentionYears = $script:RetentionYears
    }
}

#endregion

Export-ModuleMember -Function @(
    "Initialize-ArchiveStore"
    "Archive-GRCItem"
    "Get-ArchivedItem"
    "Get-ArchiveItems"
    "Get-ArchiveMetadata"
    "Remove-ExpiredArchiveItems"
    "Test-ArchiveStoreHealth"
)
