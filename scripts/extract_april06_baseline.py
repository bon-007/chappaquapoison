#!/usr/bin/env python3
"""
Extract the April 6 baseline prose for the 13 chapters that were modified after
April 6 (Sessions 165-167 and later), from ChappaquaPoison_BOOK_2026-04-06.docx.

For each modified chapter, writes:
  Standards/april06_baseline/B<XX>.md
  = current frontmatter (preserved, so the harness still identifies the chapter)
  + April 6 body prose (extracted from the docx)

Also writes:
  Standards/rewrite_report_manifest_april06.json
  which points the harness at the baseline files for the 13 modified chapters
  and at posts/md/ for the other 40 chapters.

This is Phase B of the harness iteration plan from REWRITE_REPORT_SCHEMA.md.
The goal is a true Report A comparable to later reports post-rewrite.
"""

from __future__ import annotations

import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple

HERE = Path(__file__).resolve().parent.parent
DOCX = HERE / "ChappaquaPoison_BOOK_2026-04-06.docx"
MD_DIR = HERE / "posts" / "md"
BASELINE_DIR = HERE / "Standards" / "april06_baseline"
MANIFEST_PATH = HERE / "Standards" / "rewrite_report_manifest_april06.json"

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# Blog B-id -> book chapter number (Prologue="P", 1..49, or "FOR_EVIE", "WHERE_NOW")
# Derived from TOC walk in docx:
#   Prologue            -> B00
#   Book 1..12          -> B01..B12
#   Book 13..49         -> B14..B50  (shift because B13 dissolved)
#   FOR EVIE            -> B51
#   WHERE ARE THEY NOW  -> B52
BLOG_TO_BOOK: Dict[str, object] = {"B00": "P"}
for n in range(1, 13):
    BLOG_TO_BOOK[f"B{n:02d}"] = n
for n in range(13, 50):
    BLOG_TO_BOOK[f"B{n+1:02d}"] = n
BLOG_TO_BOOK["B51"] = "FOR_EVIE"
BLOG_TO_BOOK["B52"] = "WHERE_NOW"
# B53 (back cover) is not in the book body

# Chapters that were modified after April 6 (need extraction from docx).
# Determined by mtime comparison against April 6 md snapshot.
MODIFIED_CHAPTERS = [
    "B19", "B23", "B25", "B29", "B32", "B33",
    "B35", "B37", "B39", "B41", "B45", "B46", "B48",
]


def load_paragraphs(docx_path: Path) -> List[str]:
    with zipfile.ZipFile(docx_path) as z:
        with z.open("word/document.xml") as f:
            tree = ET.parse(f)
    root = tree.getroot()
    paras: List[str] = []
    for p in root.iter(W + "p"):
        text = "".join(t.text or "" for t in p.iter(W + "t"))
        paras.append(text)
    return paras


def find_body_boundaries(paras: List[str]) -> Dict[object, Tuple[int, int]]:
    """Return {book_chapter_key: (body_start_para, body_end_para_exclusive)}."""
    boundaries: List[Tuple[object, int]] = []

    # Prologue: 'PROLOGUE' heading in body region
    for i in range(130, 200):
        if paras[i].strip() == "PROLOGUE":
            # Body begins after the title line
            title_line = i + 1
            body_start = i + 2
            boundaries.append(("P", body_start))
            break

    # Numbered chapters: bare-number paragraph followed by title
    body_region_start = 170
    for i in range(body_region_start, len(paras)):
        t = paras[i].strip()
        if re.fullmatch(r"\d{1,2}", t):
            num = int(t)
            # Skip title line + possibly date line
            j = i + 1
            # Skip blanks
            while j < len(paras) and not paras[j].strip():
                j += 1
            # j = title
            j += 1
            # Skip blanks
            while j < len(paras) and not paras[j].strip():
                j += 1
            # j may be the date line (e.g. "May 2010")
            if j < len(paras) and paras[j].strip() and len(paras[j].strip()) < 60:
                # If it looks like a date or year range, advance
                if re.search(r"\d{4}", paras[j]) or re.match(
                    r"^(Late |Early |Spring|Summer|Fall|Winter|January|February|"
                    r"March|April|May|June|July|August|September|October|November|"
                    r"December|Present)",
                    paras[j].strip(),
                ):
                    j += 1
            boundaries.append((num, j))

    # FOR EVIE and WHERE ARE THEY NOW (unnumbered)
    for i in range(3900, len(paras)):
        t = paras[i].strip()
        if t == "FOR EVIE":
            boundaries.append(("FOR_EVIE", i + 1))
        elif t == "WHERE ARE THEY NOW":
            boundaries.append(("WHERE_NOW", i + 1))
        elif t == "APPENDIX A":
            # body ends here
            boundaries.append(("__APPENDIX__", i))
            break

    # Build (start, end) pairs
    result: Dict[object, Tuple[int, int]] = {}
    for idx, (key, start) in enumerate(boundaries):
        if idx + 1 < len(boundaries):
            next_start = boundaries[idx + 1][1]
            # End is the paragraph just before the next chapter's number line
            # which is next_start - 2 (date) - 1 (title) - 1 (number) - ...
            # Simpler: end at the next chapter's body_start minus a small pad.
            # Walk back from next_start to find the previous number line.
            end = next_start
            # back up past date, title, number paras
            k = next_start - 1
            while k > start and paras[k].strip() == "":
                k -= 1
            # k now on date or title. Walk back a couple more.
            for _ in range(3):
                if k > start and paras[k].strip():
                    k -= 1
            end = k
        else:
            end = len(paras)
        if key != "__APPENDIX__":
            result[key] = (start, end)
    return result


