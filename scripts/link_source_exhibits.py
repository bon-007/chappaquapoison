#!/usr/bin/env python3
"""
Phase 1: Source Exhibit Linkage — Automated Pre-Population

Reads evidence_index_canonical.json, adds `source_exhibit` field to every entry,
and pre-populates deterministic linkages based on exhibit ID patterns.

Produces a report of:
  - Items linked automatically (with reasoning)
  - Hero items still unlinked (need manual review)
  - Self-sourcing items confirmed (null)
  - Discrepancies found

Rules from SOURCE_EXHIBIT_SPEC.md v1.1:
  1. source_exhibit must be a valid exhibit_id in the index
  2. Null for self-sourcing items
  3. Points to the most specific usable parent
  4. Source entry must exist in the index
  5. One parent only

Usage:
  python3 scripts/link_source_exhibits.py                    # Dry run (report only)
  python3 scripts/link_source_exhibits.py --apply            # Apply changes to index
  python3 scripts/link_source_exhibits.py --apply --backup   # Apply with backup
"""

import json
import sys
import re
import shutil
from datetime import datetime
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
INDEX_PATH = PROJECT_DIR / "evidence_index_canonical.json"

# ============================================================
# LINKAGE RULES
# ============================================================

# Rule 1: MSG- numbered items → unsuffixed full conversation document
# e.g., MSG-JESSE-001 → MSG-JESSE, MSG-MATAN-005 → MSG-MATAN
# The unsuffixed entries are the full conversation documents (confirmed by descriptions).
# NOTE: The spec v1.1 table listed MSG-JESSE-008 as the full conversation, but the
# actual data shows MSG-JESSE (unsuffixed) = "Full iMessage Conversation (154 pages,
# 2,191 messages)". Using unsuffixed as source. Flagged for editorial review.
MSG_CONVERSATION_PARENTS = {
    "JESSE":   "MSG-JESSE",
    "MATAN":   "MSG-MATAN",
    "WALSHSR": "MSG-WALSHSR",
    "BRIENNE": "MSG-BRIENNE",
    "STEVE":   "MSG-STEVE",
    "BRENDAN": "MSG-BRENDAN",
    "LINDA":   "MSG-LINDA",
    "RHODES":  "MSG-RHODES",
    "RITA":    "MSG-RITA",
    "RASHMI":  "MSG-RASHMI",
}

# Rule 2: LEGAL-INQUEST-* items → LEGAL-INQUEST-TRANSCRIPT
# (except the transcript itself, which is self-sourcing)
INQUEST_TRANSCRIPT_ID = "LEGAL-INQUEST-TRANSCRIPT"

# Rule 3: LEGAL-DVRO-* items → PDF_DV_TRIAL_TRANSCRIPT
DVRO_TRANSCRIPT_ID = "PDF_DV_TRIAL_TRANSCRIPT"

# Rule 4: TRIAL-BATTERY-* items → ExTR_23
BATTERY_TRANSCRIPT_ID = "ExTR_23"

# Rule 5: Suffixed exhibit items → parent
# Pattern: BASE_SUFFIX where BASE is the parent exhibit_id
# e.g., C-6_03 → C-6, ExTR_10_03 → ExTR_10, A-1_02 → A-1
SUFFIX_PATTERN = re.compile(r'^(.+?)_(\d{2,3})$')

# Items explicitly known to be self-sourcing (Type 6/7/8)
# These get source_exhibit = null regardless of other patterns
KNOWN_SELF_SOURCING_PREFIXES = [
    "PHOTO_",          # Photographs are the evidence
    "SCREENSHOT_",     # Device screenshots are the evidence
    "SLE-",            # Blog posts (Type 7: blog excerpts)
    "BLOG_",           # Blog archive items
    "INT-",            # Interviews
    "VID-",            # Video files
    "VIDEO_",          # Video files
    "Clip",            # Audio/video clips
    "ExMM_",           # Audio/video recordings — the recording IS the evidence
    "ExMM__",          # Double underscore variant (ExMM__06)
    "EMAIL_",          # Email correspondence — the email IS the evidence
    "CORR-",           # Correspondence — letters are the evidence (unless file_missing)
]

# Standalone trial/court exhibit prefixes — when an item has one of these prefixes
# and is NOT a suffixed sub-item, it's self-sourcing (the document IS the evidence)
STANDALONE_EXHIBIT_PREFIXES = [
    "ExA_", "ExC_", "ExD_", "ExDD_", "ExG_", "ExI_", "ExL_", "ExN_",
    "ExO_", "ExR_", "ExSS_", "ExT_", "ExX_", "ExQQ_",
    "ExTR_",           # Transcript documents — the transcript IS the evidence
    "Decl_",           # Sworn declarations
    "Adm_",            # Admissions
    "Filing_",         # Court filings
]

