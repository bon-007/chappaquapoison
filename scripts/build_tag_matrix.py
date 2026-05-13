#!/usr/bin/env python3
"""
build_tag_matrix.py

Generates three index files from posts.json:
1. TAG_MATRIX.md - Tag frequency and organization by phase
2. PERSON_INDEX.md - Person names, roles, and references
3. COURT_CASE_INDEX.md - Court cases and dockets

Run from project root: python3 scripts/build_tag_matrix.py
"""

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Known persons in the case
KNOWN_PERSONS = {
    "Stephen Russell": {"role": "Plaintiff", "aliases": []},
    "Tara Walsh": {"role": "Respondent", "aliases": ["Tara"]},
    "Evie": {"role": "Minor child", "aliases": ["Evelyn"]},
    "Stephen Walsh Sr.": {"role": "Father of respondent", "aliases": ["Walsh Sr.", "Stephen Walsh Sr"]},
    "Maura Walsh": {"role": "Mother of respondent", "aliases": ["Maura"]},
    "Brienne Walsh": {"role": "Sister of respondent", "aliases": ["Brienne"]},
    "Brendan Walsh": {"role": "Brother of respondent", "aliases": ["Brendan"]},
    "Andrew Griffin": {"role": "Court-appointed evaluator", "aliases": ["Griffin"]},
    "Dr. Gopal": {"role": "Psychiatrist", "aliases": ["Abilash Gopal", "Gopal"]},
    "Gordon-Oliver": {"role": "Judge", "aliases": []},
    "Farquharson": {"role": "Supervising Judge", "aliases": []},
    "Horowitz": {"role": "Judge", "aliases": []},
    "Schauer": {"role": "Judge", "aliases": []},
    "Faith Miller": {"role": "AFC", "aliases": []},
    "Jennifer Jackman": {"role": "AFC", "aliases": []},
    "Donna Genovese": {"role": "AFC", "aliases": []},
    "D'Ambrosia": {"role": "Court clerk", "aliases": []},
    "Meenan": {"role": "Police", "aliases": []},
    "Abrehet Tedla": {"role": "Nanny", "aliases": ["Tedla"]},
    "Bryan Crutcher": {"role": "Security", "aliases": ["Crutcher"]},
    "Pat Williams": {"role": "Security", "aliases": ["Williams"]},
    "Bowman": {"role": "Support magistrate", "aliases": []},
    "Matan Gavish": {"role": "Walsh associate", "aliases": []},
    "LaMelle": {"role": "Supervisor", "aliases": []},
    "Veneziano": {"role": "Evaluator coordinator", "aliases": []},
    "Prendergast": {"role": "Witness", "aliases": []},
    "Guttridge": {"role": "Witness", "aliases": []},
}

# Case number patterns
CASE_PATTERNS = {
    r'FPT-18-377425': ('SF Superior Court', 'DVRO'),
    r'CGC-18-570137': ('SF Superior Court', 'Civil'),
    r'File No\.\s*154703': ('Westchester Family Court', 'Custody'),
    r'3:18-cv-06691': ('N.D. Cal.', 'Federal'),
    r'A165356': ('CA Court of Appeal', 'Appeal'),
    r'214 AD3d 890': ('NY Appellate Division', 'Appeal'),
    r'S\.D\.N\.Y\.\s*\(2026\)': ('S.D.N.Y.', 'Civil Rights'),
}


def load_posts():
    """Load and parse posts.json"""
    with open('posts.json', 'r') as f:
        return json.load(f)


def extract_tags(posts):
    """Extract all tags and their frequencies from posts"""
    tag_freq = defaultdict(int)
    tag_posts = defaultdict(list)

    for post in posts:
        post_id = post.get('id', '')
        tags = post.get('tags', [])

        for tag in tags:
            tag_freq[tag] += 1
            tag_posts[tag].append(post_id)

    return tag_freq, tag_posts


def organize_posts_by_phase(posts):
    """Organize posts by phase for TAG_MATRIX"""
    phases = defaultdict(list)

    for post in posts:
        phase_name = post.get('phase_name', 'Unknown')
        phases[phase_name].append(post)

    # Sort by phase appearance in data
    phase_order = [
        "Before Tara",
        "Meeting Tara",
        "The Crime",
        "The Flight",
        "The Cover",
        "The Silencing",
        "The Jury",
        "Civil Rights",
        "The Silence",
    ]

    ordered = {}
    for phase in phase_order:
        if phase in phases:
            ordered[phase] = phases[phase]

    # Add any remaining phases
    for phase in sorted(phases.keys()):
        if phase not in ordered:
            ordered[phase] = phases[phase]

    return ordered


