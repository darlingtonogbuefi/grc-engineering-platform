<#
    modules\orchestration\Scheduler.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Pipeline scheduling module.

.DESCRIPTION
    Provides scheduling capabilities for GRC platform
    automation workflows.

    Responsibilities:

    - Create scheduled tasks
    - Manage execution schedules
    - Track scheduled pipelines
    - Trigger automated runs
    - Support recurring assessments

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Scheduler State

$script:Schedules = @{}

#endregion

#region Schedule Creation

function New-GRCSchedule {
    <#
    .SYNOPSIS
        Creates a pipeline schedule.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Name,

        [Parameter(Mandatory)]
        [string]$PipelineName,

        [Parameter(Mandatory)]
        [ValidateSet(
            "Once",
            "Daily",
            "Weekly",
            "Monthly"
        )]
        [string]$Frequency,

        [datetime]$StartTime = (
            Get-Date
        ),

        [hashtable]$Metadata = @{}
    )

    $scheduleId = New-GuidId

    $schedule = [PSCustomObject]@{
        ScheduleId   = $scheduleId
        Name         = $Name
        PipelineName = $PipelineName
        Frequency    = $Frequency
        StartTime    = $StartTime
        Enabled      = $true
        LastRun      = $null
        NextRun      = $StartTime
        Metadata     = $Metadata
        CreatedAt    = (Get-Date).ToUniversalTime()
    }

    $script:Schedules[$scheduleId] = $schedule

    return $schedule
}

#endregion

#region Schedule Management

function Get-GRCSchedule {
    <#
    .SYNOPSIS
        Returns a schedule.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ScheduleId
    )

    if (-not $script:Schedules.ContainsKey($ScheduleId)) {
        throw "Schedule '$ScheduleId' not found."
    }

    $script:Schedules[$ScheduleId]
}

function Get-GRCSchedules {
    <#
    .SYNOPSIS
        Returns all schedules.
    #>

    [CmdletBinding()]
    param()

    $script:Schedules.Values
}

function Remove-GRCSchedule {
    <#
    .SYNOPSIS
        Removes a schedule.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ScheduleId
    )

    if ($script:Schedules.ContainsKey($ScheduleId)) {

        $script:Schedules.Remove($ScheduleId)

    }
}

function Enable-GRCSchedule {
    <#
    .SYNOPSIS
        Enables a schedule.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ScheduleId
    )

    $schedule =
    Get-GRCSchedule `
        -ScheduleId $ScheduleId

    $schedule.Enabled = $true
}

function Disable-GRCSchedule {
    <#
    .SYNOPSIS
        Disables a schedule.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ScheduleId
    )

    $schedule =
    Get-GRCSchedule `
        -ScheduleId $ScheduleId

    $schedule.Enabled = $false
}

#endregion

#region Execution

function Get-DueSchedules {
    <#
    .SYNOPSIS
        Returns schedules ready for execution.
    #>

    [CmdletBinding()]
    param()

    $now = Get-Date

    $script:Schedules.Values |
    Where-Object {
        $_.Enabled -and
        $_.NextRun -le $now
    }
}

function Update-ScheduleExecution {
    <#
    .SYNOPSIS
        Updates schedule after execution.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ScheduleId
    )

    $schedule =
    Get-GRCSchedule `
        -ScheduleId $ScheduleId

    $schedule.LastRun =
    (Get-Date).ToUniversalTime()

    switch ($schedule.Frequency) {

        "Once" {
            $schedule.Enabled = $false
        }

        "Daily" {
            $schedule.NextRun =
            $schedule.NextRun.AddDays(1)
        }

        "Weekly" {
            $schedule.NextRun =
            $schedule.NextRun.AddDays(7)
        }

        "Monthly" {
            $schedule.NextRun =
            $schedule.NextRun.AddMonths(1)
        }
    }
}

#endregion

#region Helpers

function New-GuidId {
    <#
    .SYNOPSIS
        Creates unique identifier.
    #>

    [guid]::NewGuid().ToString()
}

#endregion

#region Health

function Test-SchedulerHealth {
    <#
    .SYNOPSIS
        Performs scheduler health check.
    #>

    [CmdletBinding()]
    param()

    [PSCustomObject]@{
        Status           = "Healthy"
        TotalSchedules   = $script:Schedules.Count
        EnabledSchedules = @(
            $script:Schedules.Values |
            Where-Object {
                $_.Enabled
            }
        ).Count
        DueSchedules     = @(
            Get-DueSchedules
        ).Count
    }
}

#endregion

Export-ModuleMember -Function @(
    "New-GRCSchedule"
    "Get-GRCSchedule"
    "Get-GRCSchedules"
    "Remove-GRCSchedule"
    "Enable-GRCSchedule"
    "Disable-GRCSchedule"
    "Get-DueSchedules"
    "Update-ScheduleExecution"
    "Test-SchedulerHealth"
)
