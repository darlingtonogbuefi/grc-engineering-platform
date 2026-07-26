<#
    modules\authentication\TokenCache.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Provides token cache management.

.DESCRIPTION
    Manages authentication token metadata for supported providers.

    This module stores token metadata only. It is not intended to
    persist or expose access tokens themselves.

    Features:

    - Create cache directory
    - Save token metadata
    - Read cached metadata
    - Test cache expiry
    - Remove cached entries
    - Clear cache

.NOTES
    GRC Engineering Platform
    Version: 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"



#region Cache Configuration


$TokenCacheDirectory =
Join-Path `
    $env:LOCALAPPDATA `
    "GRCEngineeringPlatform\TokenCache"



#endregion



#region Internal Helpers


function Get-TokenCachePath {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Provider

    )


    if (-not (Test-Path $TokenCacheDirectory)) {

        New-Item `
            -Path $TokenCacheDirectory `
            -ItemType Directory `
            -Force |
        Out-Null

    }


    return (
        Join-Path `
            $TokenCacheDirectory `
            "$Provider.json"
    )

}


#endregion



#region Cache Functions


function Save-TokenCache {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Provider,


        [Parameter(Mandatory)]
        [datetime]
        $ExpiresOn,


        [Parameter()]
        [string]
        $TenantId,


        [Parameter()]
        [string]
        $Account

    )


    $cache = [PSCustomObject]@{

        Provider =
        $Provider

        CachedAt =
        (Get-Date).ToUniversalTime()

        ExpiresOn =
        $ExpiresOn.ToUniversalTime()

        TenantId =
        $TenantId

        Account =
        $Account

    }


    $cache |
    ConvertTo-Json -Depth 5 |
    Set-Content `
        -Path (
            Get-TokenCachePath `
                -Provider $Provider
        ) `
        -Encoding UTF8

}



function Get-TokenCache {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Provider

    )


    $path =
    Get-TokenCachePath `
        -Provider $Provider


    if (-not (Test-Path $path)) {

        return $null

    }


    return (

        Get-Content `
            -Path $path `
            -Raw |

        ConvertFrom-Json

    )

}



function Test-TokenCacheExpired {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Provider

    )


    $cache =
    Get-TokenCache `
        -Provider $Provider


    if ($null -eq $cache) {

        return $true

    }


    return (
        [datetime]$cache.ExpiresOn
    ) -le (Get-Date).ToUniversalTime()

}



function Remove-TokenCache {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Provider

    )


    $path =
    Get-TokenCachePath `
        -Provider $Provider


    if (Test-Path $path) {

        Remove-Item `
            -Path $path `
            -Force

    }

}



function Clear-TokenCache {

    [CmdletBinding()]

    param()


    if (Test-Path $TokenCacheDirectory) {

        Get-ChildItem `
            -Path $TokenCacheDirectory `
            -Filter *.json |
        Remove-Item `
            -Force

    }

}



function Get-TokenCacheProviders {

    [CmdletBinding()]

    param()


    if (-not (Test-Path $TokenCacheDirectory)) {

        return @()

    }


    Get-ChildItem `
        -Path $TokenCacheDirectory `
        -Filter *.json |
    Select-Object `
        -ExpandProperty BaseName

}



#endregion



Export-ModuleMember `
    -Function `
        Save-TokenCache,
        Get-TokenCache,
        Test-TokenCacheExpired,
        Remove-TokenCache,
        Clear-TokenCache,
        Get-TokenCacheProviders
