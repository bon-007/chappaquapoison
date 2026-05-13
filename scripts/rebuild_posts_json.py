#!/usr/bin/env python3
"""
rebuild_posts_json.py — Regenerate posts.json from v3 markdown source files.

Reads all B##_*.md files in posts/md/, parses their YAML frontmatter,
and writes a clean posts.json with the canonical v3 structure.

Reading order: B00 (hidden), B01-B49, B50 (hidden), B51 (hidden)
"""

import json
import os
import sys
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    os.system(f"{sys.executable} -m pip install pyyaml --break-system-packages --quiet")
    import yaml

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / 'posts' / 'md'
OUTPUT_FILE = PROJECT_ROOT / 'posts.json'

# Canonical v3 reading order
READING_ORDER = [
    'B00',
    'B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09', 'B10',
    'B11', 'B12', 'B13', 'B14', 'B15', 'B16', 'B17', 'B18',
    'B19', 'B20', 'B21', 'B22', 'B23', 'B24', 'B25', 'B26', 'B27', 'B28',
    'B29', 'B30', 'B31', 'B32', 'B33', 'B34', 'B35', 'B36', 'B37', 'B38',
    'B39', 'B40', 'B43', 'B44', 'B45', 'B46', 'B47', 'B48', 'B49',
    'B50', 'B51',
]

# Phase (act) mapping for posts that may not have it in frontmatter
DEFAULT_PHASES = {
    'B00': ('Preface', 'Preface'),
    'B01': ('I', 'Origin'),
    'B02': ('I', 'Origin'),
    'B03': ('I', 'Origin'),
    'B04': ('II', 'Discovery'),
    'B05': ('II', 'Discovery'),
    'B06': ('II', 'Discovery'),
    'B07': ('II', 'Discovery'),
    'B08': ('II', 'Discovery'),
    'B09': ('II', 'Discovery'),
    'B10': ('II', 'Discovery'),
    'B11': ('III', 'Escalation'),
    'B12': ('III', 'Escalation'),
    'B13': ('III', 'Escalation'),
    'B14': ('III', 'Escalation'),
    'B15': ('III', 'Escalation'),
    'B16': ('III', 'Escalation'),
    'B17': ('III', 'Escalation'),
    'B18': ('III', 'Escalation'),
    'B19': ('III', 'Escalation'),
    'B20': ('III', 'Escalation'),
    'B21': ('III', 'Escalation'),
    'B22': ('IV', 'Synthesis'),
    'B23': ('IV', 'Synthesis'),
    'B24': ('IV', 'Synthesis'),
    'B25': ('IV', 'Synthesis'),
    'B26': ('IV', 'Synthesis'),
    'B27': ('IV', 'Synthesis'),
    'B28': ('IV', 'Synthesis'),
    'B29': ('IV', 'Synthesis'),
    'B30': ('IV', 'Synthesis'),
    'B31': ('IV', 'Synthesis'),
    'B32': ('V', 'Institutional'),
    'B33': ('V', 'Institutional'),
    'B34': ('V', 'Institutional'),
    'B35': ('V', 'Institutional'),
    'B36': ('V', 'Institutional'),
    'B37': ('V', 'Institutional'),
    'B38': ('V', 'Institutional'),
    'B39': ('V', 'Institutional'),
    'B40': ('V', 'Institutional'),
    'B43': ('V', 'Institutional'),
    'B44': ('V', 'Institutional'),
    'B45': ('V', 'Institutional'),
    'B46': ('V', 'Institutional'),
    'B47': ('V', 'Institutional'),
    'B48': ('V', 'Institutional'),
    'B49': ('V', 'Institutional'),
    'B50': ('Afterword', 'Afterword'),
    'B51': ('Back Cover', 'Back Cover'),
}


