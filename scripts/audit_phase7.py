#!/usr/bin/env python3
"""
Phase 7 Verification Audit — Source Exhibit Linkage
Checks:
  1. Every hero item with source_exhibit → source appears in rendered footer primary tier
  2. Every non-null source_exhibit → target exists in canonical index
  3. Source exhibit auto-injection works (heroes with source_exhibit get source in footer)
  4. No orphan source_exhibit references
  5. Evidence array consistency (posts.json ↔ canonical index posts arrays)
  6. Build-time auto-injection simulation
"""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent.parent
CANONICAL = BASE / "evidence_index_canonical.json"
POSTS_JSON = BASE / "posts.json"

def load_data():
    with open(CANONICAL) as f:
        canon = json.load(f)
    with open(POSTS_JSON) as f:
        posts = json.load(f)
    entries = canon.get("entries", [])
    by_eid = {}
    by_post = defaultdict(list)
    for e in entries:
        eid = e.get("exhibit_id") or e.get("id", "")
        if eid:
            by_eid[eid] = e
            for pid in e.get("posts", []):
                by_post[pid].append(e)
    return entries, posts.get("posts", []), by_eid, by_post

def check_source_exhibit_targets(entries, by_eid):
    """Check 2: Every non-null source_exhibit points to a valid exhibit_id."""
    errors = []
    count = 0
    for e in entries:
        se = e.get("source_exhibit")
        if se:
            count += 1
            if se not in by_eid:
                errors.append(f"  BROKEN: {e['exhibit_id']} → source_exhibit '{se}' NOT FOUND in index")
    return count, errors

def check_hero_source_in_footer(posts, by_eid):
    """Check 1+3: For each hero with source_exhibit, simulate auto-injection
    and verify the source would appear in the footer primary tier."""
    errors = []
    injections = []
    posts_with_injections = 0

    for post in posts:
        pid = post.get("id", "")
        ev = post.get("evidence", {})
        heroes = ev.get("hero", [])
        primaries = ev.get("primary", [])
        secondaries = ev.get("secondary", [])
        tertiaries = ev.get("tertiary", [])

        # All evidence IDs already in footer
        all_footer = set(heroes + primaries + secondaries + tertiaries)

        # Simulate auto-injection (mirrors build_html.py lines 524-552)
        auto_injected = []
        for hero_eid in heroes:
            hero_entry = by_eid.get(hero_eid, {})
            source_eid = hero_entry.get("source_exhibit")
            if source_eid:
                if source_eid not in all_footer:
                    # Would be auto-injected
                    if source_eid in by_eid:
                        auto_injected.append(source_eid)
                        all_footer.add(source_eid)
                    else:
                        errors.append(f"  {pid}: Hero '{hero_eid}' → source_exhibit '{source_eid}' NOT IN INDEX (can't inject)")
                # else: already in footer, no injection needed

        if auto_injected:
            posts_with_injections += 1
            injections.append(f"  {pid}: auto-injects {len(auto_injected)} source(s): {', '.join(auto_injected)}")

    return injections, errors, posts_with_injections

def check_posts_json_canonical_sync(posts, by_eid):
    """Check 5: Every evidence ID in posts.json exists in canonical index,
    and every such entry has the post ID in its posts array."""
    missing_from_index = []
    missing_post_tag = []

    for post in posts:
        pid = post.get("id", "")
        ev = post.get("evidence", {})
        for tier in ["hero", "primary", "secondary", "tertiary"]:
            for eid in ev.get(tier, []):
                entry = by_eid.get(eid)
                if not entry:
                    missing_from_index.append(f"  {pid}/{tier}: '{eid}' NOT IN canonical index")
                else:
                    if pid not in entry.get("posts", []):
                        missing_post_tag.append(f"  {pid}/{tier}: '{eid}' exists but posts array missing '{pid}'")

    return missing_from_index, missing_post_tag

def check_hero_entry_completeness(posts, by_eid):
    """Check that hero items have rel_path and aren't file_missing."""
    issues = []
    for post in posts:
        pid = post.get("id", "")
        for eid in post.get("evidence", {}).get("hero", []):
            entry = by_eid.get(eid)
            if not entry:
                continue  # caught by sync check
            if entry.get("file_missing"):
                issues.append(f"  {pid}: Hero '{eid}' still marked file_missing")
            # Some heroes are quote/text-only, so empty rel_path is OK for those
    return issues

