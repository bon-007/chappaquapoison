#!/usr/bin/env python3
"""
build_canonical_evidence_index.py — Generate the single canonical EVIDENCE_INDEX.md

CORE RULE: One index entry per physical file. entries == files.
If a file contains multiple claims, the file should be split first.
The index and the Evidence/ folder stay in lockstep.

Every entry has:
  - A physical file in Evidence/
  - Extracted text quoted in-context
  - Category and reliability classification
  - Tier (Hero / Primary / Secondary / Tertiary)
  - Cross-links to posts that reference it

Usage:
  python3 scripts/build_canonical_evidence_index.py
  python3 scripts/build_canonical_evidence_index.py --dry-run
  python3 scripts/build_canonical_evidence_index.py --no-pdf  # skip PDF extraction (faster)
"""

import json
import os
import re
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

try:
    import yaml
except ImportError:
    os.system(f"{sys.executable} -m pip install pyyaml --break-system-packages --quiet")
    import yaml

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE_DIR = ROOT / 'Evidence'
OUTPUT_FILE = ROOT / 'Indexes' / 'EVIDENCE_INDEX.md'
OUTPUT_JSON = ROOT / 'evidence_index_canonical.json'
POSTS_DIR = ROOT / 'posts' / 'md'

SKIP_FILES = {'.DS_Store', 'Thumbs.db', '.gitkeep'}
META_FILES = {
    'INDEX.md', 'COMPLETION_REPORT.txt', 'DETAILED_FILE_MANIFEST.txt',
    'EVIDENCE_FILES_MANIFEST.txt', 'EXTRACTION_SUMMARY.txt',
    'TIER_2_3_COLLECTION_SUMMARY.md',
}

# ─── Category inference ───

SUBDIR_CATEGORIES = {
    'pdf/court_filings': 'Court Filing',
    'pdf/declarations': 'Sworn Declaration',
    'pdf/depositions': 'Deposition',
    'pdf/lab_reports': 'Laboratory Analysis',
    'pdf/motions': 'Court Motion',
    'pdf/correspondence': 'Correspondence',
    'pdf/media': 'Media Coverage',
    'pdf/blog_brienne': 'Blog Archive (Brienne Walsh)',
    'pdf/blog_archives': 'Blog Archive',
    'pdf/blog_archives/brie': 'Blog Archive (Brienne Walsh)',
    'pdf/journals': 'Journal / Publication',
    'pdf/imports': 'Import Document',
    'html/court_filings': 'Court Filing (HTML)',
    'html/declarations': 'Sworn Declaration (HTML)',
    'html/depositions': 'Deposition (HTML)',
    'html/lab_reports': 'Laboratory Analysis (HTML)',
    'html/imessage': 'iMessage Record (HTML)',
    'html/imports': 'Import Document (HTML)',
    'html/correspondence': 'Correspondence (HTML)',
    'html/media': 'Media Coverage (HTML)',
    'photos/evidence': 'Evidence Photograph',
    'photos/cpv1_archive': 'Photograph (CPv1 Archive)',
    'photos/sle_archive': 'Photograph (SLE Archive)',
    'media/clips/stephen': 'Video Clip — Stephen Russell Deposition',
    'media/clips/gavish': 'Video Clip — Gavish Deposition',
    'media/clips/maura': 'Video Clip — Maura Walsh Deposition',
    'media/clips/brendan': 'Video Clip — Brendan Walsh Deposition',
    'media/clips/montage_sources': 'Video Clip — Montage Source',
    'media/clips': 'Video Clip',
    'media/video': 'Video Recording',
    'media/audio': 'Audio Recording',
    'audio': 'Audio Recording',
    'video': 'Video Recording',
    'screenshots': 'Screenshot',
    'imports': 'Import Document',
    'docs': 'Document',
    'docs/imports': 'Import Document',
}


