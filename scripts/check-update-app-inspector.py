#!/usr/bin/env python3
"""Check UPDATE.APP bounds and alignment with independent synthetic records."""
import importlib.util
import io
from pathlib import Path
import struct
import sys

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location(
    "inspector", Path(__file__).with_name("inspect-update-app.py"))
inspector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inspector)


def record(name, payload):
    header = bytearray(98)
    header[:4] = b"\x55\xaa\x5a\xa5"
    struct.pack_into("<I", header, 4, 98)
    struct.pack_into("<I", header, 24, len(payload))
    header[60:60+len(name)] = name.encode()
    data = bytes(header) + payload
    return data + b"\0" * (-len(data) % 4)


data = b"\0" * 92 + record("DTS", b"example") + record("KERNEL", b"test")
result = inspector.inventory(io.BytesIO(data), len(data))
assert result["preamble_bytes"] == 92
assert [(e["name"], e["size_bytes"]) for e in result["entries"]] == [("DTS", 7), ("KERNEL", 4)]
for bad in [b"", b"random", data[:-5], data + b"bad trailer", record("../escape", b"x")]:
    try:
        inspector.inventory(io.BytesIO(bad), len(bad))
    except (ValueError, UnicodeDecodeError):
        pass
    else:
        raise AssertionError("Malformed record accepted")
print("PASS: header/payload bounds, preamble/alignment, truncation and record names")
