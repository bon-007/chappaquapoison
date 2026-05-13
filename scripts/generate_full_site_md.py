#!/usr/bin/env python3
"""
generate_full_site_md.py — Generate a single concatenated markdown file of all posts

Creates:
  _site/full_site.md — Every post in reading order, with frontmatter metadata preserved
                        as section headers. Used for QA comparison against reference indexes.

Usage:
  python3 scripts/generate_full_site_md.py              # Generate full site MD
  python3 scripts/generate_full_site_md.py --posts B06,B07,B08  # Only specific posts
  python3 scripts/generate_full_site_md.py --diff        # Show what changed since last generation
  python3 scripts/generate_full_site_md.py --book        # Book mode: omit summaries

The output file serves as a QA target: compare it against CHARACTERS.md, PLACES.md,
NARRATIVES_AND_THEMES.md, KEY_EVIDENCE.md, and v3_Master_Timeline.md to find mismatches.
"""

import os
import sys
import re
import json
import argparse
import hashlib
from pathlib import Path
from datetime import datetime

try:
    import yaml
except ImportError:
    os.system(f"{sys.executable} -m pip install pyyaml --break-system-packages --quiet")
    import yaml

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / 'posts' / 'md'
OUTPUT_DIR = PROJECT_ROOT / '_site'
OUTPUT_FILE = OUTPUT_DIR / 'full_site.md'
POSTS_JSON = PROJECT_ROOT / 'posts.json'


def load_reading_order() -> list:
    """Derive canonical reading order from posts.json (the source of truth).

    Historical note: earlier versions of this script hard-coded READING_ORDER,
    which silently drifted when chapters were added, dissolved, or renumbered
    (e.g., the B47a/B47b→B48/B49 migration and the addition of B51/B52/B53).
    Reading posts.json directly eliminates that drift forever.

    Posts are ordered by their `number` field, which matches the book's
    reading sequence. Posts marked `hidden: true` are excluded. The back
    cover is included; callers that need to omit it can filter downstream.
    """
    with POSTS_JSON.open(encoding='utf-8') as f:
        data = json.load(f)

    posts = data.get('posts', [])
    visible = [p for p in posts if not p.get('hidden', False)]
    # Sort by number field (fallback to id if number is missing)
    visible.sort(key=lambda p: (p.get('number', 9999), p.get('id', '')))
    return [p['id'] for p in visible if p.get('id')]


# Canonical post reading order — derived from posts.json at import time so the
# script can never drift out of sync with the actual post inventory.
READING_ORDER = load_reading_order()


def find_post_file(post_id: str):
    """Find the canonical markdown file for a post ID.

    Prefers the base canonical file (no variant suffix).
    Skips _ORIGINAL, _BOOK, _SUPERSEDED, _PRE_BORA_BORA, _DRAFT, and .backup files.
    Falls back to DRAFT if no canonical exists.
    """
    candidates = list(POSTS_DIR.glob(f'{post_id}_*.md'))
    # Filter out all variant files, originals, backups, and archive copies
    VARIANT_SUFFIXES = ['_ORIGINAL', '_BOOK', '_SUPERSEDED', '_PRE_BORA_BORA', '.backup', '.bak', '.stale']
    candidates = [
        c for c in candidates
        if not any(sfx in c.name for sfx in VARIANT_SUFFIXES)
        and '/archive/' not in str(c)
    ]

    # Separate canonical (no _DRAFT) from drafts
    canonicals = [c for c in candidates if '_DRAFT' not in c.name]
    drafts = [c for c in candidates if '_DRAFT' in c.name]

    # Prefer canonical, fall back to DRAFT
    if canonicals:
        # Sort to get the shortest name (most likely the base file)
        canonicals.sort(key=lambda p: len(p.name))
        return canonicals[0]
    if drafts:
        return drafts[0]
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
            except yaml.YAMLError:
                pass
    return {}, content


