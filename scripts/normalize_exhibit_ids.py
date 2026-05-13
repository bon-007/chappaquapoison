#!/usr/bin/env python3
"""Normalize exhibit IDs to consistent short format: XX-NNa

Maps long category-based and filename-based IDs to compact 2-letter prefix codes.
Preserves already-canonical single-letter IDs (A-1, B-9, etc).
Handles duplicates by appending letter suffixes (a, b, c...).
Stores original ID in 'original_exhibit_id' for reference.

⚠ DEPRECATED: This script's data has been absorbed into evidence_index_canonical.json.
To update evidence data, edit directly in canonical and re-run: python3 scripts/build_canonical_evidence_index.py
"""

import json
import re
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EVIDENCE_META = PROJECT_ROOT / "evidence_metadata.json"

# Map verbose category prefixes to 2-letter codes
PREFIX_MAP = {
    'Transcript': 'TR',
    'Exhibits Bundle': 'EB',
    'Gavish': 'GV',
    'Sworn Statements': 'SS',
    'Depositions': 'DP',
    'Blog Archive': 'BA',
    'Attorney Letters': 'AL',
    'Pattern Evidence': 'PE',
    'Brienne Records': 'BR',
    'Structural Complaint': 'SC',
    'Trial Record': 'TL',
    'Declaration': 'DC',
    'Griffin CASAC': 'GC',
    'Custody Order': 'CO',
    'Investigation': 'IN',
    'Appellate': 'AP',
    'Court Orders': 'CJ',
    'Corruption': 'CR',
    'Guttridge': 'GT',
    'Gelhaar': 'GH',
    'Toxicology': 'TX',
    'Verdict': 'VD',
    'Police Reports': 'PR',
    'FBI Complaint': 'FB',
    'Griffin License': 'GL',
    'Messages': 'MS',
    'CA Orders': 'CA',
    'Brienne Depo': 'BD',
    'Email': 'EM',
    'AFC Records': 'AR',
    'AFC Billing': 'AB',
    'LaMelle': 'LM',
    'Gun Allegation': 'GA',
    'Abuse Journal': 'AJ',
    'Financial': 'FN',
    'Photos': 'PH',
    'Adderall Text': 'AD',
    'Text': 'TM',
    'Supreme Court': 'SU',
    'Forensic': 'FR',
    'Recantation': 'RC',
    'iMsg': 'IM',
    'MM': 'MM',
    'Filing': 'FL',
}

# Clip IDs are special — they have descriptive suffixes
CLIP_MAP = {
    'Clip01': 'CL-01', 'Clip02': 'CL-02', 'Clip03': 'CL-03',
    'Clip04': 'CL-04', 'Clip05': 'CL-05', 'Clip06': 'CL-06',
    'Clip07': 'CL-07', 'Clip08': 'CL-08', 'Clip09': 'CL-09',
    'Clip10': 'CL-10', 'Clip11': 'CL-11', 'Clip12': 'CL-12',
    'Clip13': 'CL-13', 'Clip14': 'CL-14', 'Clip15': 'CL-15',
}