def extract_persons_from_text(text):
    """Extract person names from text"""
    found = defaultdict(set)

    if not text:
        return found

    # Convert text to lowercase for matching, but preserve original
    text_lower = text.lower()

    for person_name, person_info in KNOWN_PERSONS.items():
        person_lower = person_name.lower()

        # Check main name
        if person_lower in text_lower:
            found[person_name].add(person_info['role'])

        # Check aliases
        for alias in person_info['aliases']:
            alias_lower = alias.lower()
            if alias_lower in text_lower and person_lower not in text_lower:
                found[person_name].add(person_info['role'])

    return found


def extract_evidence_ids(collected_files):
    """Extract evidence IDs from file paths"""
    evidence_ids = []

    if not collected_files:
        return evidence_ids

    for filepath in collected_files:
        # Extract evidence prefix (e.g., "B-1", "C-6", etc.)
        match = re.search(r'Ex([A-Z]+)_(\d+)', filepath)
        if match:
            prefix = match.group(1)
            num = match.group(2)
            # Convert to evidence notation
            evidence_ids.append(f"{prefix}-{num}")

    return evidence_ids


def extract_case_numbers(text):
    """Extract case numbers from text"""
    cases = defaultdict(set)

    if not text:
        return cases

    for pattern, (court, docket) in CASE_PATTERNS.items():
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            case_num = match.group(0)
            cases[case_num] = (court, docket)

    return cases


def build_tag_matrix(posts, tag_freq, tag_posts):
    """Build TAG_MATRIX.md"""
    organized_by_phase = organize_posts_by_phase(posts)

    # Sort tags by frequency
    sorted_tags = sorted(tag_freq.items(), key=lambda x: x[1], reverse=True)

    # Build markdown
    md = []
    md.append("# ChappaquaPoison v2 — Tag Matrix")
    md.append("")
    md.append(f"**Total Tags:** {len(tag_freq)}")
    md.append(f"**Total Posts:** {len(posts)}")
    md.append(f"**Last Updated:** {datetime.now().strftime('%B %d, %Y')}")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## Tags by Frequency")
    md.append("")
    md.append("| Tag | Count | Posts |")
    md.append("|-----|-------|-------|")

    for tag, count in sorted_tags:
        post_list = ", ".join(tag_posts[tag][:10])
        if len(tag_posts[tag]) > 10:
            post_list += ", ..."
        md.append(f"| {tag} | {count} | {post_list} |")

    md.append("")
    md.append("## Tags by Phase")
    md.append("")

    for phase_name, phase_posts in organized_by_phase.items():
        md.append(f"### {phase_name}")

        # Collect all tags for this phase
        phase_tags = defaultdict(list)
        for post in phase_posts:
            for tag in post.get('tags', []):
                phase_tags[tag].append(post.get('id', ''))

        # Sort by frequency within phase
        sorted_phase_tags = sorted(phase_tags.items(),
                                  key=lambda x: len(x[1]),
                                  reverse=True)

        md.append("| Tag | Posts |")
        md.append("|-----|-------|")

        for tag, post_ids in sorted_phase_tags:
            post_list = ", ".join(post_ids)
            md.append(f"| {tag} | {post_list} |")

        md.append("")

    return "\n".join(md)