def find_post_file(post_id: str) -> Path | None:
    """Find the canonical markdown file for a post ID."""
    candidates = list(POSTS_DIR.glob(f'{post_id}_*.md'))
    candidates = [
        c for c in candidates
        if '_ORIGINAL' not in c.name
        and '.backup' not in c.name
        and '.bak' not in c.name
        and '/archive/' not in str(c)
    ]
    # Prefer DRAFT version
    drafts = [c for c in candidates if '_DRAFT' in c.name]
    canonicals = [c for c in candidates if '_DRAFT' not in c.name]
    if drafts:
        return drafts[0]
    if canonicals:
        return canonicals[0]
    return None


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Split YAML frontmatter from markdown body."""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1]) or {}
                body = parts[2].strip()
                return meta, body
            except yaml.YAMLError as e:
                print(f"  ⚠ YAML parse error: {e}")
    return {}, content


def slugify(text: str) -> str:
    """Convert title to URL slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def build_post_entry(post_id: str, filepath: Path, index: int) -> dict:
    """Build a posts.json entry from a markdown file."""
    content = filepath.read_text(encoding='utf-8')
    meta, body = parse_frontmatter(content)

    title = meta.get('title', post_id)
    summary = meta.get('summary', '')
    date = meta.get('date', '')
    tags = meta.get('tags', [])
    ecs = meta.get('ecs', 70)
    hidden = meta.get('hidden', False)

    # Phase/act from frontmatter or defaults
    phase = meta.get('phase', '')
    phase_name = meta.get('phase_name', '')
    if not phase and post_id in DEFAULT_PHASES:
        phase, phase_name = DEFAULT_PHASES[post_id]
    if not phase_name and post_id in DEFAULT_PHASES:
        _, phase_name = DEFAULT_PHASES[post_id]

    # Evidence
    evidence = meta.get('evidence', [])
    evidence_list = []
    for item in evidence:
        if isinstance(item, dict):
            evidence_list.append(item)
        elif isinstance(item, str):
            evidence_list.append({'exhibit': item})

    # Provenance from evidence types
    provenance = list(set(
        item.get('type', '').upper()
        for item in evidence_list
        if isinstance(item, dict) and item.get('type')
    ))

    entry = {
        'id': post_id,
        'number': index,
        'title': title,
        'summary': summary,
        'slug': slugify(title),
        'date': str(date) if date else '',
        'act': phase,
        'act_name': phase_name,
        'tags': tags if isinstance(tags, list) else [tags],
        'ecs': ecs,
        'provenance': provenance,
        'evidence': evidence_list,
    }

    if hidden:
        entry['hidden'] = True

    return entry


def main():
    print("=" * 60)
    print("Rebuilding posts.json from v3 markdown sources")
    print("=" * 60)

    # Load existing posts.json to preserve static_pages
    existing_data = {}
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE) as f:
            existing_data = json.load(f)

    static_pages = existing_data.get('static_pages', [])

    posts = []
    found = 0
    missing = []

    for i, post_id in enumerate(READING_ORDER):
        filepath = find_post_file(post_id)
        if filepath:
            entry = build_post_entry(post_id, filepath, i + 1)
            posts.append(entry)
            found += 1
            status = " (hidden)" if entry.get('hidden') else ""
            print(f"  ✓ {post_id}: {entry['title']}{status}")
        else:
            missing.append(post_id)
            print(f"  ✗ {post_id}: FILE NOT FOUND")

    output = {
        'static_pages': static_pages,
        'posts': posts,
    }

    # Backup existing
    if OUTPUT_FILE.exists():
        backup = OUTPUT_FILE.with_suffix('.json.bak')
        import shutil
        shutil.copy2(OUTPUT_FILE, backup)
        print(f"\n  Backed up existing posts.json → posts.json.bak")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"Posts found: {found}/{len(READING_ORDER)}")
    if missing:
        print(f"Missing: {', '.join(missing)}")
    hidden_count = sum(1 for p in posts if p.get('hidden'))
    print(f"Visible posts: {found - hidden_count}")
    print(f"Hidden posts: {hidden_count}")
    print(f"Static pages preserved: {len(static_pages)}")
    print(f"Written to: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
