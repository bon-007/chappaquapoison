#!/usr/bin/env python3
"""Improve evidence descriptions using post content and evidence titles.

Strategy:
1. For items with related posts — search post content for mentions of the evidence
   title/exhibit ID, extract surrounding context to write a description.
2. For items without post context — generate descriptions from title, category,
   and filename patterns using templates that explain what the evidence IS and
   why it matters.

⚠ DEPRECATED: This script's data has been absorbed into evidence_index_canonical.json.
To update evidence data, edit directly in canonical and re-run: python3 scripts/build_canonical_evidence_index.py
"""

import json
import os
import re
import glob
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EVIDENCE_META = PROJECT_ROOT / "evidence_metadata.json"
POSTS_DIR = PROJECT_ROOT / "posts" / "md"

# Minimum description length to be considered "good enough"
MIN_DESC_LEN = 70


def load_post_content():
    """Load all post markdown content, keyed by post ID."""
    posts = {}
    for md_file in glob.glob(str(POSTS_DIR / "*.md")):
        name = os.path.basename(md_file)
        pid = name.split("_")[0]
        with open(md_file) as f:
            content = f.read()
        # Strip YAML front matter
        parts = content.split("---", 2)
        body = parts[2] if len(parts) >= 3 else content
        posts[pid] = body
    return posts


def extract_context_from_posts(evidence_entry, post_content):
    """Search related posts for mentions of this evidence and extract context."""
    title = evidence_entry.get("title", "")
    exhibit_id = evidence_entry.get("exhibit_id", "")
    related = evidence_entry.get("related_posts", [])

    if not related:
        return None

    # Build search terms from title
    search_terms = []
    # Key name fragments from title
    title_words = re.sub(r'[—–\-\(\)]', ' ', title).split()
    # Build 2-3 word phrases from title
    for i in range(len(title_words) - 1):
        phrase = " ".join(title_words[i:i+2]).lower()
        if len(phrase) > 5 and phrase not in ("the ", "and ", "of the"):
            search_terms.append(phrase)

    # Also search for exhibit ID
    if exhibit_id:
        search_terms.append(exhibit_id.lower())

    # Search in related posts
    best_context = None
    best_score = 0

    for rp in related:
        pid = f"P{rp}" if not rp.startswith("P") else rp
        content = post_content.get(pid, "")
        if not content:
            continue

        # Split into paragraphs
        paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 50]

        for para in paragraphs:
            para_lower = para.lower()
            score = 0
            for term in search_terms:
                if term in para_lower:
                    score += 1

            if score > best_score:
                best_score = score
                # Clean the paragraph
                cleaned = re.sub(r'\*+', '', para)  # Remove bold/italic markers
                cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', cleaned)  # Remove links
                cleaned = re.sub(r'^>\s*', '', cleaned, flags=re.MULTILINE)  # Remove blockquotes
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()

                # Truncate to ~200 chars at sentence boundary
                if len(cleaned) > 200:
                    sentences = re.split(r'(?<=[.!?])\s+', cleaned)
                    result = ""
                    for s in sentences:
                        if len(result) + len(s) > 200:
                            break
                        result = (result + " " + s).strip()
                    best_context = result if result else cleaned[:200]
                else:
                    best_context = cleaned

    return best_context if best_score >= 1 else None


