<#
    modules\mapping\CapabilityMapper.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Capability mapping module.

.DESCRIPTION
    Provides functions to map evidence and technical assets
    to GRC capability domains.

    Responsibilities:

    - Map evidence to capabilities
    - Manage capability classifications
    - Resolve capability relationships
    - Support framework alignment
    - Provide capability summaries

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Capability Definitions

$script:CapabilityMap = @{
    Identity      = @{
        Name        = "Identity and Access Management"
        Description = "Controls related to identity lifecycle, authentication, and authorization."
    }

    Endpoint      = @{
        Name        = "Endpoint Security"
        Description = "Controls related to device security and management."
    }

    Cloud         = @{
        Name        = "Cloud Security"
        Description = "Controls related to cloud platforms and services."
    }

    Networking    = @{
        Name        = "Network Security"
        Description = "Controls related to network protection and connectivity."
    }

    Monitoring    = @{
        Name        = "Security Monitoring"
        Description = "Controls related to monitoring and detection."
    }

    Logging       = @{
        Name        = "Logging and Audit"
        Description = "Controls related to event collection and audit trails."
    }

    Backup        = @{
        Name        = "Backup and Recovery"
        Description = "Controls related to resilience and recovery."
    }

    Vulnerability = @{
        Name        = "Vulnerability Management"
        Description = "Controls related to vulnerability identification and remediation."
    }

    DevOps        = @{
        Name        = "Secure Development"
        Description = "Controls related to development lifecycle security."
    }

    BusinessApps  = @{
        Name        = "Business Applications"
        Description = "Controls related to enterprise applications."
    }
}

#endregion

#region Capability Retrieval

function Get-CapabilityList {
    <#
    .SYNOPSIS
        Returns available capabilities.
    #>

    [CmdletBinding()]
    param()

    foreach ($key in $script:CapabilityMap.Keys) {

        [PSCustomObject]@{
            Id          = $key
            Name        = $script:CapabilityMap[$key].Name
            Description = $script:CapabilityMap[$key].Description
        }
    }
}

function Get-Capability {
    <#
    .SYNOPSIS
        Returns a capability definition.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$CapabilityId
    )

    if (-not $script:CapabilityMap.ContainsKey($CapabilityId)) {
        throw "Capability '$CapabilityId' does not exist."
    }

    [PSCustomObject]@{
        Id          = $CapabilityId
        Name        = $script:CapabilityMap[$CapabilityId].Name
        Description = $script:CapabilityMap[$CapabilityId].Description
    }
}

#endregion

#region Mapping

function Map-EvidenceToCapability {
    <#
    .SYNOPSIS
        Maps evidence to a capability.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$Evidence,

        [Parameter(Mandatory)]
        [string]$CapabilityId
    )

    $capability = Get-Capability `
        -CapabilityId $CapabilityId

    [PSCustomObject]@{
        EvidenceId     = $Evidence.EvidenceId
        Capability     = $capability.Id
        CapabilityName = $capability.Name
        Source         = $Evidence.Source
        MappedAt       = (Get-Date).ToUniversalTime()
    }
}

function Map-EvidenceCollectionToCapability {
    <#
    .SYNOPSIS
        Maps evidence collection to capabilities.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Evidence,

        [Parameter(Mandatory)]
        [hashtable]$CapabilityAssignments
    )

    foreach ($item in $Evidence) {

        if ($CapabilityAssignments.ContainsKey($item.Source)) {

            Map-EvidenceToCapability `
                -Evidence $item `
                -CapabilityId $CapabilityAssignments[$item.Source]
        }
    }
}

#endregion

#region Classification

function Find-CapabilityMatch {
    <#
    .SYNOPSIS
        Finds matching capabilities from keywords.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Text
    )

    $matches = @()

    foreach ($capability in $script:CapabilityMap.Keys) {

        if (
            $Text -match $capability
        ) {
            $matches += Get-Capability `
                -CapabilityId $capability
        }
    }

    return $matches
}

#endregion

#region Reporting

function Get-CapabilityMappingSummary {
    <#
    .SYNOPSIS
        Returns capability mapping summary.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object[]]$Mappings
    )

    [PSCustomObject]@{
        TotalMappings = $Mappings.Count
        Capabilities  = @(
            $Mappings.Capability |
            Select-Object -Unique
        ).Count
        Sources       = @(
            $Mappings.Source |
            Select-Object -Unique
        ).Count
    }
}

#endregion

Export-ModuleMember -Function @(
    "Get-CapabilityList"
    "Get-Capability"
    "Map-EvidenceToCapability"
    "Map-EvidenceCollectionToCapability"
    "Find-CapabilityMatch"
    "Get-CapabilityMappingSummary"
)
