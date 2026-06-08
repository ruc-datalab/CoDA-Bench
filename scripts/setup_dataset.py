#!/usr/bin/env python3
"""
CoDA-Bench Dataset Setup Script

This script downloads the CoDA-Bench dataset from HuggingFace and extracts
the community data archives to the correct locations.

Usage:
    python scripts/setup_dataset.py [--data-dir ./datasets]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
import tarfile
import shutil

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = REPO_ROOT / "datasets"


def log(msg: str):
    print(f"[CoDA-Bench Setup] {msg}", flush=True)


def check_dependencies():
    """Check if required tools are installed."""
    try:
        subprocess.run(["huggingface-cli", "--version"],
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        log("ERROR: huggingface-cli not found. Please install it:")
        log("  pip install huggingface-hub")
        sys.exit(1)

    try:
        subprocess.run(["zstd", "--version"],
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        log("WARNING: zstd not found. Community archives use zstd compression.")
        log("  Ubuntu/Debian: sudo apt-get install zstd")
        log("  macOS: brew install zstd")
        return False
    return True


def download_dataset(data_dir: Path, force: bool = False):
    """Download dataset from HuggingFace."""
    if data_dir.exists() and not force:
        log(f"Data directory {data_dir} already exists. Use --force to re-download.")
        benchmark_file = data_dir / "coda_bench.json"
        if benchmark_file.exists():
            log("✓ Benchmark data found")
            return

    log(f"Downloading CoDA-Bench dataset to {data_dir}...")
    data_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run([
            "huggingface-cli", "download",
            "RUC-DataLab/CoDA-Bench",
            "--repo-type", "dataset",
            "--local-dir", str(data_dir)
        ], check=True, capture_output=True, text=True)
        log("✓ Dataset downloaded successfully")
    except subprocess.CalledProcessError as e:
        log(f"ERROR: Failed to download dataset: {e.stderr}")
        sys.exit(1)


def extract_archives(data_dir: Path):
    """Extract community data archives."""
    archives_dir = data_dir / "archives"

    if not archives_dir.exists():
        log(f"WARNING: Archives directory not found at {archives_dir}")
        return

    archive_files = list(archives_dir.glob("community_*.tar.zst"))
    if not archive_files:
        log("WARNING: No community archives found")
        return

    log(f"Found {len(archive_files)} community archives to extract...")

    communities_dir = data_dir / "communities"
    communities_dir.mkdir(exist_ok=True)

    for archive in sorted(archive_files):
        community_name = archive.stem.replace(".tar", "")
        output_dir = communities_dir / community_name

        if output_dir.exists():
            log(f"  ✓ {community_name} already extracted")
            continue

        log(f"  Extracting {community_name}...")
        try:
            # Decompress with zstd, then extract tar
            subprocess.run([
                "zstd", "-d", str(archive), "-c"
            ], stdout=subprocess.PIPE, check=True)

            # Use tar to extract
            subprocess.run([
                "tar", "-xf", str(archive).replace(".zst", ""),
                "-C", str(communities_dir)
            ], check=True)

            log(f"  ✓ {community_name} extracted")
        except subprocess.CalledProcessError as e:
            log(f"  ERROR: Failed to extract {community_name}: {e}")
            continue


def verify_setup(data_dir: Path):
    """Verify that the dataset is properly set up."""
    log("\nVerifying setup...")

    # Check benchmark files
    benchmark_file = data_dir / "coda_bench.json"
    hard_file = data_dir / "coda_bench_hard.json"

    if not benchmark_file.exists():
        log("  ✗ coda_bench.json not found")
        return False

    if not hard_file.exists():
        log("  ✗ coda_bench_hard.json not found")
        return False

    # Load and check benchmark
    try:
        with open(benchmark_file) as f:
            tasks = json.load(f)
        log(f"  ✓ Loaded {len(tasks)} tasks from coda_bench.json")

        with open(hard_file) as f:
            hard_tasks = json.load(f)
        log(f"  ✓ Loaded {len(hard_tasks)} tasks from coda_bench_hard.json")
    except Exception as e:
        log(f"  ✗ Error loading benchmark files: {e}")
        return False

    # Check communities
    communities_dir = data_dir / "communities"
    if communities_dir.exists():
        num_communities = len(list(communities_dir.glob("community_*")))
        log(f"  ✓ Found {num_communities} extracted communities")
    else:
        log("  ✗ No communities directory found")
        return False

    log("\n✓ Setup verification complete!")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Download and setup CoDA-Bench dataset"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Directory to store dataset (default: ./datasets)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if data exists"
    )
    parser.add_argument(
        "--skip-extract",
        action="store_true",
        help="Skip extracting community archives"
    )
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip verification step"
    )

    args = parser.parse_args()

    log("="*60)
    log("CoDA-Bench Dataset Setup")
    log("="*60)

    # Check dependencies
    has_zstd = check_dependencies()

    # Download dataset
    download_dataset(args.data_dir, args.force)

    # Extract archives
    if not args.skip_extract:
        if has_zstd:
            extract_archives(args.data_dir)
        else:
            log("\nSkipping archive extraction (zstd not available)")
            log("Install zstd to extract community data")

    # Verify setup
    if not args.skip_verify:
        if not verify_setup(args.data_dir):
            log("\nSetup incomplete. Please check errors above.")
            sys.exit(1)

    log("\n" + "="*60)
    log("Setup complete! You can now run evaluations.")
    log("="*60)
    log(f"\nDataset location: {args.data_dir.resolve()}")
    log(f"Benchmark file: {args.data_dir / 'coda_bench.json'}")
    log(f"Communities: {args.data_dir / 'communities'}/")


if __name__ == "__main__":
    main()