def infer_category(rel_path, filename):
    """Infer evidence category from path and filename."""
    # Try subdirectory match (longest first)
    parts = rel_path.replace('\\', '/').split('/')
    for depth in range(len(parts) - 1, 0, -1):
        key = '/'.join(parts[:depth])
        if key in SUBDIR_CATEGORIES:
            return SUBDIR_CATEGORIES[key]

    # Filename-based inference
    fl = filename.lower()
    if 'declaration' in fl or 'decl' in fl or 'affidavit' in fl:
        return 'Sworn Declaration'
    if 'deposition' in fl or 'depo' in fl:
        return 'Deposition'
    if 'transcript' in fl:
        return 'Court Transcript'
    if 'order' in fl or 'judgment' in fl or 'verdict' in fl:
        return 'Court Order / Judgment'
    if 'motion' in fl or 'petition' in fl or 'complaint' in fl:
        return 'Court Filing'
    if 'heavy metals' in fl or 'test results' in fl or 'lab' in fl or 'turnure kelly' in fl:
        return 'Laboratory Analysis'
    if 'text_between' in fl or 'chat' in fl:
        return 'Text Message / Chat Record'
    if '.ichat' in fl:
        return 'iMessage / iChat Record'
    if 'email' in fl or fl.endswith('.emlx'):
        return 'Email'
    if 'voicemail' in fl or fl.endswith('.m4a'):
        return 'Audio Recording'
    if 'police report' in fl or 'hunt_102' in fl:
        return 'Police Report'
    if fl.endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg')):
        return 'Photograph'
    if fl.endswith('.mp4'):
        return 'Video Recording'
    if 'memo' in fl:
        return 'Legal Memorandum'
    if 'narrative_timeline' in fl or 'carg_report' in fl:
        return 'Investigative Report'
    if fl.endswith('.pdf'):
        return 'Document (PDF)'
    if fl.endswith('.docx'):
        return 'Document (Word)'
    if fl.endswith('.html'):
        return 'Document (HTML)'
    if fl.endswith('.txt'):
        return 'Text Document'
    if fl.endswith('.md'):
        return 'Markdown Document'
    return 'Uncategorized'


def infer_reliability(category):
    """Infer reliability tier from category."""
    if any(k in category for k in ['Sworn', 'Deposition', 'Transcript']):
        return 'Sworn Under Oath'
    if any(k in category for k in ['Court', 'Judgment', 'Motion', 'Filing']):
        return 'Court Record'
    if 'Laboratory' in category:
        return 'Laboratory Analysis'
    if any(k in category for k in ['Message', 'iChat', 'iMessage', 'Email']):
        return 'Device Backup / Digital Record'
    if any(k in category for k in ['Photo', 'Video', 'Audio', 'Screenshot']):
        return 'Media Record'
    if 'Blog' in category:
        return 'Published Record'
    if 'Police' in category:
        return 'Official Report'
    if 'Investigative' in category:
        return 'Investigative Record'
    return 'Documented Record'


# ─── Text extraction ───

def extract_text_pdf(filepath, max_chars=600):
    """Extract text from PDF using pdftotext, fallback to pdfplumber."""
    try:
        result = subprocess.run(
            ['pdftotext', '-l', '3', '-q', str(filepath), '-'],
            capture_output=True, text=True, timeout=10
        )
        text = result.stdout.strip()
        if text and len(text) > 20:
            # Clean up common PDF noise
            text = re.sub(r'\x0c', '\n', text)
            text = re.sub(r'\n{3,}', '\n\n', text)
            return text[:max_chars].strip()
    except Exception:
        pass

    # Fallback to pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            text_parts = []
            for page in pdf.pages[:3]:
                pt = page.extract_text()
                if pt:
                    text_parts.append(pt)
            text = '\n'.join(text_parts)
            if text:
                return text[:max_chars].strip()
    except Exception:
        pass

    return ''


def extract_text_file(filepath, max_chars=600):
    """Extract text from text-based files."""
    ext = filepath.suffix.lower()
    try:
        if ext in ('.txt', '.md'):
            return filepath.read_text(encoding='utf-8', errors='replace')[:max_chars].strip()
        if ext in ('.html', '.htm'):
            raw = filepath.read_text(encoding='utf-8', errors='replace')
            clean = re.sub(r'<style[^>]*>.*?</style>', '', raw, flags=re.DOTALL)
            clean = re.sub(r'<script[^>]*>.*?</script>', '', clean, flags=re.DOTALL)
            clean = re.sub(r'<[^>]+>', ' ', clean)
            clean = re.sub(r'&nbsp;', ' ', clean)
            clean = re.sub(r'&[a-z]+;', '', clean)
            clean = re.sub(r'\s+', ' ', clean).strip()
            return clean[:max_chars].strip()
        if ext == '.emlx':
            raw = filepath.read_bytes()
            # emlx files have a byte count header, then the email
            text = raw.decode('utf-8', errors='replace')
            # Strip the first line (byte count) and extract readable parts
            lines = text.split('\n')[1:]
            clean = '\n'.join(l for l in lines if not l.startswith('Content-') and
                             not l.startswith('MIME-') and not l.startswith('X-') and
                             not l.startswith('Message-ID') and not l.startswith('Date:') and
                             not l.startswith('From:') and not l.startswith('To:'))
            clean = re.sub(r'<[^>]+>', ' ', clean)
            clean = re.sub(r'\s+', ' ', clean).strip()
            return clean[:max_chars].strip()
    except Exception:
        pass
    return ''


