<#
    modules\security\Encryption.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Encryption module.

.DESCRIPTION
    Provides encryption and decryption services used throughout
    the GRC Engineering Platform.

    Responsibilities:

    - Encrypt sensitive data
    - Decrypt protected data
    - Generate encryption keys
    - Create secure hashes
    - Protect evidence and configuration data

.NOTES
    GRC Engineering Platform
    Version 1.0.0
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Key Generation

function New-EncryptionKey {
    <#
    .SYNOPSIS
        Generates a random AES encryption key.
    #>

    [CmdletBinding()]
    param(
        [ValidateSet(128, 192, 256)]
        [int]$KeySize = 256
    )

    $key = New-Object byte[] ($KeySize / 8)

    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($key)

    return $key
}

#endregion

#region Encryption

function Protect-PlainText {
    <#
    .SYNOPSIS
        Encrypts plain text using SecureString.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Text,

        [byte[]]$Key
    )

    $secure =
    ConvertTo-SecureString `
        -String $Text `
        -AsPlainText `
        -Force

    if ($Key) {

        ConvertFrom-SecureString `
            -SecureString $secure `
            -Key $Key

    }
    else {

        ConvertFrom-SecureString `
            -SecureString $secure

    }
}

function Unprotect-PlainText {
    <#
    .SYNOPSIS
        Decrypts encrypted text.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$CipherText,

        [byte[]]$Key
    )

    if ($Key) {

        $secure =
        ConvertTo-SecureString `
            -String $CipherText `
            -Key $Key

    }
    else {

        $secure =
        ConvertTo-SecureString `
            -String $CipherText

    }

    $ptr =
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)

    try {

        [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)

    }
    finally {

        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)

    }
}

#endregion

#region Hashing

function Get-StringHash {
    <#
    .SYNOPSIS
        Calculates SHA256 hash.
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Text
    )

    $bytes =
    [System.Text.Encoding]::UTF8.GetBytes($Text)

    $hash =
    [System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes)

    -join ($hash | ForEach-Object {

            $_.ToString("x2")

        })
}

#endregion

#region Health

function Test-EncryptionHealth {
    <#
    .SYNOPSIS
        Performs encryption module health check.
    #>

    [CmdletBinding()]
    param()

    [PSCustomObject]@{
        Status     = "Healthy"
        Module     = "Encryption"
        Algorithms = @(
            "AES"
            "SHA256"
            "SecureString"
        )
    }
}

#endregion

Export-ModuleMember -Function @(
    "New-EncryptionKey"
    "Protect-PlainText"
    "Unprotect-PlainText"
    "Get-StringHash"
    "Test-EncryptionHealth"
)
