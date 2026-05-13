#!/usr/bin/env python3
"""
fix_index_quality.py — Normalize categories, fix reliability mismatches,
propagate phases to linked entries, and clean up the canonical evidence index.

Based on the rendering audit of 2026-03-16.
"""

import json
import re
from pathlib import Path
from collections import Counter

INDEX = Path(__file__).parent.parent / 'evidence_index_canonical.json'

with open(INDEX) as f:
    data = json.load(f)

entries = data['entries']
total = len(entries)

# ═══════════════════════════════════════════════════════════════
# 1. CATEGORY CONSOLIDATION — 29 categories → 15
# ═══════════════════════════════════════════════════════════════

CATEGORY_MAP = {
    # Video fragments → unified
    'Video Clip': 'Video Evidence',
    'Video Clip — Brendan Walsh Deposition': 'Video Evidence',
    'Video Clip — Gavish Deposition': 'Video Evidence',
    'Video Clip — Maura Walsh Deposition': 'Video Evidence',
    'Video Clip — Stephen Russell Deposition': 'Video Evidence',
    'Video Recording': 'Video Evidence',
    # Email → Correspondence
    'Email': 'Correspondence',
    # Court motions/memos → Court Filing
    'Court Motion': 'Court Filing',
    'Legal Memorandum': 'Court Filing',
    # Internal docs → Document
    'Markdown Document': 'Document',
    'Import Document': 'Document',
    'Journal / Publication': 'Document',
    'Uncategorized': 'Document',
    'Investigative Report': 'Document',
    # Court Transcript → Deposition & Testimony
    'Court Transcript': 'Deposition & Testimony',
    'Deposition': 'Deposition & Testimony',
    # Blog Archive name cleanup
    'Blog Archive (Brienne Walsh)': 'Blog Archive',
    # Text message stays distinct (different provenance from email/letters)
    # 'Text Message / Chat Record': keep as-is
}

cat_changes = 0
for e in entries:
    old = e.get('category', '')
    if old in CATEGORY_MAP:
        e['category'] = CATEGORY_MAP[old]
        cat_changes += 1

print(f"1. Category consolidation: {cat_changes} entries remapped")

# Verify new category count
new_cats = sorted(set(e.get('category','') for e in entries))
print(f"   Categories: {len(new_cats)} (was 29)")
for cat in new_cats:
    count = sum(1 for e in entries if e.get('category') == cat)
    print(f"     {count:4d}  {cat}")

# ═══════════════════════════════════════════════════════════════
# 2. RELIABILITY FIXES — correct mismatches by category
# ═══════════════════════════════════════════════════════════════

rel_fixes = 0

for e in entries:
    cat = e.get('category', '')
    rel = e.get('reliability', '')
    eid = e.get('exhibit_id', '')

    # Lab reports → Laboratory Analysis
    if cat == 'Laboratory Analysis' and rel != 'Laboratory Analysis':
        e['reliability'] = 'Laboratory Analysis'
        rel_fixes += 1

    # Depositions → Sworn Under Oath
    if cat == 'Deposition & Testimony' and rel not in ('Sworn Under Oath', 'Sworn Testimony', 'Court Record'):
        e['reliability'] = 'Sworn Under Oath'
        rel_fixes += 1

    # Court Orders → Court Record
    if cat == 'Court Order / Judgment' and rel not in ('Court Record', 'Court-Certified'):
        e['reliability'] = 'Court Record'
        rel_fixes += 1

    # Court Filings → Court Record
    if cat == 'Court Filing' and rel not in ('Court Record', 'Court-Certified'):
        e['reliability'] = 'Court Record'
        rel_fixes += 1

    # Police Reports → Official Report
    if cat == 'Police Report' and rel not in ('Official Report', 'Court Record'):
        e['reliability'] = 'Official Report'
        rel_fixes += 1

    # Sworn Declarations → Sworn Under Oath
    if cat == 'Sworn Declaration' and rel not in ('Sworn Under Oath', 'Sworn Testimony', 'Court Record'):
        e['reliability'] = 'Sworn Under Oath'
        rel_fixes += 1

    # Video Evidence with "Deposition" in title → Sworn Under Oath
    if cat == 'Video Evidence' and 'Deposition' in (e.get('title', '') + e.get('description', '')) and rel != 'Sworn Under Oath':
        e['reliability'] = 'Sworn Under Oath'
        rel_fixes += 1

    # Merge 'Sworn Testimony' → 'Sworn Under Oath' (normalize)
    if rel == 'Sworn Testimony':
        e['reliability'] = 'Sworn Under Oath'
        rel_fixes += 1

    # 'Blog / Online Archive' → 'Published Record'
    if rel == 'Blog / Online Archive':
        e['reliability'] = 'Published Record'
        rel_fixes += 1

