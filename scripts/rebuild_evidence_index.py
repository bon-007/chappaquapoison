#!/usr/bin/env python3
"""
rebuild_evidence_index.py — Rebuild v3_evidence_map from post frontmatter specs

Strategy:
1. Read each post's frontmatter evidence spec (the authoritative source)
2. For each named exhibit, find the best matching file from the existing evidence map
3. For hero items, extract and format the text for direct embedding
4. For primary, extract large excerpts for appendix
5. For secondary, trim to 1-3 sentences
6. For tertiary (from existing map), keep as citation-only
7. For photos, add text descriptions
8. Write v3_evidence_map_v2.json

Evidence text formatting guidelines per tier:
- HERO pull_quote: 1-3 sentences, formatted with attribution
- HERO message_exchange: 2-10 message bubbles with sender/time
- HERO email/note: 1-3 key paragraphs
- HERO document: 1-5 paragraphs or up to 5 excerpts
- HERO photo: [PHOTO] description of content, time, place
- PRIMARY: Full excerpt for appendix (up to ~2000 chars)
- SECONDARY: 1-3 sentences max (~50-200 chars)
- TERTIARY: Citation reference only (title + source)

⚠ DEPRECATED: This script is superseded by build_canonical_evidence_index.py.
The canonical index now contains all evidence metadata and relationships.
To update evidence data, edit directly in evidence_index_canonical.json and re-run:
python3 scripts/build_canonical_evidence_index.py
"""

import yaml
import re
import json
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher

V3_ROOT = Path("/Users/s/Claude/Blogs/ChappaquaPoison_v3")
POSTS_MD = V3_ROOT / "posts" / "md"
EVIDENCE_DIR = V3_ROOT / "Evidence"


def get_canonical_posts():
    files = sorted(POSTS_MD.glob("B[0-9]*_*.md"))
    canonical = {}
    for f in files:
        name = f.stem
        if any(tag in name for tag in ['_BOOK', '_ORIGINAL', '_SUPERSEDED', '_PRE_']):
            continue
        if name.endswith('.bak') or name.endswith('.backup'):
            continue
        match = re.match(r'(B\d+)', name)
        if not match:
            continue
        pid = match.group(1)
        if '_DRAFT' in name:
            canonical[pid] = f
        elif pid not in canonical:
            canonical[pid] = f
    for hidden in ['B00', 'B50', 'B51']:
        canonical.pop(hidden, None)
    return canonical


def extract_frontmatter(filepath):
    text = filepath.read_text(errors='replace')
    match = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
    if match:
        return yaml.safe_load(match.group(1))
    return {}


def classify_exhibit_type(exhibit_name):
    """Classify what kind of evidence an exhibit is based on its description"""
    name_lower = exhibit_name.lower()
    
    if any(w in name_lower for w in ['photo', 'photograph', 'image', 'picture', 'headshot']):
        return 'photo'
    if any(w in name_lower for w in ['text message', 'chat.db', 'imessage', 'message exchange', 'text —']):
        return 'message_exchange'
    if any(w in name_lower for w in ['audio', 'recording', 'voicemail']):
        return 'audio'
    if any(w in name_lower for w in ['video']):
        return 'video'
    if any(w in name_lower for w in ['deposition', 'transcript']):
        return 'deposition'
    if any(w in name_lower for w in ['declaration', 'affidavit', 'sworn']):
        return 'declaration'
    if any(w in name_lower for w in ['email', 'letter', 'correspondence']):
        return 'email'
    if any(w in name_lower for w in ['blog', 'sle', 'stevieloves']):
        return 'blog_post'
    if any(w in name_lower for w in ['order', 'judgment', 'verdict', 'motion', 'complaint', 'decision', 'court']):
        return 'court_document'
    if any(w in name_lower for w in ['lab', 'medical', 'hospital', 'toxicology', 'test']):
        return 'medical'
    if any(w in name_lower for w in ['author account', 'author memory']):
        return 'author_account'
    return 'document'


