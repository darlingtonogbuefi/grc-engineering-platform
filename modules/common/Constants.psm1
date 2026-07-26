<#
    modules\common\Constants.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Defines shared platform constants.

.DESCRIPTION
    Provides common constants used throughout the
    GRC Engineering Platform.

    Includes:
    - Platform metadata
    - Directory names
    - Compliance frameworks
    - Logging levels
    - Report formats
    - Hash algorithms
    - Date and time formats

.NOTES
    GRC Engineering Platform
    Version: 1.0.0
#>


Set-StrictMode -Version Latest



#region Platform


$PlatformName =
"GRC Engineering Platform"



$PlatformVersion =
"1.0.0"



#endregion



#region Directory Names


$EvidenceDirectory =
"evidence"



$ReportsDirectory =
"reports"



$OutputDirectory =
"output"



$ModulesDirectory =
"modules"



$ScriptsDirectory =
"scripts"



$TestsDirectory =
"tests"



$DocumentationDirectory =
"docs"



$DashboardDirectory =
"dashboards"



#endregion



#region Evidence Folders


$EvidenceFolders =
@(

    "raw",

    "processed",

    "runs",

    "archive"

)



#endregion



#region Compliance Frameworks


$ComplianceFrameworks =
@(

    "CAF",

    "ISO27001",

    "SOC2",

    "GovAssure",

    "CyberEssentials"

)



#endregion



#region Logging


$LogLevels =
@(

    "INFO",

    "WARNING",

    "ERROR",

    "DEBUG"

)



$DefaultLogFile =
"output\logs\grc-platform.log"



#endregion



#region Report Formats


$SupportedReportFormats =
@(

    "json",

    "csv",

    "html",

    "xml",

    "markdown"

)



#endregion



#region Hash Algorithms


$DefaultHashAlgorithm =
"SHA256"



$SupportedHashAlgorithms =
@(

    "SHA1",

    "SHA256",

    "SHA384",

    "SHA512",

    "MD5"

)



#endregion



#region Date Formats


$Iso8601DateFormat =
"yyyy-MM-dd"



$Iso8601DateTimeFormat =
"yyyy-MM-ddTHH:mm:ssZ"



$TimestampFormat =
"yyyyMMdd-HHmmss"



#endregion



#region Exit Codes


$ExitSuccess = 0

$ExitFailure = 1

$ExitValidationFailed = 2

$ExitConfigurationError = 3



#endregion



Export-ModuleMember `
    -Variable `
        PlatformName,
        PlatformVersion,
        EvidenceDirectory,
        ReportsDirectory,
        OutputDirectory,
        ModulesDirectory,
        ScriptsDirectory,
        TestsDirectory,
        DocumentationDirectory,
        DashboardDirectory,
        EvidenceFolders,
        ComplianceFrameworks,
        LogLevels,
        DefaultLogFile,
        SupportedReportFormats,
        DefaultHashAlgorithm,
        SupportedHashAlgorithms,
        Iso8601DateFormat,
        Iso8601DateTimeFormat,
        TimestampFormat,
        ExitSuccess,
        ExitFailure,
        ExitValidationFailed,
        ExitConfigurationError
