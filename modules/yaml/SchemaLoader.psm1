<#
    modules\yaml\SchemaLoader.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    YAML schema loader module.

.DESCRIPTION
    Provides schema discovery and loading capabilities
    for validating GRC platform YAML configuration files.

    Responsibilities:

    - Load YAML validation schemas
    - Discover schema definitions
    - Provide schema metadata
    - Validate schema availability
    - Support configuration validation workflows

.NOTES
    GRC Engineering Platform
    Version: 1.0.0

    Required Module:

        powershell-yaml
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Dependencies

if (-not (Get-Module -ListAvailable powershell-yaml)) {

    throw @"

Required module missing:

powershell-yaml

Install:

Install-Module powershell-yaml -Scope CurrentUser

"@

}

Import-Module `
    powershell-yaml `
    -ErrorAction Stop

#endregion

#region Configuration

$script:SchemaRoot =
Join-Path `
    -Path (Get-Location) `
    -ChildPath "schemas"

#endregion

#region Schema Loading

function Import-GRCSchema {

    <#
    .SYNOPSIS
        Loads a YAML schema file.

    .PARAMETER Path
        Schema file path.
    #>

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Path

    )


    if (-not (Test-Path $Path)) {

        throw "Schema file not found: $Path"

    }


    try {

        $yaml =
        Get-Content `
            -Path $Path `
            -Raw


        ConvertFrom-Yaml `
            -Yaml $yaml

    }

    catch {

        throw "Failed loading schema: $($_.Exception.Message)"

    }

}

#endregion

#region Schema Discovery

function Get-GRCSchemaList {

    <#
    .SYNOPSIS
        Returns available schemas.
    #>

    [CmdletBinding()]

    param(

        [string]
        $Path = $script:SchemaRoot

    )


    if (-not (Test-Path $Path)) {

        return @()

    }


    Get-ChildItem `
        -Path $Path `
        -Filter "*.yml" `
        -File

}


function Get-GRCSchemaPath {

    <#
    .SYNOPSIS
        Resolves schema path.

    .PARAMETER Name
        Schema file name.
    #>

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Name

    )


    $schema =
    Join-Path `
        -Path $script:SchemaRoot `
        -ChildPath $Name


    if (-not (Test-Path $schema)) {

        throw "Schema not found: $Name"

    }


    Resolve-Path $schema

}

#endregion

#region Schema Metadata

function Get-GRCSchemaMetadata {

    <#
    .SYNOPSIS
        Returns schema metadata.
    #>

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Path

    )


    $file =
    Get-Item `
        -Path $Path


    [PSCustomObject]@{

        Name     =
        $file.Name


        Path     =
        $file.FullName


        Size     =
        $file.Length


        Modified =
        $file.LastWriteTimeUtc


    }

}

#endregion

#region Validation Support

function Test-GRCSchemaExists {

    <#
    .SYNOPSIS
        Tests schema availability.
    #>

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Name

    )


    $path =
    Join-Path `
        -Path $script:SchemaRoot `
        -ChildPath $Name


    Test-Path $path

}

#endregion

#region Health

function Test-SchemaLoaderHealth {

    <#
    .SYNOPSIS
        Performs schema loader health check.
    #>

    [CmdletBinding()]

    param()


    [PSCustomObject]@{

        Status     =
        "Healthy"


        Module     =
        "SchemaLoader"


        SchemaRoot =
        $script:SchemaRoot


        Available  =
        (
            Test-Path $script:SchemaRoot
        )

    }

}

#endregion

Export-ModuleMember -Function @(
    "Import-GRCSchema"
    "Get-GRCSchemaList"
    "Get-GRCSchemaPath"
    "Get-GRCSchemaMetadata"
    "Test-GRCSchemaExists"
    "Test-SchemaLoaderHealth"
)
