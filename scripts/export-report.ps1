<#
    scripts\export-report.ps1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Generates GRC compliance reports.

.DESCRIPTION
    Exports assessment results into supported formats.

    Supported formats:
    - HTML
    - JSON
    - CSV
    - Markdown

.PARAMETER Framework
    Compliance framework to export.

.PARAMETER InputPath
    Assessment result source.

.PARAMETER Format
    Output report format.

.PARAMETER OutputPath
    Report destination.

.EXAMPLE
    .\export-report.ps1 -Framework CAF -Format HTML

.EXAMPLE
    .\export-report.ps1 -Framework ISO27001 -Format JSON

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

[CmdletBinding()]
param(

    [Parameter(Mandatory)]
    [ValidateSet(
        "CAF",
        "ISO27001",
        "SOC2",
        "GovAssure",
        "CyberEssentials"
    )]
    [string]
    $Framework,


    [Parameter()]
    [ValidateSet(
        "HTML",
        "JSON",
        "CSV",
        "Markdown"
    )]
    [string]
    $Format = "HTML",


    [Parameter()]
    [string]
    $RootPath =
    (Split-Path $PSScriptRoot -Parent),


    [Parameter()]
    [string]
    $InputPath,


    [Parameter()]
    [string]
    $OutputPath

)


Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"


#region Logging

$LogFile =
Join-Path `
    $RootPath `
    "output\logs\report-export.log"



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


    $line =
    "$(Get-Date -Format s) [$Level] $Message"


    Write-Host $line


    if (Test-Path (Split-Path $LogFile)) {

        Add-Content `
            -Path $LogFile `
            -Value $line

    }

}

#endregion



#region Helpers


function Get-AssessmentData {


    param(
        [string]
        $Path
    )


    if (-not $Path) {


        $Path =
        Join-Path `
            $RootPath `
            "output\assessments\$Framework.json"

    }



    if (-not (Test-Path $Path)) {


        throw `
            "Assessment data not found: $Path"

    }



    Write-GrcLog INFO `
        "Loading assessment: $Path"



    return (
        Get-Content `
            -Path $Path `
            -Raw |
        ConvertFrom-Json
    )

}



function Resolve-OutputPath {


    if ($OutputPath) {

        return $OutputPath

    }



    $folder =
    Join-Path `
        $RootPath `
        "reports\$Framework"



    if (-not (Test-Path $folder)) {


        New-Item `
            -ItemType Directory `
            -Path $folder `
            -Force |
        Out-Null

    }



    $date =
    Get-Date -Format "yyyyMMdd"



    switch ($Format) {


        "HTML" {

            return Join-Path `
                $folder `
                "$Framework-$date.html"

        }


        "JSON" {

            return Join-Path `
                $folder `
                "$Framework-$date.json"

        }


        "CSV" {

            return Join-Path `
                $folder `
                "$Framework-$date.csv"

        }


        "Markdown" {

            return Join-Path `
                $folder `
                "$Framework-$date.md"

        }

    }

}


#endregion



#region Exporters


function Export-HtmlReport {


    param($Data, $Path)


    $html = @"
<!DOCTYPE html>

<html>

<head>

<title>
$Framework Compliance Report
</title>


<style>

body {
font-family: Arial;
margin:40px;
}

table {
border-collapse:collapse;
width:100%;
}

td,th {
border:1px solid #ccc;
padding:8px;
}

PASS {
color:green;
}

FAIL {
color:red;
}

</style>


</head>


<body>


<h1>
$Framework Compliance Assessment
</h1>


<p>
Generated:
$(Get-Date)
</p>


<table>

<tr>
<th>Control</th>
<th>Status</th>
<th>Score</th>
</tr>

"@



    foreach ($control in $Data.controls) {


        $html += @"

<tr>

<td>
$($control.id)
</td>

<td>
$($control.status)
</td>

<td>
$($control.score)
</td>

</tr>

"@

    }



    $html += @"

</table>

</body>

</html>

"@



    Set-Content `
        -Path $Path `
        -Value $html `
        -Encoding UTF8

}



function Export-MarkdownReport {


    param($Data, $Path)


    $content = @"

# $Framework Compliance Report

Generated: $(Get-Date)

| Control | Status | Score |
|---|---|---|

"@



    foreach ($control in $Data.controls) {


        $content +=
        "| $($control.id) | $($control.status) | $($control.score) |`n"

    }



    Set-Content `
        -Path $Path `
        -Value $content `
        -Encoding UTF8

}



#endregion



#region Main


try {


    Write-GrcLog INFO `
        "Starting report export."



    $data =
    Get-AssessmentData `
        -Path $InputPath



    $destination =
    Resolve-OutputPath



    switch ($Format) {


        "HTML" {

            Export-HtmlReport `
                -Data $data `
                -Path $destination

        }


        "JSON" {

            $data |
            ConvertTo-Json `
                -Depth 20 |
            Set-Content `
                $destination

        }


        "CSV" {


            $data.controls |
            Export-Csv `
                -Path $destination `
                -NoTypeInformation

        }


        "Markdown" {


            Export-MarkdownReport `
                -Data $data `
                -Path $destination

        }

    }



    Write-GrcLog INFO `
        "Report created: $destination"



    exit 0


}

catch {


    Write-GrcLog ERROR `
        $_.Exception.Message


    exit 1

}


#endregion
