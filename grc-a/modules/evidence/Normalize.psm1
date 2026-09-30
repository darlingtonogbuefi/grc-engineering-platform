<#
    modules\evidence\Normalize.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Evidence normalization module.

.DESCRIPTION
    Provides functions to normalize collected evidence
    into a consistent GRC evidence format.

    Responsibilities:

    - Normalize evidence objects
    - Standardize metadata fields
    - Remove inconsistent formatting
    - Generate evidence identifiers
    - Prepare evidence for validation and mapping

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Normalization

function Normalize-EvidenceObject {
    <#
    .SYNOPSIS
        Normalizes a single evidence object.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence,

        [string]$Source = "Unknown",

        [string]$Category = "General"
    )

    if ($null -eq $Evidence) {
        throw "Evidence object cannot be null."
    }

    $timestamp = (Get-Date).ToUniversalTime()

    [PSCustomObject]@{
        EvidenceId  = New-EvidenceId
        Source      = $Source
        Category    = $Category
        CollectedAt = $timestamp
        Data        = $Evidence
        Hash        = Get-EvidenceHash -Object $Evidence
        Status      = "Normalized"
    }
}

function Normalize-EvidenceCollection {
    <#
    .SYNOPSIS
        Normalizes multiple evidence objects.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Evidence,

        [string]$Source = "Unknown",

        [string]$Category = "General"
    )

    foreach ($Item in $Evidence) {
        Normalize-EvidenceObject `
            -Evidence $Item `
            -Source $Source `
            -Category $Category
    }
}

#endregion

#region Identifiers

function New-EvidenceId {
    <#
    .SYNOPSIS
        Creates a unique evidence identifier.
    #>

    [CmdletBinding()]
    param()

    "EVD-" + ([guid]::NewGuid().ToString())
}

#endregion

#region Hashing

function Get-EvidenceHash {
    <#
    .SYNOPSIS
        Generates a SHA256 evidence hash.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Object
    )

    $json = $Object | ConvertTo-Json -Depth 20 -Compress

    $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)

    $sha = [System.Security.Cryptography.SHA256]::Create()

    $hash = $sha.ComputeHash($bytes)

    ([System.BitConverter]::ToString($hash)).Replace("-", "").ToLower()
}

#endregion

#region Cleaning

function Remove-EvidenceEmptyValues {
    <#
    .SYNOPSIS
        Removes empty properties from evidence objects.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence
    )

    $result = [ordered]@{}

    foreach ($property in $Evidence.PSObject.Properties) {
        if ($null -ne $property.Value -and
            $property.Value.ToString().Trim() -ne "") {

            $result[$property.Name] = $property.Value
        }
    }

    [PSCustomObject]$result
}

function Convert-EvidenceDateFields {
    <#
    .SYNOPSIS
        Converts date fields to UTC format.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence
    )

    foreach ($property in $Evidence.PSObject.Properties) {

        if ($property.Value -is [datetime]) {
            $property.Value =
            $property.Value.ToUniversalTime()
        }
    }

    return $Evidence
}

#endregion

#region Validation Helpers

function Test-NormalizedEvidence {
    <#
    .SYNOPSIS
        Tests whether evidence is normalized.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence
    )

    $required = @(
        "EvidenceId"
        "Source"
        "CollectedAt"
        "Data"
        "Hash"
    )

    foreach ($field in $required) {

        if (-not ($Evidence.PSObject.Properties.Name -contains $field)) {
            return $false
        }
    }

    return $true
}

#endregion

Export-ModuleMember -Function @(
    "Normalize-EvidenceObject"
    "Normalize-EvidenceCollection"
    "New-EvidenceId"
    "Get-EvidenceHash"
    "Remove-EvidenceEmptyValues"
    "Convert-EvidenceDateFields"
    "Test-NormalizedEvidence"
)
