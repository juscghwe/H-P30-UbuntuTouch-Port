#!/usr/bin/env python3
"""Compare explicit kernel config values; optionally locate source definitions."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def read_config(path):
    values = {}
    for line in path.read_text().splitlines():
        match = re.fullmatch(r"(CONFIG_\w+)=(.*)", line)
        unset = re.fullmatch(r"# (CONFIG_\w+) is not set", line)
        if not (match or unset):
            continue
        name, value = match.groups() if match else (unset[1], "n")
        if name in values:
            raise ValueError(f"Duplicate symbol {name} in {path.name}")
        values[name] = value
    return values


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("stock", type=Path)
parser.add_argument("candidate", type=Path)
parser.add_argument("--source", type=Path, help="Search Kconfig definitions without evaluating dependencies")
args = parser.parse_args()
stock, candidate = read_config(args.stock), read_config(args.candidate)
shared = stock.keys() & candidate.keys()
result = {
    "method": "Literal explicit values; absent symbols are not disabled values. Definition search does not evaluate dependencies or prove active hardware.",
    "stock_sha256": hashlib.sha256(args.stock.read_bytes()).hexdigest(),
    "candidate_sha256": hashlib.sha256(args.candidate.read_bytes()).hexdigest(),
    "stock_symbols": len(stock), "candidate_symbols": len(candidate),
    "common_symbols": len(shared),
    "equal_common_symbols": sum(stock[k] == candidate[k] for k in shared),
    "differences": [{"symbol": k, "stock": stock[k], "candidate": candidate[k]}
                    for k in sorted(shared) if stock[k] != candidate[k]],
    "stock_only": [{"symbol": k, "stock": stock[k]} for k in sorted(stock.keys() - candidate.keys())],
    "candidate_only": [{"symbol": k, "candidate": candidate[k]} for k in sorted(candidate.keys() - stock.keys())],
}
if args.source:
    definitions = {}
    for path in sorted(args.source.rglob("Kconfig*")):
        if not path.is_file() or path.is_symlink():
            continue
        for line_number, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
            match = re.fullmatch(r"\s*(?:menu)?config\s+(\w+)\s*", line)
            if match:
                definitions.setdefault("CONFIG_" + match[1], []).append({
                    "path": str(path.relative_to(args.source)), "line": line_number})
    for entry in result["stock_only"] + result["differences"]:
        entry["definitions"] = definitions.get(entry["symbol"], [])
print(json.dumps(result, indent=2))
