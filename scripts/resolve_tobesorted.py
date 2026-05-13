#!/usr/bin/env python3
"""
resolve_tobesorted.py — Fix all missing evidence file paths.
Uses pre-built file index for fast lookups.
"""

import json
import os
import shutil
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
EVIDENCE_DIR = PROJECT / 'evidence'
INDEX_PATH = PROJECT / 'evidence_index_canonical.json'
CASEFILES_INDEX = '/tmp/casefiles_index.txt'

def build_lookup():
    """Build filename → full_path lookup from pre-built index."""
    lookup = {}
    with open(CASEFILES_INDEX) as f:
        for line in f:
            path = line.strip()
            if not path:
                continue
            fname = os.path.basename(path).lower()
            if fname not in lookup:
                lookup[fname] = path
    # Also add v2 TOBESORTED
    v2 = '/sessions/kind-busy-planck/mnt/Claude/Blogs/ChappaquaPoison_v2/TOBESORTED'
    if os.path.isdir(v2):
        for f in os.listdir(v2):
            fl = f.lower()
            if fl not in lookup:
                lookup[fl] = os.path.join(v2, f)
    return lookup

def safe_copy(src, dest):
    dest_path = Path(dest)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    if not dest_path.exists():
        shutil.copy2(src, dest)
        return True
    return False

CATEGORY_DIRS = {
    'images': 'sorted_images',
    'PDFs': 'sorted_pdfs',
    'Text': 'sorted_text',
    'Tara Letters': 'sorted_tara_letters',
    'Movies': 'sorted_movies',
    'Tara Screenshots': 'sorted_tara_screenshots',
}

def main():
    print("Building file lookup index...")
    lookup = build_lookup()
    print(f"  Index: {len(lookup)} unique filenames")

    with open(INDEX_PATH) as f:
        data = json.load(f)

    entries = data['entries']
    copied = 0
    cleared = 0
    skipped = 0

    for entry in entries:
        rp = entry.get('rel_path', '')
        if not rp:
            skipped += 1
            continue

        # Check if file already exists
        full = EVIDENCE_DIR / rp
        if full.exists():
            skipped += 1
            continue

        # Virtual entries — no physical file expected
        if rp.endswith('.virtual'):
            skipped += 1
            continue

        eid = entry['exhibit_id']
        filename = os.path.basename(rp)

        # Determine target subdirectory
        if 'TOBESORTED' in rp:
            parts = rp.replace('TOBESORTED/', '').split('/')
            subdir_key = parts[0] if len(parts) > 1 else 'images'
            target_subdir = CATEGORY_DIRS.get(subdir_key, 'sorted_misc')
        elif rp.startswith('CaseFiles/'):
            target_subdir = 'sorted_casefiles'
        elif rp.startswith('emails/'):
            target_subdir = 'sorted_emails'
        else:
            target_subdir = 'sorted_misc'

        # Try to find source file
        source = lookup.get(filename.lower())

        # For CaseFiles-pathed entries, also try the direct path
        if not source and rp.startswith('CaseFiles/'):
            direct = Path('/sessions/kind-busy-planck/mnt/Claude') / rp
            if direct.exists() and direct.is_file():
                source = str(direct)

        if source and os.path.isfile(source):
            dest = EVIDENCE_DIR / target_subdir / filename
            safe_copy(source, str(dest))
            entry['rel_path'] = f"{target_subdir}/{filename}"
            if 'file_missing' in entry:
                del entry['file_missing']
            copied += 1
            print(f"  ✓ {eid}: → evidence/{target_subdir}/{filename}")
        else:
            entry['rel_path'] = ''
            entry['file_missing'] = True
            cleared += 1
            print(f"  ○ {eid}: cleared (no source for {filename})")

    # Write back
    with open(INDEX_PATH, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"  Files copied:    {copied}")
    print(f"  Paths cleared:   {cleared}")
    print(f"  Already OK:      {skipped}")
    print(f"  Total entries:   {len(entries)}")

if __name__ == '__main__':
    main()
