<#
    modules\graph\GraphPaging.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Microsoft Graph paging management module.

.DESCRIPTION
    Provides reusable paging functions for Microsoft Graph APIs.

    Responsibilities:

    - Follow @odata.nextLink responses
    - Retrieve complete datasets
    - Support large evidence collections
    - Provide page-level processing

    Used by collectors requiring large datasets:

    - Entra Users
    - Groups
    - Devices
    - Applications
    - Intune inventory
    - Defender data

    Authentication is handled by:

    modules\graph\GraphClient.psm1

.NOTES
    GRC Engineering Platform
    Version: 1.0.0

    Required Modules:
      Microsoft.Graph.Authentication
#>


Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"



#region Dependencies


if (-not (Get-Module -ListAvailable Microsoft.Graph.Authentication)) {

    throw @"
Microsoft.Graph.Authentication module is required.

Install:

Install-Module Microsoft.Graph.Authentication -Scope CurrentUser

"@

}


Import-Module Microsoft.Graph.Authentication `
    -ErrorAction Stop



#endregion



#region Paging Functions


function Get-GraphAllPages {

    <#
    .SYNOPSIS
        Retrieves all pages from a Microsoft Graph endpoint.
    #>


    [CmdletBinding()]

    param(

        [Parameter(
            Mandatory
        )]
        [string]
        $Uri,


        [ValidateSet(
            "v1.0",
            "beta"
        )]
        [string]
        $ApiVersion = "v1.0"

    )


    if ($Uri -notmatch "^https://") {

        $Uri =
        "https://graph.microsoft.com/$ApiVersion$Uri"

    }


    $results =
    [System.Collections.Generic.List[object]]::new()



    do {


        $response =
        Invoke-MgGraphRequest `
            -Method GET `
            -Uri $Uri



        if ($response.value) {


            foreach ($item in $response.value) {

                $results.Add(
                    $item
                )

            }

        }



        $Uri =
        $response.'@odata.nextLink'



    }
    while ($Uri)



    return $results

}



function Get-GraphPagedResponse {

    <#
    .SYNOPSIS
        Returns a single Graph response page.

    .DESCRIPTION
        Useful when collectors process evidence incrementally.
    #>


    [CmdletBinding()]

    param(

        [Parameter(
            Mandatory
        )]
        [string]
        $Uri,


        [ValidateSet(
            "v1.0",
            "beta"
        )]
        [string]
        $ApiVersion = "v1.0"

    )



    if ($Uri -notmatch "^https://") {

        $Uri =
        "https://graph.microsoft.com/$ApiVersion$Uri"

    }



    return Invoke-MgGraphRequest `
        -Method GET `
        -Uri $Uri

}



function Test-GraphHasNextPage {

    <#
    .SYNOPSIS
        Checks whether a response contains another page.
    #>


    [CmdletBinding()]

    param(

        [Parameter(
            Mandatory
        )]
        $Response

    )



    return (
        -not [string]::IsNullOrEmpty(
            $Response.'@odata.nextLink'
        )
    )

}



function Get-GraphNextPageLink {

    <#
    .SYNOPSIS
        Returns the next page URL.
    #>


    [CmdletBinding()]

    param(

        [Parameter(
            Mandatory
        )]
        $Response

    )



    return $Response.'@odata.nextLink'

}



#endregion



#region Streaming Collection


function Invoke-GraphPagedCollection {

    <#
    .SYNOPSIS
        Processes Graph pages using a callback.

    .DESCRIPTION
        Avoids storing large evidence collections in memory.
    #>


    [CmdletBinding()]

    param(

        [Parameter(
            Mandatory
        )]
        [string]
        $Uri,


        [Parameter(
            Mandatory
        )]
        [scriptblock]
        $Action,


        [string]
        $ApiVersion = "v1.0"

    )



    $pageUri =
    $Uri



    do {


        $response =
        Get-GraphPagedResponse `
            -Uri $pageUri `
            -ApiVersion $ApiVersion



        foreach ($item in $response.value) {


            & $Action $item


        }



        $pageUri =
        Get-GraphNextPageLink `
            -Response $response



    }
    while ($pageUri)



}



#endregion



Export-ModuleMember -Function @(
    "Get-GraphAllPages"
    "Get-GraphPagedResponse"
    "Test-GraphHasNextPage"
    "Get-GraphNextPageLink"
    "Invoke-GraphPagedCollection"
)
