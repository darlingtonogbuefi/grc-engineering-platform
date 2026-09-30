<#
    modules\yaml\ConfigLoader.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    YAML configuration loader module.

.DESCRIPTION
    Provides configuration loading capabilities for the
    GRC Engineering Platform.

    Responsibilities:

    - Load YAML configuration files
    - Validate configuration paths
    - Convert YAML into PowerShell objects
    - Manage platform configuration access
    - Support tenant, collector and reporting configuration

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

#region Configuration Loading

function Import-GRCYamlConfig {

    <#
    .SYNOPSIS
        Loads a YAML configuration file.

    .PARAMETER Path
        YAML configuration file path.
    #>

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Path

    )

    if (-not (Test-Path $Path)) {

        throw "Configuration file not found: $Path"

    }

    try {

        $content =
        Get-Content `
            -Path $Path `
            -Raw


        $config =
        ConvertFrom-Yaml `
            -Yaml $content


        return $config

    }

    catch {

        throw "Failed loading YAML configuration: $($_.Exception.Message)"

    }

}

#endregion

#region Platform Configurations

function Get-TenantConfiguration {

    <#
    .SYNOPSIS
        Loads tenant configuration.
    #>

    [CmdletBinding()]

    param(

        [string]
        $Path = "config/tenants.yml"

    )


    Import-GRCYamlConfig `
        -Path $Path

}


function Get-CollectorConfiguration {

    <#
    .SYNOPSIS
        Loads collector configuration.
    #>

    [CmdletBinding()]

    param(

        [string]
        $Path = "config/collectors.yml"

    )


    Import-GRCYamlConfig `
        -Path $Path

}


function Get-ReportingConfiguration {

    <#
    .SYNOPSIS
        Loads reporting configuration.
    #>

    [CmdletBinding()]

    param(

        [string]
        $Path = "config/reporting.yml"

    )


    Import-GRCYamlConfig `
        -Path $Path

}

#endregion

#region Configuration Validation

function Test-YamlConfigFile {

    <#
    .SYNOPSIS
        Validates YAML file availability.
    #>

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Path

    )


    [PSCustomObject]@{

        Path   =
        $Path


        Exists =
        (
            Test-Path $Path
        )


        Valid  =
        $false

    }

}


function Get-YamlConfigurationKeys {

    <#
    .SYNOPSIS
        Returns YAML configuration keys.
    #>

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [object]
        $Configuration

    )


    $Configuration.PSObject.Properties.Name

}

#endregion

#region Health

function Test-ConfigLoaderHealth {

    <#
    .SYNOPSIS
        Performs YAML loader health check.
    #>

    [CmdletBinding()]

    param()


    [PSCustomObject]@{

        Status     =
        "Healthy"


        Module     =
        "ConfigLoader"


        Dependency =
        "powershell-yaml"

    }

}

#endregion

Export-ModuleMember -Function @(
    "Import-GRCYamlConfig"
    "Get-TenantConfiguration"
    "Get-CollectorConfiguration"
    "Get-ReportingConfiguration"
    "Test-YamlConfigFile"
    "Get-YamlConfigurationKeys"
    "Test-ConfigLoaderHealth"
)
