#!/usr/bin/env python3
"""
Evidence Deep Dive Scanner
==========================
Scans CaseFiles raw archives against blog posts and evidence index
to find potentially relevant, unindexed evidence.

Two modes:
  --mode filename   (default) Fast filename-only matching (~90 seconds)
  --mode content    Deep content scanning — reads .emlx, .txt, .html, .docx
                    files and keyword-matches their text. Catches evidence
                    hiding behind numbered filenames (e.g., 1921.partial.emlx).
                    Slower (~10-30 min depending on archive size).
  --mode both       Runs filename scan first, then content scan on files
                    that had zero filename hits.

Usage:
    python3 evidence_deep_dive.py [--blog-root /path/to/ChappaquaPoison_v3] [--mode filename|content|both]

Output:
    Audits/evidence_deep_dive_log.md          (human-readable report)
    Audits/evidence_deep_dive_hits.json       (machine-readable hits)
    Audits/evidence_content_scan_log.md       (content scan report, if --mode content|both)
    Audits/evidence_content_scan_hits.json    (content scan hits, if --mode content|both)
"""

import os
import re
import json
import sys
import email
import argparse
import traceback
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

ARCHIVE_DIRS = {
    "Blue_PDF_Archive": "../../CaseFiles/16_Raw_Archives/Blue_PDF_Archive",
    "Blue_DOC_Archive": "../../CaseFiles/16_Raw_Archives/Blue_DOC_Archive",
    "Blue_MAIL_Archive": "../../CaseFiles/16_Raw_Archives/Blue_MAIL_Archive",
    "Blue_IMAGE_Archive": "../../CaseFiles/16_Raw_Archives/Blue_IMAGE_Archive",
    "Blue_AUDIO_Archive": "../../CaseFiles/16_Raw_Archives/Blue_AUDIO_Archive",
    "Blue_VIDEO_Archive": "../../CaseFiles/16_Raw_Archives/Blue_VIDEO_Archive",
    "Treasure_Hunt_Archive": "../../CaseFiles/18_Treasure_Hunt_Archive",
    "Ring_Prism": "../../CaseFiles/11_Ring_Prism_v_Amazon",
    "Depositions": "../../CaseFiles/15_Depositions",
    "RICO": "../../CaseFiles/03_Federal_RICO_18-cv-06691",
    "Preservation": "../../CaseFiles/16_Raw_Archives/_Blue_Preservation_Archive",
}

# Key people in the case
PEOPLE = [
    "walsh", "tara", "brienne", "matan", "gavish", "steve", "russell",
    "evie", "tedla", "lamelle", "petrella", "hymowitz", "gopal",
    "crutcher", "ochoa", "gootzeit", "gordon-oliver", "griffin",
    "schauer", "azizi", "rouhi", "rashid", "guttridge", "zarabi",
    "rhodes", "linda", "brendan", "stephen", "nanny", "babysitter",
]

# Key events / concepts
EVENTS = [
    "seroquel", "poisoning", "poison", "drugging", "drugged", "lithium",
    "adderall", "wine", "lethal dose", "overdose",
    "abuse journal", "abuse", "domestic violence", "restraining order",
    "custody", "deposition", "trial", "jury", "verdict", "appeal",
    "rico", "fraud", "fabricat", "falsif", "perjur",
    "bruise", "injury", "hospital", "c-section", "pregnancy",
    "hamptons", "uber", "ambush", "911", "police",
    "forensic", "toxicology", "blood test", "lab report",
    "niacin", "flush", "supplement",
    "supervised visit", "visitation", "family court",
    "blog", "brie grows", "brooklyn",
    "affidavit", "declaration", "testimony", "transcript",
    "hymowitz", "discrepanc",
    "ring", "stock option", "prism", "bot home",
    "sheraton", "hotel", "morning after",
    "iphone", "chat.db", "imessage", "text message",
    "fake crying", "pretending", "coaching",
]

# Exhibit ID patterns to match
EXHIBIT_PATTERNS = [
    r'Ex[A-Z]{1,2}[_-]\d+',    # ExTR_19, ExMM_04, ExA_02, etc.
    r'[A-G]-\d+',               # A-1, B-9, C-6, D-12, F-060, G-36
    r'K-\d+',                    # K-49, K-50
    r'L-\d+',                    # L-series
    r'SLE-\d+',                  # SLE-051, SLE-131, SLE-018
    r'INT-\d+',                  # INT-002
    r'INT-B\d+-\d+',            # INT-B14-001
    r'IMSG-\d+',                 # IMSG-001
    r'EXHIBIT[_ ]P\d+',         # EXHIBIT_P1
    r'D-\d+[a-z]?',             # D-12, D-7, D-2, D-36
]

# Court case identifiers
CASE_IDS = [
    "18-cv-06691", "18SMC00162", "A165356", "214 A.D.3d 890",
    "walsh v. russell", "russell v. ring", "russell v. walsh",
]


# ─────────────────────────────────────────────
# Core Scanner
# ─────────────────────────────────────────────