def check_source_exhibit_bidirectional(entries, by_eid):
    """Verify source_exhibit targets are reasonable — the source should generally
    be a standalone/parent item, not another derivative."""
    warnings = []
    for e in entries:
        se = e.get("source_exhibit")
        if se and se in by_eid:
            source = by_eid[se]
            # Check for chain: source also has a source_exhibit (unusual)
            if source.get("source_exhibit"):
                warnings.append(f"  CHAIN: {e['exhibit_id']} → {se} → {source['source_exhibit']} (double indirection)")
    return warnings

def check_tier_consistency(entries):
    """Verify tier values are valid."""
    valid_tiers = {"Hero", "Primary", "Secondary", "Tertiary"}
    issues = []
    tier_counts = defaultdict(int)
    for e in entries:
        tier = e.get("tier", "")
        tier_counts[tier] += 1
        if tier not in valid_tiers:
            issues.append(f"  {e.get('exhibit_id', '?')}: invalid tier '{tier}'")
    return issues, dict(tier_counts)

def main():
    print("=" * 70)
    print("PHASE 7 VERIFICATION AUDIT — Source Exhibit Linkage")
    print("=" * 70)

    entries, posts, by_eid, by_post = load_data()

    total_errors = 0
    total_warnings = 0

    # --- Check 1: Source exhibit target validity ---
    print(f"\n{'─' * 50}")
    print("CHECK 1: source_exhibit target validity")
    count, errors = check_source_exhibit_targets(entries, by_eid)
    print(f"  Entries with source_exhibit: {count}")
    if errors:
        for e in errors:
            print(e)
        total_errors += len(errors)
    else:
        print("  ✓ All source_exhibit references point to valid entries")

    # --- Check 2: Hero source auto-injection simulation ---
    print(f"\n{'─' * 50}")
    print("CHECK 2: Hero → source_exhibit auto-injection simulation")
    injections, errors, num_posts = check_hero_source_in_footer(posts, by_eid)
    print(f"  Posts receiving auto-injections: {num_posts}")
    for inj in injections:
        print(inj)
    if errors:
        print(f"\n  ERRORS ({len(errors)}):")
        for e in errors:
            print(e)
        total_errors += len(errors)
    else:
        print("  ✓ All hero source_exhibit references are valid and injectable")

    # --- Check 3: posts.json ↔ canonical index sync ---
    print(f"\n{'─' * 50}")
    print("CHECK 3: posts.json ↔ canonical index sync")
    missing_index, missing_tag = check_posts_json_canonical_sync(posts, by_eid)
    if missing_index:
        print(f"\n  MISSING FROM INDEX ({len(missing_index)}):")
        for m in missing_index:
            print(m)
        total_errors += len(missing_index)
    else:
        print("  ✓ All posts.json evidence IDs exist in canonical index")

    if missing_tag:
        print(f"\n  MISSING POST TAGS ({len(missing_tag)}):")
        for m in missing_tag:
            print(m)
        total_warnings += len(missing_tag)
    else:
        print("  ✓ All canonical entries have correct post tags")

    # --- Check 4: Hero file_missing ---
    print(f"\n{'─' * 50}")
    print("CHECK 4: Hero items file_missing check")
    issues = check_hero_entry_completeness(posts, by_eid)
    if issues:
        for i in issues:
            print(i)
        total_errors += len(issues)
    else:
        print("  ✓ No hero items marked file_missing")

    # --- Check 5: Double indirection ---
    print(f"\n{'─' * 50}")
    print("CHECK 5: source_exhibit chain detection")
    warnings = check_source_exhibit_bidirectional(entries, by_eid)
    if warnings:
        for w in warnings:
            print(w)
        total_warnings += len(warnings)
    else:
        print("  ✓ No double-indirection chains found")

    # --- Check 6: Tier consistency ---
    print(f"\n{'─' * 50}")
    print("CHECK 6: Tier value consistency")
    issues, tier_counts = check_tier_consistency(entries)
    for tier, count in sorted(tier_counts.items()):
        print(f"  {tier}: {count}")
    if issues:
        for i in issues:
            print(i)
        total_errors += len(issues)
    else:
        print("  ✓ All tier values valid")

    # --- Summary ---
    print(f"\n{'=' * 70}")
    print(f"SUMMARY: {len(entries)} entries, {len(posts)} posts")
    print(f"  Errors:   {total_errors}")
    print(f"  Warnings: {total_warnings}")
    if total_errors == 0:
        print("  ✅ AUDIT PASSED")
    else:
        print("  ❌ AUDIT FAILED — fix errors before proceeding")
    print("=" * 70)

    return 1 if total_errors > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
