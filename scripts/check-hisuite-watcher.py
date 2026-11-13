#!/usr/bin/env python3
"""Exercise local copy behavior with synthetic files; no HiSuite or phone needed."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--pwsh', default='pwsh')
args = parser.parse_args()
script = Path(__file__).with_name('watch-hisuite-downloads.ps1')
with tempfile.TemporaryDirectory(prefix='firmware-watch-test-') as temporary:
    root = Path(temporary)
    source = root / 'local' / 'HiSuite' / 'ROM'
    source.mkdir(parents=True)
    output = root / 'capture'
    env = os.environ.copy()
    env.update(LOCALAPPDATA=str(root / 'local'), APPDATA=str(root / 'roaming'),
               ProgramData=str(root / 'programdata'), ProgramFiles=str(root / 'programfiles'),
               USERPROFILE=str(root / 'profile'), TEMP=str(root / 'temp'))
    temp = Path(env['TEMP'])
    temp.mkdir()
    # Sparse input reproduces the actual >Int32.MaxValue length without copying
    # gigabytes. Load the authored script, then exercise one real 4 MiB read.
    large = root / 'large.zip'
    with large.open('wb') as stream:
        stream.truncate(3_199_657_640)
    harness = root / 'large-read.ps1'
    harness.write_text('''param($Watcher, $Root)
. $Watcher -Destination (Join-Path $Root 'empty-output') -WatchPath (Join-Path $Root 'absent') -StopAfterSeconds 1
$record = [pscustomobject]@{ Source = (Join-Path $Root 'large.zip'); Target = (Join-Path $Root 'large.capture'); Cursor = [long]0; SourceLength = [long]3199657640; LastPass = [DateTime]::MinValue; Passes = 0; LastError = $null; Truncated = $false }
Copy-Step $record
if ($record.LastError -or $record.Cursor -ne 4MB) { throw ('Large-file read failed: ' + $record.LastError) }
if ((Get-Item -LiteralPath $record.Target).Length -ne 4MB) { throw 'Incorrect snapshot size' }
''')
    result = subprocess.run([args.pwsh, '-NoLogo', '-NoProfile', '-File', str(harness),
                             str(script), str(root)], env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    expected = []
    for index in range(12):
        file = source / f'update_{index}.zip'
        file.write_bytes(bytes([index]) * 200_000)
        expected.append(file)
    changing = source / 'update_changing.zip'
    changing.write_bytes(b'a' * 1_000_000)
    expected.append(changing)
    preallocated = source / 'update_preallocated.zip'
    preallocated.write_bytes(b'\0' * 6_000_000)
    expected.append(preallocated)
    app = temp / 'random-buffer.tmp'
    app.write_bytes(b'\0' * 92 + b'\x55\xaa\x5a\xa5' + b'x' * 1_100_000)
    expected.append(app)
    (source / 'backup').mkdir()
    (source / 'backup' / 'update_private.zip').write_bytes(b'exclude backup')
    (temp / 'unrelated.zip').write_bytes(b'x' * 1_100_000)
    command = [args.pwsh, '-NoLogo', '-NoProfile', '-File', str(script),
               '-Destination', str(output), '-IntervalMilliseconds', '100',
               '-RescanSeconds', '1', '-StopAfterSeconds', '9']
    with (root / 'test-output.txt').open('w+') as log:
        process = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT)
        try:
            time.sleep(2)
            with changing.open('ab') as stream:
                stream.write(b'b' * 9_000_000)
            with preallocated.open('r+b') as stream:
                stream.seek(2_000_000)
                stream.write(b'changed' * 1000)
            time.sleep(2)
            changing.write_bytes(b'c' * 2_000_000)
            code = process.wait(timeout=20)
            log.seek(0)
            diagnostic = log.read()
            assert code == 0, diagnostic
            records = json.loads((output / 'capture-index.json').read_text(encoding='utf-8-sig'))
            assert len(records) == len(expected), diagnostic
            by_source = {record['Source']: record for record in records}
            for file in expected:
                record = by_source[str(file)]
                assert Path(record['Target']).read_bytes() == file.read_bytes(), file.name
                assert record['LastError'] is None, record
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
print('PASS: >2 GiB input, discovery, >8 candidates, growth, truncation, preallocation rewrite, backup exclusion')
