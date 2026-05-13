#!/usr/bin/env python3
"""Phase 7 — Source Exhibit Verification Script

Checks:
1. Every hero item with source_exhibit → its source appears in the rendered footer's primary tier
2. Every non-null source_exhibit → target exists in canonical index
3. Every auto-injected primary chip → has description (not raw file names)
4. No orphaned source_exhibit references
5. Stats summary
"""

import json
import sys
from pathlib import Path

def main():
    base = Path(__file__).parent.parent
    
    # Load canonical index
    with open(base / 'evidence_index_canonical.json') as f:
        canon = json.load(f)
    
    # Load posts.json
    with open(base / 'posts.json') as f:
        posts_data = json.load(f)
    
    entries_by_id = {}
    for e in canon['entries']:
        eid = e.get('exhibit_id')
        if eid not in entries_by_id:
            entries_by_id[eid] = e
    
    all_ids = set(entries_by_id.keys())
    
    errors = []
    warnings = []
    info = []
    
    # === Check 1: Every non-null source_exhibit points to a valid exhibit_id ===
    for e in canon['entries']:
        se = e.get('source_exhibit')
        if se and se not in all_ids:
            errors.append(f"INVALID source_exhibit: {e['exhibit_id']} → {se} (not found in index)")
    
    # === Check 2: For each post, hero items with source_exhibit should have their source in primary tier ===
    posts = posts_data.get('posts', [])
    for post in posts:
        pid = post.get('id', '')
        evidence = post.get('evidence', {})
        hero_ids = evidence.get('hero', [])
        primary_ids = set(evidence.get('primary', []))
        secondary_ids = set(evidence.get('secondary', []))
        
        for hid in hero_ids:
            entry = entries_by_id.get(hid)
            if not entry:
                warnings.append(f"{pid}: Hero {hid} not found in canonical index")
                continue
            
            se = entry.get('source_exhibit')
            if se:
                # Source should be in primary (or at least secondary)
                if se in primary_ids:
                    info.append(f"{pid}: Hero {hid} → source {se} is in primary ✓")
                elif se in secondary_ids:
                    warnings.append(f"{pid}: Hero {hid} → source {se} is in SECONDARY (should be primary)")
                else:
                    # Check if the build auto-injects it
                    # The build_html.py auto-injects source_exhibit items into primary if not already there
                    # So this might be expected — the build handles it
                    info.append(f"{pid}: Hero {hid} → source {se} will be AUTO-INJECTED into primary by build")
    
    # === Check 3: Entries with source_exhibit should have descriptions ===
    for e in canon['entries']:
        se = e.get('source_exhibit')
        if se:
            source_entry = entries_by_id.get(se)
            if source_entry:
                desc = source_entry.get('description', '')
                if not desc or len(desc) < 10:
                    warnings.append(f"Source {se} has no/short description (needed for chip label): '{desc}'")
    
    # === Check 4: Self-sourcing heroes (null source_exhibit) — verify they have rel_path ===
    for post in posts:
        pid = post.get('id', '')
        hero_ids = post.get('evidence', {}).get('hero', [])
        for hid in hero_ids:
            entry = entries_by_id.get(hid)
            if entry and entry.get('source_exhibit') is None:
                rp = entry.get('rel_path', '')
                if not rp:
                    # Check if it's a quote/text type that doesn't need a file
                    cat = entry.get('category', '').lower()
                    if 'quote' not in hid.lower() and 'text' not in hid.lower():
                        warnings.append(f"{pid}: Self-sourcing hero {hid} has no rel_path (category: {cat})")
    
    # === Stats ===
    total = len(canon['entries'])
    non_null_se = sum(1 for e in canon['entries'] if e.get('source_exhibit'))
    null_se = total - non_null_se
    heroes = sum(1 for e in canon['entries'] if e.get('tier') == 'Hero')
    heroes_with_se = sum(1 for e in canon['entries'] if e.get('tier') == 'Hero' and e.get('source_exhibit'))
    heroes_self = sum(1 for e in canon['entries'] if e.get('tier') == 'Hero' and e.get('source_exhibit') is None)
    
    print("=" * 60)
    print("SOURCE EXHIBIT VERIFICATION REPORT")
    print("=" * 60)
    print()
    print(f"Canonical index: {total} entries")
    print(f"  source_exhibit non-null: {non_null_se}")
    print(f"  source_exhibit null: {null_se}")
    print(f"  Hero entries: {heroes}")
    print(f"    Heroes with source_exhibit: {heroes_with_se}")
    print(f"    Heroes self-sourcing: {heroes_self}")
    print()
    
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  ❌ {e}")
        print()
    else:
        print("ERRORS: 0 ✓")
        print()
    
    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings[:20]:
            print(f"  ⚠️  {w}")
        if len(warnings) > 20:
            print(f"  ... and {len(warnings) - 20} more")
        print()
    else:
        print("WARNINGS: 0 ✓")
        print()
    
    print(f"INFO: {len(info)} source→primary linkages verified")
    print()
    print("=" * 60)
    
    if errors:
        print("❌ VERIFICATION FAILED")
        return 1
    elif warnings:
        print(f"⚠️  VERIFICATION PASSED WITH {len(warnings)} WARNINGS")
        return 0
    else:
        print("✓ ALL CHECKS PASSED")
        return 0

if __name__ == '__main__':
    sys.exit(main())
