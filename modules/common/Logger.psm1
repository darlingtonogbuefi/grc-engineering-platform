<#
    modules\common\Logger.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Provides common logging functionality.

.DESCRIPTION
    Centralised logging module used by GRC automation scripts.

    Features:
    - UTC timestamps
    - Console output
    - JSON structured log files
    - Log severity levels

    Supported levels:
    - INFO
    - WARNING
    - ERROR
    - DEBUG

.EXAMPLE
    Write-GrcLog `
        -Level INFO `
        -Message "Evidence collection started"

.EXAMPLE
    Write-GrcLog `
        -Level ERROR `
        -Message "Validation failed"

.NOTES
    GRC Engineering Platform
    Version: 1.0.0
#>


Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"



#region Logging Configuration


$DefaultLogPath =
"output\logs\grc-platform.log"



#endregion



#region Logging Functions


function Write-GrcLog {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [ValidateSet(
            "INFO",
            "WARNING",
            "ERROR",
            "DEBUG"
        )]
        [string]
        $Level,


        [Parameter(Mandatory)]
        [string]
        $Message,


        [Parameter()]
        [string]
        $LogPath =
        $DefaultLogPath

    )


    $timestamp =
    (Get-Date).ToUniversalTime()



    $entry =
    [PSCustomObject]@{

        Timestamp =
        $timestamp.ToString(
            "yyyy-MM-ddTHH:mm:ssZ"
        )


        Level =
        $Level


        Message =
        $Message

    }



    switch ($Level) {

        "INFO" {

            Write-Host `
                "[$Level] $Message" `
                -ForegroundColor Green

        }


        "WARNING" {

            Write-Host `
                "[$Level] $Message" `
                -ForegroundColor Yellow

        }


        "ERROR" {

            Write-Host `
                "[$Level] $Message" `
                -ForegroundColor Red

        }


        "DEBUG" {

            Write-Host `
                "[$Level] $Message" `
                -ForegroundColor Cyan

        }

    }



    $directory =
    Split-Path `
        -Path $LogPath `
        -Parent



    if (-not (Test-Path $directory)) {


        New-Item `
            -Path $directory `
            -ItemType Directory `
            -Force |
        Out-Null

    }



    $entry |
    ConvertTo-Json -Compress |
    Add-Content `
        -Path $LogPath

}



function Get-GrcLogPath {


    return $DefaultLogPath

}



#endregion



Export-ModuleMember `
    -Function `
        Write-GrcLog,
        Get-GrcLogPath
