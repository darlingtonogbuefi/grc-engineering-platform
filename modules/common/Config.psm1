<#
    modules\common\Config.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Provides configuration management functions.

.DESCRIPTION
    Loads platform configuration from YAML files and provides
    common access methods for GRC automation scripts.

    Configuration files:
    - config\platform.yml
    - config\storage.yml

    If configuration files are not present, sensible defaults
    are returned.

.NOTES
    GRC Engineering Platform
    Version: 1.0.0
#>


Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"



#region Configuration Paths


function Get-ConfigPath {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $RootPath,


        [Parameter(Mandatory)]
        [string]
        $FileName

    )


    return (
        Join-Path `
            $RootPath `
            "config\$FileName"
    )

}


#endregion



#region YAML Support


function Import-YamlModule {

    [CmdletBinding()]

    param()


    if (-not (Get-Module -ListAvailable powershell-yaml)) {

        throw @"
The 'powershell-yaml' module is required.

Install using:

Install-Module powershell-yaml -Scope CurrentUser
"@

    }


    Import-Module `
        powershell-yaml `
        -ErrorAction Stop

}


#endregion



#region Platform Configuration


function Get-PlatformConfig {

    [CmdletBinding()]

    param(

        [string]
        $RootPath =
        (Split-Path $PSScriptRoot -Parent -Parent)

    )


    $configFile =
    Get-ConfigPath `
        -RootPath $RootPath `
        -FileName "platform.yml"


    if (-not (Test-Path $configFile)) {

        return @{

            Platform = @{
                Name    = "GRC Engineering Platform"
                Version = "1.0.0"
            }

            Evidence = @{
                Root = "evidence"
            }

            Reports = @{
                Root = "reports"
            }

            Output = @{
                Root = "output"
            }

        }

    }


    Import-YamlModule


    return (

        Get-Content `
            $configFile `
            -Raw |

        ConvertFrom-Yaml

    )

}


#endregion



#region Storage Configuration


function Get-StorageConfig {

    [CmdletBinding()]

    param(

        [string]
        $RootPath =
        (Split-Path $PSScriptRoot -Parent -Parent)

    )


    $configFile =
    Get-ConfigPath `
        -RootPath $RootPath `
        -FileName "storage.yml"


    if (-not (Test-Path $configFile)) {

        return @{

            retention = @{

                raw_days       = 90
                processed_days = 365
                runs_days      = 180
                archive_years  = 7

            }

        }

    }


    Import-YamlModule


    return (

        Get-Content `
            $configFile `
            -Raw |

        ConvertFrom-Yaml

    )

}


#endregion



#region Generic Configuration


function Get-GrcConfig {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Name,


        [string]
        $RootPath =
        (Split-Path $PSScriptRoot -Parent -Parent)

    )


    $configFile =
    Get-ConfigPath `
        -RootPath $RootPath `
        -FileName "$Name.yml"


    if (-not (Test-Path $configFile)) {

        throw "Configuration file not found: $configFile"

    }


    Import-YamlModule


    return (

        Get-Content `
            $configFile `
            -Raw |

        ConvertFrom-Yaml

    )

}


#endregion



Export-ModuleMember `
    -Function `
        Get-ConfigPath,
        Import-YamlModule,
        Get-PlatformConfig,
        Get-StorageConfig,
        Get-GrcConfig
