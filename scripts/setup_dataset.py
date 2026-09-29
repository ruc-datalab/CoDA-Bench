#!/usr/bin/env python3
"""Download a pinned CoDA-Bench release, verify its archives, and extract them."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request

REPO_ID = 'RUC-DataLab/CoDA-Bench'
METADATA = ('coda_bench.json', 'coda_bench_hard.json', 'archives_manifest.json',
            'source_to_archive.json', 'release_notes.md')


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def verify_archive(path, entry):
    path = Path(path)
    if not path.is_file() or path.stat().st_size != entry['size_bytes']:
        raise ValueError(f'Archive size mismatch: {path}')
    if sha256(path) != entry['sha256']:
        raise ValueError(f'Archive SHA-256 mismatch: {path}')


def extract_archive(path, entry, communities_dir, force=False):
    """Validate content and atomically replace one community after successful extraction."""
    verify_archive(path, entry)
    community = entry['community_id']
    if not community.startswith('community_') or not community[10:].isdigit():
        raise ValueError(f'Invalid community: {community}')
    communities_dir = Path(communities_dir)
    communities_dir.mkdir(parents=True, exist_ok=True)
    target = communities_dir / community
    marker = target / '.archive.sha256'
    if not force and marker.is_file() and marker.read_text().strip() == entry['sha256']:
        if (target / 'full_community').is_dir():
            return
    with tempfile.TemporaryDirectory(prefix='.extract-', dir=communities_dir) as tmp:
        tmp = Path(tmp)
        proc = subprocess.Popen(['zstd', '-dc', str(path)], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        try:
            with tarfile.open(fileobj=proc.stdout, mode='r|') as archive:
                for member in archive:
                    name = member.name.removeprefix('./')
                    parts = PurePosixPath(name).parts
                    if name.startswith('/') or '..' in parts:
                        raise ValueError(f'Unsafe archive path: {name}')
                    if parts == ('data',) and member.isdir():
                        continue
                    if len(parts) < 2 or parts[:2] != ('data', community):
                        raise ValueError(f'Unexpected archive root: {name}')
                    dest = tmp.joinpath(*parts[1:])
                    if member.isdir():
                        dest.mkdir(parents=True, exist_ok=True)
                    elif member.isfile():
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        with archive.extractfile(member) as src, dest.open('wb') as dst:
                            shutil.copyfileobj(src, dst, 1024 * 1024)
                    else:
                        raise ValueError(f'Unsupported archive entry: {name}')
            error = proc.stderr.read().decode(errors='replace')
            if proc.wait() != 0:
                raise RuntimeError(f'zstd failed: {error}')
        finally:
            if proc.poll() is None:
                proc.kill()
            proc.wait()
            proc.stdout.close()
            proc.stderr.close()
        staged = tmp / community
        if not (staged / 'full_community').is_dir():
            raise ValueError(f'Archive has no full_community directory: {community}')
        (staged / '.archive.sha256').write_text(entry['sha256'] + '\n')
        previous = tmp / 'previous'
        if target.exists():
            target.rename(previous)
        try:
            staged.rename(target)
        except Exception:
            if previous.exists():
                previous.rename(target)
            raise


def install(data_dir, revision='main', communities=None, force=False, base_url=None):
    """base_url is an optional HTTP mirror used for offline/release integration tests."""
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    if base_url:
        if not base_url.startswith(('http://', 'https://')):
            raise ValueError('base_url must be HTTP(S)')
        resolved_revision = 'http-mirror'

        def fetch(name, dest):
            dest.parent.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(base_url.rstrip('/') + '/' + name, timeout=120) as src:
                with dest.open('wb') as dst:
                    shutil.copyfileobj(src, dst, 1024 * 1024)
    else:
        try:
            from huggingface_hub import HfApi, hf_hub_download
        except ImportError as exc:
            raise RuntimeError('Install huggingface_hub: pip install huggingface_hub') from exc
        resolved_revision = HfApi().dataset_info(REPO_ID, revision=revision).sha

        def fetch(name, dest):
            cached = hf_hub_download(REPO_ID, name, repo_type='dataset',
                                     revision=resolved_revision, force_download=force)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(cached, dest)

    # Always refresh metadata, even when an older task JSON already exists.
    with tempfile.TemporaryDirectory(prefix='.download-', dir=data_dir) as tmp:
        stage = Path(tmp)
        for name in METADATA:
            fetch(name, stage / name)
        manifest = json.loads((stage / 'archives_manifest.json').read_text())
        entries = {e['community_id']: e for e in manifest['archives']}
        if len(entries) != len(manifest['archives']):
            raise ValueError('Duplicate communities in archive manifest')
        tasks = json.loads((stage / 'coda_bench.json').read_text())
        hard = json.loads((stage / 'coda_bench_hard.json').read_text())
        required = {r['release_community'] for r in tasks + hard}
        if required - entries.keys():
            raise ValueError(f'Manifest missing communities: {sorted(required - entries.keys())}')
        selected = set(communities) if communities else required
        if selected - entries.keys():
            raise ValueError(f'Unknown communities: {sorted(selected - entries.keys())}')
        for community in sorted(selected, key=lambda c: int(c.split('_')[1])):
            entry = entries[community]
            name = f'archives/{community}.tar.zst'
            if entry['archive_path'] != name:
                raise ValueError(f'Unexpected archive path: {entry["archive_path"]}')
            archive = data_dir / name
            valid = False
            if archive.exists() and not force:
                try:
                    verify_archive(archive, entry)
                    valid = True
                except ValueError:
                    pass
            if not valid:
                downloaded = stage / name
                print(f'Downloading {community}', flush=True)
                fetch(name, downloaded)
                verify_archive(downloaded, entry)
                archive.parent.mkdir(parents=True, exist_ok=True)
                os.replace(downloaded, archive)
            print(f'Verifying and extracting {community}', flush=True)
            extract_archive(archive, entry, data_dir / 'communities', force=force)
        for name in METADATA:
            os.replace(stage / name, data_dir / name)
        record = dict(revision=resolved_revision, version=manifest['version'],
                      installed_communities=sorted(selected), partial=selected != required)
        (data_dir / 'installed_release.json').write_text(json.dumps(record, indent=2) + '\n')
    print(f'Installed {len(selected)} communities at revision {resolved_revision}', flush=True)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=Path(__file__).resolve().parents[1] / 'datasets')
    parser.add_argument('--revision', default='main', help='HF branch, tag, or immutable commit SHA')
    parser.add_argument('--community', action='append', help='Install one community; repeat as needed')
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--base-url', help='Optional HTTP mirror, primarily for release testing')
    args = parser.parse_args()
    install(args.data_dir, args.revision, args.community, args.force, args.base_url)


if __name__ == '__main__':
    main()
