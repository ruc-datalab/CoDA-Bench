"""Extract CoDA-Bench data archives.

Usage:
    python scripts/extract_archives.py --archives-dir ./archives --output-dir ./data
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def extract_archive(archive_path: Path, output_dir: Path) -> bool:
    """Extract a single .tar.zst archive."""
    print(f"Extracting {archive_path.name}...")
    try:
        subprocess.run(
            ["tar", "--use-compress-program=zstd -d", "-xf", str(archive_path), "-C", str(output_dir)],
            check=True,
            capture_output=True,
        )
        print(f"✓ {archive_path.name} extracted successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to extract {archive_path.name}: {e.stderr.decode()}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("✗ Error: 'zstd' or 'tar' not found. Please install zstd:", file=sys.stderr)
        print("  Ubuntu/Debian: sudo apt-get install zstd", file=sys.stderr)
        print("  macOS: brew install zstd", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Extract CoDA-Bench data archives")
    parser.add_argument(
        "--archives-dir",
        type=Path,
        required=True,
        help="Directory containing .tar.zst archives",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Output directory for extracted data",
    )
    parser.add_argument(
        "--community",
        type=str,
        help="Extract only a specific community (e.g., 'community_26')",
    )
    args = parser.parse_args()

    archives_dir = args.archives_dir
    output_dir = args.output_dir

    if not archives_dir.exists():
        print(f"✗ Error: Archives directory not found: {archives_dir}", file=sys.stderr)
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all .tar.zst files
    if args.community:
        archives = list(archives_dir.glob(f"{args.community}.tar.zst"))
        if not archives:
            print(f"✗ Error: Archive not found: {args.community}.tar.zst", file=sys.stderr)
            sys.exit(1)
    else:
        archives = sorted(archives_dir.glob("community_*.tar.zst"))

    if not archives:
        print(f"✗ Error: No .tar.zst archives found in {archives_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(archives)} archive(s) to extract")
    print(f"Output directory: {output_dir}")
    print()

    success_count = 0
    for archive in archives:
        if extract_archive(archive, output_dir):
            success_count += 1

    print()
    print(f"Extraction complete: {success_count}/{len(archives)} archives extracted successfully")

    if success_count < len(archives):
        sys.exit(1)


if __name__ == "__main__":
    main()
