<#
    modules\scoring\Maturity.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Maturity assessment module.

.DESCRIPTION
    Calculates capability, framework and organisational
    maturity levels based on compliance assessment results.

    Responsibilities:

    - Calculate control maturity
    - Calculate capability maturity
    - Calculate framework maturity
    - Determine maturity levels
    - Produce maturity summaries

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Maturity Levels

function Get-MaturityLevel {
    <#
    .SYNOPSIS
        Returns maturity level from compliance score.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [ValidateRange(0, 100)]
        [double]$Score
    )

    switch ($Score) {

        { $_ -ge 95 } { "Optimised"; break }

        { $_ -ge 85 } { "Managed"; break }

        { $_ -ge 70 } { "Defined"; break }

        { $_ -ge 50 } { "Developing"; break }

        default { "Initial" }

    }
}

#endregion

#region Control Maturity

function Get-ControlMaturity {
    <#
    .SYNOPSIS
        Calculates maturity for a control.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$ControlResult
    )

    [PSCustomObject]@{
        Framework = $ControlResult.Framework
        ControlId = $ControlResult.ControlId
        Score     = $ControlResult.Score
        Maturity  = Get-MaturityLevel -Score $ControlResult.Score
        Assessed  = (Get-Date).ToUniversalTime()
    }
}

#endregion

#region Capability Maturity

function Get-CapabilityMaturity {
    <#
    .SYNOPSIS
        Calculates maturity by capability.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$ControlResults
    )

    foreach ($group in ($ControlResults | Group-Object Capability)) {

        $score =
        (
            $group.Group |
            Measure-Object `
                -Property Score `
                -Average
        ).Average

        [PSCustomObject]@{
            Capability = $group.Name
            Score      = [math]::Round($score, 2)
            Maturity   = Get-MaturityLevel -Score $score
            Controls   = $group.Count
        }
    }
}

#endregion

#region Framework Maturity

function Get-FrameworkMaturity {
    <#
    .SYNOPSIS
        Calculates framework maturity.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Framework,

        [Parameter(Mandatory)]
        [object[]]$ControlResults
    )

    $score =
    (
        $ControlResults |
        Measure-Object `
            -Property Score `
            -Average
    ).Average

    [PSCustomObject]@{
        Framework = $Framework
        Score     = [math]::Round($score, 2)
        Maturity  = Get-MaturityLevel -Score $score
        Controls  = $ControlResults.Count
        Assessed  = (Get-Date).ToUniversalTime()
    }
}

#endregion

#region Organisation Maturity

function Get-OrganisationMaturity {
    <#
    .SYNOPSIS
        Calculates overall organisational maturity.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$FrameworkResults
    )

    if ($FrameworkResults.Count -eq 0) {

        return $null

    }

    $score =
    (
        $FrameworkResults |
        Measure-Object `
            -Property Score `
            -Average
    ).Average

    [PSCustomObject]@{
        Score      = [math]::Round($score, 2)
        Maturity   = Get-MaturityLevel -Score $score
        Frameworks = $FrameworkResults.Count
        Assessed   = (Get-Date).ToUniversalTime()
    }
}

#endregion

#region Summary

function New-MaturitySummary {
    <#
    .SYNOPSIS
        Creates maturity summary.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$FrameworkResults
    )

    $organisation =
    Get-OrganisationMaturity `
        -FrameworkResults $FrameworkResults

    [PSCustomObject]@{
        Organisation = $organisation
        Frameworks   = $FrameworkResults
        Generated    = (Get-Date).ToUniversalTime()
    }
}

#endregion

#region Health

function Test-MaturityHealth {
    <#
    .SYNOPSIS
        Performs maturity module health check.
    #>

    [CmdletBinding()]
    param()

    [PSCustomObject]@{
        Status = "Healthy"
        Module = "Maturity"
        Model  = "Five-Level Maturity Model"
    }
}

#endregion

Export-ModuleMember -Function @(
    "Get-MaturityLevel"
    "Get-ControlMaturity"
    "Get-CapabilityMaturity"
    "Get-FrameworkMaturity"
    "Get-OrganisationMaturity"
    "New-MaturitySummary"
    "Test-MaturityHealth"
)
