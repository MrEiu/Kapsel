"""
Kapsel Debian Package (.deb) Generator.
Pure-Python, cross-platform generator for Debian/Ubuntu .deb binary packages.
Does not require dpkg-deb or root privileges; runs on Linux, macOS, and Windows.
All comments and descriptions are in English.
"""

import argparse
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time
from typing import List, Tuple

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from kapsel import __version__ as DEFAULT_VERSION

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


def create_ar_header(name: str, size: int, mode: int = 0o100644, mtime: int = 0) -> bytes:
    """Generates a standard 60-byte GNU/Debian ar file header."""
    name_field = (name.ljust(16))[:16].encode("ascii")
    mtime_field = str(mtime or int(time.time())).ljust(12).encode("ascii")
    uid_field = "0".ljust(6).encode("ascii")
    gid_field = "0".ljust(6).encode("ascii")
    mode_field = oct(mode)[2:].rjust(8).encode("ascii")
    size_field = str(size).ljust(10).encode("ascii")
    trailer = b"\x60\n"
    header = name_field + mtime_field + uid_field + gid_field + mode_field + size_field + trailer
    if len(header) != 60:
        raise ValueError(f"Invalid ar header length: {len(header)}")
    return header


def create_ar_archive(members: List[Tuple[str, bytes, int]]) -> bytes:
    """Combines members into a standard ar archive."""
    out = io.BytesIO()
    out.write(b"!<arch>\n")
    for name, data, mode in members:
        header = create_ar_header(name, len(data), mode=mode)
        out.write(header)
        out.write(data)
        if len(data) % 2 != 0:
            out.write(b"\n")
    return out.getvalue()


def build_deb_package(
    version: str,
    binary_dir: Path,
    out_dir: Path,
    arch: str = "amd64",
) -> Path:
    """
    Builds a Debian binary package (.deb) containing 'kapsel' and 'kps' executables.
    """
    clean_version = version.lstrip("v")
    out_dir.mkdir(parents=True, exist_ok=True)
    deb_filename = f"kapsel_{clean_version}_{arch}.deb"
    out_path = out_dir / deb_filename

    print(f"📦 Packaging Debian package: {deb_filename}...")

    # 1. Check for required binaries
    kapsel_bin = binary_dir / "kapsel"
    kps_bin = binary_dir / "kps"

    if not kapsel_bin.exists() or not kps_bin.exists():
        raise FileNotFoundError(
            f"Required binaries 'kapsel' and 'kps' not found in {binary_dir.resolve()}. "
            "Please build binaries first via 'python packaging/build.py --target linux'."
        )

    # 2. Member: debian-binary
    debian_binary = b"2.0\n"

    # 3. Member: control.tar.gz
    control_content = f"""Package: kapsel
Version: {clean_version}
Section: utils
Priority: optional
Architecture: {arch}
Maintainer: MrEiu <k648888@vip.qq.com>
Homepage: https://github.com/MrEiu/Kapsel
Description: Next-generation cross-platform terminal capsule & ergonomic shell multiplexer
 Kapsel provides a non-invasive, context-aware command abstraction layer
 with zero global pollution, sub-millisecond autocompletion, Linux-first
 universal command mapping, and isolated developer workflows.
"""
    control_bytes_io = io.BytesIO()
    with tarfile.open(fileobj=control_bytes_io, mode="w:gz") as tar:
        ti = tarfile.TarInfo(name="./control")
        ti.size = len(control_content.encode("utf-8"))
        ti.mode = 0o644
        ti.mtime = int(time.time())
        tar.addfile(ti, io.BytesIO(control_content.encode("utf-8")))

    control_tar_gz = control_bytes_io.getvalue()

    # 4. Member: data.tar.gz
    data_bytes_io = io.BytesIO()
    with tarfile.open(fileobj=data_bytes_io, mode="w:gz") as tar:
        # Directories
        for d in ["./usr", "./usr/bin"]:
            ti = tarfile.TarInfo(name=d)
            ti.type = tarfile.DIRTYPE
            ti.mode = 0o755
            ti.mtime = int(time.time())
            tar.addfile(ti)

        # Binary: /usr/bin/kapsel
        kapsel_data = kapsel_bin.read_bytes()
        ti_kapsel = tarfile.TarInfo(name="./usr/bin/kapsel")
        ti_kapsel.size = len(kapsel_data)
        ti_kapsel.mode = 0o755
        ti_kapsel.mtime = int(time.time())
        tar.addfile(ti_kapsel, io.BytesIO(kapsel_data))

        # Binary: /usr/bin/kps
        kps_data = kps_bin.read_bytes()
        ti_kps = tarfile.TarInfo(name="./usr/bin/kps")
        ti_kps.size = len(kps_data)
        ti_kps.mode = 0o755
        ti_kps.mtime = int(time.time())
        tar.addfile(ti_kps, io.BytesIO(kps_data))

    data_tar_gz = data_bytes_io.getvalue()

    # 5. Combine into .deb ar archive
    members = [
        ("debian-binary", debian_binary, 0o100644),
        ("control.tar.gz", control_tar_gz, 0o100644),
        ("data.tar.gz", data_tar_gz, 0o100644),
    ]
    deb_data = create_ar_archive(members)
    out_path.write_bytes(deb_data)

    print(f"✔ Successfully generated Debian package: {out_path.resolve()} ({len(deb_data) / 1024 / 1024:.2f} MB)")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Kapsel Debian Package (.deb) Generator")
    parser.add_argument("--version", default=DEFAULT_VERSION, help=f"Package version (default: {DEFAULT_VERSION})")
    parser.add_argument("--binary-dir", type=Path, default=ROOT_DIR / "dist" / "bin" / "linux", help="Directory containing linux 'kapsel' and 'kps' binaries")
    parser.add_argument("--out-dir", type=Path, default=ROOT_DIR / "dist", help="Output directory for .deb file")
    parser.add_argument("--arch", default="amd64", help="Architecture (default: amd64)")
    args = parser.parse_args()

    build_deb_package(
        version=args.version,
        binary_dir=args.binary_dir,
        out_dir=args.out_dir,
        arch=args.arch,
    )


if __name__ == "__main__":
    main()
