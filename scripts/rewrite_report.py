#!/usr/bin/env python3
"""
rewrite_report.py — Phase 2 rewrite measurement harness.

Reads chapter source files defined in a manifest, runs structural and tagged
measurements, writes a structured Markdown + JSON report. Two reports can be
diffed to show whether identified issues were addressed and whether new errors
were introduced.

See Standards/REWRITE_REPORT_SCHEMA.md for what's in the report.

Usage:
    python3 scripts/rewrite_report.py --source current_state
    python3 scripts/rewrite_report.py --source april06_baseline --manifest Standards/rewrite_report_manifest_april06.json
    python3 scripts/rewrite_report.py --diff Audits/rewrite_report_april06_baseline.json Audits/rewrite_report_current_state.json
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import statistics
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_MD_DIR = REPO_ROOT / "posts" / "md"
AUDITS_DIR = REPO_ROOT / "Audits"
STANDARDS_DIR = REPO_ROOT / "Standards"
DEFAULT_MANIFEST = STANDARDS_DIR / "rewrite_report_manifest.json"

# ---------------------------------------------------------------------------
# Chapter list (53 active chapters; B13 dissolved; B100/B101 outside main seq)
# ---------------------------------------------------------------------------

CHAPTER_IDS: List[str] = [
    f"B{n:02d}" for n in list(range(0, 13)) + list(range(14, 54))
]
ACTS: Dict[str, str] = {}
for cid in [f"B{n:02d}" for n in range(0, 4)]:
    ACTS[cid] = "I"
for cid in [f"B{n:02d}" for n in range(4, 10)]:
    ACTS[cid] = "II"
for cid in [f"B{n:02d}" for n in range(10, 18) if n != 13]:
    ACTS[cid] = "III"
for cid in [f"B{n:02d}" for n in range(18, 24)]:
    ACTS[cid] = "IV"
for cid in [f"B{n:02d}" for n in range(24, 32)]:
    ACTS[cid] = "V"
for cid in [f"B{n:02d}" for n in range(32, 40)]:
    ACTS[cid] = "VI"
for cid in [f"B{n:02d}" for n in range(40, 48)]:
    ACTS[cid] = "VII"
for cid in [f"B{n:02d}" for n in range(48, 54)]:
    ACTS[cid] = "Coda"

# ---------------------------------------------------------------------------
# Voice heuristic word lists
# ---------------------------------------------------------------------------

PROC_TERMS = {
    "court", "filing", "filed", "motion", "order", "ordered", "default",
    "judge", "dvro", "petition", "petitioner", "respondent", "subpoena",
    "hearing", "hearings", "transcript", "attorney", "counsel", "deposition",
    "testimony", "witness", "ruling", "appellate", "appeal", "complaint",
    "trial", "jury", "verdict", "jurisdiction", "statute", "docket",
    "objection", "sustained", "overruled", "exhibit", "evidence", "judgment",
    "magistrate", "referee", "stipulation", "discovery", "interrogatory",
}

DENSITY_HOTSPOT_TERMS = {"system", "architecture", "machinery", "scheme", "mechanism"}

LYR_TERMS = {
    "light", "sky", "rain", "snow", "fog", "river", "ocean", "wind",
    "morning", "evening", "dusk", "dawn", "shadow", "sun", "moon",
    "trees", "leaves", "grass", "flowers", "garden", "window", "ceiling",
}

ROB_TERMS = {
    "evie", "small", "sleeping", "father", "love", "drew", "held", "child",
    "daughter", "tender", "quiet", "her hand", "her voice", "her face",
}

CONDITIONAL_MARKERS = {
    "perhaps", "might have", "could have", "would have", "as if",
    "as though", "seemed", "seemed to", "appeared to", "wandering",
}

# ---------------------------------------------------------------------------
# Test definitions (AR findings + Do Not Touch + names)
# ---------------------------------------------------------------------------

@dataclass
class PhraseTest:
    """A test that asserts a phrase appears (or does not) in a chapter."""
    test_id: str
    chapter_id: str
    pattern: str  # case-insensitive substring or regex
    expected_present: bool  # True = should be present; False = should not
    is_regex: bool = False
    notes: str = ""

# Tests are written in their post-rewrite expected state. Before the rewrite,
# many will fail — that's the baseline. The diff between Report A and Report B
# shows which ones flipped from FAIL to PASS (resolutions) or from PASS to FAIL
# (regressions).

ISSUE_TESTS: List[PhraseTest] = [
    # AR-001 — Horowitz reprise B29 ↔ B32
    PhraseTest("AR-001_horowitz_in_b32_censure", "B32",
               r"censure", expected_present=False, is_regex=True,
               notes="Horowitz censure backstory should not appear in B32 after rewrite (B29 owns)"),
    PhraseTest("AR-001_horowitz_in_b29_canonical", "B29",
               r"horowitz", expected_present=True, is_regex=True,
               notes="B29 is the canonical owner of Horowitz backstory"),
    PhraseTest("AR-001_horowitz_voicemail_b32_texture", "B32",
               r"voicemail|nilda", expected_present=True, is_regex=True,
               notes="B32 retains the Horowitz voicemail as texture only"),

    # AR-002 — Kelly interior in B32
    PhraseTest("AR-002_b32_kelly_thinks", "B32",
               r"kelly (thought|wondered|felt|knew|believed|imagined)",
               expected_present=False, is_regex=True,
               notes="Kelly should be rendered externally only (no interior verbs)"),

    # AR-003 / AR-009 — Jackman relief and six-hours preview
    PhraseTest("AR-003_jackman_relieved_b35_kept", "B35",
               r"jackman", expected_present=True, is_regex=True,
               notes="B35 keeps the five-sentence Jackman landing"),
    PhraseTest("AR-009_six_hours_in_b37", "B37",
               r"six hours", expected_present=False, is_regex=True,
               notes="Six-hours preview belongs to B41 only"),
    PhraseTest("AR-009_six_hours_in_b41", "B41",
               r"six hours", expected_present=True, is_regex=True,
               notes="Six-hours rendering belongs to B41"),

    # AR-013 — B29 fourth-wall break
    PhraseTest("AR-013_b29_fourth_wall_dear_reader", "B29",
               r"\b(dear reader|the reader)\b", expected_present=False, is_regex=True,
               notes="No narrator-direct address in B29"),

    # AR-014 — B39 hand-delivered repetition (count <= 1 in chapter)
    PhraseTest("AR-014_b39_hand_delivered_count", "B39",
               r"hand[- ]delivered", expected_present=True, is_regex=True,
               notes="Should appear at most once in B39 (count flag handled separately)"),

    # AR-015 — B39 closing Baldwin-analytical passage
    PhraseTest("AR-015_b39_closes_with_evidence_not_argument", "B39",
               r"the system that", expected_present=False, is_regex=True,
               notes="B39 should not close with Baldwin mechanism-naming"),

    # ExTR_03 deployment
    PhraseTest("ExTR_03_b33_im_not_in_california", "B33",
               r"i'?m not in california|not in california", expected_present=True, is_regex=True,
               notes="Humphrey 'I'm not in California' exchange should be in B33"),
    PhraseTest("ExTR_03_b33_fail_to_appear_rule", "B33",
               r"fail(ed)? to appear", expected_present=True, is_regex=True,
               notes="Humphrey rule announcement should be in B33"),
    PhraseTest("ExTR_03_b32_setup_beat_present", "B32",
               r"i'?m not in california|january 26", expected_present=True, is_regex=True,
               notes="B32 should have a 3-5 sentence ExTR_03 setup beat"),

    # Walsh Sr. excursion
    PhraseTest("walsh_sr_excursion_b29_drexel", "B29",
               r"drexel|walsh sr", expected_present=True, is_regex=True,
               notes="B29 should reprise the Walsh Sr./Drexel backstory at the silencing moment"),
]

DNT_TESTS: List[PhraseTest] = [
    PhraseTest("dnt_b25_understood_exchange", "B25",
               r"understood\.", expected_present=True, is_regex=True,
               notes="The 'Understood.' Antoncic exchange must remain"),
    PhraseTest("dnt_b25_baseball_bats_close", "B25",
               r"baseball bat", expected_present=True, is_regex=True,
               notes="The two men in camouflage closing must remain (B48 ambush foreshadowing)"),
    PhraseTest("dnt_b29_evidence_survives", "B29",
               r"evidence survives", expected_present=True, is_regex=True,
               notes="The 'evidence survives, the person who made it does not' line must remain"),
    PhraseTest("dnt_machinery_of_accountability_book", "ANY",
               r"machinery of accountability", expected_present=True, is_regex=True,
               notes="Phrase must appear somewhere in the book (motif anchor)"),
    PhraseTest("dnt_b25_three_women_in_a_room", "B25",
               r"three women", expected_present=True, is_regex=True,
               notes="The 'three women in a room' formulation must remain (rendered scene seed)"),
]

NAME_TESTS: List[PhraseTest] = [
    PhraseTest("name_b52_difabio_not_anthony", "B52",
               r"anthony difabio", expected_present=False, is_regex=True,
               notes="B52 should use Massimo/Max DiFabio, not Anthony DiFabio"),
    PhraseTest("name_genovese_not_justice", "ANY",
               r"justice genovese|supreme court justice genovese", expected_present=False, is_regex=True,
               notes="Genovese is a Court Attorney Referee, not a Justice"),
]

CROSS_CHAPTER_PHRASE_SCAN: Dict[str, str] = {
    "phrase_five_sentences": r"five sentences",
    "phrase_six_hours": r"six hours",
    "phrase_three_thousand_miles": r"three thousand miles",
    "phrase_hand_delivered": r"hand[- ]delivered",
    "phrase_seismograph": r"seismograph",
    "phrase_battery_trial_san_francisco": r"battery trial in san francisco",
    "phrase_machinery_of_accountability": r"machinery of accountability",
}

# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
EMBED_BLOCK_RE = re.compile(r"^embed\s*:.*?(?=^[a-zA-Z]|\Z)", re.MULTILINE | re.DOTALL)
EMBED_DIRECTIVE_RE = re.compile(r"^embed\s*:", re.MULTILINE)
EVIDENCE_ID_RE = re.compile(r"\b(?:[A-Z]{2,8}_\d{2,4}(?:_\d{2,4})?|EB\d_MASTER_\d+|SLE-\d+|MED-\d+|EMAIL_[A-Z0-9_]+|PHOTO_[A-Z0-9_]+|TEXT_[A-Z0-9_]+|SCREENSHOT_[A-Z0-9_]+|G-\d+(?:_\d+)?|D-\d+|ExO_\d+|ExTR_\d+(?:_\d+)?|ExBCD_\d+|ExOO_\d+|B-\d+_\d+)\b")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"])")
DIALOGUE_RE = re.compile(r"\"[^\"]{3,}\"|\u201c[^\u201d]{3,}\u201d|\u2018[^\u2019]{3,}\u2019|'[^']{3,}'")


@dataclass
class ChapterReport:
    id: str
    title: str
    act: str
    source_path: str
    source_modified: str
    source_sha256: str
    word_count: int
    sentence_count: int
    paragraph_count: int
    sentence_length_mean: float
    sentence_length_median: float
    sentence_length_p10: float
    sentence_length_p90: float
    paragraph_length_mean: float
    dialogue_paragraph_count: int
    dialogue_ratio: float
    evidence_embed_count: int
    evidence_id_set: List[str]
    density_hotspot_count: int
    density_hotspot_per_1k: float
    voice_estimate: Dict[str, float]
    proc_plus_bal: float
    human_voice_floor: float
    monotony_flag: bool
    floor_violation_flag: bool
    ceiling_violation_flag: bool
    issue_test_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    dnt_test_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    name_test_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    custom_counts: Dict[str, int] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)


def parse_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    raw = m.group(1)
    body = text[m.end():]
    fm: Dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip().strip('"\'')
    return fm, body


def strip_embeds(body: str) -> Tuple[str, int]:
    embed_count = len(EMBED_DIRECTIVE_RE.findall(body))
    cleaned = re.sub(r"^embed\s*:[\s\S]*?(?=^\S|\Z)", "", body, flags=re.MULTILINE)
    return cleaned, embed_count


def split_sentences(text: str) -> List[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    return [s.strip() for s in SENTENCE_SPLIT_RE.split(text) if s.strip()]


def split_paragraphs(text: str) -> List[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w']+\b", text))


def is_proc_sentence(s: str) -> bool:
    s_low = s.lower()
    return any(t in s_low for t in PROC_TERMS)


def is_bal_sentence(s: str) -> bool:
    s_low = s.lower()
    n_words = len(s.split())
    n_subordinators = len(re.findall(r"\b(which|that|because|although|while|as|when|where|whose|whom|whereby|wherein|insofar)\b", s_low))
    has_hotspot = any(t in s_low for t in DENSITY_HOTSPOT_TERMS)
    return n_words >= 25 and n_subordinators >= 2 and has_hotspot


def is_seb_sentence(s: str) -> bool:
    s_low = s.lower()
    return any(m in s_low for m in CONDITIONAL_MARKERS)


def is_lyr_sentence(s: str) -> bool:
    s_low = s.lower()
    return sum(1 for t in LYR_TERMS if t in s_low) >= 2


def is_rob_paragraph(p: str) -> bool:
    p_low = p.lower()
    rob_hits = sum(1 for t in ROB_TERMS if t in p_low)
    proc_hits = sum(1 for t in PROC_TERMS if t in p_low)
    return rob_hits >= 2 and proc_hits == 0


def is_dialogue_paragraph(p: str) -> bool:
    return bool(DIALOGUE_RE.search(p))


def is_int_paragraph(p: str) -> bool:
    p_low = p.lower()
    interior_markers = ["he thought", "he felt", "he knew", "he wondered", "he remembered",
                        "his mind", "in his head", "he could not", "he understood"]
    return any(m in p_low for m in interior_markers)


def estimate_voice(sentences: List[str], paragraphs: List[str]) -> Dict[str, float]:
    n_sent = max(len(sentences), 1)
    n_para = max(len(paragraphs), 1)

    proc = sum(1 for s in sentences if is_proc_sentence(s))
    bal = sum(1 for s in sentences if is_bal_sentence(s))
    seb = sum(1 for s in sentences if is_seb_sentence(s))
    lyr = sum(1 for s in sentences if is_lyr_sentence(s))

    rob = sum(1 for p in paragraphs if is_rob_paragraph(p))
    soc = sum(1 for p in paragraphs if is_dialogue_paragraph(p))
    intp = sum(1 for p in paragraphs if is_int_paragraph(p))

    proc_pct = round(100 * proc / n_sent, 1)
    bal_pct = round(100 * bal / n_sent, 1)
    seb_pct = round(100 * seb / n_sent, 1)
    lyr_pct = round(100 * lyr / n_sent, 1)
    rob_pct = round(100 * rob / n_para, 1)
    soc_pct = round(100 * soc / n_para, 1)
    int_pct = round(100 * intp / n_para, 1)
    lean_pct = round(max(0.0, 100 - proc_pct - bal_pct - seb_pct - lyr_pct), 1)

    return {
        "PROC": proc_pct,
        "BAL": bal_pct,
        "SEB": seb_pct,
        "LYR": lyr_pct,
        "ROB": rob_pct,
        "SOC": soc_pct,
        "INT": int_pct,
        "LEAN": lean_pct,
    }


def run_phrase_test(test: PhraseTest, body: str) -> Dict[str, Any]:
    if test.is_regex:
        match = re.search(test.pattern, body, re.IGNORECASE)
    else:
        match = test.pattern.lower() in body.lower()
    found = bool(match)
    passed = (found == test.expected_present)
    return {
        "test_id": test.test_id,
        "expected_present": test.expected_present,
        "found": found,
        "passed": passed,
        "notes": test.notes,
    }


def analyze_chapter(chapter_id: str, source_path: Path) -> ChapterReport:
    raw = source_path.read_text(encoding="utf-8")
    sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    mtime = dt.datetime.fromtimestamp(source_path.stat().st_mtime).isoformat()

    fm, body = parse_frontmatter(raw)
    title = fm.get("title", chapter_id)
    body_no_embeds, embed_count = strip_embeds(body)

    paragraphs = split_paragraphs(body_no_embeds)
    sentences = []
    for p in paragraphs:
        sentences.extend(split_sentences(p))

    wc = word_count(body_no_embeds)
    sent_lengths = [len(s.split()) for s in sentences] or [0]
    para_lengths = [len(split_sentences(p)) for p in paragraphs] or [0]
    dialogue_paras = sum(1 for p in paragraphs if is_dialogue_paragraph(p))

    evidence_ids = sorted(set(EVIDENCE_ID_RE.findall(body)))
    hotspot_total = 0
    body_low = body_no_embeds.lower()
    for term in DENSITY_HOTSPOT_TERMS:
        hotspot_total += len(re.findall(rf"\b{term}\b", body_low))
    hotspot_per_1k = round(1000 * hotspot_total / max(wc, 1), 2)

    voice = estimate_voice(sentences, paragraphs)
    proc_plus_bal = round(voice["PROC"] + voice["BAL"], 1)
    human_voice = round(voice["SOC"] + voice["INT"] + voice["LYR"] + voice["ROB"], 1)

    report = ChapterReport(
        id=chapter_id,
        title=title,
        act=ACTS.get(chapter_id, "?"),
        source_path=str(source_path),
        source_modified=mtime,
        source_sha256=sha,
        word_count=wc,
        sentence_count=len(sentences),
        paragraph_count=len(paragraphs),
        sentence_length_mean=round(statistics.mean(sent_lengths), 1),
        sentence_length_median=round(statistics.median(sent_lengths), 1),
        sentence_length_p10=round(statistics.quantiles(sent_lengths, n=10)[0], 1) if len(sent_lengths) >= 10 else float(min(sent_lengths)),
        sentence_length_p90=round(statistics.quantiles(sent_lengths, n=10)[-1], 1) if len(sent_lengths) >= 10 else float(max(sent_lengths)),
        paragraph_length_mean=round(statistics.mean(para_lengths), 1),
        dialogue_paragraph_count=dialogue_paras,
        dialogue_ratio=round(dialogue_paras / max(len(paragraphs), 1), 2),
        evidence_embed_count=embed_count,
        evidence_id_set=evidence_ids,
        density_hotspot_count=hotspot_total,
        density_hotspot_per_1k=hotspot_per_1k,
        voice_estimate=voice,
        proc_plus_bal=proc_plus_bal,
        human_voice_floor=human_voice,
        monotony_flag=proc_plus_bal >= 45,
        floor_violation_flag=human_voice < 35,
        ceiling_violation_flag=proc_plus_bal > 40,
    )

    # Run tests scoped to this chapter
    for test in ISSUE_TESTS:
        if test.chapter_id == chapter_id:
            report.issue_test_results[test.test_id] = run_phrase_test(test, body)
    for test in DNT_TESTS:
        if test.chapter_id == chapter_id:
            report.dnt_test_results[test.test_id] = run_phrase_test(test, body)
    for test in NAME_TESTS:
        if test.chapter_id == chapter_id:
            report.name_test_results[test.test_id] = run_phrase_test(test, body)

    # Per-chapter custom counts useful for tests
    report.custom_counts["hand_delivered_count"] = len(re.findall(r"hand[- ]delivered", body_low))
    report.custom_counts["six_hours_count"] = len(re.findall(r"six hours", body_low))
    report.custom_counts["three_thousand_miles_count"] = len(re.findall(r"three thousand miles", body_low))

    return report


def load_manifest(path: Path) -> Dict[str, str]:
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        # Support two shapes:
        #   flat: {"B00": "path", "B01": "path", ...}
        #   nested: {"source_label": ..., "chapters": {"B00": "path", ...}}
        if isinstance(data, dict) and "chapters" in data and isinstance(data["chapters"], dict):
            chapters = data["chapters"]
        else:
            chapters = data
        # Resolve relative paths against the project root
        root = Path(__file__).resolve().parent.parent
        resolved: Dict[str, str] = {}
        for cid, p in chapters.items():
            if p is None:
                continue
            pp = Path(p)
            if not pp.is_absolute():
                pp = root / pp
            resolved[cid] = str(pp)
        return resolved
    # Default: discover from posts/md/
    discovered: Dict[str, str] = {}
    for cid in CHAPTER_IDS:
        matches = sorted(POSTS_MD_DIR.glob(f"{cid}_*.md"))
        if matches:
            discovered[cid] = str(matches[0])
    return discovered


def run_book_tests(reports: Dict[str, ChapterReport], manifest: Dict[str, str]) -> Dict[str, Any]:
    """Run tests scoped to ANY chapter (book-wide DNT and name checks)."""
    book_text_lower_parts = []
    for cid in CHAPTER_IDS:
        if cid in manifest:
            book_text_lower_parts.append(Path(manifest[cid]).read_text(encoding="utf-8").lower())
    book_text = "\n".join(book_text_lower_parts)

    results: Dict[str, Any] = {"dnt": {}, "name": {}}
    for test in DNT_TESTS:
        if test.chapter_id == "ANY":
            if test.is_regex:
                found = bool(re.search(test.pattern, book_text, re.IGNORECASE))
            else:
                found = test.pattern.lower() in book_text
            results["dnt"][test.test_id] = {
                "expected_present": test.expected_present,
                "found": found,
                "passed": found == test.expected_present,
                "notes": test.notes,
            }
    for test in NAME_TESTS:
        if test.chapter_id == "ANY":
            if test.is_regex:
                found = bool(re.search(test.pattern, book_text, re.IGNORECASE))
            else:
                found = test.pattern.lower() in book_text
            results["name"][test.test_id] = {
                "expected_present": test.expected_present,
                "found": found,
                "passed": found == test.expected_present,
                "notes": test.notes,
            }
    return results


def cross_chapter_phrase_sweep(manifest: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
    sweep: Dict[str, Dict[str, Any]] = {}
    for label, pattern in CROSS_CHAPTER_PHRASE_SCAN.items():
        chapters_with: List[str] = []
        total_count = 0
        for cid in CHAPTER_IDS:
            if cid not in manifest:
                continue
            text = Path(manifest[cid]).read_text(encoding="utf-8").lower()
            hits = re.findall(pattern, text, re.IGNORECASE)
            if hits:
                chapters_with.append(cid)
                total_count += len(hits)
        sweep[label] = {
            "pattern": pattern,
            "total_count": total_count,
            "chapters": chapters_with,
        }
    return sweep


def aggregate(reports: Dict[str, ChapterReport]) -> Dict[str, Any]:
    if not reports:
        return {}
    monotony = [r.id for r in reports.values() if r.monotony_flag]
    floor = [r.id for r in reports.values() if r.floor_violation_flag]
    ceiling = [r.id for r in reports.values() if r.ceiling_violation_flag]
    total_words = sum(r.word_count for r in reports.values())
    avg_proc_bal = round(statistics.mean(r.proc_plus_bal for r in reports.values()), 1)
    avg_human = round(statistics.mean(r.human_voice_floor for r in reports.values()), 1)
    all_evidence_ids: set = set()
    for r in reports.values():
        all_evidence_ids.update(r.evidence_id_set)
    return {
        "total_chapters": len(reports),
        "total_words": total_words,
        "unique_evidence_ids": sorted(all_evidence_ids),
        "unique_evidence_id_count": len(all_evidence_ids),
        "book_proc_plus_bal_avg": avg_proc_bal,
        "book_human_voice_floor_avg": avg_human,
        "monotony_zone_chapter_count": len(monotony),
        "monotony_zone_chapters": monotony,
        "floor_violation_chapter_count": len(floor),
        "floor_violation_chapters": floor,
        "ceiling_violation_chapter_count": len(ceiling),
        "ceiling_violation_chapters": ceiling,
    }


def write_markdown_report(reports: Dict[str, ChapterReport],
                          aggregates: Dict[str, Any],
                          book_tests: Dict[str, Any],
                          phrase_sweep: Dict[str, Any],
                          source_label: str,
                          out_path: Path) -> None:
    lines: List[str] = []
    lines.append(f"# Rewrite Report — {source_label}")
    lines.append("")
    lines.append(f"**Generated:** {dt.datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"**Source label:** `{source_label}`")
    lines.append(f"**Schema:** `Standards/REWRITE_REPORT_SCHEMA.md`")
    lines.append(f"**Harness:** `scripts/rewrite_report.py`")
    lines.append("")
    lines.append("## Aggregates")
    lines.append("")
    for k, v in aggregates.items():
        if isinstance(v, list):
            if k == "unique_evidence_ids":
                lines.append(f"- **{k}:** {len(v)} ids (omitted from Markdown — see JSON)")
            else:
                lines.append(f"- **{k}:** {', '.join(v) if v else '(none)'}")
        else:
            lines.append(f"- **{k}:** {v}")
    lines.append("")

    # Book-wide test results
    lines.append("## Book-Wide Test Results")
    lines.append("")
    lines.append("### Do Not Touch (book-wide)")
    if book_tests["dnt"]:
        for tid, r in book_tests["dnt"].items():
            mark = "PASS" if r["passed"] else "FAIL"
            lines.append(f"- **{tid}** — {mark} (found={r['found']}, expected_present={r['expected_present']}) — {r['notes']}")
    else:
        lines.append("- (none)")
    lines.append("")
    lines.append("### Name Regression (book-wide)")
    if book_tests["name"]:
        for tid, r in book_tests["name"].items():
            mark = "PASS" if r["passed"] else "FAIL"
            lines.append(f"- **{tid}** — {mark} (found={r['found']}, expected_present={r['expected_present']}) — {r['notes']}")
    else:
        lines.append("- (none)")
    lines.append("")

    # Cross-chapter phrase sweep
    lines.append("## Cross-Chapter Phrase Sweep")
    lines.append("")
    lines.append("| Phrase | Total Count | Chapters |")
    lines.append("|--------|-------------|----------|")
    for label, data in phrase_sweep.items():
        chapters = ", ".join(data["chapters"]) if data["chapters"] else "—"
        lines.append(f"| `{data['pattern']}` | {data['total_count']} | {chapters} |")
    lines.append("")

    # Per-chapter sections
    lines.append("## Per-Chapter Reports")
    lines.append("")
    lines.append("| Ch | Title | Act | Words | Sent | PROC+BAL | Human | Monotony | Floor | Hotspot/1k |")
    lines.append("|----|-------|-----|-------|------|----------|-------|----------|-------|------------|")
    for cid in CHAPTER_IDS:
        if cid not in reports:
            continue
        r = reports[cid]
        mono = "Y" if r.monotony_flag else ""
        floor = "Y" if r.floor_violation_flag else ""
        lines.append(f"| {r.id} | {r.title[:30]} | {r.act} | {r.word_count} | {r.sentence_count} | {r.proc_plus_bal} | {r.human_voice_floor} | {mono} | {floor} | {r.density_hotspot_per_1k} |")
    lines.append("")

    # Test results per chapter
    lines.append("## Issue Resolution Tests (per chapter)")
    lines.append("")
    for cid in CHAPTER_IDS:
        if cid not in reports:
            continue
        r = reports[cid]
        if not (r.issue_test_results or r.dnt_test_results or r.name_test_results):
            continue
        lines.append(f"### {r.id} — {r.title}")
        if r.issue_test_results:
            lines.append("**AR finding tests:**")
            for tid, res in r.issue_test_results.items():
                mark = "PASS" if res["passed"] else "FAIL"
                lines.append(f"- {tid} — {mark} (found={res['found']}, expected={res['expected_present']})")
        if r.dnt_test_results:
            lines.append("**Do Not Touch tests:**")
            for tid, res in r.dnt_test_results.items():
                mark = "PASS" if res["passed"] else "FAIL"
                lines.append(f"- {tid} — {mark} (found={res['found']}, expected={res['expected_present']})")
        if r.name_test_results:
            lines.append("**Name tests:**")
            for tid, res in r.name_test_results.items():
                mark = "PASS" if res["passed"] else "FAIL"
                lines.append(f"- {tid} — {mark} (found={res['found']}, expected={res['expected_present']})")
        if r.custom_counts:
            interesting = {k: v for k, v in r.custom_counts.items() if v > 0}
            if interesting:
                lines.append(f"**Phrase counts:** {interesting}")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_json_report(reports: Dict[str, ChapterReport],
                      aggregates: Dict[str, Any],
                      book_tests: Dict[str, Any],
                      phrase_sweep: Dict[str, Any],
                      source_label: str,
                      out_path: Path) -> None:
    payload = {
        "schema_version": 1,
        "generated": dt.datetime.now().isoformat(timespec="seconds"),
        "source_label": source_label,
        "aggregates": aggregates,
        "book_tests": book_tests,
        "phrase_sweep": phrase_sweep,
        "chapters": {cid: asdict(r) for cid, r in reports.items()},
    }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def diff_reports(report_a_path: Path, report_b_path: Path, out_path: Path) -> None:
    a = json.loads(report_a_path.read_text(encoding="utf-8"))
    b = json.loads(report_b_path.read_text(encoding="utf-8"))
    lines: List[str] = []
    lines.append(f"# Rewrite Report Diff")
    lines.append("")
    lines.append(f"**A:** `{a['source_label']}` ({a['generated']})")
    lines.append(f"**B:** `{b['source_label']}` ({b['generated']})")
    lines.append("")

    # Aggregate diff
    lines.append("## Aggregate Diff")
    lines.append("")
    keys = ["total_chapters", "total_words", "unique_evidence_id_count",
            "book_proc_plus_bal_avg", "book_human_voice_floor_avg",
            "monotony_zone_chapter_count", "floor_violation_chapter_count",
            "ceiling_violation_chapter_count"]
    lines.append("| Field | A | B | Delta |")
    lines.append("|-------|---|---|-------|")
    for k in keys:
        av = a["aggregates"].get(k)
        bv = b["aggregates"].get(k)
        if isinstance(av, (int, float)) and isinstance(bv, (int, float)):
            delta = round(bv - av, 2)
        else:
            delta = ""
        lines.append(f"| {k} | {av} | {bv} | {delta} |")
    lines.append("")

    a_mono = set(a["aggregates"].get("monotony_zone_chapters", []))
    b_mono = set(b["aggregates"].get("monotony_zone_chapters", []))
    left_mono = sorted(a_mono - b_mono)
    joined_mono = sorted(b_mono - a_mono)
    lines.append(f"- **Left monotony zone (improvement):** {', '.join(left_mono) if left_mono else '(none)'}")
    lines.append(f"- **Joined monotony zone (regression):** {', '.join(joined_mono) if joined_mono else '(none)'}")
    lines.append("")

    # Per-chapter test result deltas
    lines.append("## Issue Resolution Deltas")
    lines.append("")
    flips_to_pass: List[str] = []
    flips_to_fail: List[str] = []
    for cid in a["chapters"]:
        if cid not in b["chapters"]:
            continue
        a_tests = a["chapters"][cid].get("issue_test_results", {})
        b_tests = b["chapters"][cid].get("issue_test_results", {})
        for tid in a_tests:
            if tid not in b_tests:
                continue
            ap = a_tests[tid]["passed"]
            bp = b_tests[tid]["passed"]
            if not ap and bp:
                flips_to_pass.append(f"{cid}:{tid}")
            elif ap and not bp:
                flips_to_fail.append(f"{cid}:{tid}")
    lines.append(f"- **Resolved (FAIL → PASS):** {', '.join(flips_to_pass) if flips_to_pass else '(none)'}")
    lines.append(f"- **Regressed (PASS → FAIL):** {', '.join(flips_to_fail) if flips_to_fail else '(none)'}")
    lines.append("")

    # DNT regressions
    lines.append("## Do Not Touch Regressions")
    lines.append("")
    dnt_failures: List[str] = []
    for cid in a["chapters"]:
        if cid not in b["chapters"]:
            continue
        a_dnt = a["chapters"][cid].get("dnt_test_results", {})
        b_dnt = b["chapters"][cid].get("dnt_test_results", {})
        for tid in a_dnt:
            if tid in b_dnt and a_dnt[tid]["passed"] and not b_dnt[tid]["passed"]:
                dnt_failures.append(f"{cid}:{tid}")
    a_book_dnt = a.get("book_tests", {}).get("dnt", {})
    b_book_dnt = b.get("book_tests", {}).get("dnt", {})
    for tid in a_book_dnt:
        if tid in b_book_dnt and a_book_dnt[tid]["passed"] and not b_book_dnt[tid]["passed"]:
            dnt_failures.append(f"BOOK:{tid}")
    lines.append(f"- **DNT failures introduced:** {', '.join(dnt_failures) if dnt_failures else '(none)'}")
    lines.append("")

    # Word count regressions
    lines.append("## Word Count Regressions")
    lines.append("")
    lines.append("| Ch | A words | B words | Delta | Pct |")
    lines.append("|----|---------|---------|-------|-----|")
    regressions: List[str] = []
    for cid in a["chapters"]:
        if cid not in b["chapters"]:
            continue
        aw = a["chapters"][cid]["word_count"]
        bw = b["chapters"][cid]["word_count"]
        delta = bw - aw
        pct = round(100 * delta / max(aw, 1), 1)
        flag = "REGRESSION" if pct < -10 else ""
        if pct < -10:
            regressions.append(cid)
        if abs(pct) >= 5:
            lines.append(f"| {cid} | {aw} | {bw} | {delta} | {pct}% {flag} |")
    lines.append("")
    if regressions:
        lines.append(f"**Word count regressions (>10% loss):** {', '.join(regressions)}")
    else:
        lines.append("**No word count regressions over 10%.**")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="current_state",
                    help="label for this run (e.g. current_state, april06_baseline)")
    ap.add_argument("--manifest", default=str(DEFAULT_MANIFEST),
                    help="path to JSON mapping chapter IDs to source files")
    ap.add_argument("--out-md", default=None, help="output Markdown report path")
    ap.add_argument("--out-json", default=None, help="output JSON report path")
    ap.add_argument("--diff", nargs=2, metavar=("REPORT_A_JSON", "REPORT_B_JSON"),
                    help="diff two existing JSON reports and exit")
    ap.add_argument("--diff-out", default=None, help="output path for diff report")
    args = ap.parse_args()

    if args.diff:
        a_path = Path(args.diff[0])
        b_path = Path(args.diff[1])
        out = Path(args.diff_out) if args.diff_out else (
            AUDITS_DIR / f"rewrite_report_diff_{a_path.stem}_to_{b_path.stem}.md"
        )
        diff_reports(a_path, b_path, out)
        print(f"Diff written to {out}")
        return 0

    manifest_path = Path(args.manifest)
    manifest = load_manifest(manifest_path)
    if not manifest:
        print(f"ERROR: empty manifest at {manifest_path}", file=sys.stderr)
        return 1

    reports: Dict[str, ChapterReport] = {}
    for cid in CHAPTER_IDS:
        if cid not in manifest:
            print(f"WARN: no manifest entry for {cid}", file=sys.stderr)
            continue
        path = Path(manifest[cid])
        if not path.exists():
            print(f"WARN: missing source file for {cid}: {path}", file=sys.stderr)
            continue
        reports[cid] = analyze_chapter(cid, path)

    aggregates = aggregate(reports)
    book_tests = run_book_tests(reports, manifest)
    phrase_sweep = cross_chapter_phrase_sweep(manifest)

    out_md = Path(args.out_md) if args.out_md else AUDITS_DIR / f"rewrite_report_{args.source}.md"
    out_json = Path(args.out_json) if args.out_json else AUDITS_DIR / f"rewrite_report_{args.source}.json"

    write_markdown_report(reports, aggregates, book_tests, phrase_sweep, args.source, out_md)
    write_json_report(reports, aggregates, book_tests, phrase_sweep, args.source, out_json)

    print(f"Report written: {out_md}")
    print(f"JSON written:   {out_json}")
    print(f"Chapters analyzed: {len(reports)}")
    print(f"Monotony zone:     {aggregates.get('monotony_zone_chapter_count')} chapters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