def find_best_match(exhibit_name, emap_items, pid):
    """Find the best matching evidence map item for a named exhibit"""
    exhibit_lower = exhibit_name.lower()
    
    # Extract key terms from exhibit name
    key_terms = set(re.findall(r'\b\w{3,}\b', exhibit_lower))
    # Remove common words
    key_terms -= {'the', 'and', 'for', 'from', 'with', 'that', 'this', 'author', 'account'}
    
    best_match = None
    best_score = 0
    
    for item in emap_items:
        fname = item.get('filename', '').lower()
        reason = item.get('reason', '').lower()
        text = item.get('evidence_text', '').lower()[:500]
        
        # Compute relevance score
        score = 0
        combined = f"{fname} {reason} {text}"
        
        for term in key_terms:
            if term in combined:
                score += 1
        
        # Bonus for filename match
        if any(term in fname for term in key_terms if len(term) > 4):
            score += 2
        
        # Bonus for reason mentioning key terms
        if any(term in reason for term in key_terms if len(term) > 4):
            score += 1
        
        if score > best_score:
            best_score = score
            best_match = item
    
    return best_match, best_score


def format_hero_text(item, exhibit_name, exhibit_type):
    """Format hero evidence text for direct embedding"""
    raw_text = item.get('evidence_text', '').strip() if item else ''
    fname = item.get('filename', '') if item else ''
    
    if not raw_text or raw_text == '[File not located on disk]':
        return {
            'status': 'NEEDS_EXTRACTION',
            'embed_text': f'[{exhibit_type.upper()}] {exhibit_name}',
            'raw_available': False,
        }
    
    # Clean OCR artifacts
    cleaned = raw_text
    # Remove court header junk
    cleaned = re.sub(r'^\d+\s+SUPERIOR COURT.*?(?=\w{4,})', '', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'~[^\n]+', '', cleaned)  # OCR artifacts
    cleaned = re.sub(r'\s{3,}', ' ', cleaned)  # Multiple spaces
    cleaned = cleaned.strip()
    
    if exhibit_type == 'photo':
        return {
            'status': 'NEEDS_DESCRIPTION',
            'embed_text': f'[PHOTO] {exhibit_name}',
            'embed_format': 'photo_description',
            'raw_available': bool(raw_text),
        }
    
    if exhibit_type == 'audio':
        return {
            'status': 'OK' if cleaned else 'NEEDS_TRANSCRIPTION',
            'embed_text': cleaned if cleaned else f'[AUDIO] {exhibit_name}',
            'embed_format': 'audio_description',
            'raw_available': bool(raw_text),
        }
    
    if exhibit_type == 'message_exchange':
        # Try to format as message bubbles
        # Keep first ~1500 chars of message content
        if len(cleaned) > 1500:
            # Try to cut at a message boundary
            cut_point = cleaned[:1500].rfind('\n')
            if cut_point > 500:
                cleaned = cleaned[:cut_point]
        return {
            'status': 'OK',
            'embed_text': cleaned,
            'embed_format': 'message_exchange',
            'raw_available': True,
        }
    
    if exhibit_type == 'deposition':
        # Extract the most relevant testimony excerpt
        if len(cleaned) > 1500:
            cleaned = cleaned[:1500]
            # Cut at a sentence boundary
            last_period = cleaned.rfind('.')
            if last_period > 500:
                cleaned = cleaned[:last_period + 1]
        return {
            'status': 'NEEDS_CURATION',
            'embed_text': cleaned,
            'embed_format': 'pull_quote',
            'raw_available': True,
        }
    
    if exhibit_type in ['declaration', 'court_document']:
        if len(cleaned) > 2000:
            cleaned = cleaned[:2000]
            last_period = cleaned.rfind('.')
            if last_period > 500:
                cleaned = cleaned[:last_period + 1]
        return {
            'status': 'NEEDS_CURATION',
            'embed_text': cleaned,
            'embed_format': 'document_excerpt',
            'raw_available': True,
        }
    
    if exhibit_type == 'author_account':
        return {
            'status': 'NEEDS_WRITING',
            'embed_text': f'[AUTHOR ACCOUNT] {exhibit_name}',
            'embed_format': 'narrative',
            'raw_available': False,
        }
    
    # Default: use cleaned text, trim if too long
    if len(cleaned) > 2000:
        cleaned = cleaned[:2000]
        last_period = cleaned.rfind('.')
        if last_period > 500:
            cleaned = cleaned[:last_period + 1]
    
    return {
        'status': 'OK' if len(cleaned) > 50 else 'NEEDS_EXTRACTION',
        'embed_text': cleaned if cleaned else f'[{exhibit_type.upper()}] {exhibit_name}',
        'embed_format': 'pull_quote' if len(cleaned) < 500 else 'document_excerpt',
        'raw_available': bool(raw_text),
    }


