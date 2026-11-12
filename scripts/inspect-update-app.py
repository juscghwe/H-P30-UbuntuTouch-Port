#!/usr/bin/env python3
"""Inventory Huawei UPDATE.APP records and optionally copy selected images offline.

The 98-byte header layout is described by marcominetti/split_updata.pl's
data_structure at 7f3182406cb0deec612fd6795af5b578de1c7c6b. This implementation
checks bounds; it does not verify Huawei signatures or per-record checksums.
"""
import argparse
import hashlib
import json
import re
import stat
import struct
from pathlib import Path

MAGIC = b"\x55\xaa\x5a\xa5"
HEADER_SIZE = 98


def inventory(stream, total_size):
    stream.seek(0)
    prefix = stream.read(min(total_size, 1024 * 1024))
    position = prefix.find(MAGIC)
    if position < 0 or any(prefix[:position]):
        raise ValueError("Expected an UPDATE.APP header after an optional zero preamble")
    preamble = position
    entries = []
    while position < total_size:
        if len(entries) >= 4096:
            raise ValueError("Too many records")
        stream.seek(position)
        header = stream.read(HEADER_SIZE)
        if header[:4] != MAGIC:
            # Accept only a short zero trailer; do not search inside payloads.
            remaining = total_size - position
            if remaining <= 4096:
                stream.seek(position)
                if not any(stream.read(remaining)):
                    break
            raise ValueError("Unexpected data after an aligned record")
        if len(header) != HEADER_SIZE:
            raise ValueError("Truncated record header")
        header_size = struct.unpack_from("<I", header, 4)[0]
        payload_size = struct.unpack_from("<I", header, 24)[0]
        name = header[60:76].split(b"\0", 1)[0].decode("ascii")
        if not re.fullmatch(r"[A-Za-z0-9_.-]{1,16}", name):
            raise ValueError("Unsupported record name")
        if header_size < HEADER_SIZE or header_size > 16 * 1024 * 1024:
            raise ValueError("Invalid record header size")
        payload_offset = position + header_size
        end = payload_offset + payload_size
        if end > total_size:
            raise ValueError("Record exceeds input bounds")
        entries.append({"name": name, "header_offset": position,
                        "header_size": header_size, "payload_offset": payload_offset,
                        "size_bytes": payload_size})
        position = (end + 3) & ~3
        if end < min(position, total_size):
            stream.seek(end)
            if any(stream.read(min(position, total_size) - end)):
                raise ValueError("Nonzero alignment padding")
    if not entries:
        raise ValueError("No records")
    return {"preamble_bytes": preamble, "entries": entries}


def digest(stream):
    stream.seek(0)
    sha = hashlib.sha256()
    while block := stream.read(4 * 1024 * 1024):
        sha.update(block)
    return sha.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--extract", action="append", default=[], help="Exact record name; repeatable")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if not stat.S_ISREG(args.image.stat().st_mode):
        parser.error("Input must be a regular offline file")
    if args.extract and args.output_dir is None:
        parser.error("--extract requires --output-dir outside this repository")
    if args.output_dir:
        if args.output_dir.resolve().is_relative_to(Path(__file__).resolve().parents[1]):
            parser.error("Proprietary image output must remain outside the repository")
    with args.image.open("rb") as stream:
        result = inventory(stream, args.image.stat().st_size)
        result.update(size_bytes=args.image.stat().st_size, sha256=digest(stream),
                      record_checksums_verified=False, huawei_signatures_verified=False)
        for name in args.extract:
            matched = [r for r in result["entries"] if r["name"] == name]
            if len(matched) != 1:
                parser.error("Each requested record must match exactly once")
        for name in args.extract:
            record = next(r for r in result["entries"] if r["name"] == name)
            args.output_dir.mkdir(parents=True, exist_ok=True)
            # Names were validated above; exclusive creation preserves existing evidence.
            target = args.output_dir / (name + ".img")
            stream.seek(record["payload_offset"])
            sha = hashlib.sha256()
            remaining = record["size_bytes"]
            with target.open("xb") as output:
                while remaining:
                    block = stream.read(min(remaining, 4 * 1024 * 1024))
                    if not block:
                        raise ValueError("Source truncated during extraction")
                    output.write(block)
                    sha.update(block)
                    remaining -= len(block)
            record["extracted_sha256"] = sha.hexdigest()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
