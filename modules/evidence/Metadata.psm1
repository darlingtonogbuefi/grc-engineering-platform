<#
    modules\evidence\Metadata.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Evidence metadata management module.

.DESCRIPTION
    Provides functions to create, enrich, retrieve, and manage
    metadata associated with evidence objects.

    Responsibilities:

    - Generate evidence metadata
    - Track evidence ownership
    - Track collection details
    - Maintain evidence lineage
    - Record processing history
    - Support audit traceability

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Metadata Creation

function New-EvidenceMetadata {
    <#
    .SYNOPSIS
        Creates evidence metadata.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Source,

        [string]$Collector = "Unknown",

        [string]$Category = "General",

        [string]$Classification = "Internal",

        [string]$Owner = "Unknown"
    )

    [PSCustomObject]@{
        MetadataId     = New-GuidId
        Source         = $Source
        Collector      = $Collector
        Category       = $Category
        Classification = $Classification
        Owner          = $Owner
        CreatedAt      = (Get-Date).ToUniversalTime()
    }
}

function Add-EvidenceMetadata {
    <#
    .SYNOPSIS
        Adds metadata to an evidence object.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence,

        [Parameter(Mandatory)]
        [object]$Metadata
    )

    $Evidence | Add-Member `
        -MemberType NoteProperty `
        -Name Metadata `
        -Value $Metadata `
        -Force

    return $Evidence
}

#endregion

#region Collection Metadata

function Set-EvidenceCollectionMetadata {
    <#
    .SYNOPSIS
        Adds collection information to evidence.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence,

        [Parameter(Mandatory)]
        [string]$CollectorName,

        [string]$RunId
    )

    $collection = [PSCustomObject]@{
        Collector   = $CollectorName
        RunId       = $RunId
        CollectedAt = (Get-Date).ToUniversalTime()
    }

    $Evidence | Add-Member `
        -MemberType NoteProperty `
        -Name Collection `
        -Value $collection `
        -Force

    return $Evidence
}

#endregion

#region Lineage

function Add-EvidenceProcessingHistory {
    <#
    .SYNOPSIS
        Records evidence processing actions.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence,

        [Parameter(Mandatory)]
        [string]$Action,

        [string]$Component = "Unknown"
    )

    $historyItem = [PSCustomObject]@{
        Action    = $Action
        Component = $Component
        Timestamp = (Get-Date).ToUniversalTime()
    }

    if ($Evidence.PSObject.Properties.Name -contains "ProcessingHistory") {

        $Evidence.ProcessingHistory += $historyItem

    }
    else {

        $Evidence | Add-Member `
            -MemberType NoteProperty `
            -Name ProcessingHistory `
            -Value @($historyItem) `
            -Force

    }

    return $Evidence
}

function Get-EvidenceLineage {
    <#
    .SYNOPSIS
        Returns evidence lineage information.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence
    )

    [PSCustomObject]@{
        EvidenceId        = $Evidence.EvidenceId
        Source            = $Evidence.Source
        Metadata          = $Evidence.Metadata
        Collection        = $Evidence.Collection
        ProcessingHistory = $Evidence.ProcessingHistory
    }
}

#endregion

#region Identification

function New-GuidId {
    <#
    .SYNOPSIS
        Creates a unique identifier.
    #>

    [CmdletBinding()]
    param()

    [guid]::NewGuid().ToString()
}

function Get-EvidenceMetadataSummary {
    <#
    .SYNOPSIS
        Returns metadata summary.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Evidence
    )

    [PSCustomObject]@{
        TotalEvidence = $Evidence.Count
        Sources       = @(
            $Evidence.Source |
            Select-Object -Unique
        ).Count
        Collectors    = @(
            $Evidence.Metadata.Collector |
            Select-Object -Unique
        ).Count
        Categories    = @(
            $Evidence.Metadata.Category |
            Select-Object -Unique
        ).Count
    }
}

#endregion

#region Validation

function Test-EvidenceMetadata {
    <#
    .SYNOPSIS
        Validates evidence metadata.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence
    )

    if (-not (
            $Evidence.PSObject.Properties.Name -contains "Metadata"
        )) {
        return $false
    }

    $required = @(
        "MetadataId"
        "Source"
        "CreatedAt"
    )

    foreach ($field in $required) {

        if (-not (
                $Evidence.Metadata.PSObject.Properties.Name -contains $field
            )) {
            return $false
        }
    }

    return $true
}

#endregion

Export-ModuleMember -Function @(
    "New-EvidenceMetadata"
    "Add-EvidenceMetadata"
    "Set-EvidenceCollectionMetadata"
    "Add-EvidenceProcessingHistory"
    "Get-EvidenceLineage"
    "Get-EvidenceMetadataSummary"
    "Test-EvidenceMetadata"
)
