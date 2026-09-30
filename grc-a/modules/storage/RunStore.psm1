<#
    modules\storage\RunStore.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Assessment run storage module.

.DESCRIPTION
    Provides storage operations for GRC assessment execution
    history and run lifecycle tracking.

    Responsibilities:

    - Create assessment runs
    - Store run metadata
    - Track execution status
    - Retrieve historical runs
    - Support audit traceability

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Configuration

$script:RunRoot =
Join-Path `
    -Path (Get-Location) `
    -ChildPath "evidence\runs"

#endregion

#region Initialisation

function Initialize-RunStore {
    <#
    .SYNOPSIS
        Creates run storage directory.
    #>

    [CmdletBinding()]
    param(
        [string]$Path = $script:RunRoot
    )

    if (-not (Test-Path $Path)) {

        New-Item `
            -Path $Path `
            -ItemType Directory `
            -Force |
        Out-Null

    }

    Resolve-Path $Path
}

#endregion

#region Run Management

function New-AssessmentRun {
    <#
    .SYNOPSIS
        Creates a new assessment run.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Framework,

        [string]$TenantId,

        [string]$InitiatedBy = "System"
    )

    Initialize-RunStore |
    Out-Null

    $runId =
    [guid]::NewGuid().ToString()

    $run =
    [PSCustomObject]@{
        RunId       = $runId
        Framework   = $Framework
        TenantId    = $TenantId
        Status      = "Started"
        InitiatedBy = $InitiatedBy
        Started     = (Get-Date).ToUniversalTime()
        Completed   = $null
    }

    Save-AssessmentRun `
        -Run $run

    $run
}

function Save-AssessmentRun {
    <#
    .SYNOPSIS
        Saves assessment run metadata.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Run
    )

    Initialize-RunStore |
    Out-Null

    $file =
    Join-Path `
        -Path $script:RunRoot `
        -ChildPath "$($Run.RunId).json"

    $Run |
    ConvertTo-Json `
        -Depth 20 |
    Out-File `
        -FilePath $file `
        -Encoding UTF8

    Get-Item $file
}

function Get-AssessmentRun {
    <#
    .SYNOPSIS
        Retrieves an assessment run.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$RunId
    )

    $file =
    Join-Path `
        -Path $script:RunRoot `
        -ChildPath "$RunId.json"

    if (-not (Test-Path $file)) {

        throw "Assessment run not found: $RunId"

    }

    Get-Content `
        -Path $file `
        -Raw |
    ConvertFrom-Json
}

function Update-AssessmentRun {
    <#
    .SYNOPSIS
        Updates assessment run status.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$RunId,

        [ValidateSet(
            "Started",
            "Running",
            "Completed",
            "Failed"
        )]
        [string]$Status
    )

    $run =
    Get-AssessmentRun `
        -RunId $RunId

    $run.Status = $Status

    if ($Status -in @(
            "Completed",
            "Failed"
        )) {

        $run.Completed =
        (Get-Date).ToUniversalTime()

    }

    Save-AssessmentRun `
        -Run $run
}

#endregion

#region Discovery

function Get-AssessmentRuns {
    <#
    .SYNOPSIS
        Lists assessment runs.
    #>

    [CmdletBinding()]
    param()

    Initialize-RunStore |
    Out-Null

    foreach ($file in (
            Get-ChildItem `
                -Path $script:RunRoot `
                -Filter "*.json"
        )) {

        Get-Content `
            -Path $file.FullName `
            -Raw |
        ConvertFrom-Json

    }
}

#endregion

#region Health

function Test-RunStoreHealth {
    <#
    .SYNOPSIS
        Performs run store health check.
    #>

    [CmdletBinding()]
    param()

    [PSCustomObject]@{
        Status    = "Healthy"
        Module    = "RunStore"
        Path      = $script:RunRoot
        Available = Test-Path $script:RunRoot
    }
}

#endregion

Export-ModuleMember -Function @(
    "Initialize-RunStore"
    "New-AssessmentRun"
    "Save-AssessmentRun"
    "Get-AssessmentRun"
    "Update-AssessmentRun"
    "Get-AssessmentRuns"
    "Test-RunStoreHealth"
)
