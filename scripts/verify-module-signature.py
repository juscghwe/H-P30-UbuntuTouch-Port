#!/usr/bin/env python3
"""Verify a regular, uncompressed module against an explicit public certificate.

Requires OpenSSL 3. Does not load modules or evaluate kernel ABI compatibility.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('module', type=Path)
    parser.add_argument('certificate', type=Path, help='Public X.509 certificate, DER or PEM; never a private key')
    args = parser.parse_args()
    if not args.module.is_file() or not args.certificate.is_file():
        raise ValueError('Inputs must be regular files')
    data = args.module.read_bytes()
    cert = args.certificate.read_bytes()
    if b'PRIVATE KEY' in cert:
        raise ValueError('Supply only the public certificate')
    magic = b'~Module signature appended~\n'
    if len(data) < len(magic) + 12 or not data.endswith(magic):
        raise ValueError('No supported module signature trailer')
    trailer = len(data) - len(magic) - 12
    algo, digest, kind, signer, key, padding, size = struct.unpack('>5B3sI', data[trailer:trailer + 12])
    if (algo, digest, kind, signer, key, padding) != (0, 0, 2, 0, 0, b'\0' * 3):
        raise ValueError('Unsupported signature trailer fields')
    if not 0 < size < trailer:
        raise ValueError('Invalid signature bounds')
    payload, signature = data[:trailer - size], data[trailer - size:trailer]
    if len(payload) < 64 or payload[:6] != b'\x7fELF\x02\x01':
        raise ValueError('Expected uncompressed little-endian ELF64')
    if struct.unpack_from('<HH', payload, 16) != (1, 183):
        raise ValueError('Expected AArch64 relocatable ELF')
    with tempfile.TemporaryDirectory(prefix='module-signature-') as directory:
        scratch = Path(directory)
        body, sig, pem = (scratch / name for name in ('payload', 'signature.der', 'certificate.pem'))
        body.write_bytes(payload)
        sig.write_bytes(signature)
        fmt = 'PEM' if b'-----BEGIN CERTIFICATE-----' in cert else 'DER'
        subprocess.run(['openssl', 'x509', '-inform', fmt, '-in', str(args.certificate),
                        '-out', str(pem)], check=True, capture_output=True)
        subprocess.run(['openssl', 'cms', '-verify', '-binary', '-inform', 'DER',
                        '-in', str(sig), '-content', str(body), '-certfile', str(pem),
                        '-nointern', '-CAfile', str(pem), '-no-CApath', '-no-CAstore',
                        '-purpose', 'any', '-out', '/dev/null'], check=True, capture_output=True)
    print(json.dumps({
        'module_sha256': hashlib.sha256(data).hexdigest(),
        'certificate_file_sha256': hashlib.sha256(cert).hexdigest(),
        'unsigned_payload_bytes': len(payload),
        'signature_bytes': size,
        'signature_verified_against_supplied_certificate': True,
        'scope': 'Offline CMS signature and explicit certificate trust; no module loading, kernel-policy or ABI test',
    }, indent=2))


if __name__ == '__main__':
    try:
        main()
    except ValueError as error:
        raise SystemExit(f'Verification failed: {error}') from None
    except (OSError, subprocess.CalledProcessError) as error:
        # OpenSSL diagnostics can include user paths and certificate subjects.
        raise SystemExit(f'Verification failed: {type(error).__name__}') from None
