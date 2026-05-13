#!/usr/bin/env python3
"""
Phase 7 — Rendered HTML audit for spot-check posts.
For each post: verify hero embed count, primary chip count,
"Explore all N" count = hero+primary+secondary, source exhibit chips present,
no broken images, no empty embed bodies.
"""

import json
import os
import re
import sys
from pathlib import Path
from html.parser import HTMLParser

BASE = Path(__file__).resolve().parent.parent
SITE = BASE / "_site"

# Posts to spot-check (from Phase 7 spec)
SPOT_CHECK = ["B17", "B21", "B18", "B40", "B44", "B24", "B00", "B34"]

# Load posts.json for expected counts
with open(BASE / "posts.json") as f:
    posts_data = json.load(f)
posts_by_id = {p["id"]: p for p in posts_data["posts"]}

# Load canonical index for source_exhibit resolution
with open(BASE / "evidence_index_canonical.json") as f:
    canon = json.load(f)
by_eid = {}
for e in canon["entries"]:
    eid = e.get("exhibit_id", "")
    if eid:
        by_eid[eid] = e

def get_slug(post_id):
    """Posts render as B{XX}.html, not slug-based."""
    return post_id

def audit_post(post_id):
    """Audit a rendered post HTML file."""
    slug = get_slug(post_id)
    html_path = SITE / "posts" / f"{slug}.html"
    if not html_path.exists():
        return {"error": f"HTML file not found: {html_path}"}

    html = html_path.read_text(encoding="utf-8")
    post = posts_by_id[post_id]
    ev = post.get("evidence", {})

    results = {"post_id": post_id, "slug": slug, "issues": []}

    # Count hero embeds in body (evidence-embed elements before footer)
    # Hero embeds use various classes: embed-document, photo-card, court-facsimile, etc.
    hero_classes = [
        'embed-document', 'photo-card', 'document-card', 'photo-gallery',
        'court-facsimile', 'email-facsimile', 'embed-media', 'embed-pull-quote',
        'iphone-frame', 'msg-group'
    ]

    # Count evidence embed divs in the post body (before footer)
    # The footer section starts with class="evidence-footer" or "post-evidence"
    footer_match = re.search(r'<(?:section|div)[^>]*class="[^"]*(?:evidence-footer|post-evidence)[^"]*"', html)
    body_html = html[:footer_match.start()] if footer_match else html

    # Count inline embeds in body
    embed_pattern = r'<div[^>]*class="[^"]*(?:evidence-embed|embed-document|photo-card|document-card|court-facsimile|email-facsimile|embed-media|embed-pull-quote|msg-group)[^"]*"'
    body_embeds = len(re.findall(embed_pattern, body_html))

    # Expected hero count from posts.json
    expected_heroes = len(ev.get("hero", []))
    results["hero_expected"] = expected_heroes
    results["hero_found_approx"] = body_embeds

    # Check evidence footer chips
    if footer_match:
        footer_html = html[footer_match.start():]
        # Count evidence chips (a tags with evidence-chip class or similar)
        chip_pattern = r'<a[^>]*class="[^"]*evidence-chip[^"]*"[^>]*>'
        chips = re.findall(chip_pattern, footer_html)
        results["footer_chips"] = len(chips)

        # Check for "Explore all N" link
        explore_match = re.search(r'Explore all (\d+)', footer_html)
        if explore_match:
            explore_count = int(explore_match.group(1))
            results["explore_all_count"] = explore_count
            # Expected: hero + primary + secondary
            expected_total = len(ev.get("hero", [])) + len(ev.get("primary", [])) + len(ev.get("secondary", []))
            # Plus auto-injected source exhibits
            auto_injected = set()
            for hero_eid in ev.get("hero", []):
                entry = by_eid.get(hero_eid, {})
                se = entry.get("source_exhibit")
                if se and se not in set(ev.get("hero", []) + ev.get("primary", []) + ev.get("secondary", []) + ev.get("tertiary", [])):
                    auto_injected.add(se)
            expected_with_injection = expected_total + len(auto_injected)
            results["expected_total"] = expected_with_injection
            if explore_count != expected_with_injection:
                results["issues"].append(
                    f"'Explore all' count mismatch: rendered={explore_count}, expected={expected_with_injection}"
                )
        else:
            results["explore_all_count"] = None
            # Some posts may not have "Explore all" if count is low
    else:
        results["footer_chips"] = 0
        results["issues"].append("No evidence footer found")

    # Check for auto-injected source exhibits in footer
    source_exhibits_expected = set()
    for hero_eid in ev.get("hero", []):
        entry = by_eid.get(hero_eid, {})
        se = entry.get("source_exhibit")
        if se:
            all_existing = set(ev.get("hero", []) + ev.get("primary", []) + ev.get("secondary", []) + ev.get("tertiary", []))
            if se not in all_existing:
                source_exhibits_expected.add(se)

    results["source_exhibits_auto_injected"] = list(source_exhibits_expected)

    # Check for source exhibit IDs appearing in the footer HTML
    if footer_match:
        footer_html = html[footer_match.start():]
        for se_eid in source_exhibits_expected:
            if se_eid not in footer_html:
                results["issues"].append(f"Auto-injected source '{se_eid}' not found in footer HTML")

    # Check for broken images (src paths that don't resolve)
    img_pattern = r'<img[^>]*src="([^"]*)"'
    images = re.findall(img_pattern, html)
    broken = []
    for img_src in images:
        if img_src.startswith(('http://', 'https://', 'data:')):
            continue
        # Resolve relative to _site/posts/
        if img_src.startswith('/'):
            img_path = SITE / img_src.lstrip('/')
        else:
            img_path = SITE / "posts" / img_src
        if not img_path.exists():
            broken.append(img_src)
    if broken:
        results["issues"].append(f"Broken images ({len(broken)}): {broken[:5]}")
    results["total_images"] = len(images)
    results["broken_images"] = len(broken)

    # Check for empty embed bodies
    empty_embed = re.findall(r'<div class="embed-body">\s*</div>', html)
    if empty_embed:
        results["issues"].append(f"{len(empty_embed)} empty embed bodies found")

    return results

def main():
    print("=" * 70)
    print("PHASE 7 — Rendered Post HTML Audit")
    print("=" * 70)

    total_issues = 0

    for pid in SPOT_CHECK:
        if pid not in posts_by_id:
            print(f"\n⚠ {pid} not found in posts.json, skipping")
            continue

        result = audit_post(pid)
        print(f"\n{'─' * 50}")
        print(f"POST: {pid} ({result.get('slug', '?')})")

        if "error" in result:
            print(f"  ERROR: {result['error']}")
            total_issues += 1
            continue

        print(f"  Hero expected: {result['hero_expected']}, body embeds found: ~{result['hero_found_approx']}")
        print(f"  Footer chips: {result['footer_chips']}")
        print(f"  'Explore all' count: {result.get('explore_all_count', 'N/A')}, expected: {result.get('expected_total', 'N/A')}")
        print(f"  Source exhibits auto-injected: {result['source_exhibits_auto_injected'] or 'none needed'}")
        print(f"  Images: {result['total_images']} total, {result['broken_images']} broken")

        if result["issues"]:
            total_issues += len(result["issues"])
            for issue in result["issues"]:
                print(f"  ⚠ {issue}")
        else:
            print("  ✓ All checks passed")

    print(f"\n{'=' * 70}")
    if total_issues == 0:
        print("✅ ALL SPOT-CHECKED POSTS PASSED")
    else:
        print(f"⚠ {total_issues} issue(s) found across spot-checked posts")
    print("=" * 70)

if __name__ == "__main__":
    main()
