<#
    modules\common\Helpers.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Provides common helper functions.

.DESCRIPTION
    Contains reusable utility functions used throughout the
    GRC Engineering Platform.

    Functions include:
    - Directory management
    - File operations
    - Date/time helpers
    - Hash generation
    - JSON utilities

.NOTES
    GRC Engineering Platform
    Version: 1.0.0
#>


Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"



#region Directory Functions


function Ensure-Directory {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Path

    )


    if (-not (Test-Path $Path)) {

        New-Item `
            -ItemType Directory `
            -Path $Path `
            -Force |
        Out-Null

    }


    return (
        Resolve-Path $Path
    ).Path

}


#endregion



#region File Functions


function Test-FileExists {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Path

    )


    return (
        Test-Path `
            -Path $Path `
            -PathType Leaf
    )

}



function Get-FileHashSafe {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Path,


        [ValidateSet(
            "SHA1",
            "SHA256",
            "SHA384",
            "SHA512",
            "MD5"
        )]
        [string]
        $Algorithm = "SHA256"

    )


    if (-not (Test-Path $Path)) {

        throw "File not found: $Path"

    }


    return (
        Get-FileHash `
            -Path $Path `
            -Algorithm $Algorithm
    ).Hash

}


#endregion



#region Date Functions


function Get-UtcNow {

    [CmdletBinding()]

    param()


    return (
        Get-Date
    ).ToUniversalTime()

}



function Get-TimeStamp {

    [CmdletBinding()]

    param()


    return (
        Get-Date
    ).ToString(
        "yyyyMMdd-HHmmss"
    )

}


#endregion



#region JSON Functions


function Save-Json {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [object]
        $InputObject,


        [Parameter(Mandatory)]
        [string]
        $Path

    )


    $directory =
    Split-Path `
        $Path `
        -Parent


    Ensure-Directory `
        -Path $directory |
    Out-Null


    $InputObject |
    ConvertTo-Json `
        -Depth 10 |
    Set-Content `
        -Path $Path `
        -Encoding UTF8

}



function Read-Json {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Path

    )


    if (-not (Test-Path $Path)) {

        throw "JSON file not found: $Path"

    }


    return (

        Get-Content `
            -Path $Path `
            -Raw |

        ConvertFrom-Json

    )

}


#endregion



#region Environment Functions


function Test-IsAdministrator {

    [CmdletBinding()]

    param()


    $identity =
    [Security.Principal.WindowsIdentity]::GetCurrent()


    $principal =
    New-Object `
        Security.Principal.WindowsPrincipal `
        $identity


    return $principal.IsInRole(

        [Security.Principal.WindowsBuiltInRole]::Administrator

    )

}


#endregion



Export-ModuleMember `
    -Function `
        Ensure-Directory,
        Test-FileExists,
        Get-FileHashSafe,
        Get-UtcNow,
        Get-TimeStamp,
        Save-Json,
        Read-Json,
        Test-IsAdministrator