# Court exhibit letter series (A-1, B-4, C-6, D-33, F-013, G-19, etc.)
# These are standalone court exhibit documents — self-sourcing UNLESS they have
# a numeric suffix indicating they're a page/section of a parent
COURT_EXHIBIT_PATTERN = re.compile(r'^([A-G])-\d+$')

# DOC_ and PDF_ and DOCX_ items — standalone documents
DOC_PREFIXES = ["DOC_", "PDF_", "DOCX_"]

# HERO-1, MATAN-2, ABUSE-1, SUM-1 — these are standalone evidence items
MISC_SELF_SOURCING = {"HERO-1", "MATAN-2", "ABUSE-1", "SUM-1"}

# Specific self-sourcing items (confirmed in spec)
KNOWN_SELF_SOURCING_IDS = {
    "ExQQ_05",         # IS the Tedla deposition PDF
    "ExQQ_06",         # IS the Brienne blog abuse admission PDF
    "ExT_01",          # IS the LaMelle affidavit PDF
    "C-6",             # IS the Walsh DV120 response
    "ExF_01",          # IS the abuse journal email PDF
    "ExSS_09",         # IS the LaMelle intimidation PDF
    "ExSS_10",         # IS the Brienne deposition abuse/CPS PDF
    "LEGAL-INQUEST-TRANSCRIPT",  # IS the transcript
    "LEGAL-HUMPHREY-RECUSAL",    # IS the recusal order
    "QUOTE-GOOD-VICTIM",         # Author account
    "QUOTE-TARA-CRAZY-TOO-TOGETHER",  # Witnessed verbal statement
    "ExEMAIL_SEROQUEL_ADMISSION",     # The email IS the evidence
}

# Items needing manual source location (file_missing or TBD in spec)
NEEDS_MANUAL_REVIEW = {
    "TEXT_TARA_HINDSIGHT_ADMISSION",
    "TEXT_TARA_JUL21_MISCARRIAGE_CONDITIONAL",
    "QUOTE-TARA-LEAVE-COMPOUND",
    "QUOTE-TARA-FAMILY-CUSTODY-THREAT",
    "DOC_NY_DEMAND_PROSECUTION",
    "PDF_TARA_WALSH_DECLARATION",
    "SCREENSHOT_TARA_WALSH_HOUSEHOLD_ABUSE",
    "PDF_WALSH_ABUSE_MOTION_02",
    "CORR-TURNURE-FURMAN",
    "CORR-TURNURE-EGITTO",
    "LAB-MYCOPHENOLIC-ACID",
    "LEGAL-RUSSELL-AFFIDAVIT-DEFAULT",
    "LEGAL-EGITTO-RESPONSE",
    "LEGAL-TEDLA-DECLARATION",
}

# ============================================================
# LINKAGE ENGINE
# ============================================================

def build_exhibit_id_set(entries):
    """Build a set of all valid exhibit_ids for validation."""
    return {e.get("exhibit_id") or e.get("id") for e in entries if e.get("exhibit_id") or e.get("id")}


def get_exhibit_id(entry):
    """Get exhibit_id, falling back to id field."""
    return entry.get("exhibit_id") or entry.get("id", "")


build_exhibit_id_set_cache = set()

