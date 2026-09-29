import functools
import http.server
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tarfile
import threading

import pytest

spec = importlib.util.spec_from_file_location('setup_dataset', Path(__file__).parents[1] / 'scripts/setup_dataset.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


def make_archive(root, name='data/community_4/full_community/example/source/input.csv'):
    root.mkdir(parents=True, exist_ok=True)
    raw = root / 'test.tar'
    with tarfile.open(raw, 'w') as tar:
        if name.startswith('data/community_4/'):
            d = tarfile.TarInfo('data/community_4/full_community')
            d.type = tarfile.DIRTYPE
            tar.addfile(d)
        data = b'value\n42\n'
        info = tarfile.TarInfo(name)
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    compressed = root / 'community_4.tar.zst'
    subprocess.run(['zstd', '-q', '-f', str(raw), '-o', str(compressed)], check=True)
    return compressed, dict(community_id='community_4', archive_path='archives/community_4.tar.zst',
                           size_bytes=compressed.stat().st_size, sha256=setup.sha256(compressed))


def test_extract_layout_and_stale_directory(tmp_path):
    archive, entry = make_archive(tmp_path / 'input')
    dest = tmp_path / 'communities'
    stale = dest / 'community_4/full_community'
    stale.mkdir(parents=True)
    (stale / 'stale.csv').write_text('old')
    setup.extract_archive(archive, entry, dest)
    assert (stale / 'example/source/input.csv').read_text() == 'value\n42\n'
    assert not (stale / 'stale.csv').exists()
    assert not (dest / 'data').exists()


def test_bad_checksum_keeps_existing_data(tmp_path):
    archive, entry = make_archive(tmp_path / 'input')
    dest = tmp_path / 'communities/community_4/full_community'
    dest.mkdir(parents=True)
    (dest / 'keep').write_text('valid old data')
    entry['sha256'] = '0' * 64
    with pytest.raises(ValueError, match='SHA-256'):
        setup.extract_archive(archive, entry, dest.parent.parent)
    assert (dest / 'keep').read_text() == 'valid old data'


def test_rejects_path_traversal(tmp_path):
    archive, entry = make_archive(tmp_path / 'input', 'data/community_4/../../escaped')
    with pytest.raises(ValueError, match='Unsafe'):
        setup.extract_archive(archive, entry, tmp_path / 'communities')
    assert not (tmp_path / 'escaped').exists()


def test_download_refreshes_existing_json_and_fetches_missing_archive(tmp_path):
    mirror = tmp_path / 'mirror'
    archive, entry = make_archive(mirror / 'archives')
    tasks = [{'instance_id': 0, 'release_community': 'community_4'}]
    for filename in ('coda_bench.json', 'coda_bench_hard.json'):
        (mirror / filename).write_text(json.dumps(tasks))
    (mirror / 'archives_manifest.json').write_text(json.dumps({'version': '1.0.1', 'archives': [entry]}))
    (mirror / 'source_to_archive.json').write_text('{}')
    (mirror / 'release_notes.md').write_text('release')
    dest = tmp_path / 'download'
    dest.mkdir()
    (dest / 'coda_bench.json').write_text('[{"release_community":"community_30"}]')
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(mirror))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        record = setup.install(dest, base_url=f'http://127.0.0.1:{server.server_port}')
    finally:
        server.shutdown()
        thread.join()
        server.server_close()
    assert json.loads((dest / 'coda_bench.json').read_text()) == tasks
    assert (dest / 'communities/community_4/full_community/example/source/input.csv').is_file()
    assert record['version'] == '1.0.1'
    assert setup.sha256(dest / entry['archive_path']) == entry['sha256']
