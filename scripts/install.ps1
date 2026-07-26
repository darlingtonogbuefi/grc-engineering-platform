<#
    install.ps1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Installs and prepares the GRC Engineering Platform environment.

.DESCRIPTION
    Performs environment setup including:

    - PowerShell version validation
    - Required module installation
    - Repository validation
    - Module path configuration
    - Folder initialization
    - Dependency checks

.PARAMETER RootPath
    Root directory of the GRC platform repository.

.PARAMETER Force
    Reinstall dependencies even if already installed.

.PARAMETER SkipModules
    Skip PowerShell module installation.

.EXAMPLE
    .\install.ps1

.EXAMPLE
    .\install.ps1 -Force

.NOTES
    GRC Engineering Platform
    Version: 1.0.0
#>

[CmdletBinding()]
param(

    [Parameter()]
    [string]
    $RootPath =
    (Split-Path $PSScriptRoot -Parent),


    [Parameter()]
    [switch]
    $Force,


    [Parameter()]
    [switch]
    $SkipModules

)


Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"


#region Logging


$LogDirectory =
Join-Path `
    $RootPath `
    "output\logs"


$LogFile =
Join-Path `
    $LogDirectory `
    "install.log"



function Write-GrcLog {

    param(

        [ValidateSet(
            "INFO",
            "WARNING",
            "ERROR"
        )]
        [string]
        $Level,


        [string]
        $Message

    )


    $timestamp =
    Get-Date `
        -Format "yyyy-MM-dd HH:mm:ss"



    $entry =
    "$timestamp [$Level] $Message"



    Write-Host $entry



    if (Test-Path $LogDirectory) {

        Add-Content `
            -Path $LogFile `
            -Value $entry

    }

}


#endregion



#region Validation


function Test-PowerShellVersion {


    $requiredMajor = 7


    if ($PSVersionTable.PSVersion.Major -lt $requiredMajor) {


        throw @"

PowerShell $requiredMajor or higher is required.

Current version:
$($PSVersionTable.PSVersion)

"@

    }


    Write-GrcLog INFO `
        "PowerShell version validated."

}



function Test-Repository {


    $requiredPaths = @(

        "modules",
        "scripts",
        "config",
        "evidence",
        "reports"

    )



    foreach ($path in $requiredPaths) {


        $fullPath =
        Join-Path `
            $RootPath `
            $path



        if (-not (Test-Path $fullPath)) {


            throw `
                "Missing repository directory: $path"

        }

    }


    Write-GrcLog INFO `
        "Repository structure validated."

}


#endregion



#region Dependencies


function Install-RequiredModules {


    if ($SkipModules) {


        Write-GrcLog INFO `
            "Skipping PowerShell module installation."


        return

    }



    $modules = @(

        @{
            Name           =
            "powershell-yaml"

            MinimumVersion =
            "0.4.7"
        },


        @{
            Name           =
            "Pester"

            MinimumVersion =
            "5.5.0"
        },


        @{
            Name           =
            "PSScriptAnalyzer"

            MinimumVersion =
            "1.21.0"
        }

    )



    foreach ($module in $modules) {


        $installed =
        Get-Module `
            -ListAvailable `
            -Name $module.Name



        if ($installed -and -not $Force) {


            Write-GrcLog INFO `
                "$($module.Name) already installed."


            continue

        }



        Write-GrcLog INFO `
            "Installing $($module.Name)"



        Install-Module `
            -Name $module.Name `
            -MinimumVersion $module.MinimumVersion `
            -Scope CurrentUser `
            -Force `
            -AllowClobber

    }

}


#endregion



#region Module Registration


function Register-GrcModules {


    $moduleRoot =
    Join-Path `
        $RootPath `
        "modules"



    if (-not ($env:PSModulePath -split ";" |
            Where-Object {
                $_ -eq $moduleRoot
            })) {


        $env:PSModulePath =
        "$moduleRoot;$env:PSModulePath"


        Write-GrcLog INFO `
            "Registered local module path."

    }

}



#endregion



#region Environment Setup


function Initialize-Directories {


    $directories = @(

        "output\logs",

        "output\exports",

        "evidence\raw",

        "evidence\processed",

        "evidence\runs",

        "evidence\normalized",

        "evidence\archive"

    )



    foreach ($directory in $directories) {


        $path =
        Join-Path `
            $RootPath `
            $directory



        if (-not (Test-Path $path)) {


            New-Item `
                -ItemType Directory `
                -Path $path `
                -Force |
            Out-Null


            Write-GrcLog INFO `
                "Created $directory"

        }

    }

}


#endregion



#region Main


try {


    Write-GrcLog INFO `
        "Starting GRC platform installation."



    if (-not (Test-Path $RootPath)) {


        throw `
            "Root path does not exist: $RootPath"

    }



    Initialize-Directories


    Test-PowerShellVersion


    Test-Repository


    Install-RequiredModules


    Register-GrcModules



    Write-GrcLog INFO `
        "Installation completed successfully."


    exit 0


}

catch {


    Write-GrcLog ERROR `
        $_.Exception.Message


    exit 1

}


#endregion
