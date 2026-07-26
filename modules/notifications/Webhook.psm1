<#
    modules\notifications\Email.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Email notification module.

.DESCRIPTION
    Provides reusable email notification operations for
    compliance alerts, evidence events, reports, and
    platform notifications.

    Responsibilities:

    - Configure SMTP notifications
    - Send email alerts
    - Send compliance reports
    - Send evidence notifications
    - Support HTML email content

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Configuration

$script:EmailConfig = @{
    SmtpServer = $null
    Port       = 587
    From       = $null
    UseSsl     = $true
    Credential = $null
}

#endregion

#region Initialization

function Initialize-EmailClient {
    <#
    .SYNOPSIS
        Initializes email notification settings.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$SmtpServer,

        [int]$Port = 587,

        [Parameter(Mandatory)]
        [string]$From,

        [bool]$UseSsl = $true,

        [PSCredential]$Credential
    )

    $script:EmailConfig.SmtpServer = $SmtpServer
    $script:EmailConfig.Port = $Port
    $script:EmailConfig.From = $From
    $script:EmailConfig.UseSsl = $UseSsl
    $script:EmailConfig.Credential = $Credential
}

#endregion

#region Connection

function Test-EmailConnection {
    <#
    .SYNOPSIS
        Tests email configuration.
    #>

    [CmdletBinding()]
    param()

    return (
        -not [string]::IsNullOrWhiteSpace(
            $script:EmailConfig.SmtpServer
        ) -and
        -not [string]::IsNullOrWhiteSpace(
            $script:EmailConfig.From
        )
    )
}

#endregion

#region Sending

function Send-GRCEmail {
    <#
    .SYNOPSIS
        Sends an email notification.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string[]]$To,

        [Parameter(Mandatory)]
        [string]$Subject,

        [Parameter(Mandatory)]
        [string]$Body,

        [switch]$Html
    )

    if (-not (Test-EmailConnection)) {
        throw "Email client has not been initialized."
    }

    $parameters = @{
        SmtpServer = $script:EmailConfig.SmtpServer
        Port       = $script:EmailConfig.Port
        From       = $script:EmailConfig.From
        To         = $To
        Subject    = $Subject
        Body       = $Body
        UseSsl     = $script:EmailConfig.UseSsl
    }

    if ($Html) {
        $parameters.BodyAsHtml = $true
    }

    if ($null -ne $script:EmailConfig.Credential) {
        $parameters.Credential =
        $script:EmailConfig.Credential
    }

    Send-MailMessage @parameters
}

#endregion

#region Compliance Notifications

function Send-ComplianceReportEmail {
    <#
    .SYNOPSIS
        Sends compliance report notification.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string[]]$Recipients,

        [Parameter(Mandatory)]
        [string]$Framework,

        [Parameter(Mandatory)]
        [string]$ReportPath
    )

    $body = @"
GRC Compliance Report Generated

Framework:
$Framework

Report Location:
$ReportPath

Generated:
$(Get-Date -Format u)
"@

    Send-GRCEmail `
        -To $Recipients `
        -Subject "Compliance Report - $Framework" `
        -Body $body
}

function Send-EvidenceEmail {
    <#
    .SYNOPSIS
        Sends evidence processing notification.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string[]]$Recipients,

        [Parameter(Mandatory)]
        [string]$EvidenceId,

        [Parameter(Mandatory)]
        [string]$Status
    )

    $body = @"
Evidence Processing Notification

Evidence ID:
$EvidenceId

Status:
$Status

Timestamp:
$(Get-Date -Format u)
"@

    Send-GRCEmail `
        -To $Recipients `
        -Subject "Evidence Status Update" `
        -Body $body
}

function Send-SecurityAlertEmail {
    <#
    .SYNOPSIS
        Sends security alert email.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string[]]$Recipients,

        [Parameter(Mandatory)]
        [string]$Alert
    )

    Send-GRCEmail `
        -To $Recipients `
        -Subject "GRC Security Alert" `
        -Body $Alert
}

#endregion

#region Templates

function New-EmailTemplate {
    <#
    .SYNOPSIS
        Creates HTML email template.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Title,

        [Parameter(Mandatory)]
        [string]$Content
    )

    @"
<html>
<body>
<h2>$Title</h2>
<p>$Content</p>
<hr/>
<p>GRC Engineering Platform</p>
</body>
</html>
"@
}

#endregion

#region Health

function Test-EmailHealth {
    <#
    .SYNOPSIS
        Performs email notification health check.
    #>

    [CmdletBinding()]
    param()

    try {

        [PSCustomObject]@{
            Configured = Test-EmailConnection
            Status     = if (Test-EmailConnection) {
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
    "Initialize-EmailClient"
    "Test-EmailConnection"
    "Send-GRCEmail"
    "Send-ComplianceReportEmail"
    "Send-EvidenceEmail"
    "Send-SecurityAlertEmail"
    "New-EmailTemplate"
    "Test-EmailHealth"
)