def determine_source_exhibit(entry, valid_ids):
    """
    Determine the source_exhibit for a given entry.

    Returns: (source_exhibit_value, rule_name, reasoning)
      - source_exhibit_value: str or None
      - rule_name: str identifying which rule matched
      - reasoning: str explaining the decision
    """
    global build_exhibit_id_set_cache
    build_exhibit_id_set_cache = valid_ids

    eid = get_exhibit_id(entry)
    tier = entry.get("tier", "").lower()

    if not eid:
        return None, "no_id", "Entry has no exhibit_id"

    # Check explicit self-sourcing IDs first
    if eid in KNOWN_SELF_SOURCING_IDS:
        return None, "self_sourcing_explicit", f"Confirmed self-sourcing per SOURCE_EXHIBIT_SPEC"

    # Check misc self-sourcing
    if eid in MISC_SELF_SOURCING:
        return None, "self_sourcing_misc", f"Standalone evidence item — self-sourcing"

    # Check needs-manual-review items (file_missing or TBD)
    if eid in NEEDS_MANUAL_REVIEW:
        return None, "needs_manual", f"Source needs to be located (file_missing or TBD in spec)"

    # Check self-sourcing prefixes
    for prefix in KNOWN_SELF_SOURCING_PREFIXES:
        if eid.startswith(prefix):
            return None, "self_sourcing_prefix", f"Prefix {prefix} indicates self-sourcing"

    # Check standalone exhibit prefixes (ExA_02, ExTR_10, Decl_01, etc.)
    # Only if NOT a suffixed sub-item (the suffix rule below will handle those)
    for prefix in STANDALONE_EXHIBIT_PREFIXES:
        if eid.startswith(prefix):
            # Check if this is a suffixed sub-item
            suffix_match_check = SUFFIX_PATTERN.match(eid)
            if suffix_match_check:
                parent_check = suffix_match_check.group(1)
                if parent_check in build_exhibit_id_set_cache:
                    break  # Let the suffix rule handle it below
            return None, "self_sourcing_standalone_exhibit", f"Standalone exhibit ({prefix}*) — self-sourcing"

    # Check DOC_/PDF_/DOCX_ prefixes
    for prefix in DOC_PREFIXES:
        if eid.startswith(prefix):
            # Check if file_missing — those need manual review
            if entry.get("file_missing", False):
                return None, "needs_manual", f"Standalone document but file_missing — needs source location"
            return None, "self_sourcing_document", f"Standalone document ({prefix}*) — self-sourcing"

    # Check court exhibit letter series (A-1, B-4, C-6, D-33, etc.)
    if COURT_EXHIBIT_PATTERN.match(eid):
        return None, "self_sourcing_court_exhibit", f"Court exhibit series — standalone document"

    # Rule 1: MSG- numbered items → full conversation document
    msg_match = re.match(r'^MSG-([A-Z]+)-(\d+)$', eid)
    if msg_match:
        convo_name = msg_match.group(1)
        parent = MSG_CONVERSATION_PARENTS.get(convo_name)
        if parent:
            if parent == eid:
                # This IS the full conversation
                return None, "self_sourcing_msg_parent", "This is the full conversation document"
            if parent in valid_ids:
                return parent, "msg_numbered_to_parent", f"Numbered message excerpt → full conversation {parent}"
            else:
                return None, "msg_parent_missing", f"Parent {parent} not found in index"

    # MSG unsuffixed entries are full conversation documents → self-sourcing
    if re.match(r'^MSG-[A-Z]+$', eid) and eid in MSG_CONVERSATION_PARENTS.values():
        return None, "self_sourcing_msg_parent", "This is the full conversation document"

    # Special MSG entries that don't follow the pattern
    if eid in ("MSG-SIX-REGISTER-FEB20", "MSG-CLEO-INCIDENT"):
        return None, "needs_manual", f"Non-standard MSG entry — needs manual review"

    # Rule 2: LEGAL-INQUEST-* → LEGAL-INQUEST-TRANSCRIPT
    if eid.startswith("LEGAL-INQUEST-") and eid != INQUEST_TRANSCRIPT_ID:
        if INQUEST_TRANSCRIPT_ID in valid_ids:
            return INQUEST_TRANSCRIPT_ID, "inquest_to_transcript", f"Inquest testimony excerpt → {INQUEST_TRANSCRIPT_ID}"
        else:
            return None, "inquest_transcript_missing", f"{INQUEST_TRANSCRIPT_ID} not found in index"

    # Rule 3: LEGAL-DVRO-* → PDF_DV_TRIAL_TRANSCRIPT
    if eid.startswith("LEGAL-DVRO-") and eid != DVRO_TRANSCRIPT_ID:
        if DVRO_TRANSCRIPT_ID in valid_ids:
            return DVRO_TRANSCRIPT_ID, "dvro_to_transcript", f"DVRO hearing excerpt → {DVRO_TRANSCRIPT_ID}"
        else:
            return None, "dvro_transcript_missing", f"{DVRO_TRANSCRIPT_ID} not found in index"

    # Rule 4: TRIAL-BATTERY-* → ExTR_23
    if eid.startswith("TRIAL-BATTERY-"):
        if BATTERY_TRANSCRIPT_ID in valid_ids:
            return BATTERY_TRANSCRIPT_ID, "battery_to_transcript", f"Battery trial excerpt → {BATTERY_TRANSCRIPT_ID}"
        else:
            return None, "battery_transcript_missing", f"{BATTERY_TRANSCRIPT_ID} not found in index"

    # Rule 5: Suffixed items → parent
    # But only when the parent exists in the index
    suffix_match = SUFFIX_PATTERN.match(eid)
    if suffix_match:
        parent_id = suffix_match.group(1)
        if parent_id in valid_ids and parent_id != eid:
            return parent_id, "suffix_to_parent", f"Suffixed item → parent {parent_id}"

    # LEGAL- items that are standalone filings (not INQUEST/DVRO) → likely self-sourcing
    if eid.startswith("LEGAL-"):
        # Items like LEGAL-KIDNAP-COMPLAINT, LEGAL-TEDLA-DECL, etc.
        # These are standalone legal documents — the filing IS the evidence
        return None, "self_sourcing_legal", f"Standalone legal filing — self-sourcing"

    # TEXT_ items — text message evidence
    if eid.startswith("TEXT_"):
        if entry.get("file_missing", False):
            return None, "needs_manual", f"Text message evidence — file_missing, needs source location"
        # If the file exists, it's self-sourcing (the text/screenshot IS the evidence)
        return None, "self_sourcing_text", f"Text message evidence — file exists, self-sourcing"

    # EB_ items — Evie Story Book pages
    # Per SOURCE_EXHIBIT_SPEC: these need page spread extraction (Phase 3)
    # For now, mark as needing Phase 3 work
    if eid.startswith("EB"):
        return None, "needs_phase3", f"Evie Story Book item — needs page spread extraction (Phase 3)"

    # F-### items (court exhibits from the F series)
    if re.match(r'^F-\d+$', eid):
        return None, "self_sourcing_court_exhibit", f"F-series court exhibit — standalone document"

    # Remaining standalone items with file_missing flag
    if entry.get("file_missing", False):
        return None, "needs_manual", f"File missing — needs source location"

    # Everything else → null (unclassified, needs manual review for heroes)
    return None, "unclassified", "No deterministic rule matched"


