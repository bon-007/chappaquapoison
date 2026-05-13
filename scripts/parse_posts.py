#!/usr/bin/env python3
"""
Parse PROPOSED_POSTS_AND_EVIDENCE.md into structured JSON format.

This script parses the ChappaquaPoison v2 markdown documentation into a machine-readable
JSON structure with the following top-level keys:
  - static_pages: Array of 14 static pages (S-1 through S-14)
  - posts: Array of 91 posts organized across 9 phases

POSTS STRUCTURE:
Each post contains:
  - id: Post ID (e.g., "P1", "P22B", "P41A")
  - number: Post number (1-72)
  - title: Post title from markdown heading
  - phase: Phase number (Roman I-IX)
  - phase_name: Phase name (e.g., "Before Tara")
  - date_context: Date range or timeline context
  - summary: Post summary text
  - evidence: Object containing:
      - timeline: Timeline details
      - supporting_documents: Document references
      - collected_files: Array of evidence file paths
      - editor_note: Editor's note (may contain ECS score)
      - source_note: Source methodology note
  - tags: Array of topic tags (3-5 tags per post)
  - ecs: Evidence Confidence Score (50-100, extracted from editor/source notes)
  - cross_links: Array of related post IDs (for future use)

SUB-POST HANDLING:
Posts with letter suffixes (B, C, D, etc.) are parsed with full ID:
  - P22B (Mycophenolic Acid — Seven Times Normal)
  - P27B (Two Courts, One Child)
  - P35B (The Procedural Paradox)
  - P41A-P41I (The LaMelle Confrontation through The Permanent DVRO)
  - P48A-P48D (Phase VI sub-posts)
  - P66A-P66D (Phase VIII sub-posts)

ECS SCORE EXTRACTION:
Automatically extracts Evidence Confidence Scores from Editor's Notes and Source Notes.
Handles ranges (e.g., "ECS 65–85") by taking the higher value.
Scores reflect source reliability:
  - 90-100: Court filings, judicial orders, sworn testimony
  - 75-89: Discovery materials, deposition transcripts, Bates-stamped documents
  - 60-74: Published blog posts, media coverage, public correspondence
  - 50-59: Reconstructed from secondary sources with noted limitations

PHASE MAPPING:
  - Phase I: Posts 1-6 (Before Tara)
  - Phase II: Posts 7-13 (Meeting Tara)
  - Phase III: Posts 14-22 (The Crime)
  - Phase IV: Posts 23-28 (The Flight)
  - Phase V: Posts 29-41 (The Cover)
  - Phase VI: Posts 42-48 (The Silencing)
  - Phase VII: Posts 49-55 (The Jury)
  - Phase VIII: Posts 56-66 (Civil Rights)
  - Phase IX: Posts 67-72 (The Silence)

OUTPUT:
Generates posts.json in the same directory as the markdown source.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Phase mapping
PHASES = {
    "I": {"name": "Before Tara", "posts": (1, 6)},
    "II": {"name": "Meeting Tara", "posts": (7, 13)},
    "III": {"name": "The Crime", "posts": (14, 22)},
    "IV": {"name": "The Flight", "posts": (23, 28)},
    "V": {"name": "The Cover", "posts": (29, 41)},
    "VI": {"name": "The Silencing", "posts": (42, 48)},
    "VII": {"name": "The Jury", "posts": (49, 57)},
    "VIII": {"name": "Civil Rights", "posts": (58, 66)},
    "IX": {"name": "The Silence", "posts": (67, 72)},
}

# Static pages
STATIC_PAGES = [
    {"id": "S-1", "title": "Homepage / Index", "purpose": "Reverse-chronological post feed with phase navigation, tag cloud, search"},
    {"id": "S-2", "title": "About This Archive", "purpose": "What this site is, what it is not, source provenance"},
    {"id": "S-3", "title": "How to Read This Archive", "purpose": "Reader orientation: ECS scoring explained, reconstruction notices, source tiers"},
    {"id": "S-4", "title": "Methodology & Sources", "purpose": "ECS framework explanation, source tiers, reconstruction transparency"},
    {"id": "S-5", "title": "Master Timeline", "purpose": "Interactive chronological timeline (234 entries, 1993–2026)"},
    {"id": "S-6", "title": "Evidence Index", "purpose": "Searchable catalog of all referenced evidence artifacts"},
    {"id": "S-7", "title": "Person Index", "purpose": "Linked directory of all named individuals and their roles"},
    {"id": "S-8", "title": "Court Case Index", "purpose": "All dockets: FPT-18-377425, CGC-18-570137, 3:18-cv-06691, File No. 154703, etc."},
    {"id": "S-9", "title": "Patterns", "purpose": "Cross-cutting synthesis: defaults, supervisor replacements, police incidents, Griffin reliance, recusals, speech restrictions"},
    {"id": "S-10", "title": "If This Archive Is Wrong", "purpose": "Falsifiability page: what documents would disprove key claims"},
    {"id": "S-11", "title": "Public Record Notice", "purpose": "Standing disclaimer, source provenance shield"},
    {"id": "S-12", "title": "Audit Log", "purpose": "Transparent versioning: launch date, major updates, artifact counts"},
    {"id": "S-13", "title": "The Case in 10 Documents", "purpose": "Ten one-page document excerpts, no commentary"},
    {"id": "S-14", "title": "Public Record Inventory", "purpose": "Checkable inventory of every document category with public-record status"},
]


def parse_ecs_score(text: str) -> Optional[int]:
    """Extract ECS score from text. Returns highest value if range given."""
    if not text:
        return None

    # Look for patterns like "ECS 90", "ECS 65–85", "ECS 95", etc.
    ecs_pattern = r'ECS\s+(\d+)(?:–(\d+))?'
    match = re.search(ecs_pattern, text, re.IGNORECASE)

    if match:
        first = int(match.group(1))
        second = int(match.group(2)) if match.group(2) else None
        # Return the higher value if range is given
        return max(first, second) if second else first

    return None


def parse_post_id(heading: str) -> Tuple[str, int, Optional[str]]:
    """
    Parse post ID from heading like 'Post 1:', 'Post 22B:', 'Post 41A:', etc.
    Returns tuple of (full_id, number, sub_id).
    Example: 'Post 1:' -> ('P1', 1, None)
             'Post 22B:' -> ('P22B', 22, 'B')
             'Post 41A:' -> ('P41A', 41, 'A')
    """
    # Remove markdown heading syntax
    clean_heading = heading.replace('###', '').strip()
    match = re.match(r'Post\s+(\d+)([A-Z])?:', clean_heading)
    if not match:
        return None, None, None

    num = int(match.group(1))
    sub_id = match.group(2)

    # Format as P + number + optional letter
    if sub_id:
        full_id = f"P{num}{sub_id}"
    else:
        full_id = f"P{num}"

    return full_id, num, sub_id


def determine_phase(post_num: int, sub_id: Optional[str]) -> Tuple[str, str]:
    """Determine phase number and name from post number."""
    for phase_num, phase_info in PHASES.items():
        start, end = phase_info["posts"]
        if start <= post_num <= end:
            return phase_num, phase_info["name"]
    return None, None


def extract_section(lines: List[str], start_idx: int, end_idx: int, label: str) -> str:
    """Extract a section from lines between two indices."""
    section_lines = []
    for i in range(start_idx, min(end_idx, len(lines))):
        line = lines[i]
        # Stop at the next heading or bullet
        if i > start_idx and (line.strip().startswith('###') or line.strip().startswith('-')):
            break
        section_lines.append(line.rstrip())

    return '\n'.join(section_lines).strip()


def parse_bullet_field(lines: List[str], start_idx: int, field_name: str) -> Tuple[str, int]:
    """
    Parse a bullet field like '- **Date context:** ...'
    Returns (content, next_line_index)
    """
    if start_idx >= len(lines):
        return "", start_idx

    line = lines[start_idx]
    pattern = rf'^\s*-\s*\*\*{re.escape(field_name)}:\*\*\s*(.*)'
    match = re.match(pattern, line)

    if not match:
        return "", start_idx

    content = match.group(1).strip()
    idx = start_idx + 1

    # Handle multi-line content (continuation lines without bullet)
    while idx < len(lines):
        next_line = lines[idx]
        # Stop if we hit another bullet field or a heading
        if next_line.strip().startswith('-') or next_line.strip().startswith('###'):
            break
        # Stop if we hit a blank line followed by a bullet or heading
        if next_line.strip() == '' and idx + 1 < len(lines):
            if lines[idx + 1].strip().startswith('-') or lines[idx + 1].strip().startswith('###'):
                break

        if next_line.strip() and not next_line.strip().startswith('-'):
            content += ' ' + next_line.strip()
            idx += 1
        else:
            break

    return content, idx


def parse_evidence_section(lines: List[str], start_idx: int) -> Tuple[Dict[str, Any], int]:
    """
    Parse the 'Evidence & Context:' section.
    Returns dict with timeline, supporting_documents, collected_files, editor_note, source_note
    Format can be either:
      - **Evidence & Context:**
        - Timeline: ...
        - Supporting Documents: ...
    OR
      - **Evidence & Context:**
        - Timeline: ...
        - Supporting Documents: ...
    """
    evidence = {
        "timeline": None,
        "supporting_documents": None,
        "collected_files": [],
        "editor_note": None,
        "source_note": None,
    }

    idx = start_idx
    line = lines[idx].strip() if idx < len(lines) else ""

    if not line.startswith('- **Evidence & Context:**'):
        return evidence, idx

    idx += 1  # Move past the "Evidence & Context:" line

    while idx < len(lines):
        line = lines[idx]
        stripped = line.strip()

        # Stop at next post or major section
        if stripped.startswith('###') or stripped.startswith('## PHASE'):
            break

        # Stop at Tags field
        if stripped.startswith('- **Tags:'):
            break

        # Skip blank lines
        if stripped == '':
            idx += 1
            continue

        # Parse indented sub-fields (format: "  - Timeline: ..." or "  - Timeline:")
        if '- Timeline:' in stripped:
            # Extract content after "Timeline:"
            match = re.match(r'\s*-\s+Timeline:\s*(.*)', line)
            if match:
                content = match.group(1).strip()
                idx += 1
                # Accumulate multi-line content
                while idx < len(lines) and lines[idx].startswith('    '):
                    content += ' ' + lines[idx].strip()
                    idx += 1
                evidence["timeline"] = content if content else None
            else:
                idx += 1

        elif '- Supporting Documents:' in stripped:
            match = re.match(r'\s*-\s+Supporting Documents:\s*(.*)', line)
            if match:
                content = match.group(1).strip()
                idx += 1
                # Accumulate multi-line content
                while idx < len(lines) and lines[idx].startswith('    '):
                    content += ' ' + lines[idx].strip()
                    idx += 1
                evidence["supporting_documents"] = content if content else None
            else:
                idx += 1

        elif '- Collected Files:' in stripped:
            # Extract files from the line (can be inline or multi-line)
            match = re.match(r'\s*-\s+Collected Files:\s*(.*)', line)
            if match:
                content = match.group(1).strip()
                idx += 1

                # If content starts with "Evidence/", parse files
                if content.startswith('Evidence/') or content.startswith('('):
                    # Split by semicolon and extract file paths
                    if content.startswith('('):
                        # Special case like "(Background post — no primary evidence files collected)"
                        evidence["collected_files"] = []
                    else:
                        # Parse semicolon-separated files
                        files = [f.strip() for f in content.split(';') if f.strip().startswith('Evidence/')]
                        evidence["collected_files"] = files
                else:
                    # Might be empty or special case
                    if '(Background post' in content or 'no primary evidence' in content:
                        evidence["collected_files"] = []
                    else:
                        # Try to parse as file path anyway
                        if content.startswith('Evidence/'):
                            evidence["collected_files"] = [content.rstrip(';')]
                        else:
                            evidence["collected_files"] = []
            else:
                idx += 1

        elif "- Editor's Note:" in stripped or '- Editor\'s Note:' in stripped:
            match = re.match(r"\s*-\s+Editor.?s Note:\s*(.*)", line)
            if match:
                content = match.group(1).strip()
                idx += 1
                # Accumulate multi-line content
                while idx < len(lines) and lines[idx].startswith('    '):
                    content += ' ' + lines[idx].strip()
                    idx += 1
                evidence["editor_note"] = content if content else None
            else:
                idx += 1

        elif '- Source Note:' in stripped:
            match = re.match(r'\s*-\s+Source Note:\s*(.*)', line)
            if match:
                content = match.group(1).strip()
                idx += 1
                # Accumulate multi-line content
                while idx < len(lines) and lines[idx].startswith('    '):
                    content += ' ' + lines[idx].strip()
                    idx += 1
                evidence["source_note"] = content if content else None
            else:
                idx += 1
        else:
            idx += 1

    return evidence, idx


def parse_tags(lines: List[str], start_idx: int) -> Tuple[List[str], int]:
    """Parse Tags field."""
    if start_idx >= len(lines):
        return [], start_idx

    line = lines[start_idx].strip()
    if not line.startswith('- **Tags:'):
        return [], start_idx

    # Extract content after "- **Tags:** "
    match = re.match(r'^\s*-\s*\*\*Tags:\*\*\s*(.*)', line)
    if not match:
        return [], start_idx + 1

    tag_str = match.group(1).strip()
    tags = [t.strip() for t in tag_str.split(',')]

    return tags, start_idx + 1


def parse_posts(content: str) -> List[Dict[str, Any]]:
    """Parse all posts from markdown content."""
    lines = content.split('\n')
    posts = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Look for post headers: "### Post N:" or "### Post NA:"
        if line.strip().startswith('### Post '):
            heading = line.strip()
            post_id, post_num, sub_id = parse_post_id(heading)

            if post_id is None:
                i += 1
                continue

            # Extract title from heading (everything after "### Post N: ")
            # Format: ### Post 1: "The Inventor"
            title_match = re.match(r'###\s+Post\s+\d+[A-Z]?:\s*"([^"]+)"', heading)
            if not title_match:
                i += 1
                continue

            title = title_match.group(1)

            # Determine phase
            phase_num, phase_name = determine_phase(post_num, sub_id)

            # Parse bullet fields
            i += 1
            date_context = ""
            summary = ""

            while i < len(lines):
                bullet_line = lines[i].strip()

                if bullet_line.startswith('- **Date context:'):
                    date_context, i = parse_bullet_field(lines, i, "Date context")
                elif bullet_line.startswith('- **Summary:'):
                    summary, i = parse_bullet_field(lines, i, "Summary")
                elif bullet_line.startswith('- **Evidence & Context:'):
                    evidence, i = parse_evidence_section(lines, i)
                elif bullet_line.startswith('- **Tags:'):
                    tags, i = parse_tags(lines, i)
                elif bullet_line.startswith('###') or bullet_line.startswith('##'):
                    break
                elif bullet_line == '---':
                    i += 1
                    break
                else:
                    i += 1

            # Extract ECS score from evidence
            ecs_score = None
            if evidence.get("editor_note"):
                ecs_score = parse_ecs_score(evidence["editor_note"])
            if not ecs_score and evidence.get("source_note"):
                ecs_score = parse_ecs_score(evidence["source_note"])

            # Create post object
            post = {
                "id": post_id,
                "number": post_num,
                "title": title,
                "phase": phase_num,
                "phase_name": phase_name,
                "date_context": date_context,
                "summary": summary,
                "evidence": evidence,
                "tags": tags,
                "ecs": ecs_score,
                "cross_links": []
            }

            posts.append(post)
        else:
            i += 1

    return posts


def main():
    """Main parsing function."""
    project_root = Path(__file__).resolve().parent.parent
    md_path = project_root / "PROPOSED_POSTS_AND_EVIDENCE.md"
    output_path = project_root / "posts.json"

    # Read markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse posts
    posts = parse_posts(content)

    # Create output structure
    output = {
        "static_pages": STATIC_PAGES,
        "posts": posts
    }

    # Write JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"Parsed {len(posts)} posts from {len(STATIC_PAGES)} static pages")
    print(f"\nBreakdown by phase:")

    phase_counts = {}
    for post in posts:
        phase = post.get("phase")
        if phase:
            phase_counts[phase] = phase_counts.get(phase, 0) + 1

    for phase_num in sorted(PHASES.keys(), key=lambda x: int(x.split()[0]) if x[0].isdigit() else 0):
        count = phase_counts.get(phase_num, 0)
        phase_name = PHASES[phase_num]["name"]
        print(f"  Phase {phase_num} ({phase_name}): {count} posts")

    print(f"\nTotal: {len(posts)} posts")
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    main()
