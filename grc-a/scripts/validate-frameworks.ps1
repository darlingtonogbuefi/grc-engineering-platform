<#
    validate-frameworks.ps1

    GRC Engineering Platform
#>

<#
    scripts\validate-frameworks.ps1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Validates configured compliance frameworks.

.DESCRIPTION
    Checks that supported GRC compliance frameworks are correctly
    configured and available.

    Operations:
    - Loads platform configuration
    - Validates framework directories
    - Checks required report locations
    - Produces validation audit logs

.PARAMETER RootPath
    Root repository path.

.PARAMETER Framework
    Optional framework name to validate.

.PARAMETER Detailed
    Produces detailed validation output.

.EXAMPLE
    .\validate-frameworks.ps1

.EXAMPLE
    .\validate-frameworks.ps1 -Framework ISO27001

.EXAMPLE
    .\validate-frameworks.ps1 -Detailed

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
    [switch]
    $Detailed

)


Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"



#region Modules


Import-Module `
    "$RootPath\modules\common\Logger.psm1"

Import-Module `
    "$RootPath\modules\common\Config.psm1"

Import-Module `
    "$RootPath\modules\common\Helpers.psm1"

Import-Module `
    "$RootPath\modules\common\Exceptions.psm1"

Import-Module `
    "$RootPath\modules\common\Constants.psm1"



#endregion



#region Configuration


function Get-FrameworkList {


    if ($Framework) {

        return @($Framework)

    }


    return $ComplianceFrameworks

}



#endregion



#region Validation


function Test-FrameworkDirectory {


    param(

        [Parameter(Mandatory)]
        [string]
        $Name

    )


    $path =
    Join-Path `
        $RootPath `
        "reports\$Name"



    $result =
    [PSCustomObject]@{

        Framework =
        $Name


        Path      =
        $path


        Exists    =
        (Test-Path $path)


        Status    =
        "FAILED"

    }



    if ($result.Exists) {

        $result.Status =
        "PASSED"

    }



    return $result

}



function Test-FrameworkStructure {


    param(

        [Parameter(Mandatory)]
        [string]
        $Name

    )



    $required =
    @(
        "reports\$Name"
    )



    foreach ($item in $required) {


        $path =
        Join-Path `
            $RootPath `
            $item



        if (-not (Test-Path $path)) {


            Write-GrcLog `
                -Level WARNING `
                -Message `
                "Missing framework path: $path"


            return $false

        }

    }


    return $true

}



#endregion



#region Main


try {


    Write-GrcLog `
        -Level INFO `
        -Message `
        "Starting framework validation."



    $results =
    @()



    foreach ($frameworkName in Get-FrameworkList) {


        Write-GrcLog `
            -Level INFO `
            -Message `
            "Validating framework: $frameworkName"



        $validation =
        Test-FrameworkDirectory `
            -Name $frameworkName



        if ($Detailed) {


            Write-Host ""

            Write-Host `
                "Framework: $($validation.Framework)"

            Write-Host `
                "Location : $($validation.Path)"

            Write-Host `
                "Status   : $($validation.Status)"

        }



        $results +=
        $validation

    }



    Write-GrcLog `
        -Level INFO `
        -Message `
        "Framework validation completed."



    $failed =
    $results |
    Where-Object {
        $_.Status -eq "FAILED"
    }



    if ($failed) {


        Write-GrcLog `
            -Level ERROR `
            -Message `
            "$($failed.Count) framework validation failures detected."



        $results |
        ConvertTo-Json -Depth 5 |
        Out-File `
            "$RootPath\output\framework-validation.json"



        exit 1

    }



    $results |
    ConvertTo-Json -Depth 5 |
    Out-File `
        "$RootPath\output\framework-validation.json"



    exit 0


}


catch {


    Write-GrcLog `
        -Level ERROR `
        -Message `
        $_.Exception.Message


    exit 1

}


#endregion
