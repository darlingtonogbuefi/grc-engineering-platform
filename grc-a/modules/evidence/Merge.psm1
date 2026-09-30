<#
    modules\evidence\Merge.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Evidence merge module.

.DESCRIPTION
    Provides functions to merge normalized evidence
    from multiple collectors and sources.

    Responsibilities:

    - Merge evidence collections
    - Preserve evidence lineage
    - Remove duplicates
    - Combine related evidence
    - Maintain source traceability

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Merge

function Merge-EvidenceCollection {
    <#
    .SYNOPSIS
        Merges multiple evidence collections.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$EvidenceCollections
    )

    $merged = New-Object System.Collections.Generic.List[object]

    foreach ($collection in $EvidenceCollections) {

        if ($null -eq $collection) {
            continue
        }

        foreach ($item in $collection) {

            if (-not (Test-EvidenceDuplicate `
                        -Existing $merged `
                        -Evidence $item)) {

                $merged.Add($item)

            }
        }
    }

    return $merged
}

function Merge-EvidenceObject {
    <#
    .SYNOPSIS
        Merges two evidence objects.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Primary,

        [Parameter(Mandatory)]
        [object]$Secondary
    )

    $merged = [ordered]@{}

    foreach ($property in $Primary.PSObject.Properties) {
        $merged[$property.Name] = $property.Value
    }

    foreach ($property in $Secondary.PSObject.Properties) {

        if ($merged.Contains($property.Name)) {

            if ($property.Name -eq "Source") {

                $merged[$property.Name] =
                @(
                    $merged[$property.Name]
                    $property.Value
                ) |
                Select-Object -Unique
            }

            continue
        }

        $merged[$property.Name] = $property.Value
    }

    [PSCustomObject]$merged
}

#endregion

#region Deduplication

function Test-EvidenceDuplicate {
    <#
    .SYNOPSIS
        Checks whether evidence already exists.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Existing,

        [Parameter(Mandatory)]
        [object]$Evidence
    )

    foreach ($item in $Existing) {

        if ($item.Hash -eq $Evidence.Hash) {
            return $true
        }

        if ($item.EvidenceId -eq $Evidence.EvidenceId) {
            return $true
        }
    }

    return $false
}

function Remove-DuplicateEvidence {
    <#
    .SYNOPSIS
        Removes duplicate evidence entries.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Evidence
    )

    $result = New-Object System.Collections.Generic.List[object]

    foreach ($item in $Evidence) {

        if (-not (Test-EvidenceDuplicate `
                    -Existing $result `
                    -Evidence $item)) {

            $result.Add($item)

        }
    }

    return $result
}

#endregion

#region Lineage

function Add-EvidenceLineage {
    <#
    .SYNOPSIS
        Adds lineage information to evidence.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence,

        [Parameter(Mandatory)]
        [string]$ParentId
    )

    $Evidence | Add-Member `
        -MemberType NoteProperty `
        -Name ParentEvidenceId `
        -Value $ParentId `
        -Force

    return $Evidence
}

function Get-EvidenceSources {
    <#
    .SYNOPSIS
        Returns unique evidence sources.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Evidence
    )

    $Evidence.Source |
    Sort-Object |
    Select-Object -Unique
}

#endregion

#region Statistics

function Get-EvidenceMergeSummary {
    <#
    .SYNOPSIS
        Returns merge statistics.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Evidence
    )

    [PSCustomObject]@{
        TotalEvidence = $Evidence.Count
        Sources       = @(Get-EvidenceSources -Evidence $Evidence).Count
        UniqueHashes  = @(
            $Evidence.Hash |
            Select-Object -Unique
        ).Count
    }
}

#endregion

Export-ModuleMember -Function @(
    "Merge-EvidenceCollection"
    "Merge-EvidenceObject"
    "Remove-DuplicateEvidence"
    "Test-EvidenceDuplicate"
    "Add-EvidenceLineage"
    "Get-EvidenceSources"
    "Get-EvidenceMergeSummary"
)