def extract_text(filepath, skip_pdf=False):
    """Extract text from any supported file type."""
    ext = filepath.suffix.lower()
    if ext == '.pdf' and not skip_pdf:
        return extract_text_pdf(filepath)
    if ext in ('.txt', '.md', '.html', '.htm', '.emlx'):
        return extract_text_file(filepath)
    if ext in ('.ichat',):
        # Binary plist — can't easily extract readable text
        return ''
    # Images, video, audio — no text extraction
    return ''


# ─── Load metadata sources ───

def load_enrichment_from_canonical():
    """Load enrichment data from the existing canonical JSON.
    On rebuilds, previously captured metadata, editorial text, post linkages,
    and tier assignments are preserved by reading the prior canonical output.
    This is the ONLY enrichment source — legacy files have been retired."""
    if not OUTPUT_JSON.exists():
        print("   (No previous canonical JSON — starting fresh)")
        return {}, {}
    try:
        with open(OUTPUT_JSON) as f:
            data = json.load(f)
        # Build filename → entry lookup for metadata enrichment
        by_fname = {}
        # Build post_id → list of entries for post-tier linkage
        by_post = {}
        for entry in data.get('entries', []):
            fname = entry.get('filename', '')
            if fname:
                by_fname[fname] = entry
            for pid in entry.get('posts', []):
                by_post.setdefault(pid, []).append(entry)
        return by_fname, by_post
    except Exception:
        return {}, {}


def load_post_frontmatter():
    posts = {}
    for md_file in sorted(POSTS_DIR.glob('B*_*.md')):
        if any(s in md_file.name for s in ['_ORIGINAL', '_BOOK', '_SUPERSEDED', '.backup', '.bak', '.stale']):
            continue
        content = md_file.read_text(encoding='utf-8', errors='replace')
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    meta = yaml.safe_load(parts[1]) or {}
                    pid = meta.get('id', '')
                    if pid:
                        posts[pid] = {'title': meta.get('title', ''), 'evidence': meta.get('evidence', {})}
                except yaml.YAMLError:
                    pass
    return posts


# ─── Build file→post mapping from v3_evidence_map ───

def build_file_to_posts(v3_map):
    """Build reverse lookup: filename → list of (post_id, tier, exhibit_name, embed_text)."""
    f2p = {}
    for post_id, post_data in v3_map.items():
        for tier in ['hero', 'primary', 'secondary', 'tertiary']:
            for item in post_data.get(tier, []):
                if not isinstance(item, dict):
                    continue
                mf = item.get('matched_file', '')
                if mf:
                    fname = mf.split('/')[-1]
                    f2p.setdefault(fname, []).append({
                        'post_id': post_id,
                        'tier': tier,
                        'exhibit_name': item.get('exhibit_name', ''),
                        'embed_text': item.get('embed_text', ''),
                        'appendix_text': item.get('appendix_text', ''),
                        'embed_format': item.get('embed_format', ''),
                        'exhibit_type': item.get('exhibit_type', ''),
                    })
    return f2p


def build_exhibit_to_posts(post_data):
    """Build exhibit_id → list of post_ids from frontmatter."""
    e2p = {}
    for pid, pdata in post_data.items():
        ev = pdata.get('evidence', {})
        if isinstance(ev, list):
            continue
        for tier in ['hero', 'primary', 'secondary']:
            for item in ev.get(tier, []):
                ex_str = item.get('exhibit', '') if isinstance(item, dict) else str(item)
                m = re.match(r'^([A-Za-z]+-?\d+\.?\d*[a-z]?)', ex_str)
                if m:
                    eid = m.group(1)
                    e2p.setdefault(eid, set()).add(pid)
    return e2p


# ─── Main build ───