class EvidenceScanner:
    def __init__(self, blog_root: Path):
        self.blog_root = blog_root
        self.posts_dir = blog_root / "posts" / "md"
        self.evidence_index_path = blog_root / "evidence_index_canonical.json"
        self.evidence_dir = blog_root / "Evidence"
        self.audits_dir = blog_root / "Audits"
        self.audits_dir.mkdir(exist_ok=True)

        # Built during analysis
        self.post_keywords = {}          # post_file -> set of keywords
        self.post_exhibit_ids = {}       # post_file -> set of exhibit IDs
        self.indexed_files = set()       # already-indexed file basenames
        self.indexed_exhibit_ids = set() # already-indexed exhibit IDs
        self.all_keywords = set()        # union of all post keywords
        self.all_exhibit_ids = set()     # union of all post exhibit IDs
        self.hits = []                   # scored hits

        # Stats
        self.stats = {
            "files_scanned": 0,
            "archives_scanned": 0,
            "hits_found": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "per_archive": {},
        }

    def run(self):
        """Main entry point."""
        print("=" * 60)
        print("EVIDENCE DEEP DIVE SCANNER")
        print(f"Blog root: {self.blog_root}")
        print(f"Started: {datetime.now().isoformat()}")
        print("=" * 60)

        print("\n[1/5] Extracting keywords from posts...")
        self._extract_post_keywords()

        print("\n[2/5] Loading evidence index...")
        self._load_evidence_index()

        print("\n[3/5] Scanning archives...")
        self._scan_all_archives()

        print("\n[4/5] Scoring and ranking hits...")
        self._score_hits()

        print("\n[5/5] Writing reports...")
        self._write_reports()

        print("\n" + "=" * 60)
        print(f"COMPLETE — {self.stats['hits_found']} hits found across {self.stats['files_scanned']} files")
        print(f"  Critical: {self.stats['critical']}")
        print(f"  High:     {self.stats['high']}")
        print(f"  Medium:   {self.stats['medium']}")
        print(f"  Low:      {self.stats['low']}")
        print(f"\nReports written to:")
        print(f"  {self.audits_dir / 'evidence_deep_dive_log.md'}")
        print(f"  {self.audits_dir / 'evidence_deep_dive_hits.json'}")
        print("=" * 60)

    # ── Step 1: Extract keywords from posts ──

    def _extract_post_keywords(self):
        if not self.posts_dir.exists():
            print(f"  WARNING: Posts directory not found: {self.posts_dir}")
            return

        md_files = sorted(self.posts_dir.glob("B*.md"))
        print(f"  Found {len(md_files)} post files")

        for md_file in md_files:
            try:
                text = md_file.read_text(encoding="utf-8", errors="replace")
                text_lower = text.lower()

                # Extract keywords
                keywords = set()
                for person in PEOPLE:
                    if person in text_lower:
                        keywords.add(person)
                for event in EVENTS:
                    if event in text_lower:
                        keywords.add(event)
                for case_id in CASE_IDS:
                    if case_id.lower() in text_lower:
                        keywords.add(case_id.lower())

                self.post_keywords[md_file.name] = keywords
                self.all_keywords.update(keywords)

                # Extract exhibit IDs
                exhibit_ids = set()
                for pattern in EXHIBIT_PATTERNS:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    exhibit_ids.update(m.upper() for m in matches)

                self.post_exhibit_ids[md_file.name] = exhibit_ids
                self.all_exhibit_ids.update(exhibit_ids)

            except Exception as e:
                print(f"  ERROR reading {md_file.name}: {e}")

        print(f"  Extracted {len(self.all_keywords)} unique keywords, {len(self.all_exhibit_ids)} exhibit IDs")

    # ── Step 2: Load evidence index ──

    def _load_evidence_index(self):
        if not self.evidence_index_path.exists():
            print(f"  WARNING: Evidence index not found: {self.evidence_index_path}")
            return

        try:
            with open(self.evidence_index_path, "r", encoding="utf-8") as f:
                index = json.load(f)

            entries = index if isinstance(index, list) else index.get("entries", index.get("evidence", []))

            for entry in entries:
                # Get file path
                fp = entry.get("file_path", "") or entry.get("path", "")
                if fp:
                    self.indexed_files.add(os.path.basename(fp).lower())
                    # Also add without extension
                    self.indexed_files.add(os.path.splitext(os.path.basename(fp))[0].lower())

                # Get exhibit ID
                eid = entry.get("exhibit_id", "") or entry.get("id", "")
                if eid:
                    self.indexed_exhibit_ids.add(eid.upper())
                    self.indexed_exhibit_ids.add(eid.lower())

            print(f"  Loaded {len(entries)} index entries")
            print(f"  {len(self.indexed_files)} indexed file basenames")
            print(f"  {len(self.indexed_exhibit_ids)} indexed exhibit IDs")

        except Exception as e:
            print(f"  ERROR loading evidence index: {e}")

    # ── Step 3: Scan archives ──

    def _scan_all_archives(self):
        for archive_name, rel_path in ARCHIVE_DIRS.items():
            archive_path = (self.blog_root / rel_path).resolve()
            if not archive_path.exists():
                print(f"  SKIP {archive_name}: directory not found at {archive_path}")
                continue

            print(f"\n  Scanning {archive_name}...")
            self._scan_archive(archive_name, archive_path)
            self.stats["archives_scanned"] += 1

    def _scan_archive(self, archive_name: str, archive_path: Path):
        file_count = 0
        hit_count = 0

        for root, dirs, files in os.walk(archive_path):
            # Skip hidden directories and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

            for fname in files:
                if fname.startswith("."):
                    continue

                file_count += 1
                fpath = Path(root) / fname
                fname_lower = fname.lower()
                fname_no_ext = os.path.splitext(fname)[0].lower()

                # Skip if already indexed
                if fname_lower in self.indexed_files or fname_no_ext in self.indexed_files:
                    continue

                # Match against keywords and exhibit IDs
                hit = self._match_file(fname, fpath, archive_name)
                if hit:
                    self.hits.append(hit)
                    hit_count += 1

                # Progress indicator for large archives
                if file_count % 500 == 0:
                    print(f"    ...scanned {file_count} files, {hit_count} hits so far")

        self.stats["files_scanned"] += file_count
        self.stats["per_archive"][archive_name] = {
            "files_scanned": file_count,
            "hits_found": hit_count,
        }
        print(f"  {archive_name}: {file_count} files scanned, {hit_count} hits")

    def _match_file(self, fname: str, fpath: Path, archive_name: str) -> dict | None:
        fname_lower = fname.lower()
        fname_no_ext = os.path.splitext(fname)[0].lower()

        matched_keywords = []
        matched_exhibits = []
        matched_people = []
        matched_events = []
        matched_cases = []

        # Check exhibit ID patterns
        for pattern in EXHIBIT_PATTERNS:
            matches = re.findall(pattern, fname, re.IGNORECASE)
            for m in matches:
                m_upper = m.upper()
                if m_upper in self.all_exhibit_ids:
                    matched_exhibits.append(m_upper)

        # Check people
        for person in PEOPLE:
            if person in fname_lower:
                matched_people.append(person)

        # Check events
        for event in EVENTS:
            if event in fname_lower:
                matched_events.append(event)

        # Check case IDs
        for case_id in CASE_IDS:
            if case_id.lower() in fname_lower:
                matched_cases.append(case_id)

        # Combine all matches
        all_matches = matched_exhibits + matched_people + matched_events + matched_cases
        if not all_matches:
            return None

        # Determine which posts this might be relevant to
        relevant_posts = set()
        for post_name, post_kw in self.post_keywords.items():
            overlap = post_kw.intersection(set(matched_people + matched_events + matched_cases))
            if overlap:
                relevant_posts.add(post_name)
        for post_name, post_ex in self.post_exhibit_ids.items():
            if set(matched_exhibits).intersection(post_ex):
                relevant_posts.add(post_name)

        # Get file size
        try:
            size = fpath.stat().st_size
        except:
            size = 0

        return {
            "file": fname,
            "path": str(fpath),
            "archive": archive_name,
            "size_bytes": size,
            "matched_exhibits": matched_exhibits,
            "matched_people": matched_people,
            "matched_events": matched_events,
            "matched_cases": matched_cases,
            "total_matches": len(all_matches),
            "relevant_posts": sorted(relevant_posts),
            "score": 0,  # scored in Step 4
            "tier": "",   # assigned in Step 4
        }

    # ── Step 4: Score hits ──

    def _score_hits(self):
        for hit in self.hits:
            score = 0

            # CRITICAL: matches an exhibit ID referenced in posts but missing from index
            for ex_id in hit["matched_exhibits"]:
                if ex_id.upper() not in self.indexed_exhibit_ids:
                    score += 3
                    hit["tier"] = "CRITICAL"

            # HIGH: multiple keyword categories matched
            categories_matched = sum([
                1 if hit["matched_exhibits"] else 0,
                1 if hit["matched_people"] else 0,
                1 if hit["matched_events"] else 0,
                1 if hit["matched_cases"] else 0,
            ])
            if categories_matched >= 2:
                score += 2
                if not hit["tier"]:
                    hit["tier"] = "HIGH"

            # MEDIUM: strong single-keyword match
            if hit["total_matches"] >= 2 and not hit["tier"]:
                score += 1
                hit["tier"] = "MEDIUM"

            # LOW: weak match
            if not hit["tier"]:
                score += 0.5
                hit["tier"] = "LOW"

            # Bonus for relevant to many posts
            if len(hit["relevant_posts"]) >= 3:
                score += 0.5

            # Bonus for larger files (more likely substantive)
            if hit["size_bytes"] > 100_000:
                score += 0.25

            hit["score"] = score

        # Sort by score descending
        self.hits.sort(key=lambda h: (-h["score"], h["file"]))

        # Update stats
        self.stats["hits_found"] = len(self.hits)
        self.stats["critical"] = sum(1 for h in self.hits if h["tier"] == "CRITICAL")
        self.stats["high"] = sum(1 for h in self.hits if h["tier"] == "HIGH")
        self.stats["medium"] = sum(1 for h in self.hits if h["tier"] == "MEDIUM")
        self.stats["low"] = sum(1 for h in self.hits if h["tier"] == "LOW")

    # ── Step 5: Write reports ──

    def _write_reports(self):
        self._write_markdown_report()
        self._write_json_report()

    def _write_markdown_report(self):
        out = self.audits_dir / "evidence_deep_dive_log.md"
        lines = []
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines.append("# Evidence Deep Dive Log")
        lines.append(f"**Run date:** {ts}")
        lines.append(f"**Archives scanned:** {self.stats['archives_scanned']}")
        lines.append(f"**Total files scanned:** {self.stats['files_scanned']}")
        lines.append(f"**Potential hits found:** {self.stats['hits_found']}")
        lines.append(f"**Critical:** {self.stats['critical']} | **High:** {self.stats['high']} | **Medium:** {self.stats['medium']} | **Low:** {self.stats['low']}")
        lines.append("")

        # Per-archive stats
        lines.append("## Archive Scan Summary")
        lines.append("| Archive | Files Scanned | Hits Found |")
        lines.append("|---------|--------------|------------|")
        for name, stats in self.stats["per_archive"].items():
            lines.append(f"| {name} | {stats['files_scanned']:,} | {stats['hits_found']:,} |")
        lines.append("")

        # CRITICAL hits
        critical = [h for h in self.hits if h["tier"] == "CRITICAL"]
        lines.append(f"## CRITICAL HITS ({len(critical)} items)")
        lines.append("*These match exhibit IDs referenced in posts but missing from the evidence index.*")
        lines.append("")
        if critical:
            for h in critical:
                lines.append(f"### {h['file']}")
                lines.append(f"- **Archive:** {h['archive']}")
                lines.append(f"- **Path:** `{h['path']}`")
                lines.append(f"- **Size:** {_fmt_size(h['size_bytes'])}")
                lines.append(f"- **Matched Exhibits:** {', '.join(h['matched_exhibits'])}")
                lines.append(f"- **Matched People:** {', '.join(h['matched_people'])}")
                lines.append(f"- **Matched Events:** {', '.join(h['matched_events'])}")
                lines.append(f"- **Relevant Posts:** {', '.join(h['relevant_posts'][:10])}")
                lines.append(f"- **Score:** {h['score']}")
                lines.append("")
        else:
            lines.append("*None found.*\n")

        # HIGH hits
        high = [h for h in self.hits if h["tier"] == "HIGH"]
        lines.append(f"## HIGH-RELEVANCE HITS ({len(high)} items)")
        lines.append("")
        if high:
            lines.append("| File | Archive | People | Events | Posts | Score |")
            lines.append("|------|---------|--------|--------|-------|-------|")
            for h in high[:100]:  # Cap at 100
                people = ", ".join(h["matched_people"][:3])
                events = ", ".join(h["matched_events"][:3])
                posts = ", ".join(h["relevant_posts"][:3])
                lines.append(f"| {h['file'][:60]} | {h['archive']} | {people} | {events} | {posts} | {h['score']} |")
            if len(high) > 100:
                lines.append(f"| *...and {len(high)-100} more* | | | | | |")
            lines.append("")
        else:
            lines.append("*None found.*\n")

        # MEDIUM hits
        medium = [h for h in self.hits if h["tier"] == "MEDIUM"]
        lines.append(f"## MEDIUM-RELEVANCE HITS ({len(medium)} items)")
        lines.append("")
        if medium:
            lines.append("| File | Archive | Matches | Score |")
            lines.append("|------|---------|---------|-------|")
            for h in medium[:200]:  # Cap at 200
                matches = ", ".join(h["matched_people"][:2] + h["matched_events"][:2])
                lines.append(f"| {h['file'][:60]} | {h['archive']} | {matches} | {h['score']} |")
            if len(medium) > 200:
                lines.append(f"| *...and {len(medium)-200} more* | | | |")
            lines.append("")
        else:
            lines.append("*None found.*\n")

        # LOW hits (just count)
        low = [h for h in self.hits if h["tier"] == "LOW"]
        lines.append(f"## LOW-RELEVANCE HITS ({len(low)} items)")
        lines.append("*Low-relevance hits are logged in the JSON output only.*\n")

        # Top 20 overall
        lines.append("## TOP 20 UNINDEXED FILES BY RELEVANCE")
        lines.append("")
        for i, h in enumerate(self.hits[:20], 1):
            lines.append(f"**{i}. {h['file']}** (Score: {h['score']}, {h['tier']})")
            lines.append(f"   Archive: {h['archive']} | Size: {_fmt_size(h['size_bytes'])}")
            all_matches = h["matched_exhibits"] + h["matched_people"] + h["matched_events"] + h["matched_cases"]
            lines.append(f"   Matches: {', '.join(all_matches[:8])}")
            lines.append(f"   Relevant posts: {', '.join(h['relevant_posts'][:5])}")
            lines.append("")

        # Post coverage analysis
        lines.append("## POST COVERAGE ANALYSIS")
        lines.append("*Which posts have the most unindexed evidence in the archives?*\n")
        post_hit_count = defaultdict(int)
        post_critical_count = defaultdict(int)
        for h in self.hits:
            for p in h["relevant_posts"]:
                post_hit_count[p] += 1
                if h["tier"] == "CRITICAL":
                    post_critical_count[p] += 1

        lines.append("| Post | Total Hits | Critical | Priority |")
        lines.append("|------|-----------|----------|----------|")
        for post in sorted(post_hit_count, key=lambda p: (-post_critical_count.get(p, 0), -post_hit_count[p])):
            crit = post_critical_count.get(post, 0)
            priority = "!!!" if crit > 0 else ("!!" if post_hit_count[post] > 10 else "!")
            lines.append(f"| {post} | {post_hit_count[post]} | {crit} | {priority} |")
        lines.append("")

        out.write_text("\n".join(lines), encoding="utf-8")
        print(f"  Wrote {out} ({len(lines)} lines)")

    def _write_json_report(self):
        out = self.audits_dir / "evidence_deep_dive_hits.json"
        report = {
            "run_date": datetime.now().isoformat(),
            "stats": self.stats,
            "keyword_universe_size": len(self.all_keywords),
            "exhibit_id_universe_size": len(self.all_exhibit_ids),
            "indexed_files_count": len(self.indexed_files),
            "indexed_exhibit_ids_count": len(self.indexed_exhibit_ids),
            "hits": self.hits,
        }
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"  Wrote {out}")


