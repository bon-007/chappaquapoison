#!/usr/bin/env python3
"""
extract_evidence_spec.py — Extract all evidence specifications from post frontmatter
and compare against v3_evidence_map.json to find gaps and misalignments.

⚠ DEPRECATED: This script's data has been absorbed into evidence_index_canonical.json.
To update evidence data, edit directly in canonical and re-run: python3 scripts/build_canonical_evidence_index.py
"""

import yaml
import re
import json
from pathlib import Path
from collections import defaultdict

V3_ROOT = Path(__file__).resolve().parent.parent
POSTS_MD = V3_ROOT / "posts" / "md"


def get_canonical_posts():
    files = sorted(POSTS_MD.glob("B[0-9]*_*.md"))
    canonical = {}
    for f in files:
        name = f.stem
        if any(tag in name for tag in ['_BOOK', '_ORIGINAL', '_SUPERSEDED', '_PRE_']):
            continue
        if name.endswith('.bak') or name.endswith('.backup'):
            continue
        match = re.match(r'(B\d+)', name)
        if not match:
            continue
        pid = match.group(1)
        if '_DRAFT' in name:
            canonical[pid] = f
        elif pid not in canonical:
            canonical[pid] = f
    for hidden in ['B00', 'B50', 'B51']:
        canonical.pop(hidden, None)
    return canonical


def extract_frontmatter(filepath):
    text = filepath.read_text(errors='replace')
    match = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if match:
        return yaml.safe_load(match.group(1))
    return {}


def main():
    canonical = get_canonical_posts()

    with open(V3_ROOT / "v3_evidence_map.json") as f:
        emap = json.load(f)

    # Build complete evidence spec from frontmatter
    all_specs = {}

    for pid in sorted(canonical.keys(), key=lambda x: int(re.search(r'\d+', x).group())):
        fm = extract_frontmatter(canonical[pid])
        title = fm.get('title', pid)
        ev = fm.get('evidence', {})
        provenance = fm.get('provenance', [])

        spec = {
            'pid': pid,
            'title': title,
            'provenance': provenance,
            'hero': [],
            'primary': [],
            'secondary': [],
            'tertiary': [],
        }

        if isinstance(ev, dict):
            for tier in ['hero', 'primary', 'secondary', 'tertiary']:
                items = ev.get(tier, [])
                for item in items:
                    if isinstance(item, dict):
                        exhibit = item.get('exhibit', '')
                    else:
                        exhibit = str(item)
                    if exhibit and exhibit not in ['hero', 'primary', 'secondary', 'tertiary', '']:
                        spec[tier].append(exhibit)
        elif isinstance(ev, list):
            # Flat list — treat as untiered
            for item in ev:
                if isinstance(item, dict):
                    exhibit = item.get('exhibit', '')
                else:
                    exhibit = str(item)
                if exhibit and exhibit not in ['hero', 'primary', 'secondary', 'tertiary', '']:
                    spec['primary'].append(exhibit)  # Default untiered to primary

        all_specs[pid] = spec

    # Print full evidence spec
    print("=" * 80)
    print("EVIDENCE SPECIFICATION FROM POST FRONTMATTER")
    print("(This is what each post WANTS)")
    print("=" * 80)

    total_hero = 0
    total_primary = 0
    total_secondary = 0
    total_tertiary = 0

    for pid in sorted(all_specs.keys(), key=lambda x: int(re.search(r'\d+', x).group())):
        spec = all_specs[pid]
        h = len(spec['hero'])
        p = len(spec['primary'])
        s = len(spec['secondary'])
        t = len(spec['tertiary'])
        total_hero += h
        total_primary += p
        total_secondary += s
        total_tertiary += t

        print(f"\n{'─' * 70}")
        print(f"{pid}: {spec['title']}")
        print(f"  Provenance: {', '.join(spec['provenance'])}")

        for tier in ['hero', 'primary', 'secondary', 'tertiary']:
            items = spec[tier]
            if items:
                print(f"  {tier.upper()}:")
                for item in items:
                    print(f"    • {item}")

        # Compare with emap
        map_entry = emap.get(pid, {})
        map_h = len(map_entry.get('hero', []))
        map_p = len(map_entry.get('primary', []))
        map_s = len(map_entry.get('secondary', []))
        map_t = len(map_entry.get('tertiary', []))

        print(f"  MAP: H={map_h} P={map_p} S={map_s} T={map_t}")

        # Flag misalignments
        if h == 0 and map_h > 0:
            print(f"  ⚠ No hero in spec but {map_h} in map")
        if h > 0 and map_h == 0:
            print(f"  ⚠ {h} hero in spec but 0 in map")

    print(f"\n{'=' * 80}")
    print(f"TOTALS FROM FRONTMATTER SPECS:")
    print(f"  Hero: {total_hero}")
    print(f"  Primary: {total_primary}")
    print(f"  Secondary: {total_secondary}")
    print(f"  Tertiary: {total_tertiary}")
    print(f"  Total named exhibits: {total_hero + total_primary + total_secondary + total_tertiary}")
    print(f"\nTOTALS FROM v3_evidence_map.json:")
    map_total_h = sum(len(e.get('hero', [])) for e in emap.values())
    map_total_p = sum(len(e.get('primary', [])) for e in emap.values())
    map_total_s = sum(len(e.get('secondary', [])) for e in emap.values())
    map_total_t = sum(len(e.get('tertiary', [])) for e in emap.values())
    print(f"  Hero: {map_total_h}")
    print(f"  Primary: {map_total_p}")
    print(f"  Secondary: {map_total_s}")
    print(f"  Tertiary: {map_total_t}")
    print(f"  Total items: {map_total_h + map_total_p + map_total_s + map_total_t}")

    # Write the spec to JSON for the rebuild
    with open(V3_ROOT / "evidence_spec_from_posts.json", 'w') as f:
        json.dump(all_specs, f, indent=2)
    print(f"\nWrote evidence_spec_from_posts.json")


if __name__ == "__main__":
    main()
