#!/usr/bin/env python3
"""Inspect image hashes and numeric headers without extracting data or printing identifiers.

Recognizes Android boot headers v0-v2, Android DT tables v0, and FDT headers.
No image is changed. Boot command lines, image names and DT properties are omitted.
"""
import argparse
import hashlib
import json
import stat
import struct
import sys
from pathlib import Path


def inspect(path):
    with path.open("rb") as stream:
        initial = path.stat()
        if not stat.S_ISREG(initial.st_mode):
            raise ValueError("Input must be a regular image file")
        length = initial.st_size

        def read(offset, size):
            if offset < 0 or size < 0 or offset + size > length:
                raise ValueError("Header or region exceeds image size")
            stream.seek(offset)
            data = stream.read(size)
            if len(data) != size:
                raise ValueError("Truncated image")
            return data

        def digest(offset, size):
            if offset < 0 or size < 0 or offset + size > length:
                raise ValueError("Region exceeds image size")
            stream.seek(offset)
            sha = hashlib.sha256()
            while size:
                block = stream.read(min(size, 1024 * 1024))
                if not block:
                    raise ValueError("Truncated image")
                sha.update(block)
                size -= len(block)
            return sha.hexdigest()

        result = {"size_bytes": length, "sha256": digest(0, length), "format": "unrecognized"}

        def region(name, offset, size):
            return {"name": name, "offset": offset, "size": size,
                    "sha256": digest(offset, size)}

        def fdt(offset, available):
            values = struct.unpack(">10I", read(offset, 40))
            magic, total, structure, strings, reserve, version, compatible, _, string_size, structure_size = values
            if magic != 0xD00DFEED or total < 40 or total > available:
                raise ValueError("Invalid FDT size or magic")
            if version < 17 or compatible > 17:
                raise ValueError("Unsupported FDT header version")
            if (structure < 40 or strings < 40 or reserve < 40 or reserve % 8
                    or structure + structure_size > total or strings + string_size > total
                    or reserve + 16 > total):
                raise ValueError("Invalid FDT section bounds")
            return {"total_size": total, "version": version,
                    "structure_offset": structure, "structure_size": structure_size,
                    "strings_offset": strings, "strings_size": string_size}

        magic = read(0, min(length, 8))
        if magic == b"ANDROID!":
            fields = struct.unpack("<10I", read(8, 40))
            kernel_size, kernel_addr, ramdisk_size, ramdisk_addr, second_size, second_addr, tags_addr, page, version, os_version = fields
            result.update(format="android-boot", header_version=version)
            if version > 2:
                result["layout"] = "unsupported header version; no offsets inferred"
            else:
                header_size = (1632, 1648, 1660)[version]
                read(0, header_size)
                if page < header_size or page > length or page & (page - 1):
                    raise ValueError("Invalid Android boot page size")
                align = lambda value: (value + page - 1) // page * page
                offsets = [page, align(page + kernel_size)]
                offsets.append(align(offsets[1] + ramdisk_size))
                regions = [region(name, offset, size) for name, offset, size in zip(
                    ("kernel", "ramdisk", "second"), offsets,
                    (kernel_size, ramdisk_size, second_size)) if size]
                end = align(offsets[2] + second_size)
                if version >= 1:
                    recovery_size, recovery_offset, declared_header_size = struct.unpack("<IQI", read(1632, 16))
                    if declared_header_size != header_size:
                        raise ValueError("Android boot header size disagrees with version")
                    if recovery_size:
                        if recovery_offset < end or recovery_offset % page:
                            raise ValueError("Invalid recovery DTBO offset")
                        regions.append(region("recovery_dtbo", recovery_offset, recovery_size))
                        end = align(recovery_offset + recovery_size)
                if version == 2:
                    dtb_size, dtb_addr = struct.unpack("<IQ", read(1648, 12))
                    result["dtb_load_address"] = dtb_addr
                    if dtb_size:
                        regions.append(region("dtb", end, dtb_size))
                result.update(page_size=page, os_version_encoded=os_version,
                              load_addresses={"kernel": kernel_addr, "ramdisk": ramdisk_addr,
                                              "second": second_addr, "tags": tags_addr}, regions=regions)
        elif magic[:4] == bytes.fromhex("d7b7ab1e"):
            _, total, header_size, entry_size, count, entries_offset, page, version = struct.unpack(">8I", read(0, 32))
            if (version != 0 or header_size < 32 or total > length or total < header_size
                    or entry_size < 32 or entries_offset < header_size
                    or entries_offset + count * entry_size > total):
                raise ValueError("Invalid or unsupported Android DT table")
            entries = []
            table_end = entries_offset + count * entry_size
            for index in range(count):
                size, offset = struct.unpack(">2I", read(entries_offset + index * entry_size, 8))
                if offset < table_end or offset + size > total:
                    raise ValueError("DT entry overlaps table or exceeds table size")
                entry = region(str(index), offset, size)
                entry["fdt"] = fdt(offset, size)
                entries.append(entry)
            result.update(format="android-dt-table", version=version, total_size=total,
                          page_size=page, entry_count=count, entries=entries)
        elif magic[:4] == bytes.fromhex("d00dfeed"):
            result.update(format="fdt", header=fdt(0, length))
        final = path.stat()
        if (initial.st_size, initial.st_mtime_ns) != (final.st_size, final.st_mtime_ns):
            raise ValueError("Image changed during inspection")
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(inspect(args.image), indent=2))
    except (OSError, ValueError, struct.error) as error:
        # OSError may include a private path; return only its class.
        message = type(error).__name__ if isinstance(error, OSError) else str(error)
        print(json.dumps({"error": message}), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
