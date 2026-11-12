#!/usr/bin/env python3
"""Decode a saved FirmFinder catalog as data; never execute its website scripts."""
import argparse
import hashlib
import json
from pathlib import Path

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
RESET_CODE = (1 << 18) - 1
MAX_INPUT = 16 * 1024 * 1024
MAX_OUTPUT = 64 * 1024 * 1024


def decode_payload(raw, reset_code=RESET_CODE):
    """Three little-endian sextets/code; resettable LZW; reverse +24 character shift."""
    if len(raw) > MAX_INPUT:
        raise ValueError("Catalog exceeds input limit")
    text = raw.decode("ascii").strip()
    if not text or len(text) % 3:
        raise ValueError("Expected a nonempty sequence of three-character codes")
    values = {c: i for i, c in enumerate(ALPHABET)}
    block_length = reset_code - 256
    if block_length <= 0:
        raise ValueError("Invalid dictionary reset code")
    output = []
    output_length = 0
    dictionary = {}
    previous = ""
    for index, pos in enumerate(range(0, len(text), 3)):
        try:
            code = sum(values[c] << (6 * j) for j, c in enumerate(text[pos:pos+3]))
        except KeyError as exc:
            raise ValueError("Invalid catalog alphabet") from exc
        if index % block_length == 0:
            dictionary = {i: chr(i) for i in range(256)}
            if code >= 256:
                raise ValueError("A dictionary block must start with a literal")
            entry = chr(code)
        else:
            entry = dictionary.get(code)
            if entry is None:
                if code != len(dictionary):
                    raise ValueError("Invalid LZW code")
                entry = previous + previous[0]
            dictionary[len(dictionary)] = previous + entry[0]
        output_length += len(entry)
        if output_length > MAX_OUTPUT:
            raise ValueError("Decoded catalog exceeds output limit")
        output.append(entry)
        previous = entry
    return "".join(chr((ord(c) - 24) % 65536) for piece in output for c in piece)


def select_rows(rows, model=None, customization=None, versions=()):
    selected = []
    for row in rows:
        if not isinstance(row, list) or len(row) < 4:
            raise ValueError("Unexpected catalog row schema")
        # Root/BaseArchive/Downgrade use [id, model-region, vendor, version, url, date].
        # v2 uses [model, region-vendor, component tuple, compatibility tuples, ...].
        if isinstance(row[0], int):
            row_model, _, row_region = row[1].partition(" - ")
            row_versions = [row[3]]
        else:
            row_model = row[0]
            row_region = row[1].split(" - ")[0]
            row_versions = row[2]
        if model and row_model != model:
            continue
        if customization and row_region != customization:
            continue
        if versions and not any(v in item.split() for v in versions for item in row_versions):
            continue
        selected.append(row)
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", type=Path)
    parser.add_argument("--model")
    parser.add_argument("--customization")
    parser.add_argument("--version", action="append", default=[])
    args = parser.parse_args()
    raw = args.catalog.read_bytes()
    decoded = decode_payload(raw)
    rows = json.loads(decoded)
    result = {
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "decoded_sha256": hashlib.sha256(decoded.encode()).hexdigest(),
        "row_count": len(rows),
        "selected_rows": select_rows(rows, args.model, args.customization, args.version),
        "classification": "Third-party catalog observations, not verified device compatibility",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
