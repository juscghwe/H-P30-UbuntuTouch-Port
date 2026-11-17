#!/usr/bin/env python3
"""Check GPT CRC failures, malformed dimensions and unsafe partition ranges."""
import importlib.util
import struct
import sys
import zlib
from pathlib import Path

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("gpt", Path(__file__).with_name("inspect-gpt.py"))
gpt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gpt)


def fixture(*, overlap=False, duplicate=False, placeholder=False, huge=False):
    image = bytearray(2048)
    array = bytearray(512)
    for i, (name, first, last) in enumerate([
            ("kernel", 34, 40),
            ("kernel" if duplicate else "userdata", 40 if overlap else 41, 50)]):
        offset = i * 128
        array[offset:offset + 16] = b"\1" * 16
        struct.pack_into("<QQQ", array, offset + 32, first, last, 0)
        encoded = name.encode("utf-16le")
        array[offset + 56:offset + 56 + len(encoded)] = encoded
    image[1024:1536] = array
    header = bytearray(struct.pack("<8sIIIIQQQQ16sQIII", b"EFI PART", 0x10000,
                                  92, 0, 0, 1, 0 if placeholder else 100,
                                  34, 0 if placeholder else 99, b"\2" * 16, 2,
                                  0xffffffff if huge else 4, 128, zlib.crc32(array)))
    struct.pack_into("<I", header, 16, zlib.crc32(header))
    image[512:604] = header
    return image


normal = gpt.inspect(fixture(), 512, 1024, 512)
assert normal["entries"][0]["size_bytes"] == 7 * 512
assert normal["entries"][1]["entry_number"] == 2
assert not normal["placeholder_capacity_fields"]
assert gpt.inspect(fixture(placeholder=True), 512, 1024, 512)["placeholder_capacity_fields"]
assert gpt.inspect(fixture(), 512, 1024, 4096)["entries"][0]["size_bytes"] == 7 * 4096
bad_header = fixture()
bad_header[528] ^= 1
bad_array = fixture()
bad_array[1100] ^= 1
for bad in [bad_header, bad_array, fixture()[:1200], fixture(overlap=True),
            fixture(duplicate=True), fixture(huge=True)]:
    try:
        gpt.inspect(bad, 512, 1024, 512)
    except ValueError:
        pass
    else:
        raise AssertionError("Malformed GPT accepted")
print("PASS: GPT/header CRCs, truncation/dimensions, overlaps, duplicate labels, sector units and placeholders")