def generate_title_based_description(entry):
    """Generate a description from the title, category, and filename patterns."""
    title = entry.get("title", "")
    category = entry.get("category", "")
    reliability = entry.get("reliability", "")
    file_path = entry.get("file_path", "")
    exhibit_id = entry.get("exhibit_id", "")
    phase = entry.get("phase", "")

    # Extract key entities from the title
    title_clean = title.replace("—", "-").replace("–", "-")

    # Category-specific description templates
    if category == "Declarations & Affidavits":
        # Parse who declared and about what
        if "declaration" in title.lower() or "affidavit" in title.lower():
            person = re.search(r'^(.*?)(?:\s+Declaration|\s+Affidavit)', title, re.I)
            person_name = person.group(1).strip() if person else ""
            topic = re.search(r'(?:Declaration|Affidavit)\s*[-—–]\s*(.+)', title, re.I)
            topic_text = topic.group(1).strip() if topic else ""

            if person_name and topic_text:
                return f"Sworn declaration by {person_name} regarding {topic_text.lower()}. Filed as court evidence establishing firsthand testimony under penalty of perjury."
            elif person_name:
                return f"Sworn declaration by {person_name}, filed as court evidence under penalty of perjury. Part of the discovery record in the custody proceedings."
            else:
                return f"Sworn declaration filed in the custody proceedings. Provides firsthand testimony under oath as part of the evidentiary record."

        if "brief" in title.lower() or "motion" in title.lower():
            return f"Legal filing: {title}. Court document submitted as part of the litigation record in the custody proceedings."

    elif category == "Court Filings":
        if "order" in title.lower():
            return f"Court order: {title}. Official judicial directive issued during the proceedings, carrying the authority of the court."
        elif "judgment" in title.lower() or "ruling" in title.lower():
            return f"Judicial ruling: {title}. Formal court decision establishing binding legal findings in the custody matter."
        elif "motion" in title.lower():
            return f"Court motion: {title}. Formal legal request filed with the court seeking specific judicial action."
        elif "complaint" in title.lower() or "petition" in title.lower():
            return f"Legal filing: {title}. Formal submission initiating or advancing a claim within the court proceedings."
        else:
            return f"Court filing: {title}. Official document submitted to or issued by the court as part of the custody proceedings."

    elif category == "Transcripts & Hearings":
        if "deposition" in title.lower():
            person = re.search(r'^(.*?)\s+Deposition', title, re.I)
            person_name = person.group(1).strip() if person else "witness"
            return f"Sworn deposition testimony of {person_name}, recorded under oath during discovery. Provides direct testimony subject to cross-examination."
        elif "hearing" in title.lower():
            return f"Transcript of court hearing: {title}. Verbatim record of proceedings before the court, documenting judicial statements and party arguments."
        elif "transcript" in title.lower():
            return f"Official transcript: {title}. Verbatim record of proceedings or testimony, certified by the court reporter."
        else:
            return f"Hearing or testimony record: {title}. Official record of statements made under oath or in court proceedings."

    elif category == "Correspondence":
        if "letter" in title.lower():
            return f"Documented correspondence: {title}. Letter forming part of the evidentiary record, establishing positions, demands, or communications between parties."
        elif "email" in title.lower():
            return f"Email correspondence: {title}. Electronic communication preserved as evidence, documenting exchanges between parties relevant to the proceedings."
        else:
            return f"Written correspondence: {title}. Documented communication between parties, preserved as part of the evidentiary record."

    elif category == "Communications":
        if "text" in title.lower() or "sms" in title.lower() or "message" in title.lower():
            return f"Text message evidence: {title}. Preserved mobile communications produced through discovery, documenting real-time exchanges between parties."
        elif "voicemail" in title.lower():
            return f"Voicemail recording: {title}. Audio communication preserved as evidence, documenting statements made by a party."
        else:
            return f"Communication record: {title}. Documented exchange between parties preserved through discovery as part of the evidentiary record."

    elif category == "Lab Reports & Toxicology":
        return f"Laboratory analysis: {title}. Scientific testing results from certified laboratory, providing objective forensic or medical evidence."

    elif category == "Photos & Documents":
        if "photo" in title.lower() or "image" in title.lower():
            return f"Photographic evidence: {title}. Visual documentation preserved as part of the evidentiary record."
        elif "screenshot" in title.lower():
            return f"Digital screenshot: {title}. Screen capture preserving digital content as evidence of communications or online activity."
        else:
            return f"Documentary evidence: {title}. Physical or digital document preserved as part of the evidentiary record in the proceedings."

    elif category == "Video & Audio":
        if "video" in title.lower() or "clip" in title.lower():
            return f"Video evidence: {title}. Audiovisual recording preserved as documentary evidence of events, statements, or conduct."
        elif "audio" in title.lower() or "recording" in title.lower():
            return f"Audio recording: {title}. Sound recording preserved as evidence, documenting statements or events."
        elif "gavish" in title.lower():
            return f"Gavish testimony excerpt: {title}. Video or audio segment from Dr. Gavish's statements, preserved as evidence in the proceedings."
        else:
            return f"Audiovisual evidence: {title}. Recording preserved as part of the evidentiary record documenting events or testimony."

    # Fallback
    return f"Evidence exhibit {exhibit_id}: {title}. Document in the {category.lower()} category, part of the evidentiary record in the custody proceedings."


def main():
    with open(EVIDENCE_META) as f:
        evidence = json.load(f)

    post_content = load_post_content()
    print(f"Loaded {len(post_content)} posts, {len(evidence)} evidence items")

    improved = 0
    from_posts = 0
    from_templates = 0
    already_good = 0

    for file_path, entry in evidence.items():
        current_desc = entry.get("description", "")

        # Skip if already has a good description
        if len(current_desc) >= MIN_DESC_LEN:
            already_good += 1
            continue

        # Try to extract from post content first
        post_context = extract_context_from_posts(entry, post_content)
        if post_context and len(post_context) > len(current_desc):
            entry["description"] = post_context
            from_posts += 1
            improved += 1
            continue

        # Fall back to template-based generation
        new_desc = generate_title_based_description(entry)
        if len(new_desc) > len(current_desc):
            entry["description"] = new_desc
            from_templates += 1
            improved += 1

    # Save
    with open(EVIDENCE_META, "w") as f:
        json.dump(evidence, f, indent=2)

    print(f"\n=== Description Improvement Complete ===")
    print(f"  Already good (>={MIN_DESC_LEN} chars): {already_good}")
    print(f"  Improved from post content: {from_posts}")
    print(f"  Improved from templates: {from_templates}")
    print(f"  Total improved: {improved}")

    # Show stats on new descriptions
    descs = [len(v.get("description", "")) for v in evidence.values()]
    short = sum(1 for d in descs if d < 50)
    medium = sum(1 for d in descs if 50 <= d < MIN_DESC_LEN)
    good = sum(1 for d in descs if d >= MIN_DESC_LEN)
    print(f"\n  Final distribution: short={short}, medium={medium}, good={good}")


if __name__ == "__main__":
    main()
