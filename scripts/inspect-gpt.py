#!/usr/bin/env python3
"""Inspect one explicitly located GPT header/array without printing GUIDs.

Huawei firmware may contain several GPT templates for different storage layouts.
Offsets and logical sector size must be supplied; this tool does not select a
phone layout, validate a backup GPT, resize partitions or write an image.
"""
import argparse
import hashlib
import json
import re
import stat
import struct
import sys
import zlib
from pathlib import Path


def inspect(data, header_offset, entries_offset, sector_bytes):
    if sector_bytes not in (512, 4096):
        raise ValueError("Unsupported logical sector size")

    def region(offset, size):
        if offset < 0 or size < 0 or offset + size > len(data):
            raise ValueError("GPT region exceeds input bounds")
        return data[offset:offset + size]

    values = struct.unpack("<8sIIIIQQQQ16sQIII", region(header_offset, 92))
    (magic, revision, header_size, header_crc, reserved, current_lba,
     backup_lba, first_usable, last_usable, _, entries_lba, count,
     entry_size, entries_crc) = values
    if magic != b"EFI PART" or revision != 0x10000 or reserved:
        raise ValueError("Unsupported GPT header")
    if not 92 <= header_size <= sector_bytes:
        raise ValueError("Invalid GPT header size")
    header = bytearray(region(header_offset, header_size))
    header[16:20] = b"\0" * 4
    if zlib.crc32(header) != header_crc:
        raise ValueError("GPT header CRC mismatch")
    if not 1 <= count <= 4096 or not 128 <= entry_size <= 4096 or entry_size % 128:
        raise ValueError("Invalid partition array dimensions")
    if entries_offset < header_offset + header_size:
        raise ValueError("Partition array overlaps GPT header")
    array = region(entries_offset, count * entry_size)
    if zlib.crc32(array) != entries_crc:
        raise ValueError("GPT partition array CRC mismatch")
    entries = []
    names = set()
    for index in range(count):
        entry = array[index * entry_size:(index + 1) * entry_size]
        if entry[:16] == b"\0" * 16:
            continue
        first, last, attributes = struct.unpack_from("<QQQ", entry, 32)
        name = entry[56:128].decode("utf-16le").split("\0", 1)[0]
        if not re.fullmatch(r"[A-Za-z0-9_.+-]{1,36}", name):
            raise ValueError("Unsupported partition label")
        if name in names:
            raise ValueError("Duplicate partition label")
        names.add(name)
        if last < first or first < first_usable or (last_usable and last > last_usable):
            raise ValueError("Partition lies outside declared usable range")
        entries.append({"entry_number": index + 1, "name": name,
                        "first_lba": first, "last_lba": last,
                        "offset_bytes": first * sector_bytes,
                        "size_bytes": (last - first + 1) * sector_bytes,
                        "attributes": attributes})
    ordered = sorted(entries, key=lambda entry: entry["first_lba"])
    for previous, current in zip(ordered, ordered[1:]):
        if current["first_lba"] <= previous["last_lba"]:
            raise ValueError("Overlapping partitions")
    return {"size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            "header_offset": header_offset, "entries_offset": entries_offset,
            "sector_bytes_supplied": sector_bytes, "header_crc_valid": True,
            "entries_crc_valid": True, "current_lba": current_lba,
            "backup_lba": backup_lba, "first_usable_lba": first_usable,
            "last_usable_lba": last_usable, "entries_lba": entries_lba,
            "entry_slots": count, "entry_size": entry_size, "entries": entries,
            "placeholder_capacity_fields": not backup_lba or not last_usable,
            "limits": ["Explicit offsets and sector size are caller-supplied, not discovered device geometry.",
                       "GUIDs omitted; backup GPT, storage capacity and Huawei signatures not verified.",
                       "CRC validity does not make a firmware template a flash-ready disk image."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--header-offset", type=int, required=True)
    parser.add_argument("--entries-offset", type=int, required=True)
    parser.add_argument("--sector-bytes", type=int, choices=(512, 4096), required=True)
    args = parser.parse_args()
    try:
        metadata = args.image.stat()
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > 16 * 1024 * 1024:
            raise ValueError("Expected a regular offline GPT input at most 16 MiB")
        print(json.dumps(inspect(args.image.read_bytes(), args.header_offset,
                                 args.entries_offset, args.sector_bytes), indent=2))
    except (OSError, ValueError, struct.error) as error:
        print(json.dumps({"error": type(error).__name__ if isinstance(error, OSError)
                          else str(error)}), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
