<#
    modules\scoring\ScoreControl.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Control scoring module.

.DESCRIPTION
    Calculates compliance scores for individual controls using
    collected evidence and defined assessment rules.

    Responsibilities:

    - Score individual controls
    - Evaluate evidence
    - Determine compliance status
    - Calculate percentage scores
    - Generate assessment results

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Configuration

$script:PassingScore = 100

#endregion

#region Scoring

function Get-ControlScore {
    <#
    .SYNOPSIS
        Calculates score for a control.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Evidence
    )

    if ($Evidence.Count -eq 0) {

        return 0

    }

    $passed =
    @(
        $Evidence |
        Where-Object {
            $_.Status -eq "Pass"
        }
    ).Count

    [math]::Round(
        ($passed / $Evidence.Count) * 100,
        2
    )
}

function Get-ControlStatus {
    <#
    .SYNOPSIS
        Determines compliance status.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [double]$Score
    )

    switch ($Score) {

        { $_ -ge 100 } { return "Pass" }

        { $_ -ge 75 } { return "Partial" }

        default { return "Fail" }

    }
}

function Score-Control {
    <#
    .SYNOPSIS
        Scores a compliance control.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Framework,

        [Parameter(Mandatory)]
        [string]$ControlId,

        [Parameter(Mandatory)]
        [object[]]$Evidence
    )

    $score =
    Get-ControlScore `
        -Evidence $Evidence

    [PSCustomObject]@{
        Framework      = $Framework
        ControlId      = $ControlId
        Score          = $score
        Status         = Get-ControlStatus -Score $score
        EvidenceCount  = $Evidence.Count
        PassedEvidence = @(
            $Evidence |
            Where-Object {
                $_.Status -eq "Pass"
            }
        ).Count
        FailedEvidence = @(
            $Evidence |
            Where-Object {
                $_.Status -ne "Pass"
            }
        ).Count
        Assessed       = (Get-Date).ToUniversalTime()
    }
}

#endregion

#region Batch Processing

function Score-ControlSet {
    <#
    .SYNOPSIS
        Scores multiple controls.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Controls
    )

    foreach ($control in $Controls) {

        Score-Control `
            -Framework $control.Framework `
            -ControlId $control.ControlId `
            -Evidence $control.Evidence

    }
}

#endregion

#region Health

function Test-ControlScoringHealth {
    <#
    .SYNOPSIS
        Performs scoring health check.
    #>

    [CmdletBinding()]
    param()

    [PSCustomObject]@{
        Status       = "Healthy"
        Module       = "ScoreControl"
        PassingScore = $script:PassingScore
    }
}

#endregion

Export-ModuleMember -Function @(
    "Get-ControlScore"
    "Get-ControlStatus"
    "Score-Control"
    "Score-ControlSet"
    "Test-ControlScoringHealth"
)
