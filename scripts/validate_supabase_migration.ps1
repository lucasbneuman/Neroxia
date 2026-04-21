param(
    [string]$ExpectedProjectRef
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Read-EnvFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $values = @{}

    if (-not (Test-Path -LiteralPath $Path)) {
        return $values
    }

    foreach ($line in Get-Content -LiteralPath $Path) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#")) {
            continue
        }

        $separatorIndex = $trimmed.IndexOf("=")
        if ($separatorIndex -lt 1) {
            continue
        }

        $key = $trimmed.Substring(0, $separatorIndex).Trim()
        $value = $trimmed.Substring($separatorIndex + 1).Trim()
        $values[$key] = $value
    }

    return $values
}

function Get-SupabaseRefFromUrl {
    param(
        [string]$Url
    )

    if (-not $Url) {
        return $null
    }

    $match = [regex]::Match($Url, '^https://([a-z0-9-]+)\.supabase\.co/?$')
    if ($match.Success) {
        return $match.Groups[1].Value
    }

    return $null
}

function Decode-JwtPayload {
    param(
        [string]$Token
    )

    if (-not $Token) {
        return $null
    }

    $parts = $Token.Split(".")
    if ($parts.Length -lt 2) {
        return $null
    }

    $payload = $parts[1].Replace("-", "+").Replace("_", "/")
    switch ($payload.Length % 4) {
        2 { $payload += "==" }
        3 { $payload += "=" }
    }

    $json = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($payload))
    return $json | ConvertFrom-Json
}