def extract_body_text(paras: List[str], start: int, end: int) -> str:
    """Return the chapter body as markdown-ish prose."""
    lines: List[str] = []
    prev_blank = False
    for i in range(start, end):
        t = paras[i]
        stripped = t.strip()
        if not stripped:
            if not prev_blank:
                lines.append("")
            prev_blank = True
            continue
        # Section breaks
        if stripped in ("⁂", "⸻"):
            lines.append("")
            lines.append("⁂")
            lines.append("")
            prev_blank = True
            continue
        lines.append(stripped)
        prev_blank = False
    # Collapse trailing blanks
    while lines and lines[-1] == "":
        lines.pop()
    return "\n\n".join(ln for ln in lines if ln != "") if False else "\n".join(lines)


def load_current_frontmatter(blog_id: str) -> Tuple[str, str]:
    """Find the current md file for the blog_id and return (frontmatter, rest)."""
    matches = list(MD_DIR.glob(f"{blog_id}_*.md"))
    if not matches:
        raise FileNotFoundError(f"No md file for {blog_id}")
    md_path = matches[0]
    text = md_path.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 4)
        if end != -1:
            frontmatter = text[: end + 4] + "\n"
            rest = text[end + 4 :]
            return frontmatter, rest
    return "", text


def main() -> int:
    if not DOCX.exists():
        print(f"ERROR: {DOCX} not found", file=sys.stderr)
        return 1
    print(f"Loading paragraphs from {DOCX.name}...")
    paras = load_paragraphs(DOCX)
    print(f"  {len(paras)} paragraphs")
    boundaries = find_body_boundaries(paras)
    print(f"  found {len(boundaries)} chapter boundaries")

    BASELINE_DIR.mkdir(parents=True, exist_ok=True)

    extracted: List[str] = []
    for blog_id in MODIFIED_CHAPTERS:
        book_key = BLOG_TO_BOOK.get(blog_id)
        if book_key is None:
            print(f"  SKIP {blog_id}: no book mapping")
            continue
        bounds = boundaries.get(book_key)
        if bounds is None:
            print(f"  SKIP {blog_id}: book key {book_key} not found in boundaries")
            continue
        start, end = bounds
        body = extract_body_text(paras, start, end)
        try:
            frontmatter, _ = load_current_frontmatter(blog_id)
        except FileNotFoundError as e:
            print(f"  SKIP {blog_id}: {e}")
            continue
        out_path = BASELINE_DIR / f"{blog_id}.md"
        with out_path.open("w", encoding="utf-8") as f:
            f.write(frontmatter)
            f.write("\n")
            f.write(body)
            f.write("\n")
        extracted.append(blog_id)
        print(f"  wrote {out_path.name}  (book {book_key}, paras {start}..{end}, "
              f"{len(body.split())} words)")

    # Build manifest pointing at baseline files for extracted chapters and
    # posts/md/ for the rest.
    manifest = {"source_label": "april06_baseline", "chapters": {}}
    # All 53 blog chapters
    all_ids = [f"B{n:02d}" for n in list(range(0, 13)) + list(range(14, 54))]
    for blog_id in all_ids:
        if blog_id in extracted:
            manifest["chapters"][blog_id] = str(
                (BASELINE_DIR / f"{blog_id}.md").relative_to(HERE)
            )
        else:
            matches = list(MD_DIR.glob(f"{blog_id}_*.md"))
            if matches:
                manifest["chapters"][blog_id] = str(matches[0].relative_to(HERE))
            else:
                manifest["chapters"][blog_id] = None
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nManifest written: {MANIFEST_PATH.relative_to(HERE)}")
    print(f"Extracted {len(extracted)}/{len(MODIFIED_CHAPTERS)} modified chapters.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