def _fmt_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes/(1024*1024):.1f} MB"
    else:
        return f"{size_bytes/(1024*1024*1024):.1f} GB"


# ─────────────────────────────────────────────
# Content Scanner (reads file contents)
# ─────────────────────────────────────────────

# High-value keywords that justify reading a file's content.
# These are more specific than filename keywords to reduce noise.
CONTENT_KEYWORDS_CRITICAL = [
    "seroquel", "poisoning", "poison", "drugging", "drugged",
    "lethal dose", "lithium", "adderall",
    "put .{0,20} in .{0,20} wine",      # regex: "put X in Y wine"
    "abuse journal", "fabricat", "falsif", "perjur",
    "hymowitz", "discrepanc",
    "coached", "coaching the child",
    "fake crying",
]

CONTENT_KEYWORDS_HIGH = [
    "restraining order", "domestic violence", "custody",
    "supervised visit", "family court",
    "deposition", "affidavit", "declaration",
    "bruise", "injury", "toxicology", "blood test",
    "niacin flush", "ambush", "911 call",
    "uber recording",
    "brie grows in brooklyn",
    "stock option", "ring labs",
    "matan", "gavish", "brienne", "tedla", "lamelle",
    "petrella", "gootzeit", "gordon-oliver",
    "evie",
]