def run_linkage(entries):
    """Run the linkage engine on all entries. Returns results list."""
    valid_ids = build_exhibit_id_set(entries)
    results = []

    for entry in entries:
        eid = get_exhibit_id(entry)
        tier = entry.get("tier", "")
        source, rule, reasoning = determine_source_exhibit(entry, valid_ids)
        results.append({
            "exhibit_id": eid,
            "tier": tier,
            "source_exhibit": source,
            "rule": rule,
            "reasoning": reasoning,
        })

    return results


# ============================================================
# REPORTING
# ============================================================

def generate_report(entries, results):
    """Generate a human-readable report of the linkage results."""
    lines = []
    lines.append("=" * 72)
    lines.append("SOURCE EXHIBIT LINKAGE — Phase 1 Report")
    lines.append(f"Generated: {datetime.now().isoformat()}")
    lines.append(f"Total entries: {len(entries)}")
    lines.append("=" * 72)

    # Count by rule
    rule_counts = defaultdict(int)
    for r in results:
        rule_counts[r["rule"]] += 1

    lines.append("\n## Summary by Rule\n")
    for rule, count in sorted(rule_counts.items(), key=lambda x: -x[1]):
        lines.append(f"  {rule:40s} {count:5d}")

    # Count linked vs null
    linked = [r for r in results if r["source_exhibit"] is not None]
    null_confirmed = [r for r in results if r["source_exhibit"] is None and r["rule"] != "unclassified"]
    unclassified = [r for r in results if r["rule"] == "unclassified"]
    needs_manual = [r for r in results if r["rule"] == "needs_manual"]

    lines.append(f"\n  TOTAL LINKED:        {len(linked)}")
    lines.append(f"  CONFIRMED NULL:      {len(null_confirmed)}")
    lines.append(f"  NEEDS MANUAL:        {len(needs_manual)}")
    lines.append(f"  UNCLASSIFIED:        {len(unclassified)}")

    # Hero items breakdown
    hero_results = [(e, r) for e, r in zip(entries, results) if e.get("tier", "").lower() == "hero"]
    hero_linked = [(e, r) for e, r in hero_results if r["source_exhibit"] is not None]
    hero_null = [(e, r) for e, r in hero_results if r["source_exhibit"] is None and r["rule"] not in ("unclassified", "needs_manual")]
    hero_manual = [(e, r) for e, r in hero_results if r["rule"] in ("needs_manual", "unclassified")]

    lines.append(f"\n## Hero Items ({len(hero_results)} total)\n")
    lines.append(f"  Linked automatically: {len(hero_linked)}")
    lines.append(f"  Confirmed null:       {len(hero_null)}")
    lines.append(f"  Needs manual review:  {len(hero_manual)}")

    # Detail: Hero items linked
    lines.append(f"\n### Hero Items — Linked ({len(hero_linked)})\n")
    for e, r in sorted(hero_linked, key=lambda x: x[1]["rule"]):
        lines.append(f"  {r['exhibit_id']:50s} → {r['source_exhibit']:30s} [{r['rule']}]")

    # Detail: Hero items self-sourcing
    lines.append(f"\n### Hero Items — Self-Sourcing ({len(hero_null)})\n")
    for e, r in sorted(hero_null, key=lambda x: x[0].get("exhibit_id", "")):
        lines.append(f"  {r['exhibit_id']:50s} [{r['rule']}] {r['reasoning'][:60]}")

    # Detail: Hero items needing manual review
    lines.append(f"\n### Hero Items — Needs Manual Review ({len(hero_manual)})\n")
    for e, r in sorted(hero_manual, key=lambda x: x[0].get("exhibit_id", "")):
        lines.append(f"  {r['exhibit_id']:50s} [{r['rule']}] {r['reasoning'][:60]}")

    # Detail: All linked items (non-hero)
    non_hero_linked = [(e, r) for e, r in zip(entries, results)
                       if r["source_exhibit"] is not None and e.get("tier", "").lower() != "hero"]
    lines.append(f"\n### Non-Hero Items — Linked ({len(non_hero_linked)})\n")
    for e, r in sorted(non_hero_linked, key=lambda x: x[1]["rule"] + x[1]["exhibit_id"]):
        lines.append(f"  {r['exhibit_id']:50s} → {r['source_exhibit']:30s} [{r['rule']}]")

    # Discrepancies
    lines.append("\n## Discrepancies / Notes\n")
    lines.append("  1. SOURCE_EXHIBIT_SPEC v1.1 listed MSG-JESSE-008 as the full conversation document,")
    lines.append("     but MSG-JESSE (unsuffixed) has the description 'Full iMessage Conversation")
    lines.append("     (154 pages, 2,191 messages)' while MSG-JESSE-008 is 'Final messages in the")
    lines.append("     conversation.' This script uses the unsuffixed entries as source parents.")
    lines.append("     → EDITORIAL DECISION NEEDED: confirm unsuffixed = full conversation.")
    lines.append("")
    lines.append("  2. 9 entries lack exhibit_id field entirely (use 'id' instead). These are:")
    no_eid = [e for e in entries if "exhibit_id" not in e]
    for e in no_eid:
        lines.append(f"     id={e.get('id','?'):50s} desc={e.get('description','')[:50]}")

    lines.append("")
    lines.append("=" * 72)

    return "\n".join(lines)


