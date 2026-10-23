#!/usr/bin/env python3
"""Verify the release certificate, package ID, signed APK and module identity."""

import argparse
import hashlib
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "com.zatroser.kernelmanager"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def android_tool(name):
    executable = shutil.which(name)
    if executable:
        return executable
    for variable in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
        if os.environ.get(variable):
            directory = Path(os.environ[variable]) / "build-tools"
            for candidate in sorted(directory.glob(f"*/{name}*"), reverse=True):
                if candidate.name in (name, name + ".exe", name + ".bat"):
                    return str(candidate)
    raise ValueError(f"{name} not found; install Android SDK build-tools")


def length_prefixed(data, offset):
    require(offset + 4 <= len(data), "Truncated APK signing sequence")
    size = struct.unpack_from("<I", data, offset)[0]
    end = offset + 4 + size
    require(end <= len(data), "APK signing sequence exceeds its parent")
    return data[offset + 4:end], end


def apk_certificate(data):
    # Honor ZIP comments instead of interpreting an embedded EOCD as the footer.
    eocd = None
    for offset in range(len(data) - 22, max(-1, len(data) - 65558), -1):
        if data[offset:offset + 4] == b"PK\x05\x06":
            if offset + 22 + struct.unpack_from("<H", data, offset + 20)[0] == len(data):
                eocd = offset
                break
    require(eocd is not None, "APK has no ZIP footer")
    central = struct.unpack_from("<I", data, eocd + 16)[0]
    require(24 <= central <= eocd, "Invalid central directory offset")
    require(data[central - 16:central] == b"APK Sig Block 42", "No APK signing block")
    size = struct.unpack_from("<Q", data, central - 24)[0]
    start = central - size - 8
    require(size >= 24 and start >= 0, "Invalid signing block size")
    require(struct.unpack_from("<Q", data, start)[0] == size, "Signing block sizes differ")
    offset = start + 8
    blocks = []
    while offset < central - 24:
        require(offset + 12 <= central - 24, "Truncated signing block entry")
        length, kind = struct.unpack_from("<QI", data, offset)
        end = offset + 8 + length
        require(length >= 4 and end <= central - 24, "Invalid signing block entry size")
        require(kind in (0x7109871A, 0x42726577), "Kernel accepts v2-only APK signatures")
        if kind == 0x7109871A:
            blocks.append(data[offset + 12:end])
        offset = end
    require(len(blocks) == 1, "Expected exactly one APK v2 signing block")
    signers, _ = length_prefixed(blocks[0], 0)
    signer, signer_end = length_prefixed(signers, 0)
    require(signer_end == len(signers), "Expected one APK signer")
    signed, _ = length_prefixed(signer, 0)
    _, offset = length_prefixed(signed, 0)
    certificates, _ = length_prefixed(signed, offset)
    certificate, _ = length_prefixed(certificates, 0)
    return certificate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=Path)
    parser.add_argument("--module", type=Path)
    args = parser.parse_args()
    cert = (ROOT / "signing/manager.der").read_bytes()
    digest = hashlib.sha256(cert).hexdigest()
    kbuild = (ROOT / "kernel/Kbuild").read_text()
    require(0 < len(cert) <= 1024, "Certificate exceeds kernel parser limits")
    size_match = re.search(r"^KSU_EXPECTED_SIZE \?= (\S+)$", kbuild, re.M)
    hash_match = re.search(r"^KSU_EXPECTED_HASH \?= (\S+)$", kbuild, re.M)
    require(size_match and int(size_match[1], 0) == len(cert), "Kernel certificate size mismatch")
    require(hash_match and hash_match[1] == digest, "Kernel certificate hash mismatch")
    require(f"KSU_PACKAGE_NAME ?= {PACKAGE}\n" in kbuild, "Kernel package mismatch")
    gradle = (ROOT / "manager/app/build.gradle.kts").read_text()
    require(f'"{PACKAGE}.pr" else "{PACKAGE}"' in gradle, "Manager package mismatch")
    rust = (ROOT / "userspace/ksud/build.rs").read_text()
    require(f"KSU_PACKAGE_NAME={PACKAGE}" in rust, "ksud package mismatch")
    if args.apk:
        require(apk_certificate(args.apk.read_bytes()) == cert, "APK signed with another certificate")
        with zipfile.ZipFile(args.apk) as archive:
            libraries = [name for name in archive.namelist() if name.startswith("lib/") and name.endswith(".so")]
            require({name.split("/")[1] for name in libraries} == {"arm64-v8a"}, "APK must contain only ARM64 libraries")
            require("lib/arm64-v8a/libksud.so" in libraries, "APK is missing its ARM64 daemon")
        subprocess.run([android_tool("apksigner"), "verify", "--verbose", str(args.apk)], check=True)
        badging = subprocess.check_output([android_tool("aapt"), "dump", "badging", str(args.apk)], text=True)
        require(f"package: name='{PACKAGE}' " in badging, "APK applicationId mismatch")
    if args.module:
        module = args.module.read_bytes()
        require(module.startswith(b"\x7fELF"), "Module is not ELF")
        require(module[4:6] == b"\x02\x01" and struct.unpack_from("<H", module, 18)[0] == 183,
                "Module must be little-endian AArch64 ELF64")
        require(PACKAGE.encode() + b"\0" in module, "Module manager package mismatch")
        require(digest.encode() + b"\0" in module, "Module certificate hash mismatch")
    print("PASS: LinYuKernel package and signing identity" +
          (f"; APK={args.apk.name}" if args.apk else "") +
          (f"; module={args.module.name}" if args.module else ""))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
