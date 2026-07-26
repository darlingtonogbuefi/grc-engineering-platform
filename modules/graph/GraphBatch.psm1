<#
    modules\graph\GraphBatch.psm1

    GRC Engineering Platform
#>

<#
.SYNOPSIS
    Microsoft Graph batch request module.

.DESCRIPTION
    Provides support for Microsoft Graph JSON batching.

    Responsibilities:

    - Build Graph batch requests
    - Submit up to 20 requests per batch
    - Process batch responses
    - Handle request dependencies
    - Support bulk evidence collection

    Microsoft Graph batch endpoint:

    POST https://graph.microsoft.com/v1.0/$batch

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



#region Constants


$GraphBatchLimit = 20



#endregion



#region Batch Creation


function New-GraphBatchRequest {

    <#
    .SYNOPSIS
        Creates a Graph batch request object.
    #>


    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [string]
        $Id,


        [ValidateSet(
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE"
        )]
        [string]
        $Method = "GET",


        [Parameter(Mandatory)]
        [string]
        $Url,


        [object]
        $Body,


        [hashtable]
        $Headers

    )


    $request = [ordered]@{

        id     = $Id

        method = $Method

        url    = $Url

    }



    if ($Headers) {

        $request.headers = $Headers

    }



    if ($null -ne $Body) {

        $request.body = $Body

    }



    return $request

}



function New-GraphBatchBody {

    <#
    .SYNOPSIS
        Creates a Microsoft Graph batch payload.
    #>


    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [array]
        $Requests

    )



    if ($Requests.Count -gt $GraphBatchLimit) {

        throw @"
Microsoft Graph batch requests support a maximum of
$GraphBatchLimit requests per batch.

Received:
$($Requests.Count)

"@

    }



    return @{
        requests = $Requests
    }

}



#endregion



#region Batch Execution


function Invoke-GraphBatch {

    <#
    .SYNOPSIS
        Executes Microsoft Graph batch requests.
    #>


    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [array]
        $Requests,


        [ValidateSet(
            "v1.0",
            "beta"
        )]
        [string]
        $ApiVersion = "v1.0"

    )



    $body =
    New-GraphBatchBody `
        -Requests $Requests



    $uri =
    "https://graph.microsoft.com/$ApiVersion/`$batch"



    return Invoke-MgGraphRequest `
        -Method POST `
        -Uri $uri `
        -Body (
        $body |
        ConvertTo-Json -Depth 20
    ) `
        -ContentType "application/json"

}



function Invoke-GraphBatchChunked {

    <#
    .SYNOPSIS
        Executes large batches by splitting requests.

    .DESCRIPTION
        Microsoft Graph supports a maximum of 20 requests
        per batch. This function automatically chunks
        larger collections.
    #>


    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        [array]
        $Requests,


        [string]
        $ApiVersion = "v1.0"

    )



    $responses =
    [System.Collections.Generic.List[object]]::new()



    for (
        $i = 0;
        $i -lt $Requests.Count;
        $i += $GraphBatchLimit
    ) {



        $endIndex =
        [Math]::Min(
            $i + $GraphBatchLimit - 1,
            $Requests.Count - 1
        )



        $chunk =
        $Requests[$i..$endIndex]



        $response =
        Invoke-GraphBatch `
            -Requests $chunk `
            -ApiVersion $ApiVersion



        $responses.Add(
            $response
        )

    }



    return $responses

}



#endregion



#region Response Handling


function Get-GraphBatchResponses {

    <#
    .SYNOPSIS
        Returns individual batch responses.
    #>


    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        $Response

    )


    return $Response.responses

}



function Test-GraphBatchSuccess {

    <#
    .SYNOPSIS
        Tests whether a batch item succeeded.
    #>


    [CmdletBinding()]

    param(

        [Parameter(Mandatory)]
        $Response

    )


    return (
        $Response.status -ge 200 -and
        $Response.status -lt 300
    )

}



#endregion



Export-ModuleMember -Function @(
    "New-GraphBatchRequest"
    "New-GraphBatchBody"
    "Invoke-GraphBatch"
    "Invoke-GraphBatchChunked"
    "Get-GraphBatchResponses"
    "Test-GraphBatchSuccess"
)
