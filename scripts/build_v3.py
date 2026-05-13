#!/usr/bin/env python3
"""
build_v3.py — Generate v3 infrastructure from BLOG_ARCHITECTURE_v4.md

# ⚠ DEPRECATED: posts_v3.json has been merged into posts.json and retired to
# Archive/superseded_evidence_files/. The single source of truth is now posts.json.
# This script's output (posts_v3.json) is no longer used by the build pipeline.

Creates:
  1. posts_v3.json — 45-beat master index (DEPRECATED — merged into posts.json)
  2. Batch A singles — copies 1:1 posts into posts/md/beats/
  3. Batch E stubs — creates placeholder files for new beats

Usage:
  python scripts/build_v3.py              # Generate posts_v3.json + Batch A + E
  python scripts/build_v3.py --json-only  # Only generate posts_v3.json
"""

import json
import os
import sys
import re
import shutil
from pathlib import Path
from collections import OrderedDict

ROOT = Path(__file__).resolve().parent.parent
POSTS_JSON = ROOT / 'posts.json'
POSTS_V3_JSON = ROOT / 'posts_v3.json'
MD_DIR = ROOT / 'posts' / 'md'
BEATS_DIR = ROOT / 'posts' / 'md' / 'beats'

# ─── Beat definitions from BLOG_ARCHITECTURE_v4.md ───

ACTS = {
    'I':   'The Fool',
    'II':  'The Evidence',
    'III': 'The Pivot',
    'IV':  'The System',
    'V':   'The Obstruction',
    'VI':  'The Reckoning Begins',
    'VII': 'The Verdict',
    'VIII':'The Reckoning',
    'IX':  'The Record',
}

# Map old phases to act colors (reuse existing phase colors for visual continuity)
ACT_TO_PHASE = {
    'I': 'I',      # Before Tara -> The Fool
    'II': 'III',    # Criminal Events -> The Evidence
    'III': 'III',   # Criminal Events -> The Pivot
    'IV': 'IV',     # Custody Begins -> The System
    'V': 'V',       # Cover-up -> The Obstruction
    'VI': 'VI',     # Gag Orders -> The Reckoning Begins
    'VII': 'VII',   # Trial -> The Verdict
    'VIII': 'VIII', # Civil Rights -> The Reckoning
    'IX': 'IX',     # Archive -> The Record
}

