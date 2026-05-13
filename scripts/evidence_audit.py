#!/usr/bin/env python3
"""
evidence_audit.py — Comprehensive evidence index audit

Reads every post markdown, the v3_evidence_map.json, and evidence_metadata.json.
Produces a detailed report on:
1. What evidence each post references/needs
2. Quality of existing hero text excerpts (are they embeddable?)
3. Secondary text length violations (should be 1-3 sentences)
4. Missing/empty entries
5. Photo evidence that needs text descriptions
6. Tier assignment accuracy

⚠ DEPRECATED: This script's data has been absorbed into evidence_index_canonical.json.
To update evidence data, edit directly in canonical and re-run: python3 scripts/build_canonical_evidence_index.py
"""

import json
import re
import os
from pathlib import Path
from collections import defaultdict

V3_ROOT = Path(__file__).resolve().parent.parent
POSTS_MD = V3_ROOT / "posts" / "md"
EVIDENCE_DIR = V3_ROOT / "Evidence"

def load_json(path):
    with open(path) as f:
        return json.load(f)

def get_canonical_posts():
    """Get list of canonical post files (no _BOOK, _ORIGINAL, etc.)"""
    files = sorted(POSTS_MD.glob("B[0-9]*_*.md"))
    canonical = {}
    draft_pids = set()
    
    for f in files:
        name = f.stem
        # Skip variants
        if any(tag in name for tag in ['_BOOK', '_ORIGINAL', '_SUPERSEDED', '_PRE_']):
            continue
        if name.endswith('.bak') or name.endswith('.backup'):
            continue
        
        # Extract post ID
        match = re.match(r'(B\d+)', name)
        if not match:
            continue
        pid = match.group(1)
        
        # DRAFT takes priority
        if '_DRAFT' in name:
            canonical[pid] = f
            draft_pids.add(pid)
        elif pid not in canonical:
            canonical[pid] = f
    
    # Filter out hidden posts
    for hidden in ['B00', 'B50', 'B51']:
        canonical.pop(hidden, None)
    
    return canonical, draft_pids

def analyze_post_evidence_refs(text):
    """Find evidence references in post markdown"""
    refs = {
        'exhibit_refs': re.findall(r'Ex[A-Z]+[_-]\d+', text),
        'forensic_blocks': len(re.findall(r'<div class="forensic-block"', text)),
        'pull_quotes': len(re.findall(r'<blockquote|> \*\*"', text)),
        'message_exchanges': len(re.findall(r'class="(?:message|chat|imessage|text-bubble)', text)),
        'evidence_mentions': len(re.findall(r'(?:evidence|exhibit|document|deposition|transcript|declaration|affidavit)', text, re.I)),
        'photo_refs': len(re.findall(r'(?:photo|image|picture|screenshot)', text, re.I)),
    }
    return refs

def classify_hero_quality(item):
    """Classify quality of a hero evidence entry"""
    text = item.get('evidence_text', '')
    fname = item.get('filename', '')
    
    issues = []
    
    if not text or len(text.strip()) < 20:
        return 'EMPTY', issues
    
    # Check if it's raw OCR dump
    if re.search(r'[~\|]{3,}|_{5,}|\d{2,}\s+\d{2,}\s+\d{2,}', text):
        issues.append('RAW_OCR')
    
    # Check if it's a court filing header dump
    if re.search(r'SUPERIOR COURT|COUNTY OF|STATE BAR|FILED|DOCKET', text[:200]):
        issues.append('COURT_HEADER_DUMP')
    
    # Check if it's too long for embedding
    if len(text) > 2500:
        issues.append('TOO_LONG')
    
    # Check if it looks like a formatted pull quote
    is_formatted = bool(re.search(r'^["\'"]|^>\s|^—\s', text.strip()))
    
    # Check for message exchange format
    is_messages = bool(re.search(r'(?:AM|PM)\s|(?:sent|received):', text, re.I))
    
    if issues:
        return 'NEEDS_WORK', issues
    elif is_formatted or is_messages:
        return 'GOOD', issues
    else:
        return 'UNCURATED', ['needs_formatting']

