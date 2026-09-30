<#
    modules\dashboards\Workbook.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Azure Monitor Workbook management module.

.DESCRIPTION
    Provides reusable Azure Workbook operations used by
    dashboard deployment and monitoring components.

    Responsibilities

    - Validate Azure connectivity
    - Retrieve workbooks
    - Create workbooks
    - Update workbooks
    - Remove workbooks
    - Export workbook definitions
    - Perform workbook health checks

.NOTES
    GRC Engineering Platform
    Version 1.0.0

    Requires:

        Az.Accounts
        Az.ResourceGraph
        Az.Monitor
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Dependencies

$RequiredModules = @(
    "Az.Accounts"
    "Az.Monitor"
)

foreach ($Module in $RequiredModules) {
    if (-not (Get-Module -ListAvailable $Module)) {
        throw @"
Required PowerShell module missing.

Install:

Install-Module $Module -Scope CurrentUser
"@
    }

    Import-Module $Module -ErrorAction Stop
}

#endregion

#region Connection

function Test-WorkbookConnection {
    <#
    .SYNOPSIS
        Tests Azure connectivity.
    #>

    [CmdletBinding()]
    param()

    try {
        $context = Get-AzContext

        return ($null -ne $context)
    }
    catch {
        return $false
    }
}

function Get-WorkbookContext {
    <#
    .SYNOPSIS
        Returns current Azure context.
    #>

    [CmdletBinding()]
    param()

    $context = Get-AzContext

    if ($null -eq $context) {
        return $null
    }

    [PSCustomObject]@{
        SubscriptionId = $context.Subscription.Id
        TenantId       = $context.Tenant.Id
        Account        = $context.Account.Id
    }
}

#endregion

#region Workbooks

function Get-AzureWorkbookList {
    <#
    .SYNOPSIS
        Returns Azure Monitor Workbooks.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ResourceGroupName
    )

    Get-AzResource `
        -ResourceGroupName $ResourceGroupName `
        -ResourceType "microsoft.insights/workbooks"
}

function Get-AzureWorkbook {
    <#
    .SYNOPSIS
        Retrieves a workbook definition.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ResourceId
    )

    Get-AzResource `
        -ResourceId $ResourceId `
        -ExpandProperties
}

#endregion

#region Deployment

function New-AzureWorkbook {
    <#
    .SYNOPSIS
        Creates an Azure Monitor Workbook.

    .PARAMETER Name
        Workbook name.

    .PARAMETER ResourceGroupName
        Target resource group.

    .PARAMETER Location
        Azure region.

    .PARAMETER SerializedData
        Workbook JSON definition.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Name,

        [Parameter(Mandatory)]
        [string]$ResourceGroupName,

        [Parameter(Mandatory)]
        [string]$Location,

        [Parameter(Mandatory)]
        [string]$SerializedData
    )

    New-AzResource `
        -ResourceType "microsoft.insights/workbooks" `
        -ResourceGroupName $ResourceGroupName `
        -Name $Name `
        -Location $Location `
        -PropertyObject @{
        serializedData = $SerializedData
        category       = "workbook"
    } `
        -Force
}

function Update-AzureWorkbook {
    <#
    .SYNOPSIS
        Updates an Azure Monitor Workbook.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ResourceId,

        [Parameter(Mandatory)]
        [string]$SerializedData
    )

    Update-AzResource `
        -ResourceId $ResourceId `
        -Properties @{
        serializedData = $SerializedData
    } `
        -Force
}

function Remove-AzureWorkbook {
    <#
    .SYNOPSIS
        Removes an Azure Monitor Workbook.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ResourceId
    )

    Remove-AzResource `
        -ResourceId $ResourceId `
        -Force
}

#endregion

#region Export

function Export-AzureWorkbookDefinition {
    <#
    .SYNOPSIS
        Exports workbook JSON definition.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ResourceId
    )

    $workbook = Get-AzureWorkbook `
        -ResourceId $ResourceId

    $workbook.Properties.serializedData
}

#endregion

#region Health

function Test-WorkbookHealth {
    <#
    .SYNOPSIS
        Performs workbook service health check.
    #>

    [CmdletBinding()]
    param()

    try {
        $context = Get-WorkbookContext

        if ($null -eq $context) {
            return [PSCustomObject]@{
                Connected = $false
                Status    = "Disconnected"
            }
        }

        [PSCustomObject]@{
            Connected    = $true
            Status       = "Healthy"
            Subscription = $context.SubscriptionId
            Tenant       = $context.TenantId
        }
    }
    catch {
        [PSCustomObject]@{
            Connected = $false
            Status    = "Failed"
            Error     = $_.Exception.Message
        }
    }
}

#endregion

Export-ModuleMember -Function @(
    "Test-WorkbookConnection"
    "Get-WorkbookContext"
    "Get-AzureWorkbookList"
    "Get-AzureWorkbook"
    "New-AzureWorkbook"
    "Update-AzureWorkbook"
    "Remove-AzureWorkbook"
    "Export-AzureWorkbookDefinition"
    "Test-WorkbookHealth"
)
