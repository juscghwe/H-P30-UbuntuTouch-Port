#!/usr/bin/env python3
"""Exercise image metadata layouts, bounds, privacy and input immutability.

Requires dtc on PATH. Generated files remain in a temporary directory.
"""
from pathlib import Path
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
workspace = tempfile.TemporaryDirectory(prefix='image-metadata-check-')
root = Path(workspace.name)
script = str(Path(__file__).with_name('inspect-image.py'))
(root / 'fixture.dts').write_text('/dts-v1/; / { compatible = "test,fixture"; };\n')
subprocess.run(['dtc', '-I', 'dts', '-O', 'dtb', str(root / 'fixture.dts'), '-o', str(root / 'fixture.dtb')], check=True)
dtb = (root / 'fixture.dtb').read_bytes()
results = []

def run(name, data, expected=None, error=False):
    p = root / name
    p.write_bytes(data)
    before = hashlib.sha256(data).hexdigest()
    r = subprocess.run([sys.executable, script, str(p)], capture_output=True, text=True)
    assert (r.returncode != 0) == error, (name, r.stdout, r.stderr)
    assert hashlib.sha256(p.read_bytes()).hexdigest() == before
    assert 'DO_NOT_EXPORT' not in r.stdout
    if expected:
        d = json.loads(r.stdout)
        for k, v in expected.items():
            assert d[k] == v, (name, k, d[k], v)
    else:
        d = None
    results.append({'test': name, 'passed': True, 'input_sha256': before, 'exit': r.returncode})
    return d
for version in [0, 1, 2]:
    data = bytearray(12288 if version == 2 else 10240 if version == 1 else 8192)
    data[:8] = b'ANDROID!'
    struct.pack_into('<10I', data, 8, 6, 268468224, 7, 285212672, 6, 301989888, 268435712, 2048, version, 0)
    data[48:61] = b'DO_NOT_EXPORT'
    data[64:86] = b'DO_NOT_EXPORT_CMDLINE!'
    data[2048:2054] = b'kernel'
    data[4096:4103] = b'ramdisk'
    data[6144:6150] = b'second'
    if version >= 1:
        struct.pack_into('<IQI', data, 1632, len(dtb), 8192, 1648 if version == 1 else 1660)
        data[8192:8192 + len(dtb)] = dtb
    if version == 2:
        struct.pack_into('<IQ', data, 1648, len(dtb), 318767104)
        data[10240:10240 + len(dtb)] = dtb
    d = run(f'boot-v{version}.img', data, {'format': 'android-boot', 'header_version': version, 'page_size': 2048})
    assert [x['offset'] for x in d['regions']] == [2048, 4096, 6144] + ([8192] if version >= 1 else []) + ([10240] if version == 2 else [])
    if version == 2:
        good = bytes(data)
run('fdt.dtb', dtb, {'format': 'fdt'})
data = bytearray(2048 + len(dtb))
struct.pack_into('>8I', data, 0, 3619138334, len(data), 32, 32, 1, 32, 2048, 0)
struct.pack_into('>8I', data, 32, len(dtb), 2048, 0, 0, 0, 0, 0, 0)
data[2048:] = dtb
d = run('dt-table.img', data, {'format': 'android-dt-table', 'entry_count': 1})
assert d['entries'][0]['sha256'] == hashlib.sha256(dtb).hexdigest()
bad = bytearray(data)
struct.pack_into('>I', bad, 36, 63)
run('overlapping-dt.img', bad, error=True)
bad = bytearray(good)
struct.pack_into('<I', bad, 8, 4294967295)
run('oversized-kernel.img', bad, error=True)
bad = bytearray(good)
struct.pack_into('<I', bad, 36, 2000)
run('invalid-page.img', bad, error=True)
run('truncated-header.img', good[:100], error=True)
run('unrecognized.img', b'fixture', {'format': 'unrecognized'})
print(json.dumps({'origin': 'Generated host-side format fixtures, not phone images', 'cases': results, 'scope': 'Checks legacy Android layouts, DT table bounds, FDT header, rejection paths, input immutability and omission of command lines/names. No actual Huawei image has been inspected.'}, indent=2))
workspace.cleanup()