def format_primary_text(item, exhibit_name):
    """Format primary evidence for appendix excerpt"""
    if not item:
        return {
            'status': 'NEEDS_EXTRACTION',
            'appendix_text': f'{exhibit_name}',
        }
    
    raw_text = item.get('evidence_text', '').strip()
    if not raw_text:
        return {
            'status': 'NEEDS_EXTRACTION',
            'appendix_text': f'{exhibit_name}',
            'filename': item.get('filename', ''),
        }
    
    # Clean and keep up to 3000 chars for appendix
    cleaned = re.sub(r'\s{3,}', ' ', raw_text).strip()
    if len(cleaned) > 3000:
        cleaned = cleaned[:3000]
        last_period = cleaned.rfind('.')
        if last_period > 1000:
            cleaned = cleaned[:last_period + 1]
    
    return {
        'status': 'OK',
        'appendix_text': cleaned,
        'filename': item.get('filename', ''),
    }


def format_secondary_text(item, exhibit_name):
    """Format secondary evidence — 1-3 sentences max"""
    if not item:
        return {
            'status': 'NEEDS_EXTRACTION',
            'appendix_text': exhibit_name,
        }
    
    raw_text = item.get('evidence_text', '').strip()
    reason = item.get('reason', '').strip()
    
    # For secondary, we want 1-3 sentences
    # Prefer the reason field (usually a good summary) over raw text
    if reason and 20 < len(reason) < 300:
        text = reason
    elif raw_text:
        text = raw_text
        # Trim to ~3 sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        if len(sentences) > 3:
            text = ' '.join(sentences[:3])
        if len(text) > 300:
            text = text[:300]
            last_period = text.rfind('.')
            if last_period > 50:
                text = text[:last_period + 1]
    else:
        text = exhibit_name
    
    return {
        'status': 'OK' if len(text) > 20 else 'NEEDS_WRITING',
        'appendix_text': text,
        'filename': item.get('filename', '') if item else '',
    }


