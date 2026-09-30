<#
    modules\schema\Validation.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    JSON schema validation module.

.DESCRIPTION
    Provides common validation operations for configuration,
    frameworks, collectors, evidence and reporting objects.

    Responsibilities:

    - Validate JSON documents
    - Validate PowerShell objects
    - Validate required properties
    - Validate schema versions
    - Produce validation results

.NOTES
    GRC Engineering Platform
    Version 1.0.0

    Dependency:
        modules\schema\JsonSchema.psm1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Dependencies

Import-Module `
    "$PSScriptRoot\JsonSchema.psm1" `
    -Force `
    -ErrorAction Stop

#endregion

#region Validation Results

function New-ValidationResult {
    <#
    .SYNOPSIS
        Creates a validation result.
    #>

    [CmdletBinding()]
    param(
        [bool]$Valid,

        [string[]]$Errors = @(),

        [string[]]$Warnings = @()
    )

    [PSCustomObject]@{
        Valid    = $Valid
        Errors   = $Errors
        Warnings = $Warnings
    }
}

#endregion

#region Object Validation

function Test-RequiredProperties {
    <#
    .SYNOPSIS
        Validates required object properties.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Object,

        [Parameter(Mandatory)]
        [string[]]$RequiredProperties
    )

    $errors = @()

    foreach ($property in $RequiredProperties) {

        if (-not $Object.PSObject.Properties.Name.Contains($property)) {

            $errors += "Missing required property '$property'."
            continue

        }

        if ($null -eq $Object.$property) {

            $errors += "Property '$property' is null."

        }

    }

    New-ValidationResult `
        -Valid ($errors.Count -eq 0) `
        -Errors $errors
}

#endregion

#region Schema Validation

function Test-JsonObject {
    <#
    .SYNOPSIS
        Performs basic JSON schema validation.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Object,

        [Parameter(Mandatory)]
        [object]$Schema
    )

    $required = @()

    if ($Schema.required) {

        $required = @($Schema.required)

    }

    Test-RequiredProperties `
        -Object $Object `
        -RequiredProperties $required
}

function Test-JsonFile {
    <#
    .SYNOPSIS
        Validates a JSON file.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Path,

        [Parameter(Mandatory)]
        [string]$SchemaName
    )

    if (-not (Test-Path $Path)) {

        throw "JSON file not found: $Path"

    }

    $schema =
    Get-JsonSchema `
        -Name $SchemaName

    $object =
    Get-Content `
        -Path $Path `
        -Raw |
    ConvertFrom-Json

    Test-JsonObject `
        -Object $object `
        -Schema $schema
}

#endregion

#region Specialized Validation

function Test-CollectorDefinition {
    <#
    .SYNOPSIS
        Validates collector definition.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Collector
    )

    $schema =
    Get-JsonSchema `
        -Name "collector"

    Test-JsonObject `
        -Object $Collector `
        -Schema $schema
}

function Test-EvidenceObject {
    <#
    .SYNOPSIS
        Validates evidence object.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence
    )

    $schema =
    Get-JsonSchema `
        -Name "evidence"

    Test-JsonObject `
        -Object $Evidence `
        -Schema $schema
}

function Test-FrameworkDefinition {
    <#
    .SYNOPSIS
        Validates framework definition.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Framework
    )

    $schema =
    Get-JsonSchema `
        -Name "framework"

    Test-JsonObject `
        -Object $Framework `
        -Schema $schema
}

#endregion

#region Health

function Test-ValidationHealth {
    <#
    .SYNOPSIS
        Performs validation module health check.
    #>

    [CmdletBinding()]
    param()

    [PSCustomObject]@{
        Status             = "Healthy"
        Module             = "Validation"
        SchemaModuleLoaded = $null -ne (
            Get-Module JsonSchema
        )
    }
}

#endregion

Export-ModuleMember -Function @(
    "New-ValidationResult"
    "Test-RequiredProperties"
    "Test-JsonObject"
    "Test-JsonFile"
    "Test-CollectorDefinition"
    "Test-EvidenceObject"
    "Test-FrameworkDefinition"
    "Test-ValidationHealth"
)
