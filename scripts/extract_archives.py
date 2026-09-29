#!/usr/bin/env python3
"""Verify and extract downloaded archives to datasets/communities."""
import argparse
import json
from pathlib import Path
from setup_dataset import extract_archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archives-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True,
                        help='Community root, e.g. ./datasets/communities')
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--community', action='append')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    manifest = args.manifest or args.archives_dir.parent / 'archives_manifest.json'
    entries = json.loads(manifest.read_text())['archives']
    selected = set(args.community or [e['community_id'] for e in entries])
    unknown = selected - {e['community_id'] for e in entries}
    if unknown:
        parser.error(f'Unknown communities: {sorted(unknown)}')
    for entry in entries:
        if entry['community_id'] in selected:
            extract_archive(args.archives_dir / Path(entry['archive_path']).name,
                            entry, args.output_dir, force=args.force)
            print(f"Verified and extracted {entry['community_id']}")


if __name__ == '__main__':
    main()