def generate_post_section(post_id: str, filepath: Path, book_mode: bool = False) -> str:
    """Generate the full-site-MD section for one post."""
    content = filepath.read_text(encoding='utf-8')
    meta, body = parse_frontmatter(content)

    title = meta.get('title', post_id)
    summary = meta.get('summary', '')
    phase = meta.get('phase', '')
    phase_name = meta.get('phase_name', '')
    date_range = meta.get('date', '')
    ecs = meta.get('ecs', '')
    tags = meta.get('tags', [])

    # Evidence exhibits from frontmatter
    evidence = meta.get('evidence', [])
    exhibit_ids = []
    for item in evidence:
        if isinstance(item, dict) and 'exhibit' in item:
            exhibit_ids.append(item['exhibit'])
        elif isinstance(item, str):
            exhibit_ids.append(item)

    is_draft = '_DRAFT' in filepath.name
    source_note = f" ⚠️ DRAFT" if is_draft else ""

    lines = []
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"# [{post_id}] {title}{source_note}")
    lines.append(f"")
    if summary and not book_mode:
        lines.append(f"> {summary}")
        lines.append(f"")

    meta_parts = []
    if phase:
        meta_parts.append(f"Phase {phase}")
    if phase_name:
        meta_parts.append(phase_name)
    if date_range:
        meta_parts.append(str(date_range))
    if ecs:
        meta_parts.append(f"ECS {ecs}")
    if meta_parts:
        lines.append(f"**{' | '.join(meta_parts)}**")
        lines.append(f"")

    if tags:
        lines.append(f"Tags: {', '.join(str(t) for t in tags)}")
        lines.append(f"")

    if exhibit_ids:
        lines.append(f"Evidence: {len(exhibit_ids)} exhibits")
        for eid in exhibit_ids:
            lines.append(f"  - {eid}")
        lines.append(f"")

    lines.append(body)
    lines.append(f"")

    return '\n'.join(lines)


def generate_full_site_md(post_filter=None, book_mode=False):
    """Generate the full site markdown."""
    sections = []

    # Header
    sections.append("# CHAPPAQUA POISON — Full Site Markdown")
    sections.append(f"")
    sections.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    sections.append(f"")

    posts_to_process = post_filter if post_filter else READING_ORDER

    found = 0
    missing = []
    draft_count = 0

    for post_id in posts_to_process:
        filepath = find_post_file(post_id)
        if filepath:
            section = generate_post_section(post_id, filepath, book_mode=book_mode)
            sections.append(section)
            found += 1
            if '_DRAFT' in filepath.name:
                draft_count += 1
        else:
            missing.append(post_id)
            sections.append(f"---\n\n# [{post_id}] ⚠️ FILE NOT FOUND\n")

    # Footer with stats
    sections.append(f"\n---\n")
    sections.append(f"## Generation Stats")
    sections.append(f"- Posts included: {found}/{len(posts_to_process)}")
    if draft_count:
        sections.append(f"- Draft versions used: {draft_count}")
    if missing:
        sections.append(f"- Missing files: {', '.join(missing)}")

    # Content hash for change detection
    full_text = '\n'.join(sections)
    content_hash = hashlib.md5(full_text.encode()).hexdigest()[:12]
    sections.append(f"- Content hash: {content_hash}")

    return '\n'.join(sections)


def main():
    parser = argparse.ArgumentParser(description='Generate full site markdown')
    parser.add_argument('--posts', type=str, help='Comma-separated post IDs (e.g., B06,B07,B08)')
    parser.add_argument('--diff', action='store_true', help='Show what changed since last generation')
    parser.add_argument('--book', action='store_true', help='Book mode: omit summaries from output')
    parser.add_argument('--output', type=str, help='Custom output path')
    args = parser.parse_args()

    post_filter = None
    if args.posts:
        post_filter = [p.strip() for p in args.posts.split(',')]

    output_path = Path(args.output) if args.output else OUTPUT_FILE

    # Check for previous version (for diff)
    old_hash = None
    if output_path.exists() and args.diff:
        old_content = output_path.read_text()
        old_hash = hashlib.md5(old_content.encode()).hexdigest()[:12]

    # Generate
    full_md = generate_full_site_md(post_filter, book_mode=args.book)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write
    output_path.write_text(full_md, encoding='utf-8')

    # Report
    line_count = full_md.count('\n')
    word_count = len(full_md.split())
    print(f"✅ Generated {output_path}")
    print(f"   {line_count:,} lines, {word_count:,} words")

    if post_filter:
        print(f"   Filtered to: {', '.join(post_filter)}")

    new_hash = hashlib.md5(full_md.encode()).hexdigest()[:12]
    if args.diff and old_hash:
        if old_hash == new_hash:
            print(f"   No changes detected (hash: {new_hash})")
        else:
            print(f"   Changed! Old hash: {old_hash} → New hash: {new_hash}")


if __name__ == '__main__':
    main()
