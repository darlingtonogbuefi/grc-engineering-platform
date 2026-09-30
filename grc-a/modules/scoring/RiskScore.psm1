<#
    modules\scoring\RiskScore.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Risk scoring module.

.DESCRIPTION
    Calculates risk scores from compliance assessment results.

    Responsibilities:

    - Calculate inherent risk
    - Calculate residual risk
    - Determine risk ratings
    - Prioritise remediation
    - Produce risk summaries

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Risk Calculation

function Get-RiskScore {
    <#
    .SYNOPSIS
        Calculates a numerical risk score.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [ValidateRange(1, 5)]
        [int]$Likelihood,

        [Parameter(Mandatory)]
        [ValidateRange(1, 5)]
        [int]$Impact
    )

    $Likelihood * $Impact
}

function Get-RiskRating {
    <#
    .SYNOPSIS
        Returns risk rating.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [int]$Score
    )

    switch ($Score) {

        { $_ -ge 20 } { "Critical"; break }

        { $_ -ge 15 } { "High"; break }

        { $_ -ge 8 } { "Medium"; break }

        default { "Low" }

    }
}

#endregion

#region Compliance Risk

function Get-ControlRisk {
    <#
    .SYNOPSIS
        Calculates risk for a control assessment.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$ControlResult,

        [ValidateRange(1, 5)]
        [int]$Likelihood = 3,

        [ValidateRange(1, 5)]
        [int]$Impact = 3
    )

    $score =
    if ($ControlResult.Status -eq "Pass") {

        0

    }
    else {

        Get-RiskScore `
            -Likelihood $Likelihood `
            -Impact $Impact

    }

    [PSCustomObject]@{
        Framework        = $ControlResult.Framework
        ControlId        = $ControlResult.ControlId
        ComplianceStatus = $ControlResult.Status
        RiskScore        = $score
        RiskRating       = Get-RiskRating -Score $score
        Likelihood       = $Likelihood
        Impact           = $Impact
        Assessed         = (Get-Date).ToUniversalTime()
    }
}

function Get-FrameworkRisk {
    <#
    .SYNOPSIS
        Calculates framework risk summary.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$RiskResults
    )

    if ($RiskResults.Count -eq 0) {

        return $null

    }

    $average =
    (
        $RiskResults |
        Measure-Object `
            -Property RiskScore `
            -Average
    ).Average

    [PSCustomObject]@{
        AverageRisk   = [math]::Round($average, 2)
        HighestRisk   = (
            $RiskResults |
            Measure-Object `
                -Property RiskScore `
                -Maximum
        ).Maximum
        LowestRisk    = (
            $RiskResults |
            Measure-Object `
                -Property RiskScore `
                -Minimum
        ).Minimum
        OverallRating = Get-RiskRating -Score ([int][math]::Round($average))
        Controls      = $RiskResults.Count
    }
}

#endregion

#region Prioritisation

function Get-RiskPriority {
    <#
    .SYNOPSIS
        Returns remediation priority.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$RiskRating
    )

    switch ($RiskRating) {

        "Critical" { "Immediate" }

        "High" { "High" }

        "Medium" { "Planned" }

        default { "Routine" }

    }
}

#endregion

#region Health

function Test-RiskScoringHealth {
    <#
    .SYNOPSIS
        Performs risk scoring health check.
    #>

    [CmdletBinding()]
    param()

    [PSCustomObject]@{
        Status = "Healthy"
        Module = "RiskScore"
        Model  = "Likelihood × Impact"
    }
}

#endregion

Export-ModuleMember -Function @(
    "Get-RiskScore"
    "Get-RiskRating"
    "Get-ControlRisk"
    "Get-FrameworkRisk"
    "Get-RiskPriority"
    "Test-RiskScoringHealth"
)