# File extensions we can read content from
CONTENT_READABLE_EXTENSIONS = {
    ".emlx", ".eml", ".txt", ".html", ".htm", ".md",
    ".rtf", ".csv", ".tsv", ".log", ".json", ".xml",
}

# Extensions requiring special handling
DOCX_EXTENSIONS = {".docx"}
# We skip .pdf — too slow without pdftotext, and filename scan covers most


class ContentScanner:
    """Reads the actual text content of files to find keyword matches."""

    def __init__(self, blog_root: Path, all_keywords: set, all_exhibit_ids: set,
                 indexed_files: set, indexed_exhibit_ids: set,
                 post_keywords: dict, post_exhibit_ids: dict,
                 filename_hit_paths: set = None):
        self.blog_root = blog_root
        self.audits_dir = blog_root / "Audits"
        self.all_keywords = all_keywords
        self.all_exhibit_ids = all_exhibit_ids
        self.indexed_files = indexed_files
        self.indexed_exhibit_ids = indexed_exhibit_ids
        self.post_keywords = post_keywords
        self.post_exhibit_ids = post_exhibit_ids
        self.filename_hit_paths = filename_hit_paths or set()

        self.hits = []
        self.errors = []
        self.stats = {
            "files_scanned": 0,
            "files_read": 0,
            "files_skipped": 0,
            "files_errored": 0,
            "hits_found": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "per_archive": {},
        }

        # Compile regex patterns for speed
        self._critical_patterns = [
            re.compile(kw, re.IGNORECASE) for kw in CONTENT_KEYWORDS_CRITICAL
        ]
        self._high_patterns = [
            re.compile(re.escape(kw) if not any(c in kw for c in r'.*+?[](){}|\\^$') else kw, re.IGNORECASE)
            for kw in CONTENT_KEYWORDS_HIGH
        ]
        self._exhibit_patterns = [
            re.compile(p, re.IGNORECASE) for p in EXHIBIT_PATTERNS
        ]

    def run(self):
        """Scan all archives for content matches."""
        print("\n" + "=" * 60)
        print("CONTENT SCANNER")
        print(f"Started: {datetime.now().isoformat()}")
        print("=" * 60)

        for archive_name, rel_path in ARCHIVE_DIRS.items():
            archive_path = (self.blog_root / rel_path).resolve()
            if not archive_path.exists():
                print(f"  SKIP {archive_name}: not found")
                continue
            print(f"\n  Content-scanning {archive_name}...")
            self._scan_archive_content(archive_name, archive_path)

        self._score_content_hits()
        self._write_content_reports()

        print("\n" + "=" * 60)
        print(f"CONTENT SCAN COMPLETE — {self.stats['hits_found']} hits")
        print(f"  Files scanned: {self.stats['files_scanned']}")
        print(f"  Files read:    {self.stats['files_read']}")
        print(f"  Files errored: {self.stats['files_errored']}")
        print(f"  Critical hits: {self.stats['critical']}")
        print(f"  High hits:     {self.stats['high']}")
        print(f"  Medium hits:   {self.stats['medium']}")
        print("=" * 60)

    def _scan_archive_content(self, archive_name: str, archive_path: Path):
        file_count = 0
        read_count = 0
        hit_count = 0

        for root, dirs, files in os.walk(archive_path):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

            for fname in files:
                if fname.startswith("."):
                    continue

                file_count += 1
                fpath = Path(root) / fname
                ext = fpath.suffix.lower()

                # Skip files already caught by filename scanner
                if str(fpath) in self.filename_hit_paths:
                    continue

                # Skip already-indexed files
                fname_lower = fname.lower()
                fname_no_ext = os.path.splitext(fname)[0].lower()
                if fname_lower in self.indexed_files or fname_no_ext in self.indexed_files:
                    continue

                # Only read content-readable files
                if ext not in CONTENT_READABLE_EXTENSIONS and ext not in DOCX_EXTENSIONS:
                    continue

                # Read and match
                text = self._read_file_content(fpath, ext)
                if not text:
                    continue

                read_count += 1
                hit = self._match_content(fname, fpath, archive_name, text)
                if hit:
                    self.hits.append(hit)
                    hit_count += 1

                if read_count % 200 == 0:
                    print(f"    ...read {read_count} files, {hit_count} content hits")

        self.stats["files_scanned"] += file_count
        self.stats["files_read"] += read_count
        self.stats["per_archive"][archive_name] = {
            "files_scanned": file_count,
            "files_read": read_count,
            "hits_found": hit_count,
        }
        print(f"    {archive_name}: {file_count} files, {read_count} read, {hit_count} content hits")

    def _read_file_content(self, fpath: Path, ext: str) -> str:
        """Extract text content from a file. Returns empty string on failure."""
        try:
            # Cap at 500KB to avoid memory issues on huge files
            size = fpath.stat().st_size
            if size > 512_000:
                # Read just the first 500KB
                with open(fpath, "rb") as f:
                    raw = f.read(512_000)
            else:
                with open(fpath, "rb") as f:
                    raw = f.read()

            if ext == ".emlx":
                return self._parse_emlx(raw)
            elif ext in (".eml",):
                return self._parse_eml(raw)
            elif ext in DOCX_EXTENSIONS:
                return self._parse_docx(fpath)
            else:
                # Plain text / HTML / markdown — decode as UTF-8
                return raw.decode("utf-8", errors="replace")

        except Exception as e:
            self.stats["files_errored"] += 1
            self.errors.append({"file": str(fpath), "error": str(e)})
            return ""

    def _parse_emlx(self, raw: bytes) -> str:
        """Parse Apple Mail .emlx format: length line + RFC822 message + plist."""
        try:
            text = raw.decode("utf-8", errors="replace")
            # .emlx starts with a byte-count line, then the RFC822 message
            lines = text.split("\n", 1)
            if len(lines) < 2:
                return text
            # Try to parse as email
            msg = email.message_from_string(lines[1])
            parts = []
            # Get subject, from, to
            for header in ("Subject", "From", "To", "Date"):
                val = msg.get(header, "")
                if val:
                    parts.append(f"{header}: {val}")
            # Get body
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            parts.append(payload.decode("utf-8", errors="replace"))
                    elif part.get_content_type() == "text/html":
                        payload = part.get_payload(decode=True)
                        if payload:
                            # Strip HTML tags crudely
                            html_text = payload.decode("utf-8", errors="replace")
                            parts.append(re.sub(r'<[^>]+>', ' ', html_text))
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    parts.append(payload.decode("utf-8", errors="replace"))
            return "\n".join(parts)
        except:
            return raw.decode("utf-8", errors="replace")

    def _parse_eml(self, raw: bytes) -> str:
        """Parse standard .eml format."""
        try:
            msg = email.message_from_bytes(raw)
            parts = []
            for header in ("Subject", "From", "To", "Date"):
                val = msg.get(header, "")
                if val:
                    parts.append(f"{header}: {val}")
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() in ("text/plain", "text/html"):
                        payload = part.get_payload(decode=True)
                        if payload:
                            text = payload.decode("utf-8", errors="replace")
                            if part.get_content_type() == "text/html":
                                text = re.sub(r'<[^>]+>', ' ', text)
                            parts.append(text)
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    parts.append(payload.decode("utf-8", errors="replace"))
            return "\n".join(parts)
        except:
            return raw.decode("utf-8", errors="replace")

    def _parse_docx(self, fpath: Path) -> str:
        """Extract text from .docx using zipfile (no dependencies)."""
        try:
            import zipfile
            from xml.etree import ElementTree
            with zipfile.ZipFile(fpath) as z:
                if "word/document.xml" not in z.namelist():
                    return ""
                xml_content = z.read("word/document.xml")
                tree = ElementTree.fromstring(xml_content)
                # Extract all text nodes
                ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                texts = []
                for elem in tree.iter():
                    if elem.tag.endswith("}t") and elem.text:
                        texts.append(elem.text)
                return " ".join(texts)
        except:
            return ""

    def _match_content(self, fname: str, fpath: Path, archive_name: str, text: str) -> dict | None:
        """Match file content against keyword patterns."""
        text_lower = text.lower()

        critical_matches = []
        high_matches = []
        exhibit_matches = []
        context_snippets = []

        # Check critical patterns
        for pattern in self._critical_patterns:
            match = pattern.search(text)
            if match:
                critical_matches.append(pattern.pattern)
                # Extract context: 80 chars before and after
                start = max(0, match.start() - 80)
                end = min(len(text), match.end() + 80)
                snippet = text[start:end].replace("\n", " ").strip()
                context_snippets.append(f"[{pattern.pattern}] ...{snippet}...")

        # Check high patterns
        for pattern in self._high_patterns:
            if pattern.search(text):
                high_matches.append(pattern.pattern)

        # Check exhibit IDs in content
        for pattern in self._exhibit_patterns:
            found = pattern.findall(text)
            for m in found:
                m_upper = m.upper()
                if m_upper in self.all_exhibit_ids:
                    exhibit_matches.append(m_upper)

        # Must have at least one match
        if not critical_matches and not high_matches and not exhibit_matches:
            return None

        # Only promote to hit if we have critical matches, or 2+ high matches,
        # or exhibit + any other match (reduces noise)
        if not critical_matches and len(high_matches) < 2 and not exhibit_matches:
            return None

        # Determine relevant posts
        relevant_posts = set()
        all_kw = set()
        for cm in critical_matches:
            all_kw.add(cm.lower())
        for hm in high_matches:
            all_kw.add(hm.lower().replace("\\", ""))

        for post_name, post_kw in self.post_keywords.items():
            if post_kw.intersection(all_kw):
                relevant_posts.add(post_name)
        for post_name, post_ex in self.post_exhibit_ids.items():
            if set(exhibit_matches).intersection(post_ex):
                relevant_posts.add(post_name)

        try:
            size = fpath.stat().st_size
        except:
            size = 0

        # Extract email metadata if available
        email_meta = ""
        if fpath.suffix.lower() in (".emlx", ".eml"):
            for line in text.split("\n")[:6]:
                if line.startswith(("Subject:", "From:", "To:", "Date:")):
                    email_meta += line.strip() + " | "

        return {
            "file": fname,
            "path": str(fpath),
            "archive": archive_name,
            "size_bytes": size,
            "scan_type": "content",
            "critical_matches": critical_matches,
            "high_matches": high_matches,
            "exhibit_matches": exhibit_matches,
            "context_snippets": context_snippets[:5],  # Cap at 5
            "email_meta": email_meta.rstrip(" | "),
            "relevant_posts": sorted(relevant_posts),
            "score": 0,
            "tier": "",
        }

    def _score_content_hits(self):
        for hit in self.hits:
            score = 0

            if hit["critical_matches"]:
                score += 3 * len(hit["critical_matches"])
                hit["tier"] = "CRITICAL"

            if hit["exhibit_matches"]:
                unindexed = [e for e in hit["exhibit_matches"] if e not in self.indexed_exhibit_ids]
                if unindexed:
                    score += 3
                    hit["tier"] = "CRITICAL"
                else:
                    score += 1

            if hit["high_matches"]:
                score += len(hit["high_matches"])
                if not hit["tier"]:
                    hit["tier"] = "HIGH" if len(hit["high_matches"]) >= 2 else "MEDIUM"

            if not hit["tier"]:
                hit["tier"] = "MEDIUM"

            if len(hit["relevant_posts"]) >= 3:
                score += 0.5

            hit["score"] = score

        self.hits.sort(key=lambda h: (-h["score"], h["file"]))

        self.stats["hits_found"] = len(self.hits)
        self.stats["critical"] = sum(1 for h in self.hits if h["tier"] == "CRITICAL")
        self.stats["high"] = sum(1 for h in self.hits if h["tier"] == "HIGH")
        self.stats["medium"] = sum(1 for h in self.hits if h["tier"] == "MEDIUM")

    def _write_content_reports(self):
        self._write_content_markdown()
        self._write_content_json()

    def _write_content_markdown(self):
        out = self.audits_dir / "evidence_content_scan_log.md"
        lines = []
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines.append("# Evidence Content Scan Log")
        lines.append(f"**Run date:** {ts}")
        lines.append(f"**Files scanned:** {self.stats['files_scanned']}")
        lines.append(f"**Files content-read:** {self.stats['files_read']}")
        lines.append(f"**Content hits found:** {self.stats['hits_found']}")
        lines.append(f"**Critical:** {self.stats['critical']} | **High:** {self.stats['high']} | **Medium:** {self.stats['medium']}")
        lines.append("")
        lines.append("*This scan reads the actual text content of .emlx, .eml, .txt, .html, .docx files*")
        lines.append("*to find evidence hiding behind generic filenames (e.g., numbered .emlx files).*")
        lines.append("")

        # Per-archive stats
        lines.append("## Archive Content Scan Summary")
        lines.append("| Archive | Files Scanned | Files Read | Hits |")
        lines.append("|---------|--------------|-----------|------|")
        for name, stats in self.stats["per_archive"].items():
            lines.append(f"| {name} | {stats['files_scanned']:,} | {stats['files_read']:,} | {stats['hits_found']:,} |")
        lines.append("")

        # Critical content hits
        critical = [h for h in self.hits if h["tier"] == "CRITICAL"]
        lines.append(f"## CRITICAL CONTENT HITS ({len(critical)} items)")
        lines.append("")
        for h in critical:
            lines.append(f"### {h['file']}")
            lines.append(f"- **Archive:** {h['archive']}")
            lines.append(f"- **Path:** `{h['path']}`")
            lines.append(f"- **Size:** {_fmt_size(h['size_bytes'])}")
            if h.get("email_meta"):
                lines.append(f"- **Email:** {h['email_meta']}")
            lines.append(f"- **Critical keywords:** {', '.join(h['critical_matches'])}")
            if h["exhibit_matches"]:
                lines.append(f"- **Exhibit IDs found:** {', '.join(h['exhibit_matches'])}")
            lines.append(f"- **Relevant posts:** {', '.join(h['relevant_posts'][:10])}")
            lines.append(f"- **Score:** {h['score']}")
            if h.get("context_snippets"):
                lines.append("- **Context snippets:**")
                for snip in h["context_snippets"]:
                    # Truncate long snippets
                    lines.append(f"  - `{snip[:200]}`")
            lines.append("")

        # High hits
        high = [h for h in self.hits if h["tier"] == "HIGH"]
        lines.append(f"## HIGH-RELEVANCE CONTENT HITS ({len(high)} items)")
        lines.append("")
        if high:
            for h in high[:50]:
                lines.append(f"### {h['file']}")
                lines.append(f"- **Archive:** {h['archive']}")
                lines.append(f"- **Path:** `{h['path']}`")
                if h.get("email_meta"):
                    lines.append(f"- **Email:** {h['email_meta']}")
                lines.append(f"- **Keywords:** {', '.join(h['high_matches'][:5])}")
                lines.append(f"- **Score:** {h['score']}")
                lines.append("")
            if len(high) > 50:
                lines.append(f"*...and {len(high)-50} more (see JSON output)*\n")
        else:
            lines.append("*None found.*\n")

        # Medium hits (abbreviated)
        medium = [h for h in self.hits if h["tier"] == "MEDIUM"]
        lines.append(f"## MEDIUM-RELEVANCE CONTENT HITS ({len(medium)} items)")
        lines.append("*See JSON output for full details.*\n")

        # Errors
        if self.errors:
            lines.append(f"## READ ERRORS ({len(self.errors)} files)")
            lines.append("")
            for err in self.errors[:20]:
                lines.append(f"- `{err['file']}`: {err['error']}")
            if len(self.errors) > 20:
                lines.append(f"- *...and {len(self.errors)-20} more*")
            lines.append("")

        out.write_text("\n".join(lines), encoding="utf-8")
        print(f"  Wrote {out} ({len(lines)} lines)")

    def _write_content_json(self):
        out = self.audits_dir / "evidence_content_scan_hits.json"
        report = {
            "run_date": datetime.now().isoformat(),
            "scan_type": "content",
            "stats": self.stats,
            "hits": self.hits,
            "errors": self.errors[:100],  # Cap errors in JSON
        }
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"  Wrote {out}")


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evidence Deep Dive Scanner")
    parser.add_argument(
        "--blog-root",
        type=str,
        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        help="Path to ChappaquaPoison_v3 root directory",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["filename", "content", "both"],
        default="filename",
        help="Scan mode: filename (fast), content (reads files), both (filename then content)",
    )
    args = parser.parse_args()

    blog_root = Path(args.blog_root)
    if not blog_root.exists():
        print(f"ERROR: Blog root not found: {blog_root}")
        sys.exit(1)

    filename_hit_paths = set()

    if args.mode in ("filename", "both"):
        scanner = EvidenceScanner(blog_root)
        scanner.run()
        # Collect paths of filename hits so content scanner skips them
        filename_hit_paths = {h["path"] for h in scanner.hits}

    if args.mode in ("content", "both"):
        # If running content-only, we still need keywords from posts + evidence index
        if args.mode == "content":
            scanner = EvidenceScanner(blog_root)
            scanner._extract_post_keywords()
            scanner._load_evidence_index()

        content_scanner = ContentScanner(
            blog_root=blog_root,
            all_keywords=scanner.all_keywords,
            all_exhibit_ids=scanner.all_exhibit_ids,
            indexed_files=scanner.indexed_files,
            indexed_exhibit_ids=scanner.indexed_exhibit_ids,
            post_keywords=scanner.post_keywords,
            post_exhibit_ids=scanner.post_exhibit_ids,
            filename_hit_paths=filename_hit_paths,
        )
        content_scanner.run()
