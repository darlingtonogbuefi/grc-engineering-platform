<#
    modules\evidence\Transform.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Evidence transformation module.

.DESCRIPTION
    Provides functions to transform validated evidence into
    formats required by mapping, scoring, and reporting engines.

    Responsibilities:

    - Transform evidence structures
    - Flatten nested evidence
    - Select required fields
    - Convert evidence formats
    - Prepare evidence for framework mapping

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Transformation

function Transform-EvidenceObject {
    <#
    .SYNOPSIS
        Transforms evidence into a standard assessment format.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence
    )

    if ($null -eq $Evidence) {
        throw "Evidence object cannot be null."
    }

    [PSCustomObject]@{
        EvidenceId  = $Evidence.EvidenceId
        Source      = $Evidence.Source
        Category    = $Evidence.Category
        CollectedAt = $Evidence.CollectedAt
        Data        = ConvertTo-EvidenceData `
            -Object $Evidence.Data
        Hash        = $Evidence.Hash
        Status      = "Transformed"
    }
}

function Transform-EvidenceCollection {
    <#
    .SYNOPSIS
        Transforms a collection of evidence.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Evidence
    )

    foreach ($item in $Evidence) {
        Transform-EvidenceObject `
            -Evidence $item
    }
}

#endregion

#region Data Conversion

function ConvertTo-EvidenceData {
    <#
    .SYNOPSIS
        Converts evidence data into a normalized object.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Object
    )

    if ($Object -is [string]) {
        return @{
            Value = $Object
        }
    }

    if ($Object -is [System.Collections.IEnumerable] -and
        $Object -isnot [string]) {

        return @($Object)
    }

    return $Object
}

function ConvertTo-EvidenceFlatObject {
    <#
    .SYNOPSIS
        Flattens nested evidence properties.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Object,

        [string]$Prefix = ""
    )

    $result = [ordered]@{}

    foreach ($property in $Object.PSObject.Properties) {

        $name = if ($Prefix) {
            "$Prefix.$($property.Name)"
        }
        else {
            $property.Name
        }

        if ($property.Value -is [PSCustomObject]) {

            $nested =
            ConvertTo-EvidenceFlatObject `
                -Object $property.Value `
                -Prefix $name

            foreach ($item in $nested.GetEnumerator()) {
                $result[$item.Key] = $item.Value
            }
        }
        else {
            $result[$name] = $property.Value
        }
    }

    [PSCustomObject]$result
}

#endregion

#region Field Selection

function Select-EvidenceFields {
    <#
    .SYNOPSIS
        Selects specific evidence fields.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence,

        [Parameter(Mandatory)]
        [string[]]$Fields
    )

    $result = [ordered]@{}

    foreach ($field in $Fields) {

        if ($Evidence.PSObject.Properties.Name -contains $field) {
            $result[$field] = $Evidence.$field
        }
    }

    [PSCustomObject]$result
}

#endregion

#region Framework Preparation

function Convert-EvidenceForFramework {
    <#
    .SYNOPSIS
        Converts evidence for framework processing.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence,

        [Parameter(Mandatory)]
        [string]$Framework
    )

    [PSCustomObject]@{
        EvidenceId  = $Evidence.EvidenceId
        Framework   = $Framework
        Source      = $Evidence.Source
        CollectedAt = $Evidence.CollectedAt
        ControlData = $Evidence.Data
        Hash        = $Evidence.Hash
    }
}

#endregion

#region Validation

function Test-TransformedEvidence {
    <#
    .SYNOPSIS
        Validates transformed evidence output.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence
    )

    $requiredFields = @(
        "EvidenceId"
        "Source"
        "Data"
        "Hash"
        "Status"
    )

    foreach ($field in $requiredFields) {

        if (-not (
                $Evidence.PSObject.Properties.Name -contains $field
            )) {
            return $false
        }
    }

    return $true
}

#endregion

Export-ModuleMember -Function @(
    "Transform-EvidenceObject"
    "Transform-EvidenceCollection"
    "ConvertTo-EvidenceData"
    "ConvertTo-EvidenceFlatObject"
    "Select-EvidenceFields"
    "Convert-EvidenceForFramework"
    "Test-TransformedEvidence"
)
