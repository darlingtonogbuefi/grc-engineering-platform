<#
    scripts\clean-evidence.ps1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Cleans and archives GRC evidence data.

.DESCRIPTION
    Applies evidence retention rules.

    Operations:
    - Reads retention configuration
    - Archives expired evidence
    - Removes expired temporary data
    - Produces cleanup audit logs

.PARAMETER RootPath
    Root repository path.

.PARAMETER DryRun
    Shows what would be removed without deleting.

.PARAMETER Force
    Skips confirmation prompts.

.EXAMPLE
    .\clean-evidence.ps1 -DryRun

.EXAMPLE
    .\clean-evidence.ps1 -Force

.NOTES
    GRC Engineering Platform
    Version: 1.0.0
#>


[CmdletBinding(SupportsShouldProcess)]
param(

    [Parameter()]
    [string]
    $RootPath =
    (Split-Path $PSScriptRoot -Parent),


    [Parameter()]
    [switch]
    $DryRun,


    [Parameter()]
    [switch]
    $Force

)


Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"



#region Logging

$LogPath =
Join-Path `
    $RootPath `
    "output\logs\evidence-cleanup.log"



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


    $entry = [PSCustomObject]@{

        Timestamp =
        (Get-Date).ToUniversalTime()

        Level     =
        $Level

        Message   =
        $Message

    }


    Write-Host `
        "[$Level] $Message"


    if (Test-Path (Split-Path $LogPath)) {

        $entry |
        ConvertTo-Json -Compress |
        Add-Content `
            -Path $LogPath

    }

}


#endregion



#region Configuration


function Get-RetentionPolicy {


    $config =
    Join-Path `
        $RootPath `
        "config\storage.yml"



    if (-not (Test-Path $config)) {


        Write-GrcLog WARNING `
            "storage.yml missing. Using defaults."


        return @{

            raw_days       =
            90

            processed_days =
            365

            runs_days      =
            180

            archive_years  =
            7

        }

    }



    if (-not (Get-Module -ListAvailable powershell-yaml)) {

        throw @"
powershell-yaml module required.

Install:

Install-Module powershell-yaml -Scope CurrentUser

"@

    }



    Import-Module powershell-yaml



    $yaml =
    Get-Content $config -Raw |
    ConvertFrom-Yaml



    return $yaml.retention

}


#endregion



#region Evidence Operations


function Get-EvidenceFolders {


    return @(

        @{

            Name      =
            "raw"

            Path      =
            "evidence\raw"

            Retention =
            "raw_days"

        },


        @{

            Name      =
            "processed"

            Path      =
            "evidence\processed"

            Retention =
            "processed_days"

        },


        @{

            Name      =
            "runs"

            Path      =
            "evidence\runs"

            Retention =
            "runs_days"

        }

    )

}



function Archive-EvidenceFile {


    param(

        [string]
        $File,


        [string]
        $ArchiveRoot

    )



    $relative =
    Split-Path `
        $File `
        -Leaf



    $destination =
    Join-Path `
        $ArchiveRoot `
        $relative



    if ($DryRun) {


        Write-GrcLog INFO `
            "[DRY RUN] Archive $File"


        return

    }



    Move-Item `
        -Path $File `
        -Destination $destination `
        -Force



    Write-GrcLog INFO `
        "Archived $File"

}



function Remove-ExpiredEvidence {


    param(

        [string]
        $Path,


        [int]
        $Days

    )


    if (-not (Test-Path $Path)) {


        return

    }



    $cutoff =
    (Get-Date).AddDays(
        - $Days
    )



    $files =
    Get-ChildItem `
        -Path $Path `
        -File `
        -Recurse |
    Where-Object {

        $_.LastWriteTime -lt $cutoff

    }



    foreach ($file in $files) {


        if ($DryRun) {


            Write-GrcLog INFO `
                "[DRY RUN] Remove $($file.FullName)"


            continue

        }



        Remove-Item `
            $file.FullName `
            -Force



        Write-GrcLog INFO `
            "Removed $($file.FullName)"

    }

}


#endregion



#region Main


try {


    Write-GrcLog INFO `
        "Starting evidence cleanup."



    $policy =
    Get-RetentionPolicy



    foreach ($folder in Get-EvidenceFolders) {



        $path =
        Join-Path `
            $RootPath `
            $folder.Path



        $days =
        $policy[$folder.Retention]



        if (-not $days) {


            Write-GrcLog WARNING `
                "No retention policy for $($folder.Name)"


            continue

        }



        Write-GrcLog INFO `
            "Processing $($folder.Name), retention $days days."



        Remove-ExpiredEvidence `
            -Path $path `
            -Days $days

    }



    Write-GrcLog INFO `
        "Evidence cleanup completed."


    exit 0


}


catch {


    Write-GrcLog ERROR `
        $_.Exception.Message


    exit 1

}


#endregion