function Test-HostDns {
    param(
        [string]$HostName
    )

    if (-not $HostName) {
        return $false
    }

    try {
        [System.Net.Dns]::GetHostAddresses($HostName) | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Test-SupabaseRestEndpoint {
    param(
        [string]$Url,
        [string]$ApiKey
    )

    if (-not $Url) {
        return @{
            Reachable = $false
            StatusCode = $null
            Detail = "missing url"
        }
    }

    $headers = @{}
    if ($ApiKey) {
        $headers["apikey"] = $ApiKey
        $headers["Authorization"] = "Bearer $ApiKey"
    }

    try {
        $response = Invoke-WebRequest -Uri ($Url.TrimEnd("/") + "/rest/v1/") -Headers $headers -Method GET -TimeoutSec 20
        return @{
            Reachable = $true
            StatusCode = [int]$response.StatusCode
            Detail = "ok"
        }
    } catch {
        if ($_.Exception.Response) {
            return @{
                Reachable = $true
                StatusCode = [int]$_.Exception.Response.StatusCode
                Detail = "http error"
            }
        }

        return @{
            Reachable = $false
            StatusCode = $null
            Detail = $_.Exception.Message
        }
    }
}

function Write-Check {
    param(
        [string]$Status,
        [string]$Message
    )

    Write-Output ("[{0}] {1}" -f $Status, $Message)
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$rootEnvPath = Join-Path $repoRoot ".env"
$webEnvPath = Join-Path $repoRoot "apps\web\.env.local"

$rootEnv = Read-EnvFile -Path $rootEnvPath
$webEnv = Read-EnvFile -Path $webEnvPath

$supabaseUrl = $rootEnv["SUPABASE_URL"]
$supabaseAnonKey = $rootEnv["SUPABASE_ANON_KEY"]
$supabaseServiceKey = $rootEnv["SUPABASE_SERVICE_KEY"]
$supabaseDatabaseUrl = $rootEnv["SUPABASE_DATABASE_URL"]
$webSupabaseUrl = $webEnv["NEXT_PUBLIC_SUPABASE_URL"]
$webSupabaseAnonKey = $webEnv["NEXT_PUBLIC_SUPABASE_ANON_KEY"]

$urlRef = Get-SupabaseRefFromUrl -Url $supabaseUrl
$anonPayload = Decode-JwtPayload -Token $supabaseAnonKey
$servicePayload = Decode-JwtPayload -Token $supabaseServiceKey
$anonRef = if ($anonPayload) { $anonPayload.ref } else { $null }
$serviceRef = if ($servicePayload) { $servicePayload.ref } else { $null }
$currentHost = if ($supabaseUrl) { ([uri]$supabaseUrl).Host } else { $null }
$expectedUrl = if ($ExpectedProjectRef) { "https://$ExpectedProjectRef.supabase.co" } else { $null }
$expectedRest = if ($ExpectedProjectRef) { Test-SupabaseRestEndpoint -Url $expectedUrl } else { $null }
$currentRest = Test-SupabaseRestEndpoint -Url $supabaseUrl -ApiKey $supabaseAnonKey

Write-Output ""
Write-Output "Supabase migration validation"
Write-Output "Repository: $repoRoot"
Write-Output ""

Write-Output "Root environment"
Write-Check -Status ($(if ($supabaseUrl) { "OK" } else { "FAIL" })) -Message ("SUPABASE_URL: {0}" -f ($(if ($supabaseUrl) { $supabaseUrl } else { "missing" })))
Write-Check -Status ($(if ($supabaseAnonKey) { "OK" } else { "FAIL" })) -Message ("SUPABASE_ANON_KEY: {0}" -f ($(if ($supabaseAnonKey) { "set" } else { "missing" })))
Write-Check -Status ($(if ($supabaseServiceKey) { "OK" } else { "FAIL" })) -Message ("SUPABASE_SERVICE_KEY: {0}" -f ($(if ($supabaseServiceKey) { "set" } else { "missing" })))
Write-Check -Status ($(if ($supabaseDatabaseUrl) { "OK" } else { "FAIL" })) -Message ("SUPABASE_DATABASE_URL: {0}" -f ($(if ($supabaseDatabaseUrl) { "set" } else { "missing" })))
Write-Output ""

Write-Output "Reference consistency"
Write-Check -Status ($(if ($urlRef) { "OK" } else { "FAIL" })) -Message ("URL ref: {0}" -f ($(if ($urlRef) { $urlRef } else { "unparseable" })))
Write-Check -Status ($(if ($anonRef) { "OK" } else { "FAIL" })) -Message ("Anon key ref: {0}" -f ($(if ($anonRef) { $anonRef } else { "unparseable" })))
Write-Check -Status ($(if ($serviceRef) { "OK" } else { "FAIL" })) -Message ("Service key ref: {0}" -f ($(if ($serviceRef) { $serviceRef } else { "unparseable" })))

if ($urlRef -and $anonRef -and ($urlRef -ne $anonRef)) {
    Write-Check -Status "FAIL" -Message "SUPABASE_URL and SUPABASE_ANON_KEY point to different projects"
}

if ($urlRef -and $serviceRef -and ($urlRef -ne $serviceRef)) {
    Write-Check -Status "FAIL" -Message "SUPABASE_URL and SUPABASE_SERVICE_KEY point to different projects"
}

if ($ExpectedProjectRef) {
    $matchesExpected = ($urlRef -eq $ExpectedProjectRef) -and ($anonRef -eq $ExpectedProjectRef) -and ($serviceRef -eq $ExpectedProjectRef)
    Write-Check -Status ($(if ($matchesExpected) { "OK" } else { "FAIL" })) -Message "Expected project ref: $ExpectedProjectRef"
}

Write-Output ""
Write-Output "Frontend environment"
Write-Check -Status ($(if ($webSupabaseUrl) { "OK" } else { "FAIL" })) -Message ("NEXT_PUBLIC_SUPABASE_URL: {0}" -f ($(if ($webSupabaseUrl) { $webSupabaseUrl } else { "missing" })))
Write-Check -Status ($(if ($webSupabaseAnonKey) { "OK" } else { "FAIL" })) -Message ("NEXT_PUBLIC_SUPABASE_ANON_KEY: {0}" -f ($(if ($webSupabaseAnonKey) { "set" } else { "missing" })))

if ($webSupabaseUrl -and $supabaseUrl) {
    Write-Check -Status ($(if ($webSupabaseUrl -eq $supabaseUrl) { "OK" } else { "FAIL" })) -Message "Frontend URL matches root Supabase URL"
}

if ($webSupabaseAnonKey -and $supabaseAnonKey) {
    Write-Check -Status ($(if ($webSupabaseAnonKey -eq $supabaseAnonKey) { "OK" } else { "FAIL" })) -Message "Frontend anon key matches root anon key"
}

Write-Output ""
Write-Output "Connectivity"
Write-Check -Status ($(if (Test-HostDns -HostName $currentHost) { "OK" } else { "FAIL" })) -Message ("Current Supabase host DNS: {0}" -f ($(if ($currentHost) { $currentHost } else { "missing host" })))
Write-Check -Status ($(if ($currentRest.Reachable) { "OK" } else { "FAIL" })) -Message ("Current project REST endpoint: {0} ({1})" -f ($(if ($currentRest.StatusCode) { $currentRest.StatusCode } else { "unreachable" }), $currentRest.Detail))

if ($ExpectedProjectRef) {
    $expectedHost = "$ExpectedProjectRef.supabase.co"
    Write-Check -Status ($(if (Test-HostDns -HostName $expectedHost) { "OK" } else { "FAIL" })) -Message "Expected project host DNS: $expectedHost"
    Write-Check -Status ($(if ($expectedRest.Reachable) { "OK" } else { "FAIL" })) -Message ("Expected project REST endpoint: {0} ({1})" -f ($(if ($expectedRest.StatusCode) { $expectedRest.StatusCode } else { "unreachable" }), $expectedRest.Detail))
}

Write-Output ""
Write-Output "Database URL"
if ($supabaseDatabaseUrl) {
    $dbRefMatch = [regex]::Match($supabaseDatabaseUrl, 'postgres\.([a-z0-9-]+):')
    if ($dbRefMatch.Success) {
        $dbRef = $dbRefMatch.Groups[1].Value
        Write-Check -Status "OK" -Message "Database URL ref: $dbRef"
        if ($ExpectedProjectRef) {
            Write-Check -Status ($(if ($dbRef -eq $ExpectedProjectRef) { "OK" } else { "FAIL" })) -Message "Database URL matches expected project ref"
        }
    } else {
        Write-Check -Status "WARN" -Message "Could not extract project ref from SUPABASE_DATABASE_URL"
    }
} else {
    Write-Check -Status "FAIL" -Message "SUPABASE_DATABASE_URL missing"
}
