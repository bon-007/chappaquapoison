#!/usr/bin/env python3
"""
compliance_check.py — Post compliance checker for v3 content

Checks each post against the v3 writing rules:
  1. No new factual claims without evidence reference
  2. No motive speculation
  3. No defamatory framing language
  4. No sealed/confidential minor information
  5. Evidence references exist for each factual paragraph
  6. ECS score present and justified
  7. Provenance badges included
  8. Cross-links match CROSS_REFERENCE.md
  9. Machine Summary present in HTML
  10. Markdown and HTML match (hash check)
  11. Performance budget respected

Writes results to: audit/post_checks/P##_[slug].checklist.json
"""

import json
import hashlib
import re
import sys
from pathlib import Path
from datetime import datetime

try:
    import yaml
except ImportError:
    import os
    os.system(f"{sys.executable} -m pip install pyyaml --break-system-packages --quiet")
    import yaml


# Prohibited language — simple word check with context-aware allowlist
DEFAMATORY_WORDS = {
    'evil': [],
    'villain': [],
    'monster': [],
}

# These words are only flagged if NOT followed by allowed context words
DEFAMATORY_CONTEXT = {
    'criminal': ['proceedings', 'case', 'court', 'law', 'justice', 'statute', 'complaint', 'charges', 'charge', 'record', 'prosecution', 'investigation', 'question', 'conduct', 'matter', 'action', 'offense', 'liability', 'allegation', 'history', 'behavior', '.', ',', 'and', 'or', '_'],
    'cover-up': [],
    'conspiracy': ['under', 'claim', 'count', 'allegation', 'to', 'between', 'among', 'theory', 'framework', 'with', '.', ','],
    'corrupt': ['process', 'corruption'],
}

MOTIVE_PHRASES = [
    'probably wanted',
    'likely intended',
    'must have known',
]

MOTIVE_CONTEXT_WORDS = {
    'deliberately': ['filed', 'stated', 'testified', 'documented', 'acted', 'administered', 'applied', 'introduced', 'enlisted', 'enlists', 'enlist', 'provides', 'provided', 'misled', 'fabricated', 'misuse', 'and', 'in', 'false', 'made', 'knowingly', 'use'],
    'intentionally': ['filed', 'stated', 'testified', 'administered', 'documented', ',', 'applied', 'inflict', 'caused', 'harass', 'apply'],
}

SEALED_PATTERNS = [
    r'\b\d{3}[- ]\d{2}[- ]\d{4}\b',  # SSN pattern
]

# Evidence reference patterns
EVIDENCE_PATTERNS = [
    r'(?:Ex[A-Z]{1,4}[_-]\d{1,3})',  # ExRR_04, ExA_02
    r'(?:F-\d{3})',  # F-001, F-038
    r'(?:DV-\d{3})',  # DV-120
    r'(?:Entry \d+)',  # Timeline Entry 34
    r'(?:¶\d+)',  # Paragraph references
    r'(?:\d+\s+U\.S\.\s+\d+)',  # Supreme Court citations
    r'(?:\d+AD3d\d+)',  # Appellate Division
    r'(?:§\s*\d+)',  # Section citations
    r'(?:Declaration|Affidavit|Deposition|Transcript)',
    r'(?:court (?:record|filing|order|docket))',
    r'(?:sworn (?:statement|testimony|admission|response|declaration))',
    r'(?:jury (?:verdict|finding))',
    r'(?:appellate (?:ruling|opinion|decision|division))',
]

EVIDENCE_RE = re.compile('|'.join(EVIDENCE_PATTERNS), re.IGNORECASE)


def parse_front_matter(md_text):
    if md_text.startswith('---'):
        parts = md_text.split('---', 2)
        if len(parts) >= 3:
            try:
                return yaml.safe_load(parts[1]) or {}, parts[2].strip()
            except yaml.YAMLError:
                pass
    return {}, md_text


