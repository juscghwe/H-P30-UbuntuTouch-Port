#!/usr/bin/env python3
"""Exercise literal, self-reference, reset-boundary and malformed catalog codes."""
import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location(
    "catalog", Path(__file__).with_name("inspect-firmfinder-catalog.py"))
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)


def pack(codes):
    return "".join(catalog.ALPHABET[(n >> shift) & 63]
                   for n in codes for shift in (0, 6, 12)).encode()


# Independent, explicit LZW codes after the character shift: '[' becomes 115.
assert catalog.decode_payload(b"zBAzBA1BA1BA") == "[[]]"
assert catalog.decode_payload(pack([89, 90, 256, 258])) == "ABABABA"
# Four emitted codes per dictionary block for this deliberately tiny limit.
assert catalog.decode_payload(pack([89, 90, 256, 258, 91, 92]), reset_code=260) == "ABABABACD"
for raw in [b"", b"ab", b"???", pack([256]), pack([89, 999])]:
    try:
        catalog.decode_payload(raw)
    except ValueError:
        pass
    else:
        raise AssertionError("Malformed input accepted")
rows = [[1, "MAR-L21A - C431", "hw-eea", "MAR-LGRP2-OVS 10.0.0.275", "url", "date"],
        [2, "MAR-L21A - C432", "hw-eu", "MAR-LGRP2-OVS 10.0.0.275", "url", "date"]]
assert catalog.select_rows(rows, "MAR-L21A", "C431", ["10.0.0.275"]) == rows[:1]
assert catalog.select_rows(rows, versions=["10.0.0.27"]) == []
print("PASS: literal/LZW/reset decoding, malformed inputs and exact field selection")
