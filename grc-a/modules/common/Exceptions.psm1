<#
    modules\common\Exceptions.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Provides common exception handling functions.

.DESCRIPTION
    Defines reusable exception helper functions used throughout
    the GRC Engineering Platform.

    Supports:
    - Configuration exceptions
    - Validation exceptions
    - File and directory checks
    - Module dependency validation
    - Generic platform exceptions

.NOTES
    GRC Engineering Platform
    Version: 1.0.0
#>


Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"



#region Exception Functions


function Throw-GrcException {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Message

    )


    throw [System.Exception]::new(
        $Message
    )

}



function Throw-ConfigurationException {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Message

    )


    throw [System.Configuration.ConfigurationErrorsException]::new(
        $Message
    )

}



function Throw-ValidationException {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Message

    )


    throw [System.ComponentModel.DataAnnotations.ValidationException]::new(
        $Message
    )

}



#endregion



#region Validation Helpers


function Assert-FileExists {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Path

    )


    if (-not (Test-Path `
        -Path $Path `
        -PathType Leaf)) {

        Throw-GrcException `
            "Required file not found: $Path"

    }

}



function Assert-DirectoryExists {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Path

    )


    if (-not (Test-Path `
        -Path $Path `
        -PathType Container)) {

        Throw-GrcException `
            "Required directory not found: $Path"

    }

}



function Assert-ModuleInstalled {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $ModuleName

    )


    if (-not (Get-Module `
        -ListAvailable `
        -Name $ModuleName)) {

        Throw-GrcException @"
Required PowerShell module '$ModuleName' is not installed.

Install using:

Install-Module $ModuleName -Scope CurrentUser
"@

    }

}



function Assert-NotNull {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        $Value,


        [Parameter(Mandatory)]
        [string]
        $Name

    )


    if ($null -eq $Value) {

        Throw-ValidationException `
            "'$Name' cannot be null."

    }

}



function Assert-NotEmpty {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Value,


        [Parameter(Mandatory)]
        [string]
        $Name

    )


    if ([string]::IsNullOrWhiteSpace($Value)) {

        Throw-ValidationException `
            "'$Name' cannot be empty."

    }

}



#endregion



#region Safe Execution


function Invoke-Safely {

    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [scriptblock]
        $ScriptBlock

    )


    try {

        & $ScriptBlock

    }

    catch {

        throw $_

    }

}



#endregion



Export-ModuleMember `
    -Function `
        Throw-GrcException,
        Throw-ConfigurationException,
        Throw-ValidationException,
        Assert-FileExists,
        Assert-DirectoryExists,
        Assert-ModuleInstalled,
        Assert-NotNull,
        Assert-NotEmpty,
        Invoke-Safely