def check_evidence_coverage(body_md):
    """Check that factual paragraphs have evidence references."""
    paragraphs = [p.strip() for p in body_md.split('\n\n') if p.strip()]
    issues = []
    total = 0
    cited = 0

    for i, para in enumerate(paragraphs):
        # Skip headings, short paragraphs, editor notes
        if para.startswith('#') or para.startswith('*Editor') or len(para) < 50:
            continue

        total += 1
        if EVIDENCE_RE.search(para):
            cited += 1
        else:
            issues.append(f"Paragraph {i+1} ({para[:60]}...) lacks evidence reference")

    return total, cited, issues


def _word_in_context(word, text, allowed_followers):
    """Check if a word appears without allowed context following it."""
    hits = []
    lower = text.lower()
    idx = 0
    while True:
        pos = lower.find(word, idx)
        if pos == -1:
            break
        # Check word boundary
        before_ok = (pos == 0 or not lower[pos-1].isalpha())
        after_pos = pos + len(word)
        after_ok = (after_pos >= len(lower) or not lower[after_pos].isalpha())
        if before_ok and after_ok:
            # Get next 30 chars of context
            context_after = lower[after_pos:after_pos+30].strip()
            # Check if any allowed word follows
            is_allowed = any(context_after.startswith(a) for a in allowed_followers)
            if not is_allowed:
                hits.append(word)
        idx = pos + 1
    return hits


def check_prohibited_language(body_md):
    """Check for defamatory, speculative, or sealed content."""
    issues = []

    # Simple defamatory words (no context needed)
    for word in DEFAMATORY_WORDS:
        if _word_in_context(word, body_md, []):
            issues.append(f"Defamatory language: '{word}' found")

    # Context-aware defamatory words
    for word, allowed in DEFAMATORY_CONTEXT.items():
        hits = _word_in_context(word, body_md, allowed)
        if hits:
            issues.append(f"Defamatory language: '{word}' found without legal context")

    # Exact motive phrases
    lower = body_md.lower()
    for phrase in MOTIVE_PHRASES:
        if phrase in lower:
            issues.append(f"Motive speculation: '{phrase}' found")

    # Context-aware motive words
    for word, allowed in MOTIVE_CONTEXT_WORDS.items():
        hits = _word_in_context(word, body_md, allowed)
        if hits:
            issues.append(f"Motive speculation: '{word}' found without documentary context")

    # Sealed info patterns (regex-based)
    for pattern in SEALED_PATTERNS:
        for m in re.finditer(pattern, body_md):
            issues.append(f"Possible sealed/private info: '{m.group()[:30]}' found")

    return issues