def main():
    canonical = get_canonical_posts()
    
    with open(V3_ROOT / "v3_evidence_map.json") as f:
        emap = json.load(f)
    
    with open(V3_ROOT / "evidence_spec_from_posts.json") as f:
        specs = json.load(f)
    
    rebuilt = {}
    stats = defaultdict(int)
    
    for pid in sorted(specs.keys(), key=lambda x: int(re.search(r'\d+', x).group())):
        spec = specs[pid]
        title = spec['title']
        provenance = spec['provenance']
        
        # Get existing map data for this post
        existing = emap.get(pid, {})
        all_existing = []
        for tier in ['hero', 'primary', 'secondary', 'tertiary']:
            all_existing.extend(existing.get(tier, []))
        
        entry = {
            'title': title,
            'provenance': provenance,
            'hero': [],
            'primary': [],
            'secondary': [],
            'tertiary': [],
        }
        
        # Process HERO exhibits from spec
        for exhibit_name in spec.get('hero', []):
            exhibit_type = classify_exhibit_type(exhibit_name)
            
            # Find best match from existing hero items first, then all items
            hero_items = existing.get('hero', [])
            match, score = find_best_match(exhibit_name, hero_items, pid)
            
            if score < 2:
                match2, score2 = find_best_match(exhibit_name, all_existing, pid)
                if score2 > score:
                    match, score = match2, score2
            
            formatted = format_hero_text(match, exhibit_name, exhibit_type)
            
            hero_entry = {
                'exhibit_name': exhibit_name,
                'exhibit_type': exhibit_type,
                'embed_format': formatted.get('embed_format', 'unknown'),
                'embed_text': formatted['embed_text'],
                'status': formatted['status'],
                'matched_file': match.get('filename', '') if match else '',
                'match_score': score,
                'file_location': match.get('file_location', '') if match else '',
            }
            entry['hero'].append(hero_entry)
            stats[f'hero_{formatted["status"]}'] += 1
        
        # Process PRIMARY exhibits from spec
        for exhibit_name in spec.get('primary', []):
            match, score = find_best_match(exhibit_name, existing.get('primary', []), pid)
            if score < 2:
                match2, score2 = find_best_match(exhibit_name, all_existing, pid)
                if score2 > score:
                    match, score = match2, score2
            
            formatted = format_primary_text(match, exhibit_name)
            
            primary_entry = {
                'exhibit_name': exhibit_name,
                'appendix_text': formatted['appendix_text'],
                'status': formatted['status'],
                'matched_file': formatted.get('filename', match.get('filename', '') if match else ''),
                'match_score': score,
            }
            entry['primary'].append(primary_entry)
            stats[f'primary_{formatted["status"]}'] += 1
        
        # Process SECONDARY exhibits from spec
        for exhibit_name in spec.get('secondary', []):
            match, score = find_best_match(exhibit_name, existing.get('secondary', []), pid)
            if score < 2:
                match2, score2 = find_best_match(exhibit_name, all_existing, pid)
                if score2 > score:
                    match, score = match2, score2
            
            formatted = format_secondary_text(match, exhibit_name)
            
            secondary_entry = {
                'exhibit_name': exhibit_name,
                'appendix_text': formatted['appendix_text'],
                'status': formatted['status'],
                'matched_file': formatted.get('filename', match.get('filename', '') if match else ''),
                'match_score': score,
            }
            entry['secondary'].append(secondary_entry)
            stats[f'secondary_{formatted["status"]}'] += 1
        
        # Carry over TERTIARY from existing map (citation-only)
        for item in existing.get('tertiary', []):
            tertiary_entry = {
                'filename': item.get('filename', ''),
                'reason': item.get('reason', '')[:200],
                'file_location': item.get('file_location', ''),
            }
            entry['tertiary'].append(tertiary_entry)
            stats['tertiary_carried'] += 1
        
        rebuilt[pid] = entry
    
    # Write rebuilt index
    output_path = V3_ROOT / "v3_evidence_map_v2.json"
    with open(output_path, 'w') as f:
        json.dump(rebuilt, f, indent=2, ensure_ascii=False)
    
    print(f"Wrote {output_path}")
    print(f"\nPosts: {len(rebuilt)}")
    print(f"\nStats:")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")
    
    # Summary of items needing work
    print(f"\n{'='*60}")
    print("ITEMS NEEDING ATTENTION:")
    for pid in sorted(rebuilt.keys(), key=lambda x: int(re.search(r'\d+', x).group())):
        entry = rebuilt[pid]
        needs = []
        for tier in ['hero', 'primary', 'secondary']:
            for item in entry[tier]:
                status = item.get('status', '')
                if status not in ['OK']:
                    needs.append(f"{tier}:{item['exhibit_name'][:40]}={status}")
        if needs:
            print(f"\n{pid} ({entry['title']}):")
            for n in needs:
                print(f"  • {n}")


if __name__ == "__main__":
    main()
