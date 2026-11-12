#!/usr/bin/env python3
"""Check compressed DT entry bounds and gzip CRC failures with numeric fixtures."""
import gzip
import importlib.util
from pathlib import Path
import struct
import sys
import zlib

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("dt", Path(__file__).with_name("inspect-dt-containers.py"))
dt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dt)
# Minimal numeric FDT-header fixture; semantic tree validity is outside this test.
fdt = struct.pack(">10I", 0xd00dfeed, 60, 56, 60, 40, 17, 16, 0, 0, 4) + bytes(16) + struct.pack(">I", 9)
compressed = gzip.compress(fdt, mtime=0)
image = struct.pack(">8I", 0xd7b7ab1e, 64+len(compressed), 32, 32, 1, 32, 2048, 1)
image += struct.pack(">8I", len(compressed), 64, 123, 0, 2, 0, 0, 0) + compressed
assert dt.inspect(image)["entries"][0]["expanded_bytes"] == len(fdt)
wrapped = bytes(4096) + image
assert dt.inspect(wrapped, 4096)["entries"][0]["id"] == 123
hsdt = b"HSDT" + struct.pack("<II", 1, 1)
hsdt += struct.pack("<4s5I16s", b"\1\2\3\4", 0, len(compressed), 0, 0, 0, bytes(16))
hsdt += bytes(4096-len(hsdt)) + compressed
assert dt.inspect(hsdt)["entries"][0]["board_id_bytes"] == "01020304"
bad_offset = bytearray(image)
struct.pack_into(">I", bad_offset, 36, 63)
for bad in [bytes(bad_offset), image[:-1], image[:-4] + b"bad!", b"unknown"]:
    try:
        dt.inspect(bad)
    except (ValueError, zlib.error):
        pass
    else:
        raise AssertionError("Malformed table accepted")
print("PASS: DT v1/HSDT headers, explicit prefix, bounds, truncation and gzip CRC")
