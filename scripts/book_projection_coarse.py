#!/usr/bin/env python3
"""
Book Projection Coarse (Step 5, first-pass mechanism).

Purpose
-------
Produce a book-level estimate of what the guide work is likely to do to the
voice metrics, without reading every guide entry's prose. This is the
"useful but not perfect" projection — it gives a first-pass answer to
"what will the rewrite do" so we can decide whether the guide is complete
enough to drive Phase 2.

Method
------
1. Read the April 6 baseline harness output as the current state.
2. For each chapter, determine its treatment category from:
   - Guide tier label (from CHAPTER_ENRICHMENT_GUIDE.md, hardcoded here
     because parsing the guide's tier assignments cleanly requires
     per-chapter judgment that has already been done in GUIDE_STATE_AUDIT.md).
   - Presence of a guide entry (in main guide or in NEW_GUIDE_ENTRIES_DRAFT_S170.md).
   - Harness diagnosis (monotony flag, floor violation flag).
3. Apply scaled deltas derived from the B33 test-write calibration
   (the one full-voice-tool-package run we have end-to-end measurement for).
4. Emit a per-chapter before/after table and book-level aggregates.

Calibration source: B33 test-write
----------------------------------
Baseline (Standards/april06_baseline/B33.md):
  words=1786, PROC+BAL=51.7, human_voice_floor=16.7, SOC=16.7, INT=0.0

Post-test-write (Standards/test_writes/B33.md):
  words=3311, PROC+BAL=50.6, human_voice_floor=38.1, SOC=32.8, INT=4.9

Observed deltas (one full Tier-1-scale voice tool package):
  Δwords     = +85.4%
  ΔPROC+BAL  = −1.1 (additive enrichment does not meaningfully cut PROC)
  Δfloor     = +21.4
  ΔSOC       = +16.1
  ΔINT       = +4.9

These are the CAT-A1 (full enrichment) deltas. Other categories scale down
from these by the factors in CATEGORY_SCALING below.

Category definitions
--------------------
CAT-A1: Tier 1 chapter with guide entry AND harness flags monotony or severe
        floor violation. Full B33 calibration applied.
CAT-A2: Tier 1 chapter with guide entry, no harness monotony but floor or
        ceiling violation. 0.75× B33.
CAT-B:  Tier 2 chapter with guide entry. 0.40× B33 (targeted enrichment,
        narrower interventions per guide prescription).
CAT-C:  Tier 2 chapter labeled as "light touch" or single-gap. 0.20× B33.
CAT-D:  Tier 3 preserve, no harness conflict. Zero delta.
CAT-D*: Tier 3 preserve BUT harness flags monotony or floor violation.
        Zero delta applied, but flagged as guide/harness disagreement.
CAT-E:  No guide entry, harness flags monotony. Zero delta (blocker).
CAT-F:  No guide entry, harness flags floor violation. Zero delta (needs
        entry).
CAT-G:  No guide entry, clean chapter. Zero delta (correctly).
CAT-H:  Back matter (Tier 4). Minimal delta or zero.
DRAFT:  Entry exists only in NEW_GUIDE_ENTRIES_DRAFT_S170.md. Treated the
        same as its tier would otherwise imply.

Usage
-----
  python3 scripts/book_projection_coarse.py \
      --baseline Audits/rewrite_report_april06_baseline.json \
      --output Audits/BOOK_PROJECTION_COARSE.md
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Calibration: observed B33 deltas (full voice tool package)
# ---------------------------------------------------------------------------

B33_CALIBRATION = {
    "word_pct_delta": 0.854,       # +85.4%
    "proc_bal_delta": -1.1,        # additive enrichment barely moves PROC+BAL
    "floor_delta": 21.4,           # +21.4 points (16.7 -> 38.1)
    "soc_delta": 16.1,
    "int_delta": 4.9,
}

# ---------------------------------------------------------------------------
# Category scaling factors (multipliers applied to B33 calibration)
# ---------------------------------------------------------------------------

CATEGORY_SCALING = {
    "CAT-A1": 1.00,   # full enrichment, monotony or severe floor
    "CAT-A2": 0.75,   # full Tier 1 but not monotony-zone
    "CAT-B":  0.40,   # targeted Tier 2 enrichment
    "CAT-C":  0.20,   # light touch
    "CAT-D":  0.00,   # preserve
    "CAT-D*": 0.00,   # preserve but harness disagrees — flagged
    "CAT-E":  0.00,   # missing entry, monotony — blocker
    "CAT-F":  0.00,   # missing entry, floor violation — needs entry
    "CAT-G":  0.00,   # missing entry, clean
    "CAT-H":  0.00,   # back matter
    "DRAFT":  0.40,   # draft in holding file, treat as targeted Tier 2 default
}

# ---------------------------------------------------------------------------
# Chapter tier map (from GUIDE_STATE_AUDIT.md)
# ---------------------------------------------------------------------------
# Tier 1 = full enrichment
# Tier 2 = targeted
# Tier 3 = preserve
# Tier 4 = back matter
# None = no entry in the guide or draft file
# "DRAFT" = entry only in NEW_GUIDE_ENTRIES_DRAFT_S170.md

CHAPTER_TIER = {
    "B00": 2, "B01": 3, "B02": 3, "B03": 2, "B04": 2, "B05": 3,
    "B06": 2, "B07": 2, "B08": 2, "B09": 2, "B10": 2, "B11": 2,
    "B12": 3, "B14": 2, "B15": 2, "B16": 2, "B17": 2, "B18": 2,
    "B19": 2, "B20": 2, "B21": 2, "B22": 2, "B23": 3, "B24": 2,
    "B25": 2, "B26": 2, "B27": 2, "B28": 3, "B29": 1, "B30": 2,
    "B31": 2, "B32": 1, "B33": 2, "B34": 2, "B35": 2, "B36": 2,
    "B37": 1, "B38": 2, "B39": 1, "B40": None,
    "B41": 2, "B42": "DRAFT", "B43": "DRAFT", "B44": None,
    "B45": 2, "B46": 3, "B47": "DRAFT", "B48": 1,
    "B49": None, "B50": None, "B51": None, "B52": None, "B53": None,
}

# Chapters flagged as "light touch" Tier 2 in the guide (CAT-C instead of CAT-B)
LIGHT_TOUCH_CHAPTERS = {"B31", "B38"}

# Back matter (Tier 4) override
BACK_MATTER_CHAPTERS = {"B52", "B53"}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ChapterState:
    id: str
    title: str
    act: str
    words: int
    proc_bal: float
    floor: float
    monotony: bool
    floor_violation: bool
    ceiling_violation: bool

    # derived
    tier: Optional[object] = None
    category: str = ""
    category_rationale: str = ""

    # projected
    proj_words: int = 0
    proj_proc_bal: float = 0.0
    proj_floor: float = 0.0
    proj_monotony: bool = False
    proj_floor_violation: bool = False

    # disagreement flag
    guide_harness_conflict: Optional[str] = None


# ---------------------------------------------------------------------------
# Category assignment
# ---------------------------------------------------------------------------

def assign_category(ch: ChapterState) -> None:
    """Populate ch.tier, ch.category, ch.category_rationale, ch.guide_harness_conflict."""

    ch.tier = CHAPTER_TIER.get(ch.id)

    # Back matter override
    if ch.id in BACK_MATTER_CHAPTERS:
        ch.category = "CAT-H"
        ch.category_rationale = "Back matter (Tier 4 treatment)"
        # If monotony/floor flagged, note the conflict but don't treat
        if ch.monotony or ch.floor_violation:
            ch.guide_harness_conflict = (
                "back matter but harness flags "
                + ("monotony; " if ch.monotony else "")
                + ("floor violation" if ch.floor_violation else "")
            ).strip("; ")
        return

    # Missing entry cases
    if ch.tier is None:
        if ch.monotony:
            ch.category = "CAT-E"
            ch.category_rationale = "No guide entry; harness flags monotony — BLOCKER"
        elif ch.floor_violation:
            ch.category = "CAT-F"
            ch.category_rationale = "No guide entry; harness flags floor violation — needs entry"
        else:
            ch.category = "CAT-G"
            ch.category_rationale = "No guide entry; harness shows clean"
        return

    # Draft entry cases
    if ch.tier == "DRAFT":
        # Drafts in the holding file are Tier 2 by stated tier.
        # If harness flags monotony and the chapter has a draft, treat as
        # CAT-B (targeted) because the draft is Tier 2, but flag that the
        # draft's scaling may be insufficient to clear monotony.
        if ch.monotony:
            ch.category = "DRAFT"
            ch.category_rationale = "Draft entry (Tier 2); harness monotony — scaling may be insufficient"
            ch.guide_harness_conflict = "draft Tier 2 but harness monotony — revisit tier"
        else:
            ch.category = "DRAFT"
            ch.category_rationale = "Draft entry (Tier 2); awaiting merge into main guide"
        return

    # Tiered entries in main guide
    if ch.tier == 1:
        if ch.monotony:
            ch.category = "CAT-A1"
            ch.category_rationale = "Tier 1 full enrichment; harness monotony"
        elif ch.floor_violation or ch.ceiling_violation:
            ch.category = "CAT-A2"
            ch.category_rationale = "Tier 1 full enrichment; floor or ceiling violation"
        else:
            ch.category = "CAT-A2"
            ch.category_rationale = "Tier 1 (guide judgment) despite clean harness"
        return

    if ch.tier == 2:
        if ch.id in LIGHT_TOUCH_CHAPTERS:
            ch.category = "CAT-C"
            ch.category_rationale = "Tier 2 light touch"
        else:
            ch.category = "CAT-B"
            ch.category_rationale = "Tier 2 targeted enrichment"
        # Flag if harness disagrees
        if ch.monotony:
            ch.guide_harness_conflict = (
                "Tier 2 but harness flags monotony — may need Tier 1 upgrade"
            )
        return

    if ch.tier == 3:
        if ch.monotony or ch.floor_violation:
            ch.category = "CAT-D*"
            ch.category_rationale = "Tier 3 preserve; harness conflict"
            ch.guide_harness_conflict = (
                "Tier 3 preserve but harness flags "
                + ("monotony; " if ch.monotony else "")
                + ("floor violation" if ch.floor_violation else "")
            ).strip("; ")
        else:
            ch.category = "CAT-D"
            ch.category_rationale = "Tier 3 preserve"
        return

    # Fallback
    ch.category = "CAT-G"
    ch.category_rationale = f"Unclassified tier: {ch.tier}"


# ---------------------------------------------------------------------------
# Apply projection
# ---------------------------------------------------------------------------

def project(ch: ChapterState) -> None:
    scale = CATEGORY_SCALING.get(ch.category, 0.0)

    word_mult = 1.0 + (B33_CALIBRATION["word_pct_delta"] * scale)
    ch.proj_words = int(round(ch.words * word_mult))

    proc_bal_delta = B33_CALIBRATION["proc_bal_delta"] * scale
    ch.proj_proc_bal = round(ch.proc_bal + proc_bal_delta, 1)

    floor_delta = B33_CALIBRATION["floor_delta"] * scale
    ch.proj_floor = round(ch.floor + floor_delta, 1)

    ch.proj_monotony = ch.proj_proc_bal >= 45.0
    ch.proj_floor_violation = ch.proj_floor < 35.0


# ---------------------------------------------------------------------------
# Ingest baseline
# ---------------------------------------------------------------------------

def load_baseline(path: Path) -> list[ChapterState]:
    with open(path) as f:
        data = json.load(f)

    # The baseline report uses a top-level "chapters" list of dicts
    chapters_raw = data.get("chapters") or data.get("per_chapter") or []
    if isinstance(chapters_raw, dict):
        chapters_raw = list(chapters_raw.values())

    result = []
    for c in chapters_raw:
        cs = ChapterState(
            id=c.get("id") or c.get("chapter_id") or c.get("chapter"),
            title=c.get("title", ""),
            act=c.get("act", ""),
            words=c.get("word_count", 0),
            proc_bal=c.get("proc_plus_bal", 0.0),
            floor=c.get("human_voice_floor", 0.0),
            monotony=bool(c.get("monotony_flag", False)),
            floor_violation=bool(c.get("floor_violation_flag", False)),
            ceiling_violation=bool(c.get("ceiling_violation_flag", False)),
        )
        result.append(cs)

    return result


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def emit_report(chapters: list[ChapterState], baseline_path: Path, output_path: Path) -> None:
    # Aggregate before
    total_words_before = sum(c.words for c in chapters)
    avg_proc_bal_before = round(sum(c.proc_bal for c in chapters) / len(chapters), 1)
    avg_floor_before = round(sum(c.floor for c in chapters) / len(chapters), 1)
    monotony_before = sum(1 for c in chapters if c.monotony)
    floor_before = sum(1 for c in chapters if c.floor_violation)

    # Aggregate after
    total_words_after = sum(c.proj_words for c in chapters)
    avg_proc_bal_after = round(sum(c.proj_proc_bal for c in chapters) / len(chapters), 1)
    avg_floor_after = round(sum(c.proj_floor for c in chapters) / len(chapters), 1)
    monotony_after = sum(1 for c in chapters if c.proj_monotony)
    floor_after = sum(1 for c in chapters if c.proj_floor_violation)

    lines = []
    lines.append("# Book Projection — Coarse (Step 5, first-pass)")
    lines.append("")
    lines.append(f"**Baseline source:** `{baseline_path.relative_to(Path.cwd()) if baseline_path.is_absolute() else baseline_path}`")
    lines.append(f"**Calibration reference:** B33 test-write (one full voice-tool-package run, measured end-to-end)")
    lines.append("**Method:** Assign each chapter a treatment category from guide tier + harness diagnosis, then scale B33 calibration deltas by category factor. Coarse and homogeneous within category — explicitly not per-chapter prose-aware.")
    lines.append("**Tolerance:** ±30–40% at chapter level, ~±10% at book level. See ASSUMPTIONS section.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Headline aggregates
    lines.append("## Book-level aggregates: before → projected")
    lines.append("")
    lines.append("| Metric | Before (April 6 baseline) | Projected (guide executed) | Delta |")
    lines.append("|---|---|---|---|")
    lines.append(f"| Total words | {total_words_before:,} | {total_words_after:,} | {total_words_after - total_words_before:+,} ({(total_words_after - total_words_before) / total_words_before * 100:+.1f}%) |")
    lines.append(f"| Avg PROC+BAL | {avg_proc_bal_before} | {avg_proc_bal_after} | {avg_proc_bal_after - avg_proc_bal_before:+.1f} |")
    lines.append(f"| Avg human voice floor | {avg_floor_before} | {avg_floor_after} | {avg_floor_after - avg_floor_before:+.1f} |")
    lines.append(f"| Monotony zone chapters (PROC+BAL ≥ 45) | {monotony_before} | {monotony_after} | {monotony_after - monotony_before:+d} |")
    lines.append(f"| Floor violation chapters (floor < 35) | {floor_before} | {floor_after} | {floor_after - floor_before:+d} |")
    lines.append("")

    # Category tally
    from collections import Counter
    category_counter = Counter(c.category for c in chapters)
    lines.append("## Category distribution")
    lines.append("")
    lines.append("| Category | Count | Scaling | Meaning |")
    lines.append("|---|---|---|---|")
    category_meaning = {
        "CAT-A1": "Tier 1, full enrichment (monotony-zone)",
        "CAT-A2": "Tier 1, full enrichment (non-monotony)",
        "CAT-B":  "Tier 2, targeted enrichment",
        "CAT-C":  "Tier 2, light touch",
        "CAT-D":  "Tier 3, preserve",
        "CAT-D*": "Tier 3, preserve with harness conflict",
        "CAT-E":  "No entry, harness monotony — BLOCKER",
        "CAT-F":  "No entry, floor violation — needs entry",
        "CAT-G":  "No entry, clean chapter",
        "CAT-H":  "Back matter (Tier 4)",
        "DRAFT":  "Draft entry, Tier 2 scaling",
    }
    for cat in ["CAT-A1", "CAT-A2", "CAT-B", "CAT-C", "CAT-D", "CAT-D*", "DRAFT", "CAT-E", "CAT-F", "CAT-G", "CAT-H"]:
        count = category_counter.get(cat, 0)
        if count > 0:
            scale = CATEGORY_SCALING[cat]
            lines.append(f"| {cat} | {count} | {scale:.2f}× | {category_meaning[cat]} |")
    lines.append("")

    # Per-chapter table
    lines.append("## Per-chapter projection")
    lines.append("")
    lines.append("| Ch | Title | Act | Words→ | PROC+BAL→ | Floor→ | Mono→ | FV→ | Cat | Conflict? |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for c in chapters:
        mono_before_m = "Y" if c.monotony else ""
        mono_after_m = "Y" if c.proj_monotony else ""
        fv_before_m = "Y" if c.floor_violation else ""
        fv_after_m = "Y" if c.proj_floor_violation else ""
        mono_cell = f"{mono_before_m}→{mono_after_m}" if (mono_before_m or mono_after_m) else "—"
        fv_cell = f"{fv_before_m}→{fv_after_m}" if (fv_before_m or fv_after_m) else "—"
        conflict = c.guide_harness_conflict or ""
        lines.append(
            f"| {c.id} | {c.title[:30]} | {c.act} | "
            f"{c.words}→{c.proj_words} | "
            f"{c.proc_bal}→{c.proj_proc_bal} | "
            f"{c.floor}→{c.proj_floor} | "
            f"{mono_cell} | {fv_cell} | "
            f"{c.category} | {conflict} |"
        )
    lines.append("")

    # Biggest movers
    lines.append("## Biggest movers (projected)")
    lines.append("")
    lines.append("Chapters ranked by absolute floor-point lift (top 10):")
    lines.append("")
    movers = sorted(chapters, key=lambda c: (c.proj_floor - c.floor), reverse=True)[:10]
    lines.append("| Ch | Title | Floor lift | Words Δ | Category |")
    lines.append("|---|---|---|---|---|")
    for c in movers:
        word_delta = c.proj_words - c.words
        lines.append(
            f"| {c.id} | {c.title[:30]} | +{c.proj_floor - c.floor:.1f} | +{word_delta} | {c.category} |"
        )
    lines.append("")

    # Blockers
    blockers = [c for c in chapters if c.category == "CAT-E"]
    needs_entry = [c for c in chapters if c.category == "CAT-F"]
    lines.append("## Blockers")
    lines.append("")
    if blockers:
        lines.append("**Chapters with no entry AND harness monotony (must write entry before rewrite):**")
        lines.append("")
        for c in blockers:
            lines.append(f"- {c.id} \"{c.title}\": PROC+BAL={c.proc_bal}, floor={c.floor}")
        lines.append("")
    else:
        lines.append("None. Every harness-flagged monotony chapter has at least a draft or main-guide entry.")
        lines.append("")

    if needs_entry:
        lines.append("**Chapters with no entry AND harness floor violation (non-blocking but guide-incomplete):**")
        lines.append("")
        for c in needs_entry:
            lines.append(f"- {c.id} \"{c.title}\": PROC+BAL={c.proc_bal}, floor={c.floor}")
        lines.append("")

    # Conflicts
    conflicts = [c for c in chapters if c.guide_harness_conflict]
    lines.append("## Guide / harness disagreements")
    lines.append("")
    if conflicts:
        lines.append("Chapters where the guide's tier assignment and the harness diagnosis tell different stories. These are the chapters the author should resolve before Phase 2 begins — not because the coarse projection depends on it, but because the full projection (Step 5 at fidelity) will need a consistent tier map.")
        lines.append("")
        lines.append("| Ch | Tier | Harness | Conflict |")
        lines.append("|---|---|---|---|")
        for c in conflicts:
            tier_str = str(c.tier) if c.tier is not None else "—"
            harness = []
            if c.monotony:
                harness.append("mono")
            if c.floor_violation:
                harness.append("floor")
            if c.ceiling_violation:
                harness.append("ceiling")
            harness_str = ",".join(harness) if harness else "clean"
            lines.append(f"| {c.id} | {tier_str} | {harness_str} | {c.guide_harness_conflict} |")
        lines.append("")
    else:
        lines.append("None.")
        lines.append("")

    # Assumptions
    lines.append("## Assumptions and tolerances")
    lines.append("")
    lines.append("This projection rests on a specific set of assumptions. The projection is useful for book-level orientation and chapter-level ranking. It is NOT a substitute for per-chapter prose-aware projection (Step 5 at full fidelity).")
    lines.append("")
    lines.append("**Assumptions:**")
    lines.append("")
    lines.append("1. **B33 is a valid calibration reference.** The B33 test-write applied a full voice-tool package (Scene from Evidence, Backstory Excursion, Steve's Persistent Inner Voice, Baldwin preserved, Robinson preserved) and was measured end-to-end. Its deltas are the observed upper bound for what a Tier 1 intervention can do. Other calibrations would likely land within the ±30–40% tolerance.")
    lines.append("")
    lines.append("2. **Enrichment is homogeneous within category.** Every Tier 1 chapter gets roughly B33-scale deltas. Every Tier 2 chapter gets 0.40× B33. This is false in detail (each guide entry prescribes a different voice tool mix) but roughly true in aggregate.")
    lines.append("")
    lines.append("3. **PROC+BAL barely moves with additive enrichment alone.** The B33 calibration shows PROC+BAL moved only −1.1 points (51.7 → 50.6) because the test-write added scene and interior on top of existing procedural material rather than cutting procedure. To clear the monotony flag (PROC+BAL ≥ 45 → < 45), the rewrite must also PRUNE procedural material, which the B33 test-write did not do. The coarse projection therefore UNDER-predicts monotony clearance — if the guide's tier 1 prescriptions include cutting procedural material, the real monotony count may drop further than projected.")
    lines.append("")
    lines.append("4. **The human voice floor moves strongly with additive enrichment.** B33 lifted the floor by 21.4 points (16.7 → 38.1), primarily via SOC (+16.1) and INT (+4.9). This is the most reliable lever the voice tools have.")
    lines.append("")
    lines.append("5. **Tier 3 (preserve) chapters get zero delta.** This is correct by definition for true preserve cases (B01, B02, B05, B12, B23, B28, B46). For the preserve chapters where the harness disagrees (CAT-D*), the zero delta is a conservative choice — if the author decides to reclassify them upward during Gate 3, the projection will under-report their contribution.")
    lines.append("")
    lines.append("6. **Chapters with no entry get zero delta.** This means the 7 missing chapters (B40, B44, B49, B50, B51, B52, B53) contribute nothing to the projected improvement. If the guide grows to cover them, their contribution increases. CAT-E (B52) is the only true blocker — the others are non-blocking gaps.")
    lines.append("")
    lines.append("**Tolerances:**")
    lines.append("")
    lines.append("- **Chapter level:** ±30–40% on the word delta, ±5 points on floor. A projected chapter at floor=42 could land anywhere between 37 and 47. The ranking of movers is more reliable than the absolute numbers.")
    lines.append("- **Book level:** ±10% on total words, ±2 points on avg floor, ±2 chapters on monotony count (bias toward under-predicting clearance for reasons given in assumption 3).")
    lines.append("")
    lines.append("**What this projection does NOT do:**")
    lines.append("")
    lines.append("- Does not read per-chapter guide prose to see what specific interventions are prescribed.")
    lines.append("- Does not model the pruning effect (cutting procedural material), which would further reduce PROC+BAL.")
    lines.append("- Does not model evidence integration improvements (new exhibit deployments that add EVID score).")
    lines.append("- Does not account for the Gate 3 reconciliation pass that will merge duplicate entries and resolve tier conflicts.")
    lines.append("- Does not validate that the B33 calibration generalizes — that requires a second calibration point from a different chapter, ideally one with a different voice profile.")

    output_path.write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    chapters = load_baseline(args.baseline)
    for c in chapters:
        assign_category(c)
        project(c)

    emit_report(chapters, args.baseline, args.output)
    print(f"Wrote {args.output}")
    print(f"{len(chapters)} chapters projected")


if __name__ == "__main__":
    main()
