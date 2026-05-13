#!/usr/bin/env python3
"""
build_timeline.py

Generates TIMELINE.md and timeline.json from:
  - posts.json (date_context and timeline_entries fields)
  - PROPOSED_POSTS_AND_EVIDENCE.md (post details)
  - EVIDENCE.md (evidence dates)

Timeline entries are extracted, deduplicated, sorted chronologically,
and rendered as a markdown table with companion JSON for machine consumption.
"""

import json
import re
from datetime import datetime, date
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Set, Tuple
import sys

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class TimelineEntry:
    """Represents a single timeline entry."""
    number: int
    date_str: str  # Human-readable date (e.g., "Apr 26, 1993")
    date_key: str  # ISO sortable key (e.g., "1993-04-26")
    event: str
    posts: List[str]  # Post IDs (e.g., ["P03", "P04"])
    evidence: List[str]  # Evidence IDs (e.g., ["F-1", "A-2"])
    phase: str  # Phase name (e.g., "I", "II", "III")
    ecs: int  # Evidence Confidence Score (50-100)

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


# ============================================================================
# PARSING FUNCTIONS
# ============================================================================

def parse_date_string(date_str: str) -> Tuple[str, str, bool]:
    """
    Parse date_context strings and extract start date.

    Returns: (human_readable_date, iso_sortable_date, is_valid_date)
    Examples:
      "Apr 26, 1993" -> ("Apr 26, 1993", "1993-04-26", True)
      "March 9, 2017" -> ("Mar 9, 2017", "2017-03-09", True)
      "1990s–2015" -> ("Jan 1, 1990", "1990-01-01", True)
      "2010–2018" -> ("Jan 1, 2010", "2010-01-01", True)
      "Some Text" -> ("Some Text", "Some Text", False)
    """

    date_str = date_str.strip()

    # Skip obviously non-date text
    if date_str in ('—', '—', '', 'Analysis', 'Per schedule') or date_str.startswith('Posts'):
        return (date_str, 'INVALID', False)

    # Try exact date formats: "Apr 26, 1993" or "March 9, 2017"
    patterns = [
        (r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+\d{4}', '%b %d, %Y'),
        (r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}', '%B %d, %Y'),
    ]

    for pattern, fmt in patterns:
        match = re.search(pattern, date_str)
        if match:
            date_text = match.group(0)
            # Normalize month names to 3-letter abbrev
            date_text = date_text.replace('January', 'Jan').replace('February', 'Feb').replace('March', 'Mar')
            date_text = date_text.replace('April', 'Apr').replace('June', 'Jun').replace('July', 'Jul')
            date_text = date_text.replace('August', 'Aug').replace('September', 'Sep').replace('October', 'Oct')
            date_text = date_text.replace('November', 'Nov').replace('December', 'Dec')

            try:
                dt = datetime.strptime(date_text, '%b %d, %Y')
                human_date = dt.strftime('%b %d, %Y')
                iso_date = dt.strftime('%Y-%m-%d')
                return (human_date, iso_date, True)
            except ValueError:
                pass

    # Try year range: "1990s–2015" or "2010-2018" or "2010–2018"
    year_range_match = re.search(r'(\d{4})s?(?:–|-)\d{4}', date_str)
    if year_range_match:
        start_year = int(re.search(r'(\d{4})', date_str).group(1))
        # Use January 1 of start year
        dt = datetime(start_year, 1, 1)
        human_date = dt.strftime('%b %d, %Y')
        iso_date = dt.strftime('%Y-%m-%d')
        return (human_date, iso_date, True)

    # Try just a year: "2018"
    year_match = re.search(r'\b(\d{4})\b', date_str)
    if year_match:
        year = int(year_match.group(1))
        dt = datetime(year, 1, 1)
        human_date = dt.strftime('%b %d, %Y')
        iso_date = dt.strftime('%Y-%m-%d')
        return (human_date, iso_date, True)

    # Fallback: return as-is with invalid flag
    return (date_str, 'INVALID', False)


def extract_timeline_from_posts(posts_json_path: str) -> Dict[str, Dict]:
    """
    Extract timeline entries from posts.json date_context and timeline_entries fields.

    Returns: Dict mapping iso_date_key -> {date_str, posts, evidence_ids}
    """
    with open(posts_json_path, 'r') as f:
        data = json.load(f)

    posts = data.get('posts', [])
    timeline_map = {}  # iso_date -> entry_data

    for post in posts:
        post_id = post.get('id')
        date_context = post.get('date_context', '')
        timeline_entries = post.get('timeline_entries', [])
        phase = post.get('phase', 'Unknown')
        ecs = post.get('ecs', 75)

        if not date_context:
            continue

        # Parse date from date_context
        human_date, iso_date, is_valid = parse_date_string(date_context)

        # Skip invalid dates
        if not is_valid:
            continue

        if iso_date not in timeline_map:
            timeline_map[iso_date] = {
                'date_str': human_date,
                'iso_date': iso_date,
                'event': '',
                'posts': set(),
                'evidence': set(),
                'phase': phase,
                'ecs': ecs
            }

        timeline_map[iso_date]['posts'].add(post_id)

        # Extract timeline entry references (e.g., "Timeline Entry 11 (Mar 9, 2017)")
        # These are typically in the format: "Timeline Entry N (Date)"
        timeline_refs = re.findall(r'Timeline Entry\s+(\d+)', post.get('timeline_entries_text', ''))
        for ref in timeline_refs:
            timeline_map[iso_date]['evidence'].add(f'TL-{ref}')

    return timeline_map


def extract_evidence_dates(evidence_md_path: str) -> Dict[str, Dict]:
    """
    Extract evidence dates from EVIDENCE.md.
    Returns: Dict mapping evidence_id -> {date, title, posts}
    """
    with open(evidence_md_path, 'r') as f:
        content = f.read()

    evidence_dates = {}

    # Parse evidence table entries
    # Format: | A-1 | Title | Badge | Date | ECS | ... |
    table_pattern = r'\|\s*([A-Z]-\d+)\s*\|\s*([^|]+)\s*\|\s*[^|]*\|\s*([^|]+)\s*\|'

    for match in re.finditer(table_pattern, content):
        evidence_id = match.group(1).strip()
        title = match.group(2).strip()
        date_str = match.group(3).strip()

        if date_str and date_str != 'Date' and date_str != '—':
            human_date, iso_date, is_valid = parse_date_string(date_str)
            if is_valid:  # Only add valid dates
                evidence_dates[evidence_id] = {
                    'date_str': human_date,
                    'iso_date': iso_date,
                    'title': title
                }

    return evidence_dates


def build_timeline(posts_json_path: str, evidence_md_path: str) -> List[TimelineEntry]:
    """
    Build consolidated timeline from posts and evidence.
    """

    # Extract timelines
    posts_timeline = extract_timeline_from_posts(posts_json_path)
    evidence_dates = extract_evidence_dates(evidence_md_path)

    # Merge evidence into timeline
    merged_timeline = posts_timeline.copy()

    for evidence_id, evidence_data in evidence_dates.items():
        iso_date = evidence_data['iso_date']
        if iso_date not in merged_timeline:
            merged_timeline[iso_date] = {
                'date_str': evidence_data['date_str'],
                'iso_date': iso_date,
                'event': evidence_data['title'],
                'posts': set(),
                'evidence': {evidence_id},
                'phase': 'Unknown',
                'ecs': 85
            }
        else:
            merged_timeline[iso_date]['evidence'].add(evidence_id)

    # Sort by iso_date
    sorted_dates = sorted(merged_timeline.keys())

    # Build TimelineEntry objects
    timeline_entries = []
    for idx, iso_date in enumerate(sorted_dates, start=1):
        entry_data = merged_timeline[iso_date]

        entry = TimelineEntry(
            number=idx,
            date_str=entry_data['date_str'],
            date_key=iso_date,
            event=entry_data['event'],
            posts=sorted(list(entry_data['posts'])),
            evidence=sorted(list(entry_data['evidence'])),
            phase=entry_data['phase'],
            ecs=entry_data['ecs']
        )
        timeline_entries.append(entry)

    return timeline_entries


# ============================================================================
# MARKDOWN GENERATION
# ============================================================================

def generate_markdown(entries: List[TimelineEntry], output_path: str) -> str:
    """
    Generate TIMELINE.md markdown table.
    """

    lines = []
    lines.append("# ChappaquaPoison v2 — Master Timeline")
    lines.append("")
    lines.append(f"**Entries:** {len(entries)}")
    lines.append(f"**Span:** {entries[0].date_key.split('-')[0]}–{entries[-1].date_key.split('-')[0]}")
    lines.append(f"**Last Updated:** February 15, 2026")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("| # | Date | Event | Posts | Evidence | Phase | ECS |")
    lines.append("|---|------|-------|-------|----------|-------|-----|")

    for entry in entries:
        posts_str = ", ".join(entry.posts) if entry.posts else "—"
        evidence_str = ", ".join(entry.evidence) if entry.evidence else "—"

        lines.append(
            f"| {entry.number} | {entry.date_str} | {entry.event} | {posts_str} | {evidence_str} | {entry.phase} | {entry.ecs} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- **Posts:** Post IDs reference the main archive (P1–P91)")
    lines.append("- **Evidence:** Evidence artifact IDs (A-1, B-2, etc.) reference EVIDENCE.md")
    lines.append("- **Phase:** I (Origin), II (Early Allegations), III (Custody), IV (Litigation), V (Appeal), VI (Federal)")
    lines.append("- **ECS:** Evidence Confidence Score (50–100). Higher scores indicate more reliable sources (court filings, sworn testimony).")
    lines.append("")

    markdown = "\n".join(lines)

    with open(output_path, 'w') as f:
        f.write(markdown)

    return markdown


# ============================================================================
# JSON GENERATION
# ============================================================================

def generate_json(entries: List[TimelineEntry], output_path: str):
    """
    Generate timeline.json for machine consumption.
    """

    data = {
        'metadata': {
            'title': 'ChappaquaPoison v2 — Master Timeline',
            'entries_count': len(entries),
            'date_range': {
                'start': entries[0].date_key if entries else None,
                'end': entries[-1].date_key if entries else None
            },
            'last_updated': '2026-02-15',
            'version': '2.0'
        },
        'entries': [entry.to_dict() for entry in entries]
    }

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)


