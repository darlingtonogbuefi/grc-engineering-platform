<#
    modules\evidence\Validate.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Evidence validation module.

.DESCRIPTION
    Provides validation functions for normalized and merged
    evidence objects before transformation and scoring.

    Responsibilities:

    - Validate evidence structure
    - Validate required metadata
    - Validate evidence integrity
    - Validate evidence freshness
    - Generate validation results

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Schema Validation

function Test-EvidenceStructure {
    <#
    .SYNOPSIS
        Validates evidence object structure.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence
    )

    $requiredFields = @(
        "EvidenceId"
        "Source"
        "CollectedAt"
        "Data"
        "Hash"
    )

    $missingFields = @()

    foreach ($field in $requiredFields) {

        if (-not ($Evidence.PSObject.Properties.Name -contains $field)) {
            $missingFields += $field
        }
    }

    [PSCustomObject]@{
        Valid         = ($missingFields.Count -eq 0)
        MissingFields = $missingFields
    }
}

function Test-EvidenceRequiredFields {
    <#
    .SYNOPSIS
        Checks required evidence fields.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence
    )

    $valid = $true

    foreach ($property in @(
            "EvidenceId"
            "Source"
            "Hash"
        )) {

        if ([string]::IsNullOrWhiteSpace(
                $Evidence.$property
            )) {
            $valid = $false
        }
    }

    $valid
}

#endregion

#region Integrity Validation

function Test-EvidenceIntegrity {
    <#
    .SYNOPSIS
        Validates evidence hash integrity.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence
    )

    $json = $Evidence.Data |
    ConvertTo-Json -Depth 20 -Compress

    $bytes =
    [System.Text.Encoding]::UTF8.GetBytes($json)

    $sha =
    [System.Security.Cryptography.SHA256]::Create()

    $hash =
    $sha.ComputeHash($bytes)

    $calculatedHash = [System.BitConverter]::ToString($hash).Replace("-", "").ToLower()

    [PSCustomObject]@{
        Valid          = ($calculatedHash -eq $Evidence.Hash)
        ExpectedHash   = $Evidence.Hash
        CalculatedHash = $calculatedHash
    }
}

#endregion

#region Freshness Validation

function Test-EvidenceFreshness {
    <#
    .SYNOPSIS
        Validates evidence age.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence,

        [int]$MaximumAgeDays = 30
    )

    $age =
    (
        (Get-Date).ToUniversalTime() -
        $Evidence.CollectedAt
    ).Days

    [PSCustomObject]@{
        Valid          = ($age -le $MaximumAgeDays)
        AgeDays        = $age
        MaximumAgeDays = $MaximumAgeDays
    }
}

#endregion

#region Validation Engine

function Invoke-EvidenceValidation {
    <#
    .SYNOPSIS
        Runs all evidence validation checks.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence,

        [int]$MaximumAgeDays = 30
    )

    $structure =
    Test-EvidenceStructure `
        -Evidence $Evidence

    $required =
    Test-EvidenceRequiredFields `
        -Evidence $Evidence

    $integrity =
    Test-EvidenceIntegrity `
        -Evidence $Evidence

    $freshness =
    Test-EvidenceFreshness `
        -Evidence $Evidence `
        -MaximumAgeDays $MaximumAgeDays

    [PSCustomObject]@{
        EvidenceId     = $Evidence.EvidenceId
        Valid          = (
            $structure.Valid -and
            $required -and
            $integrity.Valid -and
            $freshness.Valid
        )
        Structure      = $structure
        RequiredFields = $required
        Integrity      = $integrity
        Freshness      = $freshness
        ValidatedAt    = (
            Get-Date
        ).ToUniversalTime()
    }
}

function Test-EvidenceCollection {
    <#
    .SYNOPSIS
        Validates an evidence collection.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Evidence,

        [int]$MaximumAgeDays = 30
    )

    foreach ($item in $Evidence) {

        Invoke-EvidenceValidation `
            -Evidence $item `
            -MaximumAgeDays $MaximumAgeDays
    }
}

#endregion

Export-ModuleMember -Function @(
    "Test-EvidenceStructure"
    "Test-EvidenceRequiredFields"
    "Test-EvidenceIntegrity"
    "Test-EvidenceFreshness"
    "Invoke-EvidenceValidation"
    "Test-EvidenceCollection"
)
