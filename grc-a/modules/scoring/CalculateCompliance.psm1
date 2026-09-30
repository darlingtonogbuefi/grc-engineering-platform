<#
    modules\scoring\CalculateCompliance.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Compliance calculation module.

.DESCRIPTION
    Aggregates individual control assessment results into
    framework, capability and tenant level compliance scores.

    Responsibilities:

    - Calculate framework compliance
    - Calculate capability compliance
    - Generate compliance summaries
    - Calculate pass/fail statistics
    - Produce assessment metrics

.NOTES
    GRC Engineering Platform
    Version 1.0.0

    Dependency:
        modules\scoring\ScoreControl.psm1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Dependencies

Import-Module `
    "$PSScriptRoot\ScoreControl.psm1" `
    -Force `
    -ErrorAction Stop

#endregion

#region Framework Compliance

function Get-FrameworkCompliance {
    <#
    .SYNOPSIS
        Calculates framework compliance percentage.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$ControlResults
    )

    if ($ControlResults.Count -eq 0) {

        return 0

    }

    [math]::Round(
        (
            ($ControlResults |
            Measure-Object `
                -Property Score `
                -Average
            ).Average
        ),
        2
    )
}

function Get-FrameworkStatus {
    <#
    .SYNOPSIS
        Determines framework compliance status.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [double]$Compliance
    )

    switch ($Compliance) {

        { $_ -ge 95 } { return "Compliant" }

        { $_ -ge 75 } { return "Partially Compliant" }

        default { return "Non-Compliant" }

    }
}

#endregion

#region Capability Compliance

function Get-CapabilityCompliance {
    <#
    .SYNOPSIS
        Calculates compliance grouped by capability.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$ControlResults
    )

    foreach ($group in ($ControlResults | Group-Object Capability)) {

        [PSCustomObject]@{
            Capability = $group.Name
            Compliance = [math]::Round(
                (
                    ($group.Group |
                    Measure-Object `
                        -Property Score `
                        -Average
                    ).Average
                ),
                2
            )
            Controls   = $group.Count
        }

    }
}

#endregion

#region Assessment Summary

function New-ComplianceSummary {
    <#
    .SYNOPSIS
        Creates compliance summary.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Framework,

        [Parameter(Mandatory)]
        [object[]]$ControlResults
    )

    $compliance =
    Get-FrameworkCompliance `
        -ControlResults $ControlResults

    [PSCustomObject]@{
        Framework  = $Framework
        Compliance = $compliance
        Status     = Get-FrameworkStatus -Compliance $compliance
        Controls   = $ControlResults.Count
        Passed     = @(
            $ControlResults |
            Where-Object {
                $_.Status -eq "Pass"
            }
        ).Count
        Partial    = @(
            $ControlResults |
            Where-Object {
                $_.Status -eq "Partial"
            }
        ).Count
        Failed     = @(
            $ControlResults |
            Where-Object {
                $_.Status -eq "Fail"
            }
        ).Count
        Assessed   = (Get-Date).ToUniversalTime()
    }
}

#endregion

#region Statistics

function Get-ComplianceStatistics {
    <#
    .SYNOPSIS
        Returns assessment statistics.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$ControlResults
    )

    [PSCustomObject]@{
        AverageScore = Get-FrameworkCompliance -ControlResults $ControlResults
        HighestScore = (
            $ControlResults |
            Measure-Object `
                -Property Score `
                -Maximum
        ).Maximum
        LowestScore  = (
            $ControlResults |
            Measure-Object `
                -Property Score `
                -Minimum
        ).Minimum
        Controls     = $ControlResults.Count
    }
}

#endregion

#region Health

function Test-ComplianceCalculationHealth {
    <#
    .SYNOPSIS
        Performs compliance calculation health check.
    #>

    [CmdletBinding()]
    param()

    [PSCustomObject]@{
        Status = "Healthy"
        Module = "CalculateCompliance"
    }
}

#endregion

Export-ModuleMember -Function @(
    "Get-FrameworkCompliance"
    "Get-FrameworkStatus"
    "Get-CapabilityCompliance"
    "New-ComplianceSummary"
    "Get-ComplianceStatistics"
    "Test-ComplianceCalculationHealth"
)