def build_person_index(posts):
    """Build PERSON_INDEX.md"""
    person_refs = defaultdict(lambda: {"roles": set(), "posts": set(), "evidence": set()})

    for post in posts:
        post_id = post.get('id', '')
        summary = post.get('summary', '')
        title = post.get('title', '')
        evidence_section = post.get('evidence', {})

        # Combine all text to search
        search_text = f"{title} {summary}"
        if evidence_section:
            search_text += f" {evidence_section.get('timeline', '')} {evidence_section.get('supporting_documents', '')}"

        # Extract persons
        found_persons = extract_persons_from_text(search_text)

        for person_name, roles in found_persons.items():
            person_refs[person_name]['roles'].update(roles)
            person_refs[person_name]['posts'].add(post_id)

        # Extract evidence from collected_files
        collected_files = evidence_section.get('collected_files', [])
        evidence_ids = extract_evidence_ids(collected_files)
        for person_name in found_persons.keys():
            person_refs[person_name]['evidence'].update(evidence_ids)

    # Build markdown
    md = []
    md.append("# ChappaquaPoison v2 — Person Index")
    md.append("")
    md.append("| Person | Role | Posts | Evidence |")
    md.append("|--------|------|-------|----------|")

    for person_name in sorted(person_refs.keys()):
        data = person_refs[person_name]
        role = ", ".join(sorted(data['roles'])) if data['roles'] else "Unknown"
        posts_str = ", ".join(sorted(data['posts']))
        evidence_str = ", ".join(sorted(data['evidence'])) if data['evidence'] else ""

        md.append(f"| {person_name} | {role} | {posts_str} | {evidence_str} |")

    return "\n".join(md)


def build_court_case_index(posts):
    """Build COURT_CASE_INDEX.md"""
    case_refs = defaultdict(lambda: {"court": "", "docket": "", "posts": set(), "evidence": set()})

    for post in posts:
        post_id = post.get('id', '')
        summary = post.get('summary', '')
        title = post.get('title', '')
        evidence_section = post.get('evidence', {})

        # Combine all text
        search_text = f"{title} {summary}"
        if evidence_section:
            search_text += f" {evidence_section.get('timeline', '')} {evidence_section.get('supporting_documents', '')}"

        # Extract cases
        found_cases = extract_case_numbers(search_text)

        for case_num, (court, docket) in found_cases.items():
            case_refs[case_num]['court'] = court
            case_refs[case_num]['docket'] = docket
            case_refs[case_num]['posts'].add(post_id)

        # Extract evidence
        collected_files = evidence_section.get('collected_files', [])
        evidence_ids = extract_evidence_ids(collected_files)
        for case_num in found_cases.keys():
            case_refs[case_num]['evidence'].update(evidence_ids)

    # Build markdown
    md = []
    md.append("# ChappaquaPoison v2 — Court Case Index")
    md.append("")
    md.append("| Case | Court | Docket | Posts | Evidence |")
    md.append("|------|-------|--------|-------|----------|")

    for case_num in sorted(case_refs.keys()):
        data = case_refs[case_num]
        court = data['court']
        docket = data['docket']
        posts_str = ", ".join(sorted(data['posts']))
        evidence_str = ", ".join(sorted(data['evidence'])) if data['evidence'] else "—"

        md.append(f"| {case_num} | {court} | {docket} | {posts_str} | {evidence_str} |")

    return "\n".join(md)


def main():
    """Main execution"""
    print("Loading posts.json...")
    data = load_posts()
    posts = data.get('posts', [])
    print(f"  Loaded {len(posts)} posts")

    print("\nExtracting tags...")
    tag_freq, tag_posts = extract_tags(posts)
    print(f"  Found {len(tag_freq)} unique tags")

    print("\nBuilding TAG_MATRIX.md...")
    tag_matrix = build_tag_matrix(posts, tag_freq, tag_posts)

    print("\nBuilding PERSON_INDEX.md...")
    person_index = build_person_index(posts)

    print("\nBuilding COURT_CASE_INDEX.md...")
    court_case_index = build_court_case_index(posts)

    # Write files to project root
    print("\nWriting output files...")

    tag_matrix_path = Path("TAG_MATRIX.md")
    with open(tag_matrix_path, 'w') as f:
        f.write(tag_matrix)
    print(f"  ✓ {tag_matrix_path}")

    person_index_path = Path("PERSON_INDEX.md")
    with open(person_index_path, 'w') as f:
        f.write(person_index)
    print(f"  ✓ {person_index_path}")

    court_case_path = Path("COURT_CASE_INDEX.md")
    with open(court_case_path, 'w') as f:
        f.write(court_case_index)
    print(f"  ✓ {court_case_path}")

    print("\nDone!")
    print(f"\nSummary:")
    print(f"  Tags: {len(tag_freq)}")
    print(f"  Persons: {len(extract_persons_from_text(' '.join([p.get('summary', '') + ' ' + p.get('title', '') for p in posts])))}")


if __name__ == "__main__":
    main()
