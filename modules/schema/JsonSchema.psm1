<#
    modules\schema\JsonSchema.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    JSON Schema management module.

.DESCRIPTION
    Provides common JSON Schema operations for the
    GRC Engineering Platform.

    Responsibilities:

    - Load JSON schema files
    - Parse JSON schemas
    - Validate schema existence
    - Retrieve schema metadata
    - Support schema discovery

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Schema Loading

function Import-JsonSchema {
    <#
    .SYNOPSIS
        Loads a JSON schema file.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [ValidateScript({
                Test-Path $_
            })]
        [string]$Path
    )

    Get-Content `
        -Path $Path `
        -Raw |
    ConvertFrom-Json
}

#endregion

#region Discovery

function Get-JsonSchema {
    <#
    .SYNOPSIS
        Returns a schema object.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Name,

        [string]$SchemaRoot = "schemas"
    )

    $path =
    Join-Path `
        -Path $SchemaRoot `
        -ChildPath "$Name.schema.json"

    if (-not (Test-Path $path)) {

        throw "Schema '$Name' was not found."

    }

    Import-JsonSchema `
        -Path $path
}

function Get-JsonSchemaFiles {
    <#
    .SYNOPSIS
        Returns available schema files.
    #>

    [CmdletBinding()]
    param(
        [string]$SchemaRoot = "schemas"
    )

    if (-not (Test-Path $SchemaRoot)) {

        return @()

    }

    Get-ChildItem `
        -Path $SchemaRoot `
        -Filter *.schema.json `
        -File
}

#endregion

#region Metadata

function Get-JsonSchemaMetadata {
    <#
    .SYNOPSIS
        Returns schema metadata.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Schema
    )

    [PSCustomObject]@{
        Id          = $Schema.'$id'
        Title       = $Schema.title
        Description = $Schema.description
        Schema      = $Schema.'$schema'
        Type        = $Schema.type
    }
}

#endregion

#region Validation

function Test-JsonSchemaExists {
    <#
    .SYNOPSIS
        Tests whether a schema exists.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Name,

        [string]$SchemaRoot = "schemas"
    )

    Test-Path (
        Join-Path `
            -Path $SchemaRoot `
            -ChildPath "$Name.schema.json"
    )
}

#endregion

#region Health

function Test-JsonSchemaHealth {
    <#
    .SYNOPSIS
        Performs schema module health check.
    #>

    [CmdletBinding()]
    param(
        [string]$SchemaRoot = "schemas"
    )

    [PSCustomObject]@{
        Status          = "Healthy"
        SchemaDirectory = (
            Resolve-Path `
                -Path $SchemaRoot `
                -ErrorAction SilentlyContinue
        )
        SchemaCount     = @(
            Get-JsonSchemaFiles `
                -SchemaRoot $SchemaRoot
        ).Count
    }
}

#endregion

Export-ModuleMember -Function @(
    "Import-JsonSchema"
    "Get-JsonSchema"
    "Get-JsonSchemaFiles"
    "Get-JsonSchemaMetadata"
    "Test-JsonSchemaExists"
    "Test-JsonSchemaHealth"
)
