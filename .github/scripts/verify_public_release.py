#!/usr/bin/env python3
"""Validate a reviewed public manifest and assemble only its exact files for Pages."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path


def verify(root, destination=None):
    root = Path(root).resolve()
    manifest = json.loads((root / 'release-manifest.json').read_text())
    if manifest.get('schema') != 1 or manifest.get('status') != 'reviewed_for_publication':
        raise ValueError('A reviewed publication manifest is required')
    files = manifest['files']
    required = {'index.html', 'evidence.html', 'legal.html', 'CNAME', 'full_site.md', 'llms.txt'}
    required.update(f'posts/B{i:02}.html' for i in range(54))
    required.update(f'posts/B{i:02}.ai.txt' for i in range(54))
    if not required.issubset(files):
        raise ValueError('Publication manifest is incomplete')
    checked, seen = [], set()
    for name, expected in files.items():
        relative = Path(name)
        if relative.is_absolute() or any(p in ('.', '..') or p.startswith('.') for p in relative.parts):
            raise ValueError(f'Unsafe public path: {name}')
        parts = tuple(p.casefold() for p in relative.parts)
        if (parts[0] in {'audits', '_public_assets', '_build_history'}
                or parts[:2] == ('posts', 'md')
                or relative.name.casefold() in {'private_project_record.md', 'deploy_key_new', 'deploy_key'}):
            raise ValueError(f'Private working material cannot be published: {name}')
        if name.casefold() in seen:
            raise ValueError(f'Duplicate public path: {name}')
        seen.add(name.casefold())
        source = root / relative
        if source.is_symlink() or not source.resolve().is_relative_to(root) or not source.is_file():
            raise ValueError(f'Missing or unsafe public file: {name}')
        data = source.read_bytes()
        if data.startswith(b'version https://git-lfs.github.com/spec/v1'):
            raise ValueError(f'Git LFS pointer cannot be published as media: {name}')
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f'Public file changed after review: {name}')
        checked.append((source, relative))
    if (root / 'CNAME').read_text().strip() != 'chappaquapoison.com':
        raise ValueError('Unexpected publication domain')
    if destination is not None:
        destination = Path(destination).absolute()
        if destination.exists() or destination.is_symlink():
            raise ValueError('Publication staging destination must not exist')
        destination.mkdir(parents=True)
        for source, relative in checked:
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    return len(checked)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--stage', type=Path)
    args = parser.parse_args()
    print(f'Verified {verify(args.root, args.stage)} public files.')