BEATS = [
    # (beat_num, title, slug, act, source_posts, merge_type, date_context)
    (1,  "Moscow, 2010", "moscow-2010", "I", ["P0"], "none", "May 2010"),
    (2,  "What Happened at Uber", "what-happened-at-uber", "I", [], "new", "2014–2017"),
    (3,  "The Ukraine Job", "the-ukraine-job", "I", [], "new", "2013–2018"),
    (4,  "The Boat on the Hudson", "the-boat-on-the-hudson", "I", ["P16"], "new-fold", "2015–2017"),
    (5,  "A House Called Tara Knoll", "a-house-called-tara-knoll", "I", ["P3", "P4", "P4B"], "medium", "2015–2017"),
    (6,  "Four Witnesses", "four-witnesses", "I", ["P6"], "none", "Pre-2018"),
    (7,  "The Psychiatrist Who Got It Right", "the-psychiatrist-who-got-it-right", "II", ["P7"], "none", "2017–2018"),
    (8,  "How the Drugging Worked", "how-the-drugging-worked", "II", ["P8", "P9", "P10"], "medium", "May–December 2017"),
    (9,  "The Double Life", "the-double-life", "II", ["P13", "P81", "P83", "P11", "P13B"], "heavy", "2016–2018"),
    (10, "You Shouldn't Be Here", "you-shouldnt-be-here", "II", [], "new", "2017"),
    (11, "January 27, 2018", "january-27-2018", "II", ["P14", "P15"], "light", "January 2018"),
    (12, "The Body as Evidence", "the-body-as-evidence", "II", ["P12", "P22", "P22B", "P22C"], "medium", "2017–2018"),
    (13, "She Asked Me to Put Drugs in Your Wine", "she-asked-me-to-put-drugs-in-your-wine", "III", ["P17", "P19"], "light", "January 2018"),
    (14, "I Made Up the Whole Thing", "i-made-up-the-whole-thing", "III", ["P18"], "none", "January 2018"),
    (15, "The Trip That Never Ended", "the-trip-that-never-ended", "III", ["P23"], "none", "February 2018"),
    (16, "Six Declarations", "six-declarations", "III", ["P20", "P21"], "light", "July 2018"),
    (17, "The Attic", "the-attic", "III", ["P24"], "none", "2018"),
    (18, "Two Courts, One Child", "two-courts-one-child", "IV", ["P25", "P27", "P27B"], "medium", "2018"),
    (19, "Then the Letter Vanishes", "then-the-letter-vanishes", "IV", ["P26"], "none", "2018"),
    (20, "Your Daughter or Your Rights", "your-daughter-or-your-rights", "IV", ["P28", "P28B", "P78", "P79", "P80"], "heavy", "2018–2019"),
    (21, "The Captured Court", "the-captured-court", "IV", ["P29", "P30", "P31", "P32", "P33", "P41B", "P41H"], "heavy", "2018–2020"),
    (22, "Under Oath", "under-oath", "V", ["P41C", "P41D", "P41E"], "medium", "2019–2020"),
    (23, "One Hearing, Three Descriptions", "one-hearing-three-descriptions", "V", ["P35", "P35B", "P36", "P37", "P37B"], "heavy", "2019"),
    (24, "Obstruction", "obstruction", "V", ["P34", "P38", "P39", "P40", "P41", "P41F", "P41G", "P74", "P75"], "heavy", "2019–2020"),
    (25, "Doesn't Daddy Miss Me?", "doesnt-daddy-miss-me", "V", ["P40B"], "none", "2019"),
    (26, "The Permanent DVRO", "the-permanent-dvro", "VI", ["P41I"], "none", "2020"),
    (27, "Three Judges Walk Away", "three-judges-walk-away", "VI", ["P42", "P48D"], "light", "2020–2021"),
    (28, "Erase, Deactivate, and Delete", "erase-deactivate-and-delete", "VI", ["P43", "P44", "P46"], "medium", "2020–2021"),
    (29, "The Appellate Reversal", "the-appellate-reversal", "VI", ["P45"], "none", "2021"),
    (30, "A Dollar for the Story", "a-dollar-for-the-story", "VI", [], "new", "2021"),
    (31, "Not a Victim of Any Crime", "not-a-victim-of-any-crime", "VI", ["P47"], "none", "2021"),
    (32, "Drop the Lawsuit", "drop-the-lawsuit", "VII", ["P48", "P48B", "P48C", "P77"], "medium", "2021–2022"),
    (33, "If They Could Just See the Evidence", "if-they-could-just-see-the-evidence", "VII", ["P49", "P49B"], "light-new", "2022"),
    (34, "What Twelve People Saw", "what-twelve-people-saw", "VII", ["P50", "P51"], "light", "2022"),
    (35, "What the Jury Found", "what-the-jury-found", "VII", ["P52", "P53", "P54", "P55", "P56"], "heavy", "2022–2023"),
    (36, "We Were Hit", "we-were-hit", "VII", ["P57"], "none", "2023"),
    (37, "Buy a House or You Don't See Your Daughter", "buy-a-house", "VIII", ["P65", "P76"], "light", "2023"),
    (38, "The Motion to Undo Everything", "the-motion-to-undo-everything", "VIII", ["P58", "P59", "P60", "P61", "P63"], "medium-plus", "2024–2025"),
    (39, "Three Versions of the Same Order", "three-versions-of-the-same-order", "VIII", ["P62", "P64"], "light", "2024–2026"),
    (40, "The Investigation", "the-investigation", "VIII", ["P66", "P66B", "P66C", "P66D", "P82"], "heavy", "2025–2026"),
    (41, "They Took His Daughter Because He Spoke", "they-took-his-daughter-because-he-spoke", "VIII", ["P67"], "none", "2025"),
    (42, "The Silence and the Questions", "the-silence-and-the-questions", "IX", ["P68", "P69", "P70"], "medium", "2024–2026"),
    (43, "Twenty-One Patterns, One Case", "twenty-one-patterns-one-case", "IX", ["P73"], "none", "2024–2026"),
    (44, "The Record Is Open", "the-record-is-open", "IX", ["P71"], "none", "2026"),
    (45, "For Evie", "for-evie", "IX", ["P72"], "none", "2026"),
]