# ============================================================================
# MAIN
# ============================================================================

def main():
    project_root = Path(__file__).resolve().parent.parent

    posts_json_path = project_root / "posts.json"
    evidence_md_path = project_root / "EVIDENCE.md"
    timeline_md_path = project_root / "TIMELINE.md"
    timeline_json_path = project_root / "timeline.json"

    print(f"[build_timeline.py] Building timeline...")
    print(f"  Posts: {posts_json_path}")
    print(f"  Evidence: {evidence_md_path}")
    print()

    # Build timeline
    timeline_entries = build_timeline(str(posts_json_path), str(evidence_md_path))

    print(f"[build_timeline.py] Extracted {len(timeline_entries)} timeline entries")
    print(f"  Date range: {timeline_entries[0].date_key} to {timeline_entries[-1].date_key}")
    print()

    # Generate markdown
    print(f"[build_timeline.py] Generating TIMELINE.md...")
    generate_markdown(timeline_entries, str(timeline_md_path))
    print(f"  Output: {timeline_md_path}")
    print()

    # Generate JSON
    print(f"[build_timeline.py] Generating timeline.json...")
    generate_json(timeline_entries, str(timeline_json_path))
    print(f"  Output: {timeline_json_path}")
    print()

    print("[build_timeline.py] Complete!")
    print(f"  Total entries: {len(timeline_entries)}")
    print(f"  Time span: {timeline_entries[0].date_key.split('-')[0]}–{timeline_entries[-1].date_key.split('-')[0]}")


if __name__ == '__main__':
    main()
