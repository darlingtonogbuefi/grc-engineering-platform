<#
    modules\notifications\Teams.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Microsoft Teams notification module.

.DESCRIPTION
    Provides reusable Microsoft Teams notification operations
    for alerts, workflow updates, evidence events, and
    compliance reporting notifications.

    Responsibilities:

    - Validate Teams connectivity
    - Send Teams webhook notifications
    - Build adaptive message payloads
    - Send compliance alerts
    - Send pipeline status notifications

.NOTES
    GRC Engineering Platform
    Version 1.0.0

    Requires:

        Microsoft Teams Incoming Webhook
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Configuration

$script:TeamsWebhookUri = $null

#endregion

#region Initialization

function Initialize-TeamsClient {
    <#
    .SYNOPSIS
        Initializes Teams notification client.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$WebhookUri
    )

    if (-not (
            $WebhookUri.StartsWith("https://")
        )) {
        throw "Invalid Teams webhook URI."
    }

    $script:TeamsWebhookUri = $WebhookUri
}

#endregion

#region Connection

function Test-TeamsConnection {
    <#
    .SYNOPSIS
        Tests Teams notification configuration.
    #>

    [CmdletBinding()]
    param()

    return (
        -not [string]::IsNullOrWhiteSpace(
            $script:TeamsWebhookUri
        )
    )
}

#endregion

#region Messaging

function Send-TeamsMessage {
    <#
    .SYNOPSIS
        Sends a Teams message.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Title,

        [Parameter(Mandatory)]
        [string]$Message,

        [ValidateSet(
            "Information",
            "Success",
            "Warning",
            "Error"
        )]
        [string]$Severity = "Information"
    )

    if (-not (Test-TeamsConnection)) {
        throw "Teams client has not been initialized."
    }

    $color = switch ($Severity) {
        "Success" {
            "2EB886"
        }
        "Warning" {
            "FFCC00"
        }
        "Error" {
            "FF0000"
        }
        default {
            "0078D4"
        }
    }

    $payload = @{
        "@type"    = "MessageCard"
        "@context" = "http://schema.org/extensions"
        themeColor = $color
        summary    = $Title
        sections   = @(
            @{
                activityTitle = $Title
                text          = $Message
            }
        )
    }

    Invoke-RestMethod `
        -Uri $script:TeamsWebhookUri `
        -Method POST `
        -Body (
        $payload |
        ConvertTo-Json -Depth 10
    ) `
        -ContentType "application/json"
}

#endregion

#region Compliance Notifications

function Send-ComplianceAlert {
    <#
    .SYNOPSIS
        Sends a compliance alert notification.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Framework,

        [Parameter(Mandatory)]
        [string]$Control,

        [Parameter(Mandatory)]
        [string]$Status
    )

    Send-TeamsMessage `
        -Title "Compliance Alert" `
        -Message @"
Framework: $Framework

Control: $Control

Status: $Status
"@ `
        -Severity Warning
}

function Send-EvidenceNotification {
    <#
    .SYNOPSIS
        Sends evidence processing notification.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$EvidenceId,

        [Parameter(Mandatory)]
        [string]$Status
    )

    Send-TeamsMessage `
        -Title "Evidence Processing Update" `
        -Message @"
Evidence ID: $EvidenceId

Status: $Status
"@
}

function Send-PipelineNotification {
    <#
    .SYNOPSIS
        Sends pipeline execution notification.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Pipeline,

        [Parameter(Mandatory)]
        [string]$Status
    )

    $severity = if ($Status -eq "Failed") {
        "Error"
    }
    else {
        "Success"
    }

    Send-TeamsMessage `
        -Title "GRC Pipeline Status" `
        -Message @"
Pipeline: $Pipeline

Status: $Status
"@ `
        -Severity $severity
}

#endregion

#region Adaptive Cards

function New-TeamsAdaptiveCard {
    <#
    .SYNOPSIS
        Creates a Teams adaptive card payload.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Title,

        [Parameter(Mandatory)]
        [hashtable[]]$Facts
    )

    @{
        type    = "AdaptiveCard"
        version = "1.4"
        body    = @(
            @{
                type   = "TextBlock"
                text   = $Title
                weight = "Bolder"
            }
            @{
                type  = "FactSet"
                facts = $Facts
            }
        )
    }
}

#endregion

#region Health

function Test-TeamsHealth {
    <#
    .SYNOPSIS
        Performs Teams notification health check.
    #>

    [CmdletBinding()]
    param()

    try {

        [PSCustomObject]@{
            Configured = Test-TeamsConnection
            Status     = if (Test-TeamsConnection) {
                "Healthy"
            }
            else {
                "NotConfigured"
            }
        }

    }
    catch {
        [PSCustomObject]@{
            Configured = $false
            Status     = "Failed"
            Error      = $_.Exception.Message
        }
    }
}

#endregion

Export-ModuleMember -Function @(
    "Initialize-TeamsClient"
    "Test-TeamsConnection"
    "Send-TeamsMessage"
    "Send-ComplianceAlert"
    "Send-EvidenceNotification"
    "Send-PipelineNotification"
    "New-TeamsAdaptiveCard"
    "Test-TeamsHealth"
)