def load_v2_posts():
    """Load existing posts.json and build lookup by ID"""
    with open(POSTS_JSON, 'r') as f:
        data = json.load(f)
    posts_by_id = {}
    for p in data.get('posts', []):
        posts_by_id[p['id']] = p
    return data, posts_by_id


def merge_tags(source_posts, posts_by_id):
    """Merge tags from all source posts, dedup, sorted"""
    tags = []
    seen = set()
    for pid in source_posts:
        post = posts_by_id.get(pid, {})
        for tag in post.get('tags', []):
            if tag not in seen:
                tags.append(tag)
                seen.add(tag)
    return tags


def merge_evidence(source_posts, posts_by_id):
    """Merge evidence from all source posts"""
    all_evidence = {
        'timeline': '',
        'supporting_documents': '',
        'collected_files': [],
        'editor_note': '',
        'source_note': None,
    }
    timelines = []
    support_docs = []
    collected = []
    editor_notes = []
    seen_files = set()

    for pid in source_posts:
        post = posts_by_id.get(pid, {})
        ev = post.get('evidence', {})
        if isinstance(ev, dict):
            if ev.get('timeline'):
                timelines.append(ev['timeline'])
            if ev.get('supporting_documents'):
                support_docs.append(ev['supporting_documents'])
            for f in ev.get('collected_files', []):
                if f not in seen_files:
                    collected.append(f)
                    seen_files.add(f)
            if ev.get('editor_note'):
                editor_notes.append(ev['editor_note'])

    if timelines:
        all_evidence['timeline'] = '; '.join(timelines)
    if support_docs:
        all_evidence['supporting_documents'] = '; '.join(support_docs)
    if collected:
        all_evidence['collected_files'] = collected
    if editor_notes:
        all_evidence['editor_note'] = ' '.join(editor_notes)

    return all_evidence


def compute_ecs(source_posts, posts_by_id):
    """Compute ECS as max of source posts"""
    scores = []
    for pid in source_posts:
        post = posts_by_id.get(pid, {})
        ecs = post.get('ecs')
        if ecs is not None:
            scores.append(ecs)
    return max(scores) if scores else None


def merge_cross_links(source_posts, posts_by_id):
    """Merge cross_links from sources, excluding sources themselves"""
    links = []
    seen = set(source_posts)
    for pid in source_posts:
        post = posts_by_id.get(pid, {})
        for cl in post.get('cross_links', []):
            if cl not in seen:
                links.append(cl)
                seen.add(cl)
    return links


def merge_photos(source_posts, posts_by_id):
    """Merge photos from source posts"""
    photos = []
    seen = set()
    for pid in source_posts:
        post = posts_by_id.get(pid, {})
        for photo in post.get('photos', []):
            key = photo.get('file', '')
            if key and key not in seen:
                photos.append(photo)
                seen.add(key)
    return photos


