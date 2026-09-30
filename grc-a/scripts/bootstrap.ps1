<#
    scripts\bootstrap.ps1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Bootstraps the GRC Engineering Platform environment.

.DESCRIPTION
    Creates required directories, validates prerequisites,
    initializes platform metadata, and prepares the repository
    for development or execution.

.PARAMETER RootPath
    Root path of the GRC Engineering Platform repository.

.PARAMETER Force
    Recreate generated bootstrap files if they already exist.

.EXAMPLE
    .\bootstrap.ps1

.EXAMPLE
    .\bootstrap.ps1 -RootPath "C:\Projects\grc-engineering-platform"

.NOTES
    Author: GRC Engineering Platform
    Version: 1.0.0
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]
    $RootPath = (Split-Path $PSScriptRoot -Parent),

    [Parameter()]
    [switch]
    $Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"


#region Logging

$LogDirectory = Join-Path $RootPath "output\logs"

function Write-GrcLog {
    param(
        [Parameter(Mandatory)]
        [ValidateSet(
            "INFO",
            "WARNING",
            "ERROR"
        )]
        [string]
        $Level,

        [Parameter(Mandatory)]
        [string]
        $Message
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    $entry = @{
        Timestamp = $timestamp
        Level     = $Level
        Message   = $Message
    }

    $json = $entry | ConvertTo-Json -Compress

    Write-Host "[$Level] $Message"

    if (Test-Path $LogDirectory) {
        Add-Content `
            -Path (Join-Path $LogDirectory "bootstrap.log") `
            -Value $json
    }
}

#endregion


#region Validation

function Test-CommandExists {
    param(
        [Parameter(Mandatory)]
        [string]
        $Command
    )

    return $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}


function Test-Prerequisites {

    Write-GrcLog INFO "Checking prerequisites."

    $requirements = @(
        "pwsh",
        "git"
    )

    foreach ($tool in $requirements) {

        if (-not (Test-CommandExists $tool)) {

            throw "Required dependency missing: $tool"
        }

        Write-GrcLog INFO "$tool detected."
    }

}

#endregion


#region Folder Creation

function Initialize-FolderStructure {

    Write-GrcLog INFO "Creating platform directories."

    $folders = @(

        # Runtime data
        "evidence\raw",
        "evidence\processed",
        "evidence\runs",
        "evidence\normalized",
        "evidence\archive",

        # Reports
        "reports\CAF",
        "reports\ISO27001",
        "reports\SOC2",
        "reports\GovAssure",
        "reports\CyberEssentials",

        # Dashboards
        "dashboards\powerbi",
        "dashboards\grafana",
        "dashboards\azure-workbooks",

        # Runtime
        "output\logs",
        "output\exports",

        # Configuration
        "config",

        # Documentation
        "docs",

        # Tests
        "tests"
    )


    foreach ($folder in $folders) {

        $path = Join-Path $RootPath $folder

        if (-not (Test-Path $path)) {

            New-Item `
                -ItemType Directory `
                -Path $path `
                -Force | Out-Null

            Write-GrcLog INFO "Created $folder"
        }
    }

}

#endregion


#region Metadata

function Initialize-PlatformMetadata {

    $metadataPath =
    Join-Path $RootPath "config\platform.json"


    if ((Test-Path $metadataPath) -and (-not $Force)) {

        Write-GrcLog INFO "Platform metadata already exists."
        return
    }


    $metadata = @{
        Platform   = "GRC Engineering Platform"
        Version    = "1.0.0"
        Created    = (Get-Date).ToUniversalTime()
        Host       = $env:COMPUTERNAME
        User       = $env:USERNAME
        PowerShell = $PSVersionTable.PSVersion.ToString()
    }


    $metadata |
    ConvertTo-Json -Depth 5 |
    Set-Content `
        -Path $metadataPath `
        -Encoding UTF8


    Write-GrcLog INFO "Created platform metadata."

}

#endregion


#region Git Configuration

function Initialize-GitIgnore {

    $gitignore =
    Join-Path $RootPath ".gitignore"


    if ((Test-Path $gitignore) -and (-not $Force)) {
        return
    }


    @"
# Generated evidence
evidence/raw/*
evidence/processed/*
evidence/runs/*
evidence/archive/*

# Generated reports
reports/*/*.pdf
reports/*/*.html
reports/*/*.json

# Runtime output
output/logs/*
output/exports/*

# PowerShell
*.log

# Temporary files
*.tmp
*.bak
"@ |
    Set-Content $gitignore


    Write-GrcLog INFO "Created .gitignore."

}

#endregion


#region Main

try {

    Write-GrcLog INFO "Starting GRC platform bootstrap."

    if (-not (Test-Path $RootPath)) {

        throw "Repository root does not exist: $RootPath"
    }


    Test-Prerequisites

    Initialize-FolderStructure

    Initialize-PlatformMetadata

    Initialize-GitIgnore


    Write-GrcLog INFO "Bootstrap completed successfully."

    exit 0

}
catch {

    Write-GrcLog ERROR $_.Exception.Message

    exit 1

}

#endregion
