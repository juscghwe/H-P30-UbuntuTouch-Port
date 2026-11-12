#requires -Version 5.1
<#
Continuously mirror likely firmware/cache files using shared, short-lived reads.
Copies remain unverified snapshots. No processes, source files or phone are changed.
#>
[CmdletBinding()]
param(
    [string]$Destination,
    [string[]]$WatchPath = @(),
    [int]$IntervalMilliseconds = 500,
    [int]$RescanSeconds = 15,
    [int]$StopAfterSeconds = 0
)
Set-StrictMode -Version 2
$ErrorActionPreference = 'Stop'
$started = [DateTime]::UtcNow
if (-not $Destination) {
    $Destination = Join-Path $env:USERPROFILE ('Downloads\P30-Firmware-Capture-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
}
$Destination = [IO.Path]::GetFullPath($Destination)
$null = New-Item -ItemType Directory -Path $Destination -Force
$records = @{}
$buffer = New-Object byte[] (4MB)
$share = [IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete
$roots = @()
function Add-Root([string]$Path, [bool]$Broad, [int]$Depth) {
    if ($Path) { $script:roots += [pscustomobject]@{ Path = $Path; Broad = $Broad; Depth = $Depth } }
}
if ($WatchPath.Count) {
    foreach ($path in $WatchPath) { Add-Root $path $true 6 }
} else {
    foreach ($parent in @([Environment]::GetFolderPath('MyDocuments'), [Environment]::GetFolderPath('CommonDocuments'), $env:LOCALAPPDATA, $env:APPDATA, $env:ProgramData, $env:ProgramFiles, ${env:ProgramFiles(x86)})) {
        if ($parent) { Add-Root (Join-Path $parent 'HiSuite') $true 6 }
    }
    foreach ($parent in @($env:LOCALAPPDATA, $env:APPDATA, $env:ProgramData)) {
        if ($parent) { Add-Root (Join-Path $parent 'Huawei\HiSuite') $true 6 }
    }
    Add-Root $env:TEMP $false 2
    if ($env:USERPROFILE) { Add-Root (Join-Path $env:USERPROFILE 'Downloads') $false 1 }
}

function Get-Candidates {
    $seen = @{}
    foreach ($root in $roots) {
        if (-not (Test-Path -LiteralPath $root.Path -PathType Container)) { continue }
        $queue = New-Object 'Collections.Generic.Queue[object]'
        $queue.Enqueue(@($root.Path, 0))
        $directories = 0
        while ($queue.Count -and $directories -lt 1500) {
            $item = $queue.Dequeue(); $directories++
            $directory = [IO.Path]::GetFullPath([string]$item[0])
            if ($directory.Equals($Destination, [StringComparison]::OrdinalIgnoreCase) -or $directory.StartsWith($Destination + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { continue }
            if ($directory -match '(?i)[\\/](backup|backups)([\\/]|$)') { continue }
            foreach ($entry in @(Get-ChildItem -LiteralPath $directory -Force -ErrorAction SilentlyContinue)) {
                if ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
                if ($entry.PSIsContainer) {
                    if ($item[1] -lt $root.Depth) { $queue.Enqueue(@($entry.FullName, ([int]$item[1] + 1))) }
                    continue
                }
                if ($seen.ContainsKey($entry.FullName)) { continue }
                $seen[$entry.FullName] = $true
                $known = $entry.Name -match '(?i)^(update.*\.(zip|app|bin)(\.(tmp|part|download))?|filelist\.xml|changelog.*\.xml|.*(kernel|ramdisk|dtbo?|dts)\.img(\.(tmp|part))?)$'
                $broad = $root.Broad -or $entry.FullName -match '(?i)[\\/][^\\/]*(hisuite|huawei)[^\\/]*[\\/]'
                $recent = $entry.LastWriteTimeUtc -ge $started.AddMinutes(-10)
                if ($known -or ($broad -and $recent -and $entry.Length -gt 0 -and ($entry.Extension -match '(?i)^\.(zip|app|bin|tmp|temp|part|download)$' -or $entry.Length -ge 16MB))) {
                    if ($entry.Extension -notmatch '(?i)^\.(exe|dll|pdb|log|db)$') { $entry }
                } elseif ($recent -and $entry.Length -ge 1MB -and $entry.Extension -match '(?i)^(|\.tmp|\.temp|\.part|\.download|\.zip|\.app|\.bin)$') {
                    # Generic temporary files need a recognizable Huawei package header.
                    $stream = $null
                    try {
                        $stream = [IO.File]::Open($entry.FullName, 'Open', 'Read', $share)
                        $prefix = New-Object byte[] 65536
                        $count = $stream.Read($prefix, 0, $prefix.Length)
                        $text = [Text.Encoding]::ASCII.GetString($prefix, 0, $count)
                        $app = $count -ge 4 -and $prefix[0] -eq 0x55 -and $prefix[1] -eq 0xaa -and $prefix[2] -eq 0x5a -and $prefix[3] -eq 0xa5
                        $app = $app -or ($count -ge 96 -and $prefix[92] -eq 0x55 -and $prefix[93] -eq 0xaa -and $prefix[94] -eq 0x5a -and $prefix[95] -eq 0xa5)
                        if ($app -or $text -match '(?i)full_mainpkg\.tag|SOFTWARE_VER\.mbn|PTABLE\.APP|HWHOTA') { $entry }
                    } catch { } finally { if ($stream) { $stream.Dispose() } }
                }
            }
        }
    }
}

function Copy-Step($record) {
    $sourceStream = $null; $targetStream = $null
    try {
        $sourceStream = [IO.File]::Open($record.Source, 'Open', 'Read', $share)
        $length = $sourceStream.Length
        if ($length -eq 0) { return }
        if ($length -lt $record.Cursor) { $record.Cursor = 0; $record.Truncated = $true }
        if ($record.Cursor -ge $length) {
            if (([DateTime]::UtcNow - $record.LastPass).TotalSeconds -lt $RescanSeconds) { return }
            $record.Cursor = 0
        }
        $null = $sourceStream.Seek($record.Cursor, 'Begin')
        $count = $sourceStream.Read($buffer, 0, [int][Math]::Min($buffer.Length, $length - $record.Cursor))
        if ($count -le 0) { return }
        $targetStream = [IO.File]::Open($record.Target, 'OpenOrCreate', 'Write', [IO.FileShare]::Read)
        if ($record.Truncated) { $targetStream.SetLength(0); $record.Truncated = $false }
        $null = $targetStream.Seek($record.Cursor, 'Begin')
        $targetStream.Write($buffer, 0, $count)
        $record.Cursor += $count
        $record.SourceLength = $length
        $record.LastError = $null
        if ($record.Cursor -ge $length) { $targetStream.SetLength($length); $record.LastPass = [DateTime]::UtcNow; $record.Passes++ }
    } catch {
        $record.LastError = $_.Exception.GetType().Name
    } finally {
        if ($targetStream) { $targetStream.Dispose() }
        if ($sourceStream) { $sourceStream.Dispose() }
    }
}

Write-Host ('Capture folder: ' + $Destination)
Write-Host 'Watching common HiSuite locations and recognizable firmware in temporary/download folders.'
Write-Host 'Leave this running during the download. Ctrl+C stops the watcher, not HiSuite.'
Write-Host 'Snapshots can be incomplete; verify their hashes afterward. Nothing is uploaded.'
$lastDiscovery = [DateTime]::MinValue
$lastReport = [DateTime]::MinValue
$nextRecord = 0
try {
    while ($StopAfterSeconds -eq 0 -or ([DateTime]::UtcNow - $started).TotalSeconds -lt $StopAfterSeconds) {
        if (([DateTime]::UtcNow - $lastDiscovery).TotalSeconds -ge 2) {
            foreach ($file in @(Get-Candidates)) {
                if (-not $records.ContainsKey($file.FullName)) {
                    $sha = [Security.Cryptography.SHA256]::Create()
                    try { $id = ([BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($file.FullName)))).Replace('-', '').Substring(0, 12) } finally { $sha.Dispose() }
                    $leaf = $file.Name -replace '[^A-Za-z0-9._-]', '_'
                    $target = Join-Path $Destination ($id + '-' + $leaf + '.capture')
                    $records[$file.FullName] = [pscustomobject]@{ Source = $file.FullName; Target = $target; Cursor = [long]0; SourceLength = [long]$file.Length; LastPass = [DateTime]::MinValue; Passes = 0; LastError = $null; Truncated = $false }
                    Write-Host ('FOUND ' + $file.Name)
                }
            }
            $lastDiscovery = [DateTime]::UtcNow
        }
        # At most 32 MiB per tick, using 4 MiB shared reads; no retained source handles.
        $active = @($records.Values | Sort-Object Source)
        for ($i = 0; $i -lt [Math]::Min(8, $active.Count); $i++) {
            Copy-Step $active[(($nextRecord + $i) % $active.Count)]
        }
        if ($active.Count) { $nextRecord = ($nextRecord + 8) % $active.Count }
        if (([DateTime]::UtcNow - $lastReport).TotalSeconds -ge 5) {
            foreach ($record in $records.Values) { Write-Host ('SNAPSHOT {0}: cursor {1:N1}/{2:N1} MiB; passes {3}; read error {4}' -f ([IO.Path]::GetFileName($record.Source)), ($record.Cursor / 1MB), ($record.SourceLength / 1MB), $record.Passes, $record.LastError) }
            $lastReport = [DateTime]::UtcNow
        }
        ConvertTo-Json -InputObject @($records.Values) -Depth 4 | Set-Content -LiteralPath (Join-Path $Destination 'capture-index.json') -Encoding UTF8
        Start-Sleep -Milliseconds ([Math]::Max(100, $IntervalMilliseconds))
    }
} finally {
    ConvertTo-Json -InputObject @($records.Values) -Depth 4 | Set-Content -LiteralPath (Join-Path $Destination 'capture-index.json') -Encoding UTF8
    Write-Host ('Watcher stopped. Unverified snapshots remain in ' + $Destination)
}
