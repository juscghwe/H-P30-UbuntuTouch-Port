# Downloads and optionally extracts pinned reference firmware on the PC only.
# Contains no phone commands and does not launch programs from the archives.
[CmdletBinding()]
param(
    [string]$ManifestPath = (Join-Path $PSScriptRoot '../findings/raw/2026-11-17/03-firmware-package-verification.json'),
    [string]$DestinationRoot = (Join-Path $env:USERPROFILE 'Downloads/P30-Firmware-Reference'),
    [ValidateSet('Android9', 'Android10', 'Both')][string]$Set = 'Both',
    [switch]$Extract
)

function Assert-ReferenceArtifact {
    param([string]$ArtifactPath, [long]$ExpectedBytes, [string]$ExpectedSha256)
    if ($ExpectedBytes -le 0 -or $ExpectedSha256 -notmatch '^[a-fA-F0-9]{64}$') { throw 'Invalid artifact metadata.' }
    $artifact = Get-Item -LiteralPath $ArtifactPath -ErrorAction Stop
    if ($artifact.PSIsContainer -or $artifact.Length -ne $ExpectedBytes) { throw ('Size mismatch: ' + $artifact.Name) }
    $digest = (Get-FileHash -LiteralPath $ArtifactPath -Algorithm SHA256 -ErrorAction Stop).Hash
    if ($digest -ne $ExpectedSha256) { throw ('SHA-256 mismatch: ' + $artifact.Name) }
}

function Get-ReferenceArchive {
    param([string]$SourceUrl, [string]$ArchivePath, [long]$ExpectedBytes, [string]$ExpectedSha256)
    $sourceUri = [uri]$SourceUrl
    if ($sourceUri.Scheme -ne 'https' -or $sourceUri.DnsSafeHost -ne 'update.dbankcdn.com' -or $sourceUri.UserInfo -or $sourceUri.Query -or $sourceUri.Fragment) { throw 'Expected a credential-free Huawei HTTPS archive URL.' }
    if (Test-Path -LiteralPath $ArchivePath) {
        Assert-ReferenceArtifact $ArchivePath $ExpectedBytes $ExpectedSha256
        Write-Host ('Already verified: ' + [IO.Path]::GetFileName($ArchivePath))
        return
    }
    $partial = $ArchivePath + '.part'
    if ((Test-Path -LiteralPath $partial) -and (Get-Item -LiteralPath $partial).Length -gt $ExpectedBytes) { throw 'Partial archive exceeds expected size; preserve it for inspection.' }
    New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($ArchivePath)) -Force | Out-Null
    if (-not (Test-Path -LiteralPath $partial) -or (Get-Item -LiteralPath $partial).Length -lt $ExpectedBytes) {
        $curlCommand = Get-Command curl.exe -CommandType Application -ErrorAction Stop
        Write-Host ('Downloading: ' + [IO.Path]::GetFileName($ArchivePath))
        & $curlCommand.Source --silent --show-error --fail --location --proto '=https' --proto-redir '=https' --retry 3 --connect-timeout 30 --continue-at '-' --output $partial $SourceUrl
        if ($LASTEXITCODE -ne 0) { throw ('Download failed; partial file retained. curl exit: ' + $LASTEXITCODE) }
    }
    Assert-ReferenceArtifact $partial $ExpectedBytes $ExpectedSha256
    [IO.File]::Move($partial, $ArchivePath)
    Write-Host ('Verified: ' + [IO.Path]::GetFileName($ArchivePath))
}

function Expand-ReferenceApps {
    param([string]$ArchivePath, [string]$OutputDirectory, [object[]]$Apps)
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
    $archive = [IO.Compression.ZipFile]::OpenRead($ArchivePath)
    try {
        foreach ($app in $Apps) {
            if ($app.member -notin @('PTABLE.APP', 'UPDATE.APP')) { throw 'Unexpected extraction member.' }
            $target = Join-Path $OutputDirectory $app.member
            if (Test-Path -LiteralPath $target) {
                Assert-ReferenceArtifact $target ([long]$app.size_bytes) $app.sha256
                continue
            }
            $matching = @($archive.Entries | Where-Object { $_.FullName -ceq $app.member })
            if ($matching.Count -ne 1 -or $matching[0].Length -ne [long]$app.size_bytes) { throw 'Missing, duplicate or incorrectly sized APP member.' }
            $partial = $target + '.part'
            $sourceStream = $null
            $outputStream = $null
            try {
                # Exclusive creation preserves any existing partial extraction.
                $outputStream = [IO.File]::Open($partial, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
                $sourceStream = $matching[0].Open()
                $sourceStream.CopyTo($outputStream, 4194304)
            } finally {
                if ($null -ne $sourceStream) { $sourceStream.Dispose() }
                if ($null -ne $outputStream) { $outputStream.Dispose() }
            }
            Assert-ReferenceArtifact $partial ([long]$app.size_bytes) $app.sha256
            [IO.File]::Move($partial, $target)
            Write-Host ('Extracted and verified: ' + $app.member)
        }
    } finally {
        $archive.Dispose()
    }
}

function Start-ReferencePreparation {
    $ErrorActionPreference = 'Stop'
    $manifestHash = '1fb874843e23139ac1e7da5ba619554dfef439cb836911b0e09312436376cff1'
    if ((Get-FileHash -LiteralPath $ManifestPath -Algorithm SHA256).Hash -ne $manifestHash) { throw 'Reference manifest differs from the inspected revision.' }
    $manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
    $wanted = switch ($Set) {
        'Android9' { @('android9-c431-reference') }
        'Android10' { @('android10-562-c431-reference') }
        'Both' { @('android9-c431-reference', 'android10-562-c431-reference') }
    }
    $packages = @($manifest.packages | Where-Object { $_.reference_group -in $wanted })
    if ($packages.Count -ne (3 * @($wanted).Count)) { throw 'Expected three archives per firmware set.' }
    $seen = @{}
    foreach ($package in $packages) {
        $uri = [uri]$package.url
        $leaf = [IO.Path]::GetFileName($uri.AbsolutePath)
        $component = switch ($leaf) {
            'update_full_base.zip' { 'base' }
            'update_full_cust_MAR-L21A_hw_eea.zip' { 'cust' }
            'update_full_preload_MAR-L21A_hw_eea_R2.zip' { 'preload' }
            default { throw 'Unexpected reference archive name.' }
        }
        $key = $package.reference_group + '/' + $component
        if ($seen.ContainsKey($key)) { throw 'Duplicate reference component.' }
        $seen[$key] = $true
        $directory = Join-Path $DestinationRoot $package.reference_group
        $target = Join-Path $directory $leaf
        Write-Host ('Preparing ' + $package.reference_group + ' / ' + $component + ': ' + $package.version_label)
        Get-ReferenceArchive $package.url $target ([long]$package.size) $package.sha256
        if ($Extract) { Expand-ReferenceApps $target (Join-Path $directory $component) @($package.app_inspection) }
    }
    Write-Host 'PC preparation complete. No phone operation was performed.'
}

# Dot-sourcing exposes functions for offline fixture checks without starting downloads.
if ($MyInvocation.InvocationName -ne '.') { Start-ReferencePreparation }