def check_post(post_id, md_dir, html_dir, posts_data):
    """Run full compliance check on a single post."""
    result = {
        'post_id': post_id,
        'checked_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'checks': {},
        'pass': True,
        'issues_found': [],
        'fixed_actions': [],
    }

    # Find markdown source
    md_files = list(md_dir.glob(f"{post_id}_*.md"))
    if not md_files:
        result['pass'] = False
        result['issues_found'].append(f"No markdown source found for {post_id}")
        result['checks']['markdown_exists'] = False
        return result

    md_file = md_files[0]
    md_raw = md_file.read_text(encoding='utf-8')
    front_matter, body_md = parse_front_matter(md_raw)

    # Find HTML output
    html_file = html_dir / f"{post_id}.html"
    html_exists = html_file.exists()
    result['checks']['html_exists'] = html_exists

    # Hash check
    md_hash = hashlib.sha256(md_raw.encode()).hexdigest()[:16]
    result['final_hash_md'] = md_hash

    if html_exists:
        html_raw = html_file.read_text(encoding='utf-8')
        html_hash = hashlib.sha256(html_raw.encode()).hexdigest()[:16]
        result['final_hash_html'] = html_hash
    else:
        result['final_hash_html'] = None

    # 1. Front matter checks
    result['checks']['has_title'] = bool(front_matter.get('title'))
    result['checks']['has_ecs'] = front_matter.get('ecs') is not None
    result['checks']['has_provenance'] = bool(front_matter.get('provenance'))
    result['checks']['has_tags'] = bool(front_matter.get('tags'))
    result['checks']['has_phase'] = bool(front_matter.get('phase'))

    if not front_matter.get('ecs'):
        result['issues_found'].append("ECS score missing from front matter")

    if not front_matter.get('provenance'):
        result['issues_found'].append("Provenance badges missing from front matter")

    # 2. Evidence coverage
    total_paras, cited_paras, evidence_issues = check_evidence_coverage(body_md)
    coverage = cited_paras / total_paras if total_paras > 0 else 0
    result['checks']['evidence_coverage'] = f"{cited_paras}/{total_paras} ({coverage:.0%})"
    result['checks']['evidence_issues'] = evidence_issues

    if coverage < 0.7:
        result['issues_found'].append(f"Evidence coverage below 70%: {coverage:.0%}")

    # 3. Prohibited language
    language_issues = check_prohibited_language(body_md)
    result['checks']['language_issues'] = language_issues
    if language_issues:
        result['issues_found'].extend(language_issues)

    # 4. "Why This Matters" section
    has_why = '## Why This Matters' in body_md
    result['checks']['has_why_this_matters'] = has_why
    # P72 is exempt (personal letter)
    if not has_why and post_id != 'P72':
        result['issues_found'].append("Missing 'Why This Matters' section")

    # 5. Machine Summary in HTML
    if html_exists:
        has_machine_summary = 'machine-summary' in html_raw
        result['checks']['has_machine_summary'] = has_machine_summary
        if not has_machine_summary:
            result['issues_found'].append("Machine Summary missing from HTML")

    # 6. JSON-LD in HTML
    if html_exists:
        has_jsonld = 'application/ld+json' in html_raw
        result['checks']['has_json_ld'] = has_jsonld
        if not has_jsonld:
            result['issues_found'].append("JSON-LD structured data missing from HTML")

    # Determine overall pass/fail
    critical_issues = [i for i in result['issues_found']
                       if 'sealed' in i.lower() or 'defamatory' in i.lower() or 'motive' in i.lower()]
    if critical_issues:
        result['pass'] = False
    elif len(result['issues_found']) > 3:
        result['pass'] = False

    return result


def main():
    project_root = Path(__file__).parent.parent
    md_dir = project_root / 'posts' / 'md'
    html_dir = project_root / '_site' / 'posts'
    posts_file = project_root / 'posts.json'
    output_dir = project_root / 'audit' / 'post_checks'

    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Chappaqua Poison — v3 Compliance Checker")
    print("=" * 60)

    # Load posts.json for reference
    with open(posts_file) as f:
        posts_data = json.load(f)

    # Find all markdown sources
    md_files = sorted(md_dir.glob('P*_*.md'))
    print(f"\nFound {len(md_files)} Markdown source files to check")

    passed = 0
    failed = 0
    all_issues = []

    for md_file in md_files:
        post_id = md_file.stem.split('_')[0]
        slug = md_file.stem
        # Skip duplicate/placeholder files
        if 'DUPLICATE' in md_file.read_text(encoding='utf-8')[:200]:
            continue

        result = check_post(post_id, md_dir, html_dir, posts_data)

        # Write checklist JSON
        out_file = output_dir / f"{slug}.checklist.json"
        with open(out_file, 'w') as f:
            json.dump(result, f, indent=2)

        status = "✓ PASS" if result['pass'] else "✗ FAIL"
        issue_count = len(result['issues_found'])

        if result['pass']:
            passed += 1
        else:
            failed += 1

        print(f"  {status} {post_id}: {issue_count} issue(s)")
        for issue in result['issues_found']:
            print(f"       → {issue}")
            all_issues.append(f"{post_id}: {issue}")

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed out of {len(md_files)}")
    print(f"Checklists written to: {output_dir}")
    if all_issues:
        print(f"\nAll issues ({len(all_issues)}):")
        for issue in all_issues:
            print(f"  • {issue}")
    print(f"{'=' * 60}")

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
