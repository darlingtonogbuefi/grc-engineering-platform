<#
    modules\graph\GraphThrottle.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Microsoft Graph throttling and retry management module.

.DESCRIPTION
    Provides resilient execution handling for Microsoft Graph API calls.

    Responsibilities:
    - Detect throttling responses
    - Handle HTTP 429 responses
    - Honour Retry-After headers
    - Implement exponential backoff
    - Retry transient failures

.NOTES
    Version: 1.0.0
    Required Modules:
      Microsoft.Graph.Authentication
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Dependencies

Import-Module Microsoft.Graph.Authentication `
    -ErrorAction Stop

#endregion

#region Configuration

$DefaultRetryAttempts = 3
$DefaultRetryDelaySeconds = 5
$MaximumRetryDelaySeconds = 300

#endregion

#region Throttle Detection

function Test-GraphThrottleError {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [System.Exception]
        $Exception
    )

    $message = $Exception.Message

    return (
        $message -match "429" -or
        $message -match "Too Many Requests" -or
        $message -match "throttl"
    )
}

function Get-GraphRetryAfterSeconds {
    [CmdletBinding()]
    param(
        [Parameter()]
        $Exception
    )

    try {
        if ($Exception.Response.Headers) {
            $retryAfter = $Exception.Response.Headers["Retry-After"]

            if ($retryAfter) {
                return [int]$retryAfter
            }
        }
    }
    catch {
        return $DefaultRetryDelaySeconds
    }

    return $DefaultRetryDelaySeconds
}

#endregion

#region Retry Engine

function Invoke-GraphWithRetry {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [scriptblock]
        $ScriptBlock,

        [int]
        $RetryAttempts = $DefaultRetryAttempts,

        [int]
        $InitialDelaySeconds = $DefaultRetryDelaySeconds
    )

    $attempt = 0

    while ($true) {
        try {
            return & $ScriptBlock
        }
        catch {
            $attempt++

            if ($attempt -gt $RetryAttempts) {
                throw
            }

            if (-not (
                    Test-GraphThrottleError `
                        -Exception $_.Exception
                )) {
                throw
            }

            $delay = Get-GraphRetryAfterSeconds `
                -Exception $_.Exception

            if ($delay -le 0) {
                $delay = [Math]::Min(
                    (
                        $InitialDelaySeconds *
                        [Math]::Pow(2, $attempt - 1)
                    ),
                    $MaximumRetryDelaySeconds
                )
            }

            Start-Sleep -Seconds $delay
        }
    }
}

function Invoke-GraphRequestWithRetry {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]
        $Uri,

        [ValidateSet(
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE"
        )]
        [string]
        $Method = "GET",

        [object]
        $Body,

        [string]
        $ContentType = "application/json"
    )

    Invoke-GraphWithRetry {
        Invoke-MgGraphRequest `
            -Method $Method `
            -Uri $Uri `
            -Body $Body `
            -ContentType $ContentType
    }
}

#endregion

Export-ModuleMember -Function @(
    "Test-GraphThrottleError"
    "Get-GraphRetryAfterSeconds"
    "Invoke-GraphWithRetry"
    "Invoke-GraphRequestWithRetry"
)
