<#
    modules\mapping\FrameworkMapper.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Framework mapping module.

.DESCRIPTION
    Provides functions to map capabilities and evidence
    against governance and compliance frameworks.

    Responsibilities:

    - Map capabilities to frameworks
    - Resolve framework coverage
    - Track framework alignment
    - Support compliance reporting
    - Provide framework summaries

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Framework Definitions

$script:FrameworkMap = @{
    CAF             = @{
        Name         = "Microsoft Cloud Adoption Framework"
        Description  = "Azure cloud governance and security framework."
        Capabilities = @(
            "Identity"
            "Cloud"
            "Networking"
            "Monitoring"
            "Backup"
        )
    }

    ISO27001        = @{
        Name         = "ISO/IEC 27001"
        Description  = "Information security management standard."
        Capabilities = @(
            "Identity"
            "Endpoint"
            "Logging"
            "Vulnerability"
            "DevOps"
        )
    }

    SOC2            = @{
        Name         = "SOC 2"
        Description  = "Trust services criteria framework."
        Capabilities = @(
            "Security"
            "Availability"
            "Monitoring"
            "Backup"
        )
    }

    GovAssure       = @{
        Name         = "GovAssure"
        Description  = "Government security assurance framework."
        Capabilities = @(
            "Identity"
            "Cloud"
            "Logging"
            "Vulnerability"
        )
    }

    CyberEssentials = @{
        Name         = "Cyber Essentials"
        Description  = "Baseline cyber security controls."
        Capabilities = @(
            "Identity"
            "Endpoint"
            "Networking"
        )
    }
}

#endregion

#region Framework Retrieval

function Get-FrameworkList {
    <#
    .SYNOPSIS
        Returns available frameworks.
    #>

    [CmdletBinding()]
    param()

    foreach ($key in $script:FrameworkMap.Keys) {

        [PSCustomObject]@{
            Id          = $key
            Name        = $script:FrameworkMap[$key].Name
            Description = $script:FrameworkMap[$key].Description
        }
    }
}

function Get-Framework {
    <#
    .SYNOPSIS
        Returns framework definition.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$FrameworkId
    )

    if (-not $script:FrameworkMap.ContainsKey($FrameworkId)) {
        throw "Framework '$FrameworkId' does not exist."
    }

    [PSCustomObject]@{
        Id           = $FrameworkId
        Name         = $script:FrameworkMap[$FrameworkId].Name
        Description  = $script:FrameworkMap[$FrameworkId].Description
        Capabilities = $script:FrameworkMap[$FrameworkId].Capabilities
    }
}

#endregion

#region Mapping

function Map-CapabilityToFramework {
    <#
    .SYNOPSIS
        Maps a capability to a framework.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$CapabilityId,

        [Parameter(Mandatory)]
        [string]$FrameworkId
    )

    $framework = Get-Framework `
        -FrameworkId $FrameworkId

    if ($framework.Capabilities -notcontains $CapabilityId) {

        return [PSCustomObject]@{
            Framework  = $FrameworkId
            Capability = $CapabilityId
            Covered    = $false
        }
    }

    [PSCustomObject]@{
        Framework     = $FrameworkId
        FrameworkName = $framework.Name
        Capability    = $CapabilityId
        Covered       = $true
        MappedAt      = (Get-Date).ToUniversalTime()
    }
}

function Map-CapabilityCollectionToFramework {
    <#
    .SYNOPSIS
        Maps multiple capabilities to a framework.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string[]]$Capabilities,

        [Parameter(Mandatory)]
        [string]$FrameworkId
    )

    foreach ($capability in $Capabilities) {

        Map-CapabilityToFramework `
            -CapabilityId $capability `
            -FrameworkId $FrameworkId
    }
}

#endregion

#region Discovery

function Find-FrameworkForCapability {
    <#
    .SYNOPSIS
        Finds frameworks supporting a capability.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$CapabilityId
    )

    foreach ($framework in $script:FrameworkMap.Keys) {

        if (
            $script:FrameworkMap[$framework].Capabilities `
                -contains $CapabilityId
        ) {

            Get-Framework `
                -FrameworkId $framework
        }
    }
}

#endregion

#region Reporting

function Get-FrameworkCoverageSummary {
    <#
    .SYNOPSIS
        Returns framework coverage statistics.
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
            $_.Covered -eq $true
        }
    ).Count

    [PSCustomObject]@{
        TotalMappings   = $Mappings.Count
        Covered         = $covered
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
    "Get-FrameworkList"
    "Get-Framework"
    "Map-CapabilityToFramework"
    "Map-CapabilityCollectionToFramework"
    "Find-FrameworkForCapability"
    "Get-FrameworkCoverageSummary"
)
