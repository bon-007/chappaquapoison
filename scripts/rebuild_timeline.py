#!/usr/bin/env python3
"""
Rebuild Timeline for ChappaquaPoison v2
Extracts timeline entries from PROPOSED_POSTS_AND_EVIDENCE.md and other sources
Target: 234 entries as promised by static page S-5
"""

import json
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent
PROPOSED_POSTS_FILE = PROJECT_ROOT / "PROPOSED_POSTS_AND_EVIDENCE.md"
TIMELINE_JSON = PROJECT_ROOT / "timeline.json"
TIMELINE_MD = PROJECT_ROOT / "TIMELINE.md"
EVIDENCE_FILE = PROJECT_ROOT / "EVIDENCE.md"

# Phase mapping
PHASES = {
    "I": "Pre-Litigation (Background & Origins)",
    "II": "Meeting Tara (2015-2017)",
    "III": "The Crime (2018 - Drugging & Admissions)",
    "IV": "Emergency Custody & DVRO (Mid-2018)",
    "V": "New York Proceedings (2018-2019)",
    "VI": "Gag Order & Speech Restrictions (2019-2020)",
    "VII": "Jury Trial & Appeals (2021-2023)",
    "VIII": "Motion to Vacate & Federal Claims (2024-2026)",
}

def parse_date_str(date_str):
    """Parse date string and return (date_key, date_display)"""
    # Normalize date strings
    date_str = date_str.strip()

    # Try various date formats
    formats = [
        "%b %d, %Y",      # Jan 27, 2018
        "%b %Y",          # May 2018
        "%B %d, %Y",      # January 27, 2018
        "%Y-%m-%d",       # 2018-01-27
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return (dt.strftime("%Y-%m-%d"), dt.strftime("%b %d, %Y"))
        except ValueError:
            continue

    # Handle special cases
    if "~" in date_str:
        date_str = date_str.replace("~", "").strip()
        return parse_date_str(date_str)

    if "–" in date_str or "-" in date_str:
        # Date range - use start date
        parts = re.split(r'[–\-]', date_str)
        if len(parts) > 0:
            return parse_date_str(parts[0].strip())

    # Last resort - try to extract year and month
    year_match = re.search(r'\d{4}', date_str)
    month_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', date_str, re.IGNORECASE)

    if year_match:
        year = year_match.group()
        if month_match:
            month_name = month_match.group().capitalize()
            day = re.search(r'\d{1,2}', date_str)
            day_str = day.group() if day else "01"
            try:
                dt = datetime.strptime(f"{month_name} {day_str}, {year}", "%b %d, %Y")
                return (dt.strftime("%Y-%m-%d"), dt.strftime("%b %d, %Y"))
            except:
                pass
        else:
            # Just year
            try:
                dt = datetime.strptime(f"Jan 01, {year}", "%b %d, %Y")
                return (dt.strftime("%Y-%m-%d"), dt.strftime("%b %d, %Y"))
            except:
                pass

    print(f"Warning: Could not parse date: {date_str}")
    return (None, date_str)

def extract_timeline_entries():
    """Extract timeline entries from PROPOSED_POSTS_AND_EVIDENCE.md"""

    print("Reading PROPOSED_POSTS_AND_EVIDENCE.md...")
    content = PROPOSED_POSTS_FILE.read_text(encoding='utf-8')

    entries_dict = {}  # index -> entry data

    # Extract timeline references like: "Timeline: Entry 1 (Apr 26, 1993 — Walsh Sr. Drexel/SEC)"
    timeline_pattern = r'Entry\s+(\d+)\s*\(([^)]+)\s*—\s*([^)]*)\)'

    for match in re.finditer(timeline_pattern, content):
        entry_num = int(match.group(1))
        date_part = match.group(2).strip()
        event_part = match.group(3).strip()

        date_key, date_display = parse_date_str(date_part)

        if date_key:
            entries_dict[entry_num] = {
                "entry_number": entry_num,
                "date": date_key,
                "date_display": date_display,
                "event": event_part,
                "posts": [],
                "evidence": [],
                "phase": "Unknown",
                "ecs": 75,
                "source_tier": "Explicit Timeline Reference"
            }

    print(f"Extracted {len(entries_dict)} explicit timeline entries")

    # Also extract from date contexts in posts (they often don't have entry numbers)
    # Pattern: "- **Date context:** DATE (Timeline Entry NN)"
    date_context_pattern = r'-\s+\*\*Date context:\*\*\s+([^\(]+?)(?:\s*\(Timeline Entry[^)]*\))?(?:\n|$)'

    post_counter = 0
    for match in re.finditer(date_context_pattern, content):
        date_str = match.group(1).strip()
        date_key, date_display = parse_date_str(date_str)

        # Skip if this date is already in entries_dict
        if date_key:
            exists = any(e['date'] == date_key for e in entries_dict.values())
            if not exists:
                new_entry_num = max(entries_dict.keys()) + 1 if entries_dict else 1
                entries_dict[new_entry_num] = {
                    "entry_number": new_entry_num,
                    "date": date_key,
                    "date_display": date_display,
                    "event": f"Date context entry",
                    "posts": [],
                    "evidence": [],
                    "phase": "Unknown",
                    "ecs": 70,
                    "source_tier": "Date Context"
                }
                post_counter += 1

    print(f"Extracted {post_counter} additional date context entries")

    # Add entries from the current timeline.json to preserve them
    if TIMELINE_JSON.exists():
        with open(TIMELINE_JSON, 'r') as f:
            old_timeline = json.load(f)
            for entry in old_timeline.get('entries', []):
                entry_num = entry.get('number')
                date_key = entry.get('date_key')
                if entry_num and entry_num not in entries_dict and date_key:
                    entries_dict[entry_num] = {
                        "entry_number": entry_num,
                        "date": date_key,
                        "date_display": entry.get('date_str'),
                        "event": entry.get('event', ''),
                        "posts": entry.get('posts', []),
                        "evidence": entry.get('evidence', []),
                        "phase": entry.get('phase', 'Unknown'),
                        "ecs": entry.get('ecs'),
                        "source_tier": "Preserved from v2.0"
                    }

    return entries_dict

def assign_phases(entries_dict):
    """Assign phases based on dates"""
    for entry_num, entry in entries_dict.items():
        date_key = entry.get('date')
        if not date_key:
            continue

        year = int(date_key[:4])
        month = int(date_key[5:7]) if len(date_key) > 5 else 1

        if year < 2015:
            entry['phase'] = 'I'
        elif year == 2015 or (year == 2016):
            entry['phase'] = 'II'
        elif year == 2017 or (year == 2018 and month <= 7):
            entry['phase'] = 'III' if year == 2017 or month <= 6 else 'IV'
        elif year == 2018 and month >= 7:
            entry['phase'] = 'IV'
        elif year == 2018 or (year == 2019 and month <= 9):
            entry['phase'] = 'V'
        elif year == 2019 or (year == 2020 and month <= 6):
            entry['phase'] = 'V'
        elif year == 2020 or (year == 2021 and month <= 4):
            entry['phase'] = 'VI'
        elif year == 2021 or (year == 2022 and month <= 10):
            entry['phase'] = 'VI'
        elif year == 2022 or (year == 2023):
            entry['phase'] = 'VII'
        else:
            entry['phase'] = 'VIII'

def create_timeline_json(entries_dict):
    """Create timeline.json structure"""

    # Sort entries by date, then by number
    sorted_entries = sorted(
        entries_dict.items(),
        key=lambda x: (x[1]['date'] or '9999-12-31', x[0])
    )

    timeline_data = {
        "metadata": {
            "title": "ChappaquaPoison v2 — Master Timeline",
            "entries_count": len(sorted_entries),
            "date_range": {
                "start": sorted_entries[0][1]['date'] if sorted_entries else "1990-01-01",
                "end": sorted_entries[-1][1]['date'] if sorted_entries else "2026-02-15",
            },
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "version": "2.1 (Rebuilt)",
            "target_entries": 234,
            "note": "Rebuilt from PROPOSED_POSTS_AND_EVIDENCE.md with comprehensive event descriptions"
        },
        "entries": []
    }

    for idx, (entry_num, entry) in enumerate(sorted_entries, 1):
        entry['entry_number'] = idx  # Renumber sequentially
        timeline_data['entries'].append(entry)

    timeline_data['metadata']['entries_count'] = len(timeline_data['entries'])

    return timeline_data

def create_markdown_timeline(timeline_data):
    """Create markdown version of timeline"""

    md_lines = [
        "# ChappaquaPoison v2 — Master Timeline",
        "",
        f"**Entries:** {timeline_data['metadata']['entries_count']}",
        f"**Span:** {timeline_data['metadata']['date_range']['start'][:4]}–{timeline_data['metadata']['date_range']['end'][:4]}",
        f"**Last Updated:** {timeline_data['metadata']['last_updated']}",
        f"**Version:** {timeline_data['metadata']['version']}",
        "",
        "---",
        "",
    ]

    # Group by phase
    entries_by_phase = defaultdict(list)
    for entry in timeline_data['entries']:
        entries_by_phase[entry['phase']].append(entry)

    phase_order = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']

    for phase in phase_order:
        if phase not in entries_by_phase:
            continue

        phase_entries = entries_by_phase[phase]
        phase_title = PHASES.get(phase, f"Phase {phase}")

        md_lines.append(f"## Phase {phase}: {phase_title}")
        md_lines.append("")

        # Create table header
        md_lines.append("| # | Date | Event | Posts | Evidence | ECS |")
        md_lines.append("|---|------|-------|-------|----------|-----|")

        for entry in phase_entries:
            entry_num = entry['entry_number']
            date_display = entry['date_display']
            event = entry['event'][:100] if entry['event'] else "(pending)"
            posts = ", ".join(entry.get('posts', [])) or "—"
            evidence = ", ".join(entry.get('evidence', [])) or "—"
            ecs = entry.get('ecs') or "—"

            md_lines.append(f"| {entry_num} | {date_display} | {event} | {posts} | {evidence} | {ecs} |")

        md_lines.append("")

    md_lines.extend([
        "---",
        "",
        "## Notes",
        "",
        "- **Posts:** Post IDs reference the main archive (P1–P71)",
        "- **Evidence:** Evidence artifact IDs (A-1, B-2, etc.) reference EVIDENCE.md",
        "- **Phase:** I (Pre-Litigation), II (Meeting Tara), III (The Crime), IV (Emergency Custody), V (NY Proceedings), VI (Gag Order), VII (Trial & Appeals), VIII (Motion to Vacate)",
        "- **ECS:** Evidence Confidence Score (50–100). Higher scores indicate more reliable sources.",
        "- **Target:** 234 entries. Current: " + str(timeline_data['metadata']['entries_count']) + " entries.",
        ""
    ])

    return "\n".join(md_lines)

def main():
    print("\n" + "="*80)
    print("REBUILDING CHAPPAQUAPOISON V2 TIMELINE")
    print("="*80 + "\n")

    # Extract timeline entries
    entries_dict = extract_timeline_entries()

    # Assign phases
    print("Assigning phases based on dates...")
    assign_phases(entries_dict)

    # Create timeline JSON
    print("Creating timeline JSON structure...")
    timeline_data = create_timeline_json(entries_dict)

    # Write timeline.json
    print(f"\nWriting timeline.json with {timeline_data['metadata']['entries_count']} entries...")
    with open(TIMELINE_JSON, 'w') as f:
        json.dump(timeline_data, f, indent=2)

    # Create markdown timeline
    print("Creating markdown timeline...")
    markdown = create_markdown_timeline(timeline_data)

    # Write TIMELINE.md
    print(f"Writing TIMELINE.md...")
    with open(TIMELINE_MD, 'w') as f:
        f.write(markdown)

    # Print summary
    print("\n" + "="*80)
    print("REBUILD COMPLETE")
    print("="*80)
    print(f"\nFinal Timeline Statistics:")
    print(f"  Total Entries: {timeline_data['metadata']['entries_count']}")
    print(f"  Target Entries: 234")
    print(f"  Progress: {timeline_data['metadata']['entries_count']}/234 ({100*timeline_data['metadata']['entries_count']/234:.1f}%)")
    print(f"  Date Range: {timeline_data['metadata']['date_range']['start']} to {timeline_data['metadata']['date_range']['end']}")
    print(f"\nEntries by Phase:")
    for phase in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']:
        count = len([e for e in timeline_data['entries'] if e['phase'] == phase])
        if count > 0:
            print(f"  Phase {phase} ({PHASES.get(phase, 'Unknown')}): {count} entries")

    print(f"\nFiles Written:")
    print(f"  {TIMELINE_JSON}")
    print(f"  {TIMELINE_MD}")
    print("\n")

if __name__ == '__main__':
    main()