def classify_evidence_type(item):
    """Determine evidence type: pull_quote, message_exchange, email, document, photo"""
    fname = item.get('filename', '').lower()
    text = item.get('evidence_text', '').lower()
    
    if any(ext in fname for ext in ['.jpg', '.jpeg', '.png', '.gif', '.heic']):
        return 'photo'
    if any(ext in fname for ext in ['.m4a', '.mp3', '.wav']):
        return 'audio'
    if 'ichat' in fname or 'imessage' in fname or 'signal' in fname:
        return 'message_exchange'
    if 'email' in fname or 'emlx' in fname:
        return 'email'
    if 'deposition' in fname or 'transcript' in fname:
        return 'deposition_transcript'
    if 'declaration' in fname or 'affidavit' in fname:
        return 'declaration'
    if 'blog' in fname or '.html' in fname:
        return 'blog_post'
    if any(x in fname for x in ['order', 'judgment', 'motion', 'petition', 'complaint']):
        return 'court_document'
    if '.pdf' in fname:
        return 'document_pdf'
    return 'other'

def main():
    print("=" * 80)
    print("EVIDENCE INDEX COMPREHENSIVE AUDIT")
    print("=" * 80)
    print()
    
    # Load data
    emap = load_json(V3_ROOT / "v3_evidence_map.json")
    emeta = load_json(V3_ROOT / "evidence_metadata.json")
    posts_data = load_json(V3_ROOT / "posts.json")
    posts_lookup = {p['id']: p for p in posts_data.get('posts', posts_data)}
    
    canonical, draft_pids = get_canonical_posts()
    
    # Evidence files inventory
    ev_files = set()
    photo_files = set()
    for root, dirs, files in os.walk(EVIDENCE_DIR):
        for f in files:
            if f.startswith('.'):
                continue
            fpath = os.path.join(root, f)
            ev_files.add(fpath)
            if any(f.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.heic']):
                photo_files.add(fpath)
    
    print(f"Evidence files on disk: {len(ev_files)}")
    print(f"  Photos: {len(photo_files)}")
    print(f"  evidence_metadata.json entries: {len(emeta)}")
    print(f"  v3_evidence_map.json posts: {len(emap)}")
    print(f"  Canonical posts: {len(canonical)}")
    print()
    
    # Per-post audit
    total_issues = defaultdict(int)
    post_reports = []
    
    for pid in sorted(canonical.keys(), key=lambda x: int(re.search(r'\d+', x).group())):
        post_file = canonical[pid]
        post_text = post_file.read_text(errors='replace')
        post_info = posts_lookup.get(pid, {})
        title = post_info.get('title', post_file.stem)
        word_count = len(post_text.split())
        
        # Evidence refs in post text
        ev_refs = analyze_post_evidence_refs(post_text)
        
        # Evidence map data
        map_entry = emap.get(pid, {})
        heroes = map_entry.get('hero', [])
        primaries = map_entry.get('primary', [])
        secondaries = map_entry.get('secondary', [])
        tertiaries = map_entry.get('tertiary', [])
        
        report = {
            'pid': pid,
            'title': title,
            'words': word_count,
            'is_draft': pid in draft_pids,
            'ev_refs': ev_refs,
            'hero_count': len(heroes),
            'primary_count': len(primaries),
            'secondary_count': len(secondaries),
            'tertiary_count': len(tertiaries),
            'issues': [],
        }
        
        # Audit hero entries
        hero_issues = []
        hero_types = defaultdict(int)
        for h in heroes:
            quality, qi = classify_hero_quality(h)
            etype = classify_evidence_type(h)
            hero_types[etype] += 1
            if quality != 'GOOD':
                hero_issues.append({
                    'filename': h.get('filename', '?')[:60],
                    'quality': quality,
                    'issues': qi,
                    'type': etype,
                    'text_len': len(h.get('evidence_text', '')),
                })
        
        report['hero_issues'] = hero_issues
        report['hero_types'] = dict(hero_types)
        
        # Audit secondary length
        sec_too_long = 0
        for s in secondaries:
            text = s.get('evidence_text', '')
            if len(text) > 500:  # ~3 sentences max
                sec_too_long += 1
        report['secondary_too_long'] = sec_too_long
        
        # Photo evidence check
        photo_heroes = sum(1 for h in heroes if classify_evidence_type(h) == 'photo')
        photo_primaries = sum(1 for p in primaries if classify_evidence_type(p) == 'photo')
        report['photo_heroes'] = photo_heroes
        report['photo_primaries'] = photo_primaries
        
        # Empty texts
        hero_empty = sum(1 for h in heroes if not h.get('evidence_text', '').strip())
        primary_empty = sum(1 for p in primaries if not p.get('evidence_text', '').strip())
        report['hero_empty'] = hero_empty
        report['primary_empty'] = primary_empty
        
        # Track global issues
        if hero_issues:
            total_issues['hero_needs_work'] += len(hero_issues)
        if sec_too_long:
            total_issues['secondary_too_long'] += sec_too_long
        if hero_empty:
            total_issues['hero_empty'] += hero_empty
        if primary_empty:
            total_issues['primary_empty'] += primary_empty
        if photo_heroes + photo_primaries > 0:
            total_issues['photos_needing_descriptions'] += photo_heroes + photo_primaries
        
        post_reports.append(report)
    
    # Print detailed report
    print("=" * 80)
    print("POST-BY-POST EVIDENCE AUDIT")
    print("=" * 80)
    
    for r in post_reports:
        pid = r['pid']
        print(f"\n{'─' * 70}")
        print(f"{pid}: {r['title']} ({r['words']} words){' [DRAFT]' if r['is_draft'] else ''}")
        print(f"  Tiers: H={r['hero_count']} P={r['primary_count']} S={r['secondary_count']} T={r['tertiary_count']}")
        print(f"  In-text refs: exhibits={len(r['ev_refs']['exhibit_refs'])} forensic_blocks={r['ev_refs']['forensic_blocks']} pull_quotes={r['ev_refs']['pull_quotes']} messages={r['ev_refs']['message_exchanges']}")
        
        if r['hero_types']:
            types_str = ", ".join(f"{k}={v}" for k,v in sorted(r['hero_types'].items()))
            print(f"  Hero types: {types_str}")
        
        issues = []
        if r['hero_empty']:
            issues.append(f"hero_empty={r['hero_empty']}")
        if r['primary_empty']:
            issues.append(f"primary_empty={r['primary_empty']}")
        if r['secondary_too_long']:
            issues.append(f"secondary_too_long={r['secondary_too_long']}")
        if r['photo_heroes'] + r['photo_primaries']:
            issues.append(f"photos_need_desc={r['photo_heroes']+r['photo_primaries']}")
        
        if r['hero_issues']:
            issues.append(f"hero_needs_work={len(r['hero_issues'])}")
            for hi in r['hero_issues'][:3]:
                print(f"    HERO ISSUE: {hi['filename']} [{hi['quality']}] {hi['issues']} type={hi['type']} len={hi['text_len']}")
        
        if issues:
            print(f"  ⚠ ISSUES: {', '.join(issues)}")
        else:
            print(f"  ✓ No major issues")
    
    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    print(f"Posts audited: {len(post_reports)}")
    print(f"Total evidence items: {sum(r['hero_count']+r['primary_count']+r['secondary_count']+r['tertiary_count'] for r in post_reports)}")
    print()
    print("Issues found:")
    for issue, count in sorted(total_issues.items()):
        print(f"  {issue}: {count}")
    
    print()
    print("Hero quality breakdown:")
    all_hero_qualities = defaultdict(int)
    for r in post_reports:
        for hi in r.get('hero_issues', []):
            all_hero_qualities[hi['quality']] += 1
    good_heroes = sum(r['hero_count'] for r in post_reports) - sum(all_hero_qualities.values())
    print(f"  GOOD (embeddable): {good_heroes}")
    for q, c in sorted(all_hero_qualities.items()):
        print(f"  {q}: {c}")

if __name__ == "__main__":
    main()