def normalize_id(eid):
    """Convert an exhibit ID to compact format."""
    if not eid:
        return eid

    # Already canonical (single letter + number)?
    if re.match(r'^[A-H]-\d+[a-z]?$', eid):
        return eid

    # F-series (already compact)
    if re.match(r'^F-\d+', eid):
        return eid

    # MM-series (already compact)
    if re.match(r'^MM-\d+', eid):
        return eid

    # Clip IDs — extract number
    clip_match = re.match(r'^Clip(\d+)', eid)
    if clip_match:
        num = clip_match.group(1).zfill(2)
        return f'CL-{num}'

    # Gavish clips — extract a short descriptor
    if eid.startswith('Gavish-'):
        rest = eid[7:]
        # Take first word, abbreviated
        words = re.findall(r'[A-Z][a-z]+', rest)
        if words:
            short = words[0][:4]
            return f'GV-{short}'
        return f'GV-{rest[:4]}'

    # Try prefix map (longest match first)
    for prefix, code in sorted(PREFIX_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        if eid.startswith(prefix):
            suffix = eid[len(prefix):]
            # Clean suffix: remove leading separators
            suffix = re.sub(r'^[\s\-_]+', '', suffix)
            # Extract just the number/letter part
            num_match = re.match(r'(\d+[a-z]?)', suffix)
            if num_match:
                return f'{code}-{num_match.group(1).zfill(2)}'
            # No number — just use first few chars
            clean = re.sub(r'[^a-zA-Z0-9]', '', suffix)
            return f'{code}-{clean[:4]}' if clean else code

    # Filename-derived with underscores
    if '_' in eid or len(eid) > 20:
        # Try to extract an ExXX pattern
        ex_match = re.match(r'Ex([A-Z]+)_(\d+)', eid)
        if ex_match:
            return f'Ex{ex_match.group(1)}-{ex_match.group(2).zfill(2)}'
        # Use initials of significant words
        words = re.findall(r'[A-Z][a-z]+|[A-Z]+(?=[A-Z]|$)|\d+', eid)
        if len(words) >= 2:
            code = ''.join(w[0].upper() for w in words[:2])
            num = next((w for w in words if w.isdigit()), '')
            return f'{code}-{num.zfill(2)}' if num else f'{code}-01'
        return eid[:8]

    # Date-prefixed
    if re.match(r'^\d{4}-\d{2}', eid):
        return eid[:10]  # truncate to date

    return eid


def deduplicate_ids(evidence):
    """After normalization, resolve any duplicate IDs by appending suffixes."""
    # Collect all new IDs
    id_groups = {}
    for file_path, entry in evidence.items():
        new_id = entry.get('exhibit_id', '')
        id_groups.setdefault(new_id, []).append(file_path)

    # For groups with duplicates, append a/b/c suffixes
    deduped = 0
    for eid, paths in id_groups.items():
        if len(paths) <= 1:
            continue
        for i, fp in enumerate(paths):
            suffix = chr(ord('a') + i)
            evidence[fp]['exhibit_id'] = f'{eid}{suffix}'
            deduped += 1

    return deduped


def main():
    with open(EVIDENCE_META) as f:
        evidence = json.load(f)

    changed = 0
    already_compact = 0

    for file_path, entry in evidence.items():
        old_id = entry.get('exhibit_id', '')
        new_id = normalize_id(old_id)

        if new_id != old_id:
            # Store original for reference (but don't overwrite existing original)
            if not entry.get('original_exhibit_id'):
                entry['original_exhibit_id'] = old_id
            entry['exhibit_id'] = new_id
            changed += 1
        else:
            already_compact += 1

    # Deduplicate
    deduped = deduplicate_ids(evidence)

    # Save
    with open(EVIDENCE_META, 'w') as f:
        json.dump(evidence, f, indent=2)

    # Stats
    all_ids = [v.get('exhibit_id', '') for v in evidence.values()]
    lengths = [len(eid) for eid in all_ids if eid]
    dupes = sum(1 for _, c in Counter(all_ids).items() if c > 1)

    print(f"=== Exhibit ID Normalization ===")
    print(f"  Already compact: {already_compact}")
    print(f"  Normalized: {changed}")
    print(f"  Deduplication fixes: {deduped}")
    print(f"  ID length range: {min(lengths)}-{max(lengths)} chars (avg {sum(lengths)/len(lengths):.1f})")
    print(f"  Remaining duplicates: {dupes}")

    # Show sample transformations
    print(f"\n=== Sample Changes ===")
    count = 0
    for fp, entry in evidence.items():
        orig = entry.get('original_exhibit_id', '')
        curr = entry.get('exhibit_id', '')
        if orig and orig != curr:
            print(f"  {orig:35s} -> {curr}")
            count += 1
            if count >= 20:
                break


if __name__ == '__main__':
    main()
