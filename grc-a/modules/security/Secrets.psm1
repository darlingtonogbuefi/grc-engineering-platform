<#
    modules\security\Secrets.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Secret management module.

.DESCRIPTION
    Provides a unified interface for retrieving and storing
    secrets used by the GRC Engineering Platform.

    Responsibilities:

    - Retrieve secrets
    - Store secrets
    - Remove secrets
    - Test secret availability
    - List configured secrets

.NOTES
    GRC Engineering Platform
    Version 1.0.0

    Recommended Modules:

        Microsoft.PowerShell.SecretManagement
        Microsoft.PowerShell.SecretStore
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Dependencies

$script:SecretManagementAvailable =
$null -ne (
    Get-Module `
        -ListAvailable `
        Microsoft.PowerShell.SecretManagement
)

if ($script:SecretManagementAvailable) {

    Import-Module `
        Microsoft.PowerShell.SecretManagement `
        -ErrorAction Stop

}

#endregion

#region Secret Operations

function Get-GRCSecret {
    <#
    .SYNOPSIS
        Retrieves a secret.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Name
    )

    if (-not $script:SecretManagementAvailable) {

        throw "Microsoft.PowerShell.SecretManagement is not installed."

    }

    Get-Secret `
        -Name $Name
}

function Set-GRCSecret {
    <#
    .SYNOPSIS
        Stores a secret.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Name,

        [Parameter(Mandatory)]
        [object]$Secret
    )

    if (-not $script:SecretManagementAvailable) {

        throw "Microsoft.PowerShell.SecretManagement is not installed."

    }

    Set-Secret `
        -Name $Name `
        -Secret $Secret
}

function Remove-GRCSecret {
    <#
    .SYNOPSIS
        Removes a secret.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Name
    )

    if (-not $script:SecretManagementAvailable) {

        throw "Microsoft.PowerShell.SecretManagement is not installed."

    }

    Remove-Secret `
        -Name $Name
}

#endregion

#region Discovery

function Test-GRCSecret {
    <#
    .SYNOPSIS
        Tests whether a secret exists.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Name
    )

    if (-not $script:SecretManagementAvailable) {

        return $false

    }

    try {

        $null = Get-Secret `
            -Name $Name `
            -ErrorAction Stop

        return $true

    }
    catch {

        return $false

    }
}

function Get-GRCSecretList {
    <#
    .SYNOPSIS
        Returns registered secrets.
    #>

    [CmdletBinding()]
    param()

    if (-not $script:SecretManagementAvailable) {

        return @()

    }

    Get-SecretInfo
}

#endregion

#region Health

function Test-SecretsHealth {
    <#
    .SYNOPSIS
        Performs secrets module health check.
    #>

    [CmdletBinding()]
    param()

    [PSCustomObject]@{
        Status   = if ($script:SecretManagementAvailable) {
            "Healthy"
        }
        else {
            "Unavailable"
        }
        Module   = "Secrets"
        Provider = if ($script:SecretManagementAvailable) {
            "SecretManagement"
        }
        else {
            "None"
        }
    }
}

#endregion

Export-ModuleMember -Function @(
    "Get-GRCSecret"
    "Set-GRCSecret"
    "Remove-GRCSecret"
    "Test-GRCSecret"
    "Get-GRCSecretList"
    "Test-SecretsHealth"
)
