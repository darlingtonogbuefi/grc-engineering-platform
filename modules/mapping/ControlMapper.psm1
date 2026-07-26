<#
    modules\mapping\ControlMapper.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Control mapping module.

.DESCRIPTION
    Provides functions to map evidence and capabilities
    to specific governance and compliance controls.

    Responsibilities:

    - Map evidence to controls
    - Map capabilities to controls
    - Resolve control ownership
    - Track control coverage
    - Support compliance scoring

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Control Definitions

$script:ControlMap = @{
    IAM_001 = @{
        Name        = "Identity Lifecycle Management"
        Capability  = "Identity"
        Description = "User identities are created, managed, and removed securely."
    }

    IAM_002 = @{
        Name        = "Multi Factor Authentication"
        Capability  = "Identity"
        Description = "Strong authentication controls are implemented."
    }

    END_001 = @{
        Name        = "Endpoint Protection"
        Capability  = "Endpoint"
        Description = "Endpoints are protected against security threats."
    }

    CLD_001 = @{
        Name        = "Cloud Governance"
        Capability  = "Cloud"
        Description = "Cloud resources follow governance requirements."
    }

    NET_001 = @{
        Name        = "Network Security Controls"
        Capability  = "Networking"
        Description = "Networks are securely configured and monitored."
    }

    MON_001 = @{
        Name        = "Security Monitoring"
        Capability  = "Monitoring"
        Description = "Security events are monitored and reviewed."
    }

    LOG_001 = @{
        Name        = "Audit Logging"
        Capability  = "Logging"
        Description = "Security and operational events are logged."
    }

    BAK_001 = @{
        Name        = "Backup Protection"
        Capability  = "Backup"
        Description = "Critical systems are backed up and recoverable."
    }

    VUL_001 = @{
        Name        = "Vulnerability Management"
        Capability  = "Vulnerability"
        Description = "Vulnerabilities are identified and remediated."
    }

    DEV_001 = @{
        Name        = "Secure Development Lifecycle"
        Capability  = "DevOps"
        Description = "Software development follows security practices."
    }
}

#endregion

#region Control Retrieval

function Get-ControlList {
    <#
    .SYNOPSIS
        Returns available controls.
    #>

    [CmdletBinding()]
    param()

    foreach ($key in $script:ControlMap.Keys) {

        [PSCustomObject]@{
            Id          = $key
            Name        = $script:ControlMap[$key].Name
            Capability  = $script:ControlMap[$key].Capability
            Description = $script:ControlMap[$key].Description
        }
    }
}

function Get-Control {
    <#
    .SYNOPSIS
        Returns a control definition.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ControlId
    )

    if (-not $script:ControlMap.ContainsKey($ControlId)) {
        throw "Control '$ControlId' does not exist."
    }

    [PSCustomObject]@{
        Id          = $ControlId
        Name        = $script:ControlMap[$ControlId].Name
        Capability  = $script:ControlMap[$ControlId].Capability
        Description = $script:ControlMap[$ControlId].Description
    }
}

#endregion

#region Capability Mapping

function Get-ControlsByCapability {
    <#
    .SYNOPSIS
        Returns controls for a capability.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$CapabilityId
    )

    foreach ($control in $script:ControlMap.Keys) {

        if (
            $script:ControlMap[$control].Capability -eq $CapabilityId
        ) {

            Get-Control `
                -ControlId $control
        }
    }
}

#endregion

#region Evidence Mapping

function Map-EvidenceToControl {
    <#
    .SYNOPSIS
        Maps evidence to a control.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence,

        [Parameter(Mandatory)]
        [string]$ControlId
    )

    $control = Get-Control `
        -ControlId $ControlId

    [PSCustomObject]@{
        EvidenceId  = $Evidence.EvidenceId
        ControlId   = $control.Id
        ControlName = $control.Name
        Capability  = $control.Capability
        Source      = $Evidence.Source
        Status      = "Mapped"
        MappedAt    = (Get-Date).ToUniversalTime()
    }
}

function Map-EvidenceCollectionToControls {
    <#
    .SYNOPSIS
        Maps evidence collection to controls.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Evidence,

        [Parameter(Mandatory)]
        [hashtable]$ControlAssignments
    )

    foreach ($item in $Evidence) {

        if ($ControlAssignments.ContainsKey($item.Source)) {

            Map-EvidenceToControl `
                -Evidence $item `
                -ControlId $ControlAssignments[$item.Source]
        }
    }
}

#endregion

#region Discovery

function Find-ControlByKeyword {
    <#
    .SYNOPSIS
        Finds controls using keywords.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Keyword
    )

    foreach ($control in $script:ControlMap.Keys) {

        $definition =
        $script:ControlMap[$control]

        if (
            $definition.Name -match $Keyword -or
            $definition.Description -match $Keyword
        ) {

            Get-Control `
                -ControlId $control
        }
    }
}

#endregion

#region Reporting

function Get-ControlCoverageSummary {
    <#
    .SYNOPSIS
        Returns control coverage statistics.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Mappings
    )

    $covered =
    @(
        $Mappings |
        Where-Object {
            $_.Status -eq "Mapped"
        }
    ).Count

    [PSCustomObject]@{
        TotalControls   = $Mappings.Count
        CoveredControls = $covered
        CoveragePercent = if ($Mappings.Count -gt 0) {
            [math]::Round(
                ($covered / $Mappings.Count) * 100,
                2
            )
        }
        else {
            0
        }
    }
}

#endregion

Export-ModuleMember -Function @(
    "Get-ControlList"
    "Get-Control"
    "Get-ControlsByCapability"
    "Map-EvidenceToControl"
    "Map-EvidenceCollectionToControls"
    "Find-ControlByKeyword"
    "Get-ControlCoverageSummary"
)