def scan_and_build(skip_pdf=False):
    """Scan all files and build one entry per file."""
    meta_lookup, canonical_by_post = load_enrichment_from_canonical()
    post_data = load_post_frontmatter()
    # build_file_to_posts is no longer needed — post linkage comes from canonical self-enrichment
    exhibit_to_posts = build_exhibit_to_posts(post_data)

    entries = []
    pdf_count = 0
    pdf_extracted = 0

    for root_dir, dirs, files in os.walk(EVIDENCE_DIR):
        # Sort dirs for consistent ordering
        dirs.sort()
        # Skip archive/removed directories — these are backup copies, not active evidence
        dirs[:] = [d for d in dirs if not d.startswith('_removed')]
        for filename in sorted(files):
            if filename in SKIP_FILES or filename.startswith('.'):
                continue

            filepath = Path(root_dir) / filename
            rel_path = os.path.relpath(filepath, EVIDENCE_DIR)

            # Skip meta files at top level
            if rel_path in META_FILES or filename in META_FILES:
                continue

            # Extract exhibit ID from filename
            m = re.match(r'^([A-Za-z]+-?\d+\.?\d*[a-z]?)', filename)
            exhibit_id = m.group(1) if m else ''
            if not exhibit_id:
                m2 = re.match(r'^(BR-\d+|BB-\d+|Ex[A-Z]+[_-]?\d*)', filename)
                exhibit_id = m2.group(1) if m2 else ''

            category = infer_category(rel_path, filename)
            reliability = infer_reliability(category)
            is_restored = '_removed_' in rel_path
            size = filepath.stat().st_size

            # Extract text
            if filepath.suffix.lower() == '.pdf':
                pdf_count += 1
            text = extract_text(filepath, skip_pdf=skip_pdf)
            if filepath.suffix.lower() == '.pdf' and text:
                pdf_extracted += 1

            # Get metadata enrichment from evidence_metadata.json
            meta = meta_lookup.get(filename, {})
            title = meta.get('title', '')
            description = meta.get('description', '')
            tier = meta.get('tier', '')
            # Preserve all enrichment fields from metadata
            meta_category_key = meta.get('category_key', '')
            meta_file_type = meta.get('file_type', '')
            meta_phase = meta.get('phase', '')
            meta_evidence_text_preview = meta.get('evidence_text_preview', '')
            meta_key_people = meta.get('key_people', [])
            meta_keywords = meta.get('keywords', [])
            meta_extracted_dates = meta.get('extracted_dates', [])
            meta_thumbnail = meta.get('thumbnail', '')
            meta_caption_voice = meta.get('caption_voice', '')
            meta_original_exhibit_id = meta.get('original_exhibit_id', '')
            meta_sub_files = meta.get('sub_files', [])
            meta_post_titles = meta.get('post_titles', [])
            meta_file_missing = meta.get('file_missing', False)

            # Inherit post linkages and editorial fields from previous canonical build
            posts = list(meta.get('posts', []))
            map_embed_text = meta.get('embed_text', '')
            map_embed_format = meta.get('embed_format', '')
            map_appendix_text = meta.get('appendix_text', '')
            map_exhibit_type = meta.get('exhibit_type', '')
            map_exhibit_name = meta.get('exhibit_name', '')

            # Also get post links from frontmatter (by exhibit ID)
            if exhibit_id:
                fm_posts = exhibit_to_posts.get(exhibit_id, set())
                for p in fm_posts:
                    if p not in posts:
                        posts.append(p)

            # Generate readable title if we don't have one
            if not title:
                clean = re.sub(r'^[A-Za-z]+-?\d+\.?\d*[a-z]?_\d*_?', '', filename)
                clean = re.sub(r'\.\w+$', '', clean)
                clean = clean.replace('_', ' ').replace('  ', ' ').strip()
                title = clean if clean else filename

            # Use description as text fallback
            if not text and description:
                text = description

            # Normalize tier
            if tier:
                tier = tier.strip().capitalize()
                if tier not in ('Hero', 'Primary', 'Secondary', 'Tertiary'):
                    tier = 'Primary'  # default for known items

            entries.append({
                'exhibit_id': exhibit_id,
                'filename': filename,
                'rel_path': rel_path,
                'title': title,
                'category': category,
                'tier': tier or '',
                'reliability': reliability,
                'posts': sorted(posts, key=lambda x: x.replace('B', '').zfill(4)),
                'extracted_text': text,
                'description': description,
                'is_restored': is_restored,
                'size_bytes': size,
                'extension': filepath.suffix.lower().lstrip('.'),
                # Enrichment from evidence_metadata.json
                'category_key': meta_category_key,
                'file_type': meta_file_type,
                'phase': meta_phase,
                'evidence_text_preview': meta_evidence_text_preview,
                'key_people': meta_key_people or [],
                'keywords': meta_keywords or [],
                'extracted_dates': meta_extracted_dates or [],
                'thumbnail': meta_thumbnail,
                'caption_voice': meta_caption_voice,
                'original_exhibit_id': meta_original_exhibit_id,
                'sub_files': meta_sub_files or [],
                'post_titles': meta_post_titles or [],
                'file_missing': meta_file_missing,
                # Enrichment from v3_evidence_map_v2.json
                'embed_text': map_embed_text,
                'embed_format': map_embed_format,
                'appendix_text': map_appendix_text,
                'exhibit_type': map_exhibit_type,
                'exhibit_name': map_exhibit_name,
                'parent_exhibit': meta.get('parent_exhibit', ''),
            })

    print(f"   PDFs: {pdf_count} found, {pdf_extracted} text extracted")
    return entries, post_data


