#!/usr/bin/env python3
"""Check evidence JSON, checksum inventories and local Markdown links at a revision."""
import argparse
import hashlib
import json
import posixpath
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("revision", nargs="?", help="Git revision; default: working tree")
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
if args.revision:
    def git(*items):
        return subprocess.check_output(["git", "-C", str(root), *items])
    names = git("ls-tree", "-rz", "--name-only", args.revision).decode().split("\0")
    files = {name: git("show", f"{args.revision}:{name}") for name in names if name}
else:
    files = {str(p.relative_to(root)): p.read_bytes()
             for p in root.rglob("*") if p.is_file() and ".git" not in p.relative_to(root).parts}

for name, data in files.items():
    parent = posixpath.dirname(name)
    if name.startswith("findings/") and name.endswith(".json"):
        json.loads(data)
    if posixpath.basename(name) == "SHA256SUMS":
        listed = set()
        for line in data.decode().splitlines():
            digest, target = line.split("  ", 1)
            target = posixpath.normpath(posixpath.join(parent, target))
            assert target in files, f"Missing checksum target: {target}"
            assert hashlib.sha256(files[target]).hexdigest() == digest, f"Hash mismatch: {target}"
            listed.add(target)
        expected = {p for p in files if posixpath.dirname(p) == parent and p != name}
        assert listed == expected, f"Incomplete checksum inventory: {name}"
    if name.endswith(".md"):
        for link in re.findall(r"\]\(([^)]+)\)", data.decode()):
            if urlsplit(link).scheme or link.startswith("#"):
                continue
            target = posixpath.normpath(posixpath.join(parent, unquote(link.split("#")[0])))
            assert target in files, f"Broken link in {name}: {link}"

stock = files["findings/raw/2026-11-11/08-stock-kernel.config"]
assert hashlib.sha256(stock).hexdigest() == "16623939098e19212e0f66b9117a45f3e8bf1f05d4ccb00138a1a372d11ccc5b", "Stock configuration changed"
print(f"PASS: {args.revision or 'working tree'}: JSON, inventories, local links, stock config")