print(f"\n2. Reliability fixes: {rel_fixes} entries corrected")

# Show final reliability distribution
new_rels = Counter(e.get('reliability','') for e in entries)
print(f"   Reliability tiers: {len(new_rels)}")
for rel, count in new_rels.most_common():
    print(f"     {count:4d}  {rel}")

# ═══════════════════════════════════════════════════════════════
# 3. PHASE PROPAGATION — infer phases from linked posts
# ═══════════════════════════════════════════════════════════════

# Load posts.json to get phase for each post
posts_json = Path(__file__).parent.parent / 'posts.json'
with open(posts_json) as f:
    posts_data = json.load(f)

post_phases = {}
for p in posts_data.get('posts', []):
    post_phases[p['id']] = p.get('phase', '')

phase_fills = 0
for e in entries:
    if e.get('phase'):
        continue  # already has a phase
    linked_posts = e.get('posts', [])
    if not linked_posts:
        continue
    # Use the phase from the earliest linked post
    phases_seen = []
    for pid in linked_posts:
        if pid in post_phases and post_phases[pid]:
            phases_seen.append(post_phases[pid])
    if phases_seen:
        # Pick the most common phase, or first if tied
        phase_counter = Counter(phases_seen)
        e['phase'] = phase_counter.most_common(1)[0][0]
        phase_fills += 1

print(f"\n3. Phase propagation: {phase_fills} entries got phases from linked posts")
phase_dist = Counter(e.get('phase','') or '(empty)' for e in entries)
print(f"   Entries with phase: {sum(1 for e in entries if e.get('phase'))}/{total}")

# ═══════════════════════════════════════════════════════════════
# 4. TIER ASSIGNMENT — entries linked to posts should have tiers
# ═══════════════════════════════════════════════════════════════

tier_fills = 0
for e in entries:
    if e.get('tier'):
        continue
    if not e.get('posts'):
        continue
    # Linked but no tier — assign based on category
    cat = e.get('category', '')
    if cat in ('Laboratory Analysis', 'Court Order / Judgment', 'Sworn Declaration'):
        e['tier'] = 'Primary'
    elif cat in ('Deposition & Testimony', 'Court Filing', 'Police Report'):
        e['tier'] = 'Primary'
    elif cat in ('Correspondence', 'Text Message / Chat Record', 'Audio Recording'):
        e['tier'] = 'Primary'
    else:
        e['tier'] = 'Secondary'
    tier_fills += 1

print(f"\n4. Tier assignment: {tier_fills} linked entries got tiers")
tier_dist = Counter(e.get('tier','') or '(empty)' for e in entries)
print(f"   Tier distribution:")
for t, c in tier_dist.most_common():
    print(f"     {c:4d}  {t}")

# ═══════════════════════════════════════════════════════════════
# 5. EXHIBIT ID CLEANUP — generate IDs for the 209 entries without one
# ═══════════════════════════════════════════════════════════════

no_eid = [e for e in entries if not e.get('exhibit_id')]
eid_assigned = 0

# Generate a prefix based on category
CAT_PREFIX = {
    'Correspondence': 'CORR',
    'Document': 'DOC',
    'Media Coverage': 'MED',
    'Court Filing': 'CF',
    'Court Order / Judgment': 'CO',
    'Photograph': 'PH',
    'Blog Archive': 'BLOG',
    'Deposition & Testimony': 'DEPO',
    'Sworn Declaration': 'DECL',
    'Text Message / Chat Record': 'MSG',
    'Audio Recording': 'AUD',
    'Video Evidence': 'VID',
    'Police Report': 'PR',
    'Laboratory Analysis': 'LAB',
}

# Track existing IDs to avoid collisions
existing_eids = set(e.get('exhibit_id','') for e in entries if e.get('exhibit_id'))
prefix_counters = Counter()

for e in no_eid:
    cat = e.get('category', 'Document')
    prefix = CAT_PREFIX.get(cat, 'MISC')
    prefix_counters[prefix] += 1
    new_id = f"{prefix}-{prefix_counters[prefix]:03d}"
    while new_id in existing_eids:
        prefix_counters[prefix] += 1
        new_id = f"{prefix}-{prefix_counters[prefix]:03d}"
    e['exhibit_id'] = new_id
    existing_eids.add(new_id)
    eid_assigned += 1

print(f"\n5. Exhibit ID assignment: {eid_assigned} entries got IDs")

# ═══════════════════════════════════════════════════════════════
# WRITE RESULTS
# ═══════════════════════════════════════════════════════════════

data['total_entries'] = len(entries)
with open(INDEX, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n✓ Updated {INDEX.name}")
print(f"  Total entries: {total}")
print(f"  Changes: {cat_changes} category + {rel_fixes} reliability + {phase_fills} phase + {tier_fills} tier + {eid_assigned} exhibit_id")