def generate_markdown(entries, post_data):
    """Generate EVIDENCE_INDEX.md — one section per entry."""
    lines = []
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    lines.append("# EVIDENCE INDEX — ChappaquaPoison v3")
    lines.append("")
    lines.append(f"*Canonical evidence index — {now}*")
    lines.append(f"*Rule: one entry per physical file. Entries = files.*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Stats ──
    total = len(entries)
    with_text = sum(1 for e in entries if e['extracted_text'])
    with_posts = sum(1 for e in entries if e['posts'])
    with_tier = sum(1 for e in entries if e['tier'])
    unique_posts = set()
    for e in entries:
        unique_posts.update(e['posts'])
    unique_eids = set(e['exhibit_id'] for e in entries if e['exhibit_id'])

    tier_counts = {}
    for e in entries:
        t = e['tier'] or 'Untiered'
        tier_counts[t] = tier_counts.get(t, 0) + 1

    cat_counts = {}
    for e in entries:
        cat_counts[e['category']] = cat_counts.get(e['category'], 0) + 1

    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Index entries (= physical files) | {total} |")
    lines.append(f"| Unique exhibit IDs | {len(unique_eids)} |")
    lines.append(f"| Entries with extracted text | {with_text} |")
    lines.append(f"| Entries cross-linked to posts | {with_posts} |")
    lines.append(f"| Unique posts with evidence | {len(unique_posts)} |")
    lines.append(f"| Entries with tier assigned | {with_tier} |")
    lines.append("")
    lines.append("**By tier:**")
    for t, c in sorted(tier_counts.items(), key=lambda x: -x[1]):
        lines.append(f"- {t}: {c}")
    lines.append("")
    lines.append("**By category (top 15):**")
    for c, n in sorted(cat_counts.items(), key=lambda x: -x[1])[:15]:
        lines.append(f"- {c}: {n}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Group by exhibit ID prefix for sections ──
    prefix_names = OrderedDict([
        ('A', 'A — Laboratory & Medical Evidence'),
        ('B', 'B — Court Orders & Judgments'),
        ('BB', 'BB — Brienne Walsh Blog Archive (PDF)'),
        ('BR', 'BR — Brienne Walsh Blog Archive'),
        ('C', 'C — Declarations & Affidavits'),
        ('D', 'D — Discovery & Motions'),
        ('E', 'E — Enforcement & Police Records'),
        ('Ex', 'Ex — Named Exhibits'),
        ('G', 'G — Custody & Family Court'),
        ('H', 'H — Hearing Records & Transcripts'),
        ('K', 'K — Chat / Message Database Evidence'),
        ('L', 'L — Correspondence & Communications'),
    ])

    def get_prefix(eid):
        if not eid:
            return ''
        m = re.match(r'^([A-Za-z]+)', eid)
        return m.group(1).upper() if m else ''

    def sort_key(entry):
        eid = entry['exhibit_id']
        if not eid:
            return ('ZZZZ', 0, entry['filename'])
        m = re.match(r'^([A-Za-z]+)-?(\d+\.?\d*)', eid)
        if m:
            return (m.group(1).upper(), float(m.group(2)), entry['filename'])
        return (eid.upper(), 0, entry['filename'])

    sorted_entries = sorted(entries, key=sort_key)

    # TOC
    lines.append("## Table of Contents")
    lines.append("")
    prefix_entry_counts = {}
    for e in sorted_entries:
        p = get_prefix(e['exhibit_id'])
        if not p:
            p = '_none'
        prefix_entry_counts[p] = prefix_entry_counts.get(p, 0) + 1

    for prefix, name in prefix_names.items():
        count = prefix_entry_counts.get(prefix, 0)
        if count:
            lines.append(f"- [{name}](#{prefix.lower()}) ({count} entries)")
    none_count = prefix_entry_counts.get('_none', 0)
    if none_count:
        lines.append(f"- [Unindexed Files](#unindexed) ({none_count} entries)")

    # Subdirectory-only files
    subdir_count = sum(1 for e in sorted_entries if '/' in e['rel_path'] and not e['exhibit_id'])
    if subdir_count:
        lines.append(f"- [Subdirectory Files Without Exhibit ID](#subdir-unindexed) ({subdir_count} entries)")

    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Entries ──
    current_prefix = None
    entry_num = 0

    for entry in sorted_entries:
        prefix = get_prefix(entry['exhibit_id'])
        if not prefix:
            prefix = '_none'

        # Section header
        if prefix != current_prefix:
            current_prefix = prefix
            if prefix == '_none':
                lines.append("## Unindexed Files")
                lines.append("")
                lines.append("*Files without exhibit ID prefix.*")
            else:
                section_name = prefix_names.get(prefix, f'{prefix} — Evidence')
                lines.append(f"## {section_name}")
            lines.append("")

        entry_num += 1
        eid = entry['exhibit_id'] or f"[no-id-{entry_num}]"
        title = entry['title']
        tier = entry['tier'] or 'Untiered'
        category = entry['category']
        reliability = entry['reliability']

        # Post display
        post_strs = []
        for pid in entry['posts']:
            ptitle = post_data.get(pid, {}).get('title', '')
            post_strs.append(f"{pid} ({ptitle})" if ptitle else pid)

        lines.append(f"### {eid} — {title}")
        lines.append("")
        lines.append(f"**File:** `{entry['rel_path']}`")
        lines.append(f"**Category:** {category}")
        lines.append(f"**Tier:** {tier}")
        lines.append(f"**Reliability:** {reliability}")
        if post_strs:
            lines.append(f"**Posts:** {', '.join(post_strs)}")
        else:
            lines.append(f"**Posts:** *(not yet linked)*")
        if entry['is_restored']:
            lines.append(f"**Note:** Restored from `_removed_2026-03-04/` — verify not a duplicate.")
        lines.append("")

        # Extracted text
        text = entry['extracted_text']
        if text:
            # Quote as blockquote, limit lines
            quote_lines = text.strip().split('\n')
            for ql in quote_lines[:12]:
                line = ql.strip()
                if line:
                    lines.append(f"> {line}")
            if len(quote_lines) > 12:
                lines.append(f"> *[...{len(quote_lines) - 12} more lines]*")
        else:
            ext_label = entry['extension'].upper()
            lines.append(f"> *[Text extraction pending — {ext_label} file, {entry['size_bytes']//1024}KB]*")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Footer
    lines.append(f"*Generated: {now}*")
    lines.append(f"*Physical files: {total} | Exhibit IDs: {len(unique_eids)} | Posts linked: {len(unique_posts)}*")
    lines.append(f"*This is the canonical evidence index. Replaces v3_Evidence_Archive.md, KEY_EVIDENCE.md, and Evidence/INDEX.md.*")

    return '\n'.join(lines)


def main():
    dry_run = '--dry-run' in sys.argv
    skip_pdf = '--no-pdf' in sys.argv

    print("=" * 60)
    print("Building canonical evidence index (1:1 model)")
    print("=" * 60)
    print()

    print("1. Scanning files and extracting text...")
    if skip_pdf:
        print("   (PDF extraction skipped — use without --no-pdf for full extraction)")
    entries, post_data = scan_and_build(skip_pdf=skip_pdf)
    print(f"   Total entries: {len(entries)}")

    print("\n2. Generating index...")
    md = generate_markdown(entries, post_data)

    if dry_run:
        print(f"\n[DRY RUN] Would write {len(md):,} chars ({md.count(chr(10))} lines)")
        print(f"[DRY RUN] First 3000 chars:\n")
        print(md[:3000])
    else:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(md, encoding='utf-8')
        line_count = md.count('\n')
        print(f"\n✅ {OUTPUT_FILE}")
        print(f"   {line_count:,} lines, {len(md):,} chars")

        # JSON companion
        json_data = {
            'generated': datetime.now().isoformat(),
            'total_entries': len(entries),
            'entries': [{
                'exhibit_id': e['exhibit_id'],
                'filename': e['filename'],
                'rel_path': e['rel_path'],
                'title': e['title'],
                'category': e['category'],
                'tier': e['tier'],
                'reliability': e['reliability'],
                'posts': e['posts'],
                'has_text': bool(e['extracted_text']),
                'is_restored': e['is_restored'],
                'size_bytes': e['size_bytes'],
                'extension': e.get('extension', ''),
                # Enrichment fields from evidence_metadata.json
                'description': e.get('description', ''),
                'category_key': e.get('category_key', ''),
                'file_type': e.get('file_type', ''),
                'phase': e.get('phase', ''),
                'evidence_text_preview': e.get('evidence_text_preview', ''),
                'key_people': e.get('key_people', []),
                'keywords': e.get('keywords', []),
                'extracted_dates': e.get('extracted_dates', []),
                'thumbnail': e.get('thumbnail', ''),
                'caption_voice': e.get('caption_voice', ''),
                'original_exhibit_id': e.get('original_exhibit_id', ''),
                'sub_files': e.get('sub_files', []),
                'post_titles': e.get('post_titles', []),
                'file_missing': e.get('file_missing', False),
                # Enrichment fields from v3_evidence_map_v2.json
                'embed_text': e.get('embed_text', ''),
                'embed_format': e.get('embed_format', ''),
                'appendix_text': e.get('appendix_text', ''),
                'exhibit_type': e.get('exhibit_type', ''),
                'exhibit_name': e.get('exhibit_name', ''),
                'parent_exhibit': e.get('parent_exhibit', ''),
            } for e in entries],
        }

        # Preserve virtual entries (phantom exhibits without physical files)
        # These were added manually for exhibits referenced in posts but not in Evidence/
        if OUTPUT_JSON.exists():
            try:
                with open(OUTPUT_JSON) as prev_f:
                    prev_data = json.load(prev_f)
                scanned_filenames = {e['filename'] for e in json_data['entries']}
                for prev_entry in prev_data.get('entries', []):
                    if prev_entry.get('file_type') == 'virtual' and prev_entry['filename'] not in scanned_filenames:
                        json_data['entries'].append(prev_entry)
                        json_data['total_entries'] = len(json_data['entries'])
                        print(f"   Preserved virtual entry: {prev_entry.get('exhibit_id')}")
            except Exception:
                pass

        with open(OUTPUT_JSON, 'w') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print(f"✅ {OUTPUT_JSON}")

    # Gap report
    print("\n3. Gap analysis:")
    no_text = [e for e in entries if not e['extracted_text']]
    no_posts = [e for e in entries if not e['posts']]
    no_tier = [e for e in entries if not e['tier']]
    no_eid = [e for e in entries if not e['exhibit_id']]

    print(f"   Without extracted text: {len(no_text)}/{len(entries)}")
    print(f"   Not linked to any post: {len(no_posts)}/{len(entries)}")
    print(f"   Without tier: {len(no_tier)}/{len(entries)}")
    print(f"   Without exhibit ID: {len(no_eid)}/{len(entries)}")

    # Verification: entries == files (excluding _removed archive)
    file_count = 0
    for root_dir, dirs, files in os.walk(EVIDENCE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('_removed')]
        for f in files:
            if f not in SKIP_FILES and not f.startswith('.') and f not in META_FILES:
                file_count += 1
    if len(entries) == file_count:
        print(f"\n   ✅ VERIFIED: entries ({len(entries)}) == files ({file_count})")
    else:
        print(f"\n   ⚠️  MISMATCH: entries ({len(entries)}) != files ({file_count})")

    if no_text:
        print(f"\n   Top 10 needing text extraction:")
        for e in sorted(no_text, key=lambda x: -x['size_bytes'])[:10]:
            print(f"     {e['exhibit_id'] or '???'}: {e['filename'][:55]} ({e['size_bytes']//1024}KB, {e['extension']})")


if __name__ == '__main__':
    main()