# ============================================================
# APPLY CHANGES
# ============================================================

def apply_linkage(index_data, results, backup=False):
    """Apply source_exhibit field to all entries in the canonical index."""
    if backup:
        backup_path = INDEX_PATH.with_suffix(f".json.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        shutil.copy2(INDEX_PATH, backup_path)
        print(f"Backup saved to: {backup_path}")

    entries = index_data["entries"]
    changes = 0

    for entry, result in zip(entries, results):
        source = result["source_exhibit"]
        # Add field to every entry
        entry["source_exhibit"] = source
        changes += 1

    # Update generation timestamp
    index_data["generated"] = datetime.now().isoformat()

    with open(INDEX_PATH, "w") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)

    print(f"Applied source_exhibit to {changes} entries.")
    return changes


# ============================================================
# MAIN
# ============================================================

def main():
    args = sys.argv[1:]
    do_apply = "--apply" in args
    do_backup = "--backup" in args

    with open(INDEX_PATH) as f:
        index_data = json.load(f)

    entries = index_data["entries"]
    print(f"Loaded {len(entries)} entries from canonical index.\n")

    results = run_linkage(entries)
    report = generate_report(entries, results)

    # Save report
    report_path = PROJECT_DIR / "Audits" / f"source_exhibit_linkage_report_{datetime.now().strftime('%Y%m%d')}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report)
    print(f"Report saved to: {report_path}\n")
    print(report)

    if do_apply:
        print("\n--- APPLYING CHANGES ---\n")
        apply_linkage(index_data, results, backup=do_backup)
    else:
        print("\n--- DRY RUN --- Use --apply to write changes. ---\n")


if __name__ == "__main__":
    main()