def generate_posts_v3():
    """Generate the 45-beat posts_v3.json"""
    v2_data, posts_by_id = load_v2_posts()

    beats_json = []
    for beat_num, title, slug, act, source_posts, merge_type, date_ctx in BEATS:
        # Build the beat entry
        beat = OrderedDict()
        beat['id'] = f"B{beat_num:02d}"
        beat['number'] = beat_num
        beat['title'] = title
        beat['slug'] = slug
        beat['act'] = act
        beat['act_name'] = ACTS.get(act, f'Act {act}')
        # Map act to phase for color compatibility
        beat['phase'] = ACT_TO_PHASE.get(act, act)
        beat['phase_name'] = beat['act_name']
        beat['date_context'] = date_ctx
        beat['source_posts'] = source_posts
        beat['merge_type'] = merge_type

        if source_posts:
            # Derive summary from primary source post
            primary = posts_by_id.get(source_posts[0], {})
            beat['summary'] = primary.get('summary', '')
            beat['tags'] = merge_tags(source_posts, posts_by_id)
            beat['ecs'] = compute_ecs(source_posts, posts_by_id)
            beat['evidence'] = merge_evidence(source_posts, posts_by_id)
            beat['cross_links'] = merge_cross_links(source_posts, posts_by_id)
            beat['photos'] = merge_photos(source_posts, posts_by_id)
        else:
            # New beat — stub
            beat['summary'] = f"[NEEDS AUTHOR INPUT] {title}"
            beat['tags'] = []
            beat['ecs'] = None
            beat['evidence'] = {
                'timeline': date_ctx,
                'supporting_documents': '',
                'collected_files': [],
                'editor_note': 'Stub beat — awaiting author content.',
                'source_note': None,
            }
            beat['cross_links'] = []
            beat['photos'] = []

        # Status tracking
        if merge_type == 'none' and source_posts:
            beat['status'] = 'ready'
        elif merge_type == 'new' or not source_posts:
            beat['status'] = 'stub-needs-author'
        else:
            beat['status'] = 'pending-merge'

        beats_json.append(beat)

    # Build output structure (mirrors posts.json)
    output = OrderedDict()
    output['version'] = 'v3'
    output['architecture'] = 'BLOG_ARCHITECTURE_v4.md'
    output['beat_count'] = len(beats_json)
    output['static_pages'] = v2_data.get('static_pages', [])
    output['posts'] = beats_json

    with open(POSTS_V3_JSON, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✓ Generated {POSTS_V3_JSON} with {len(beats_json)} beats")
    return beats_json


def find_source_file(post_id, md_dir):
    """Find the markdown file for a given post ID"""
    for md_file in md_dir.glob(f"{post_id}_*.md"):
        return md_file
    return None


def copy_singles(beats):
    """Batch A: Copy single-source beats into beats/ dir with updated YAML"""
    BEATS_DIR.mkdir(parents=True, exist_ok=True)
    singles_count = 0

    for beat in beats:
        if beat['merge_type'] != 'none' or not beat['source_posts']:
            continue

        source_id = beat['source_posts'][0]
        source_file = find_source_file(source_id, MD_DIR)

        if not source_file:
            print(f"  ⚠ Beat {beat['number']} ({beat['title']}): source {source_id} not found")
            continue

        # Read source file
        raw = source_file.read_text(encoding='utf-8')

        # Replace YAML front matter with v3 version
        new_yaml = f'''---
title: "{beat['title']}"
id: {beat['id']}
number: {beat['number']}
beat: {beat['number']}
act: "{beat['act']}"
act_name: "{beat['act_name']}"
date: "{beat['date_context']}"
phase: "{beat['phase']}"
phase_name: "{beat['phase_name']}"
source_posts:
{chr(10).join(f"  - {sp}" for sp in beat['source_posts'])}
tags:
{chr(10).join(f'  - "{t}"' for t in beat.get('tags', []))}
ecs: {beat.get('ecs') or 'null'}
'''
        # Preserve provenance from source
        if '---' in raw:
            parts = raw.split('---', 2)
            if len(parts) >= 3:
                import yaml
                try:
                    src_meta = yaml.safe_load(parts[1])
                    if src_meta and src_meta.get('provenance'):
                        provenance = src_meta['provenance']
                        new_yaml += f"provenance:\n"
                        for p in provenance:
                            new_yaml += f"  - {p}\n"
                    if src_meta and src_meta.get('related_posts'):
                        new_yaml += f"related_posts:\n"
                        for rp in src_meta['related_posts']:
                            new_yaml += f"  - {rp}\n"
                    if src_meta and src_meta.get('evidence'):
                        if isinstance(src_meta['evidence'], list):
                            new_yaml += f"evidence:\n"
                            for ev in src_meta['evidence']:
                                if isinstance(ev, dict) and 'exhibit' in ev:
                                    new_yaml += f'  - exhibit: "{ev["exhibit"]}"\n'
                    if src_meta and src_meta.get('media'):
                        new_yaml += f"media:\n"
                        for m in src_meta['media']:
                            if isinstance(m, dict):
                                new_yaml += f"  - path: \"{m.get('path', '')}\"\n"
                                if m.get('caption'):
                                    new_yaml += f"    caption: \"{m['caption']}\"\n"
                            else:
                                new_yaml += f"  - \"{m}\"\n"
                except Exception:
                    pass

                body = parts[2]
            else:
                body = raw
        else:
            body = raw

        new_yaml += '---'
        output = new_yaml + body

        # Write to beats dir
        beat_slug = beat['slug']
        out_file = BEATS_DIR / f"B{beat['number']:02d}_{beat_slug}.md"
        out_file.write_text(output, encoding='utf-8')
        singles_count += 1
        print(f"  ✓ Beat {beat['number']:2d}: {beat['title']} ← {source_id}")

    print(f"\n✓ Batch A: {singles_count} single-post beats copied")
    return singles_count


def create_stubs(beats):
    """Batch E: Create placeholder files for new/stub beats"""
    BEATS_DIR.mkdir(parents=True, exist_ok=True)
    stubs_count = 0

    for beat in beats:
        if beat['status'] != 'stub-needs-author':
            continue

        stub_content = f'''---
title: "{beat['title']}"
id: {beat['id']}
number: {beat['number']}
beat: {beat['number']}
act: "{beat['act']}"
act_name: "{beat['act_name']}"
date: "{beat['date_context']}"
phase: "{beat['phase']}"
phase_name: "{beat['phase_name']}"
status: draft-needs-author
tags: []
ecs: null
evidence: []
---

# {beat['title']}

*[This beat requires author input. See BLOG_ARCHITECTURE_v4.md Beat {beat['number']} for description and source notes.]*

---

**Architecture notes:**

'''
        # Add beat-specific notes
        if beat['number'] == 2:
            stub_content += """This beat covers Russell's time at Uber during the Kalanick era.
Draw from: news coverage, author testimony, digital artifacts.
Key question: What happened to Travis, Shervin, and Russell at the same time?
"""
        elif beat['number'] == 3:
            stub_content += """This beat covers Russell's work in Ukraine for Jamie Siminoff / Ring.
Draw from: news coverage, author testimony, Ring/Amazon acquisition timeline.
Key question: Russell went to Ukraine, busted his butt. Jamie sold to Amazon for a billion. Was Russell used?
"""
        elif beat['number'] == 10:
            stub_content += """This beat covers Russell's hospitalization. "You shouldn't be here."
Draw from: Book Chapter 8, medical records, Dr. Gopal connection.
The hospital confirms what Gopal said — the psychiatric characterization was manufactured.
"""
        elif beat['number'] == 30:
            stub_content += """This beat covers the Petrella / ChappaquaPoison podcast story.
Evidence: ExPetrella (death threat email from Tara Walsh, Nov 16, 2021).
Key quote: "you are putting yourself in harm's way by doing so"
Archive Character #4: The Podcast — reporter threatened, sold back rights, evidence survived.
"""

        beat_slug = beat['slug']
        out_file = BEATS_DIR / f"B{beat['number']:02d}_{beat_slug}.md"
        out_file.write_text(stub_content, encoding='utf-8')
        stubs_count += 1
        print(f"  ✓ Beat {beat['number']:2d}: {beat['title']} [STUB]")

    # Also handle Beat 4 (partial — has P16 as source but needs book material)
    beat4 = next((b for b in beats if b['number'] == 4), None)
    if beat4:
        source_file = find_source_file('P16', MD_DIR)
        if source_file:
            raw = source_file.read_text(encoding='utf-8')
            # Extract body
            if '---' in raw:
                parts = raw.split('---', 2)
                body = parts[2] if len(parts) >= 3 else raw
            else:
                body = raw

            stub_content = f'''---
title: "{beat4['title']}"
id: {beat4['id']}
number: {beat4['number']}
beat: {beat4['number']}
act: "{beat4['act']}"
act_name: "{beat4['act_name']}"
date: "{beat4['date_context']}"
phase: "{beat4['phase']}"
phase_name: "{beat4['phase_name']}"
status: draft-partial
source_posts:
  - P16
tags:
{chr(10).join(f'  - "{t}"' for t in beat4.get('tags', []))}
ecs: {beat4.get('ecs') or 'null'}
evidence: []
---

<!-- PARTIAL DRAFT: P16 content below. Needs book material about Russell's entry into Walsh's world. -->
<!-- Architecture notes: "He was drawn into Walsh's world. He paid for everything." -->
<!-- Pre-birth parenting commitments: Jan 8, 2018 text, $20K wire, CRC Kids template. -->

{body}
'''
            out_file = BEATS_DIR / f"B{beat4['number']:02d}_{beat4['slug']}.md"
            out_file.write_text(stub_content, encoding='utf-8')
            stubs_count += 1
            print(f"  ✓ Beat  4: {beat4['title']} [PARTIAL from P16]")

    print(f"\n✓ Batch E: {stubs_count} stub/partial beats created")
    return stubs_count


def print_summary(beats):
    """Print build summary"""
    print("\n" + "=" * 60)
    print("v3 BUILD SUMMARY")
    print("=" * 60)

    status_counts = {}
    for b in beats:
        s = b.get('status', 'unknown')
        status_counts[s] = status_counts.get(s, 0) + 1

    for status, count in sorted(status_counts.items()):
        print(f"  {status:25s}: {count}")

    # Check what files exist in beats/
    existing = list(BEATS_DIR.glob('B*_*.md'))
    print(f"\n  Files in beats/: {len(existing)}/45")

    # List missing
    existing_nums = set()
    for f in existing:
        m = re.match(r'B(\d+)_', f.name)
        if m:
            existing_nums.add(int(m.group(1)))

    missing = [b for b in range(1, 46) if b not in existing_nums]
    if missing:
        print(f"  Missing beats: {', '.join(str(m) for m in missing)}")
    else:
        print("  All 45 beats have files!")

    # Check afterword
    afterword_file = md_dir / 'afterword.md'
    if afterword_file.exists():
        print("  Afterword file present ✓")
    else:
        print("  ⚠ afterword.md missing from posts/md/")

    print("=" * 60)


if __name__ == '__main__':
    json_only = '--json-only' in sys.argv

    print("Building v3 infrastructure...")
    print()

    # Step 1: Generate posts_v3.json
    beats = generate_posts_v3()

    if not json_only:
        print()
        # Step 2: Copy singles (Batch A)
        print("Batch A — Single-post beats:")
        copy_singles(beats)

        print()
        # Step 3: Create stubs (Batch E)
        print("Batch E — Stub/new beats:")
        create_stubs(beats)

    print_summary(beats)
