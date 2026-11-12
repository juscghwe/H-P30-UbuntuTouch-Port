#!/usr/bin/env python3
"""Check sparse cross-chunk reads, LP checksums/extents and exclusive extraction."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('superview', Path(__file__).with_name('inspect-super.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def sparse(raw):
    assert len(raw) % 4096 == 0
    return struct.pack('<I4H4I', 0xed26ff3a, 1, 0, 28, 12, 4096, len(raw)//4096, 1, 0) + \
        struct.pack('<HHII', 0xcac1, 0, len(raw)//4096, 12+len(raw)) + raw


mixed = struct.pack('<I4H4I', 0xed26ff3a, 1, 0, 28, 12, 4, 6, 3, 0)
mixed += struct.pack('<HHII', 0xcac1, 0, 3, 24) + b'abcdefghijkl'
mixed += struct.pack('<HHII', 0xcac2, 0, 2, 16) + b'1234'
mixed += struct.pack('<HHII', 0xcac3, 0, 1, 12)
view = module.SparseView(io.BytesIO(mixed), 0, len(mixed))
assert view.read(10, 12) == b'kl12341234\0\0'
assert view.read(0, 24) == b'abcdefghijkl12341234' + bytes(4)
crc_header = bytearray(mixed)
struct.pack_into('<I', crc_header, 24, 123)
try:
    module.SparseView(io.BytesIO(crc_header), 0, len(crc_header))
except ValueError:
    pass
else:
    raise AssertionError('Unsupported sparse image CRC silently accepted')
for offset, length in [(-1, 1), (0, 25), (24, 1)]:
    try:
        view.read(offset, length)
    except ValueError:
        pass
    else:
        raise AssertionError('Out-of-bounds logical read accepted')

# Independent LP v10.0 fixture: one linear sector plus a dm-zero sector.
tables = struct.pack('<36s4I', b'vendor', 0, 0, 2, 0)
tables += struct.pack('<QIQI', 1, 0, 32, 0) + struct.pack('<QIQI', 1, 1, 0, 0)
tables += struct.pack('<36sIQ', b'default', 0, 0)
tables += struct.pack('<QIIQ36sI', 32, 4096, 0, 20480, b'super', 0)
header = bytearray(struct.pack('<IHHI32sI32s', 0x414c5030, 10, 0, 128, bytes(32),
                              len(tables), hashlib.sha256(tables).digest()))
header += struct.pack('<3I', 0, 1, 52) + struct.pack('<3I', 52, 2, 24)
header += struct.pack('<3I', 100, 1, 48) + struct.pack('<3I', 148, 1, 64)
header[12:44] = hashlib.sha256(header).digest()
geometry = bytearray(struct.pack('<II32sIII', 0x616c4467, 52, bytes(32), 512, 1, 4096))
geometry[8:40] = hashlib.sha256(geometry).digest()
raw = bytearray(20480)
raw[4096:4148] = geometry
raw[8192:8244] = geometry
for offset in [12288, 12800]:
    raw[offset:offset+128] = header
    raw[offset+128:offset+128+len(tables)] = tables
raw[16384:16896] = b'V' * 512
encoded = sparse(raw)
metadata = module.metadata(module.SparseView(io.BytesIO(encoded), 0, len(encoded)))
assert metadata['geometry_sha256_valid']
assert metadata['slots'][0]['primary_backup_bytes_equal']
assert metadata['slots'][0]['partitions'][0]['size_bytes'] == 1024
bad = bytearray(raw)
bad[12288+128] ^= 1
try:
    module.metadata(module.SparseView(io.BytesIO(sparse(bad)), 0, len(encoded)))
except ValueError:
    pass
else:
    raise AssertionError('Corrupt LP table checksum accepted')

with tempfile.TemporaryDirectory(prefix='super-inspector-') as temp:
    root = Path(temp)
    image = root/'super.img'
    image.write_bytes(encoded)
    output = root/'vendor.img'
    command = [sys.executable, str(Path(__file__).with_name('inspect-super.py')),
               str(image), '--extract-partition', 'vendor', '--output', str(output)]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    assert output.read_bytes() == b'V'*512 + bytes(512)
    assert json.loads(result.stdout)['extracted_partition']['size_bytes'] == 1024
    repeated = subprocess.run(command, capture_output=True, text=True)
    assert repeated.returncode != 0
    assert output.read_bytes() == b'V'*512 + bytes(512)
print('PASS: raw/fill/hole reads, LP SHA-256, linear/zero extents and no overwrite')
