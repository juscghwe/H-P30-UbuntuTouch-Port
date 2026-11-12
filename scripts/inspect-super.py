#!/usr/bin/env python3
"""Inspect sparse Android SUPER metadata and extract an offline logical partition.

Uses AOSP Android 10 libsparse/liblp layouts at system/core commit
5aa0e4241029c80617a8e98b07f7f48ab6b3a3d7. Operates on regular files only.
Sparse holes are modeled as zero. No mounts, phone access or firmware execution.
"""
import argparse
import bisect
import hashlib
import json
from pathlib import Path
import re
import stat
import struct


class SparseView:

    def __init__(self, stream, offset, size):
        self.stream, self.base, self.input_size = (stream, offset, size)
        header = self.input_read(0, 28)
        magic, major, minor, fh, ch, block, blocks, count, checksum = struct.unpack('<I4H4I', header)
        if magic != 0xed26ff3a or (major, minor) != (1, 0) or fh < 28 or (ch < 12) or block % 4 or (block == 0) or (count > 1000000) or (count * ch > size - fh):
            raise ValueError('Invalid sparse header')
        if checksum:
            raise ValueError('Sparse image CRC verification is not implemented; refusing nonzero CRC')
        self.size = block * blocks
        self.chunks, self.starts = ([], [])
        position, logical = (fh, 0)
        counts = {}
        for i in range(count):
            typ, _, chunk_blocks, chunk_size = struct.unpack('<HHII', self.input_read(position, 12))
            expanded = chunk_blocks * block
            data_size = chunk_size - ch
            if chunk_size < ch or position + chunk_size > size:
                raise ValueError('Sparse chunk outside input')
            if logical + expanded > self.size:
                raise ValueError('Sparse chunk exceeds expanded image bounds')
            counts[hex(typ)] = counts.get(hex(typ), 0) + 1
            payload = position + ch
            if typ == 0xcac1:
                if data_size != expanded:
                    raise ValueError('Raw size')
                fill = None
            elif typ == 0xcac2:
                if data_size != 4:
                    raise ValueError('Fill size')
                fill = self.input_read(payload, 4)
            elif typ == 0xcac3:
                if data_size != 0:
                    raise ValueError('Hole size')
                fill = b'\x00' * 4
            elif typ == 0xcac4:
                raise ValueError('Sparse CRC chunks are not supported; refusing unchecked CRC')
            else:
                raise ValueError('Unknown sparse chunk')
            if expanded:
                self.starts.append(logical)
                self.chunks.append((logical, expanded, payload, fill))
                logical += expanded
            position += chunk_size
        if logical != self.size or position != size:
            raise ValueError('Sparse total mismatch')
        self.summary = {'version': [major, minor], 'block_size': block, 'blocks': blocks, 'chunk_count': count, 'chunk_types': counts, 'expanded_bytes': self.size, 'image_crc32_field': checksum, 'image_crc32_verified': False}
        if not self.chunks:
            raise ValueError('Sparse image contains no logical data')

    def input_read(self, offset, size):
        if offset < 0 or size < 0 or offset + size > self.input_size:
            raise ValueError('Input read bounds')
        self.stream.seek(self.base + offset)
        data = self.stream.read(size)
        if len(data) != size:
            raise ValueError('Short input')
        return data

    def read(self, offset, size):
        if offset < 0 or size < 0 or offset + size > self.size:
            raise ValueError('Logical read bounds')
        out = []
        while size:
            index = bisect.bisect_right(self.starts, offset) - 1
            start, length, physical, fill = self.chunks[index]
            take = min(size, start + length - offset)
            if fill is None:
                out.append(self.input_read(physical + offset - start, take))
            else:
                phase = (offset - start) % 4
                out.append((fill * ((take + phase + 3) // 4))[phase:phase + take])
            offset += take
            size -= take
        return b''.join(out)

def checked_sha(data, start, size):
    expected = data[start:start + size]
    modified = data[:start] + bytes(size) + data[start + size:]
    if hashlib.sha256(modified).digest() != expected:
        raise ValueError('Metadata SHA-256 mismatch')

def metadata(view):
    geometries = [view.read(offset, 4096) for offset in [4096, 8192]]
    for geometry in geometries:
        magic, size = struct.unpack_from('<II', geometry)
        if magic != 0x616c4467 or size != 52:
            raise ValueError('Geometry header')
        checked_sha(geometry[:size], 8, 32)
    if geometries[0] != geometries[1]:
        raise ValueError('Geometry copies differ')
    maximum, slots, logical_block = struct.unpack_from('<III', geometries[0], 40)
    if maximum < 128 or maximum % 512 or maximum > 1024 * 1024 or (not 1 <= slots <= 8) or (logical_block < 512) or logical_block % 512:
        raise ValueError('Geometry bounds')
    results = []
    for slot in range(slots):
        raw = view.read(12288 + slot * maximum, maximum)
        magic, major, minor, hs = struct.unpack_from('<IHHI', raw)
        if magic != 0x414c5030 or (major, minor) != (10, 0) or hs != 128:
            raise ValueError(('LP header', magic, major, minor, hs))
        checked_sha(raw[:hs], 12, 32)
        ts = struct.unpack_from('<I', raw, 44)[0]
        if hs + ts > maximum:
            raise ValueError('Tables exceed slot')
        tables = raw[hs:hs + ts]
        if hashlib.sha256(tables).digest() != raw[48:80]:
            raise ValueError('Tables SHA')
        descriptors = [struct.unpack_from('<III', raw, off) for off in [80, 92, 104, 116]]
        for off, count, entry_size in descriptors:
            if off + count * entry_size > ts:
                raise ValueError('Table bounds')
        table_ranges = sorted((off, off + count * entry_size) for off, count, entry_size in descriptors if count)
        table_position = 0
        for start, end in table_ranges:
            if start != table_position:
                raise ValueError('Overlapping or noncontiguous metadata tables')
            table_position = end
        if table_position != ts:
            raise ValueError('Unexpected metadata table bytes')
        po, pc, ps = descriptors[0]
        eo, ec, es = descriptors[1]
        go, gc, gs = descriptors[2]
        bo, bc, bs = descriptors[3]
        if (ps, es, gs, bs) != (52, 24, 48, 64) or bc != 1:
            raise ValueError('Unsupported record sizes/device count')
        extents = [dict(zip(['sectors', 'type', 'target_sector', 'source'], struct.unpack_from('<QIQI', tables, eo + i * es))) for i in range(ec)]
        devices = []
        for i in range(bc):
            pos = bo + i * bs
            first, align, alignoff, ds = struct.unpack_from('<QIIQ', tables, pos)
            name = tables[pos + 24:pos + 60].split(b'\x00')[0].decode('ascii')
            devices.append({'name': name, 'first_logical_sector': first, 'size_bytes': ds})
        if devices[0]['size_bytes'] != view.size or devices[0]['first_logical_sector'] * 512 < 12288 + 2 * slots * maximum:
            raise ValueError('Unsupported block-device size or metadata overlap')
        parts = []
        for i in range(pc):
            pos = po + i * ps
            name = tables[pos:pos + 36].split(b'\x00')[0].decode('ascii')
            attrs, first, count, group = struct.unpack_from('<4I', tables, pos + 36)
            if not re.fullmatch('[A-Za-z0-9_]{1,36}', name) or any((p['name'] == name for p in parts)):
                raise ValueError('Invalid or duplicate logical partition name')
            if first + count > ec or group >= gc:
                raise ValueError('Partition indices')
            own = extents[first:first + count]
            for extent in own:
                if extent['type'] == 0:
                    if extent['source'] != 0 or extent['target_sector'] < devices[0]['first_logical_sector'] or extent['target_sector'] * 512 + extent['sectors'] * 512 > min(view.size, devices[0]['size_bytes']):
                        raise ValueError('Unsupported/out-of-range physical extent')
                elif extent['type'] != 1 or extent['source'] != 0 or extent['target_sector'] != 0:
                    raise ValueError('Unsupported extent type/zero target')
            parts.append({'name': name, 'attributes': attrs, 'size_bytes': sum((e['sectors'] * 512 for e in own)), 'extents': own})
        backup = view.read(12288 + (slots + slot) * maximum, maximum)
        results.append({'slot': slot, 'header_version': [major, minor], 'header_sha256_valid': True, 'tables_sha256_valid': True, 'primary_backup_bytes_equal': raw == backup, 'block_devices': devices, 'partitions': parts})
    return {'metadata_max_size': maximum, 'slot_count': slots, 'logical_block_size': logical_block, 'geometry_sha256_valid': True, 'geometry_copies_equal': True, 'slots': results}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--offset', type=int, default=0, help='Sparse record offset in an enclosing file')
    parser.add_argument('--length', type=int, help='Sparse record length; default: remainder of file')
    parser.add_argument('--extract-partition', help='Exact logical partition name; no suffix inference')
    parser.add_argument('--output', type=Path, help='New regular image file outside this repository')
    parser.add_argument('--slot', type=int, default=0, help='Metadata slot; no live boot-slot inference')
    args = parser.parse_args()
    initial = args.image.stat()
    if not stat.S_ISREG(initial.st_mode):
        parser.error('Input must be a regular offline file')
    length = args.length if args.length is not None else initial.st_size - args.offset
    if args.offset < 0 or length <= 0 or args.offset + length > initial.st_size:
        parser.error('Invalid sparse input region')
    if bool(args.extract_partition) != bool(args.output):
        parser.error('--extract-partition and --output must be supplied together')
    if args.output and args.output.resolve().is_relative_to(Path(__file__).resolve().parents[1]):
        parser.error('Proprietary image output must remain outside the repository')
    with args.image.open('rb') as stream:
        view = SparseView(stream, args.offset, length)
        meta = metadata(view)
        if not 0 <= args.slot < meta['slot_count']:
            parser.error('Metadata slot outside recorded geometry')
        sha = hashlib.sha256()
        stream.seek(args.offset)
        remaining = length
        while remaining:
            block = stream.read(min(remaining, 4 * 1024 * 1024))
            if not block:
                raise ValueError('Source truncated during hashing')
            sha.update(block)
            remaining -= len(block)
        result = {'input_offset': args.offset, 'input_length': length, 'input_region_sha256': sha.hexdigest(), 'sparse': view.summary, 'logical_metadata': meta, 'firmware_signatures_verified': False}
        if args.extract_partition:
            selected = [p for p in meta['slots'][args.slot]['partitions'] if p['name'] == args.extract_partition]
            if len(selected) != 1:
                parser.error('Requested partition must match exactly once')
            part = selected[0]
            extracted_sha = hashlib.sha256()
            written = 0
            with args.output.open('xb') as output:
                for extent in part['extents']:
                    position = extent['target_sector'] * 512
                    remaining = extent['sectors'] * 512
                    while remaining:
                        count = min(remaining, 4 * 1024 * 1024)
                        data = view.read(position, count) if extent['type'] == 0 else bytes(count)
                        output.write(data)
                        extracted_sha.update(data)
                        remaining -= count
                        written += count
                        position += count
            if written != part['size_bytes']:
                raise ValueError('Extracted length mismatch')
            result['extracted_partition'] = {'name': part['name'], 'slot': args.slot, 'size_bytes': written, 'sha256': extracted_sha.hexdigest()}
    final = args.image.stat()
    if (initial.st_size, initial.st_mtime_ns) != (final.st_size, final.st_mtime_ns):
        raise ValueError('Source changed during inspection')
    print(json.dumps(result, indent=2))
if __name__ == '__main__':
    main()
