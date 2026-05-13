#!/usr/bin/env python3
"""
Enrich evidence items with empty descriptions in the canonical index.

Strategy:
1. Try embed_text or appendix_text (first 200 chars)
2. Try caption_voice
3. Derive from meaningful title + category + key_people
4. Parse filename to create human-readable description
5. Combine category + title as fallback
"""

import json
import re
from pathlib import Path


def clean_filename_for_description(filename):
    """
    Parse filename to create human-readable description.

    Examples:
    - "A-1_001_Heavy Metals Test Results.pdf" → "Heavy metals test results"
    - "ExP_01_bruise-photographs.pdf" → "Bruise photographs"
    """
    # Remove extension
    base = Path(filename).stem

    # Remove exhibit prefix and numbers at the start
    # Pattern: "A-1_000_" or "ExP_01_" etc.
    base = re.sub(r'^[A-Za-z]+-?\d+_+\d+_+', '', base)

    # Remove any remaining leading numbers and underscores
    base = re.sub(r'^\d+_+', '', base)

    # Replace underscores and hyphens with spaces
    base = re.sub(r'[_-]+', ' ', base)

    # Remove "copy" suffix (case-insensitive)
    base = re.sub(r'\s+copy\s*$', '', base, flags=re.IGNORECASE)

    # Clean up extra spaces
    base = ' '.join(base.split())

    # Title case if it looks like it needs it
    if base and not any(c.isupper() for c in base[1:]):
        base = base.title()

    return base.strip()


def extract_description_from_title(title, category, key_people):
    """
    Derive description from title, category, and key_people.
    Only use if title is meaningful (not just a filename pattern).
    """
    if not title:
        return None

    # Check if title looks meaningful (contains actual words, not just numbers/patterns)
    meaningful_patterns = [
        r'\d{3,}',  # ID numbers
        r'^[a-z0-9_-]+$',  # All lowercase/numbers/special chars (filename-like)
    ]

    if re.match(r'^[\d_\-\.]+$', title):  # Only numbers/separators
        return None

    # If title is fairly short and contains actual words, it's meaningful
    if len(title) > 5 and not all(c.isdigit() or c in '_-.' for c in title):
        parts = [title]
        if category:
            parts.append(f"({category})")
        if key_people:
            parts.append(f"[{', '.join(key_people)}]")
        return ' '.join(parts)

    return None


def enrich_entry(entry):
    """
    Generate description for entry with empty description.
    Returns (success: bool, description: str, method: str)
    """
    description = entry.get('description', '').strip()

    # Skip if already has description
    if description:
        return False, description, 'existing'

    # Strategy 1: Use embed_text or appendix_text (first 200 chars)
    for field in ['embed_text', 'appendix_text']:
        text = entry.get(field, '').strip()
        if text:
            desc = text[:200].strip()
            # Only use if it's actually meaningful
            if len(desc) > 10 and not desc.startswith('CLIENT #'):
                return True, desc, field

    # Strategy 2: Use caption_voice
    caption = entry.get('caption_voice', '').strip()
    if caption:
        return True, caption, 'caption_voice'

    # Strategy 3: Derive from meaningful title + category + key_people
    title = entry.get('title', '').strip()
    category = entry.get('category', '').strip()
    key_people = entry.get('key_people', [])

    derived = extract_description_from_title(title, category, key_people)
    if derived:
        return True, derived, 'title_derived'

    # Strategy 4: Parse filename for human-readable description
    filename = entry.get('filename', '').strip()
    if filename:
        cleaned = clean_filename_for_description(filename)
        if cleaned:
            return True, cleaned, 'filename_parsed'

    # Strategy 5: Fallback - combine category + title
    if category:
        if title:
            desc = f"{category}: {title}"
        else:
            desc = category
        return True, desc, 'category_fallback'

    # Strategy 6: Just use title as last resort
    if title:
        return True, title, 'title_only'

    return False, '', 'no_source'


def main():
    index_path = Path('/sessions/gracious-awesome-newton/mnt/Claude/Blogs/ChappaquaPoison_v3/evidence_index_canonical.json')

    # Load the canonical index
    print(f"Loading index from {index_path}...")
    with open(index_path, 'r') as f:
        data = json.load(f)

    total_entries = len(data['entries'])
    print(f"Total entries in index: {total_entries}")

    # Track enrichment by method
    enrichment_stats = {
        'embed_text': 0,
        'appendix_text': 0,
        'caption_voice': 0,
        'title_derived': 0,
        'filename_parsed': 0,
        'category_fallback': 0,
        'title_only': 0,
        'no_source': 0,
        'existing': 0,
    }

    # Process entries
    enriched = 0
    unchanged = 0

    for i, entry in enumerate(data['entries']):
        success, description, method = enrich_entry(entry)

        if success and method != 'existing':
            entry['description'] = description
            enriched += 1
            enrichment_stats[method] += 1

            if i < 5 or enriched % 100 == 0:
                print(f"  [{i+1}] {method}: {description[:80]}")
        elif method == 'existing':
            unchanged += 1
            enrichment_stats['existing'] += 1
        else:
            enrichment_stats['no_source'] += 1

    # Write updated index
    print(f"\nWriting updated index...")
    with open(index_path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n" + "="*70)
    print("ENRICHMENT SUMMARY")
    print("="*70)
    print(f"Total entries processed: {total_entries}")
    print(f"Entries enriched: {enriched}")
    print(f"Entries already had descriptions: {unchanged}")

    print("\nEnrichment methods used:")
    for method, count in enrichment_stats.items():
        if count > 0:
            pct = (count / total_entries) * 100
            print(f"  {method:20s}: {count:4d} ({pct:5.1f}%)")

    print("\n" + "="*70)
    print(f"✓ Successfully updated {index_path}")


if __name__ == '__main__':
    main()
