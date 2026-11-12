#!/usr/bin/env python3
"""Inspect saved HSDT/Android DT tables; print numeric fields and hashes only.

Android v1 compression follows AOSP libufdt dt_table.h. HSDT fields follow
WerWolv/ImHex-Patterns patterns/hsdt.hexpat at 8db011b6e563686c9476a3261141ddba3831852f.
No verification field is changed and no authentication/signature claim is made.
"""
import argparse
import hashlib
import json
from pathlib import Path
import stat
import struct
import zlib


def fdt_header(data):
    if len(data) < 40:
        raise ValueError("Short FDT")
    magic, total, structure, strings, reserve, version, compatible, _, strings_size, structure_size = struct.unpack_from(">10I", data)
    if (magic != 0xd00dfeed or total < 40 or total > len(data) or version < 17 or compatible > 17
            or min(structure, strings, reserve) < 40 or reserve % 8
            or structure + structure_size > total or strings + strings_size > total
            or reserve + 16 > total):
        raise ValueError("Invalid FDT header/bounds")
    return {"total_size": total, "version": version}


def expand(data, compression):
    if compression == 0:
        return data, len(data)
    if compression not in (1, 2):
        raise ValueError("Unsupported compression")
    decoder = zlib.decompressobj(15 if compression == 1 else 31)
    output = decoder.decompress(data, 8 * 1024 * 1024)
    if not decoder.eof:
        raise ValueError("Truncated or oversized compressed FDT")
    return output, len(data) - len(decoder.unused_data)


def inspect(data, base=0):
    if base < 0 or base + 12 > len(data):
        raise ValueError("Invalid table offset")
    entries = []
    if data[base:base+4] == b"HSDT":
        _, version, count = struct.unpack_from("<4sII", data, base)
        if version != 1 or count > 4096 or base + 12 + count * 40 > len(data):
            raise ValueError("Invalid HSDT table")
        for i in range(count):
            board, unknown, length, verification_length, offset, verification_offset, _ = struct.unpack_from(
                "<4s5I16s", data, base + 12 + i * 40)
            entries.append({"index": i, "board_id_bytes": board.hex(),
                            "unknown_field": unknown, "length_field": length,
                            "verification_length_field": verification_length,
                            "verification_offset_field": verification_offset,
                            "payload_offset": base + 4096 + offset, "compression": 2})
        kind = "hsdt"
    else:
        if base + 32 > len(data):
            raise ValueError("Short DT table")
        magic, total, header, entry_size, count, table_offset, _, version = struct.unpack_from(">8I", data, base)
        table_end = table_offset + count * entry_size
        if (magic != 0xd7b7ab1e or version not in (0, 1) or header < 32 or entry_size < 32
                or count > 4096 or table_offset < header or table_end > total or base + total > len(data)):
            raise ValueError("Invalid Android DT table")
        for i in range(count):
            length, offset, ident, rev, flags, *_ = struct.unpack_from(">8I", data, base + table_offset + i * entry_size)
            if offset < table_end or offset + length > total:
                raise ValueError("DT entry overlaps table or exceeds bounds")
            entries.append({"index": i, "id": ident, "revision": rev,
                            "flags": flags if version == 1 else 0, "length_field": length,
                            "payload_offset": base + offset, "compression": flags & 15 if version == 1 else 0})
        kind = "android-dt-table"
    for entry in entries:
        start, size = entry["payload_offset"], entry["length_field"]
        minimum = base + 12 + count * 40 if kind == "hsdt" else base
        if start < minimum or start + size > len(data):
            raise ValueError("Compressed entry exceeds image bounds")
        payload = data[start:start+size]
        decoded, consumed = expand(payload, entry["compression"])
        entry.update(compressed_sha256=hashlib.sha256(payload).hexdigest(),
                     compressed_bytes_consumed=consumed, trailing_bytes=size-consumed,
                     expanded_bytes=len(decoded), expanded_sha256=hashlib.sha256(decoded).hexdigest(),
                     fdt=fdt_header(decoded))
    return {"format": kind, "table_offset": base, "version": version,
            "entry_count": count, "entries": entries,
            "size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            "signatures_verified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--offset", type=int, default=0, help="Explicit uninterpreted prefix length")
    args = parser.parse_args()
    source_stat = args.image.stat()
    if not stat.S_ISREG(source_stat.st_mode):
        parser.error("Input must be a regular offline file")
    if source_stat.st_size > 512 * 1024 * 1024:
        parser.error("Image exceeds inspection limit")
    print(json.dumps(inspect(args.image.read_bytes(), args.offset), indent=2))


if __name__ == "__main__":
    main()
