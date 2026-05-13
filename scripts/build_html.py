#!/usr/bin/env python3
"""
build_html.py — Generate static HTML files from templates and posts

Generates:
  1. _site/posts/*.html — One file per post (using post.html template)
  2. _site/index.html — Homepage (using index.html template)
  3. _site/{about,how-to-read,methodology,etc}.html — Static pages (using base.html)
  4. _site/tags/{tag-slug}.html — Tag pages (using tag.html template)

Maps phase → color from tokens.json
Resolves banner PNG paths from /images/banners/v3/
Builds prev/next navigation chain
Generates canonical URLs for all pages
"""

import json
import os
import sys
import re
from datetime import datetime, timedelta
import hashlib
import shutil
from pathlib import Path
from datetime import datetime

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError:
    print("Jinja2 not found. Installing...")
    os.system(f"{sys.executable} -m pip install jinja2 --break-system-packages --quiet")
    from jinja2 import Environment, FileSystemLoader, select_autoescape

try:
    import markdown
except ImportError:
    os.system(f"{sys.executable} -m pip install markdown --break-system-packages --quiet")
    import markdown

try:
    import yaml
except ImportError:
    os.system(f"{sys.executable} -m pip install pyyaml --break-system-packages --quiet")
    import yaml

# Site configuration — override with SITE_URL env var for staging/dev
SITE_URL = os.environ.get("SITE_URL", "https://chappaquapoison.com")

# Static page ID to filename mapping
STATIC_PAGES_MAP = {
    'S-1': 'index.html',
    'S-2': 'about.html',
    'S-3': 'how-to-read.html',
    'S-4': 'methodology.html',
    'S-5': 'timeline.html',
    'S-6': 'evidence.html',
    # S-7 (people), S-8 (cases), S-9 (patterns) — removed: no dedicated templates
    'S-10': 'falsifiability.html',
    'S-11': 'public-record-notice.html',
    # S-12 (audit-log), S-13 (ten-documents), S-14 (public-record-inventory) — removed: no dedicated templates
    'S-15': 'search.html',
    'S-16': 'timeline-guide.html',
    'S-17': 'characters.html',
    'S-18': 'legal.html',
    'S-19': 'book.html',
}

def load_json_file(filepath):
    """Load JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def load_posts(posts_file):
    """Load posts from posts.json"""
    data = load_json_file(posts_file)
    return data.get('posts', [])

def load_static_pages(posts_file):
    """Load static pages metadata from posts.json"""
    data = load_json_file(posts_file)
    return data.get('static_pages', [])

def load_tokens(tokens_file):
    """Load design tokens"""
    return load_json_file(tokens_file)

def get_phase_color(phase, tokens):
    """Get hex color for a phase from tokens"""
    phase_key = f"phase-{phase.lower()}"
    phases = tokens.get('palette', {}).get('phase', {})
    for key, config in phases.items():
        if key == phase:
            return config.get('hex', '#A69070')
    return '#A69070'  # Default fallback

def parse_sort_date(date_context, post_index=0):
    """Parse date_context string into ISO sortable date string (YYYY-MM-DD).
    Replicates and extends logic from generate_feed.py's parse_date_context."""
    if not date_context or not isinstance(date_context, str):
        return '1900-01-01'

    # Strip parenthetical annotations
    dc = re.sub(r'\s*\([^)]*\)', '', date_context)
    dc = dc.strip().lstrip('~')

    # Remove "– ongoing" / "– present" and trailing "+"
    dc = re.sub(r'\s*[–-]\s*(ongoing|present)\b', '', dc, flags=re.IGNORECASE)
    dc = re.sub(r'\+$', '', dc).strip()

    # Exact date formats (try first on full string)
    for fmt in ['%B %d, %Y', '%b %d, %Y', '%B %Y', '%b %Y', '%m/%d/%Y']:
        try:
            dt = datetime.strptime(dc, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue

    # Month Day – Month Day, Year: "July 29 – August 16, 2019"
    m = re.match(r'(\w+)\s+(\d{1,2})\s*[–-]\s*(\w+)\s+(\d{1,2}),?\s*(\d{4})', dc)
    if m:
        try:
            dt = datetime.strptime(f"{m.group(3)} {m.group(4)}, {m.group(5)}", '%B %d, %Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass

    # Month Year – Month Year: "November 2018 – January 2019", "December 2025 – February 2026"
    m = re.match(r'(\w+)\s+(\d{4})\s*[–-]\s*(\w+)\s+(\d{4})', dc)
    if m:
        try:
            dt = datetime.strptime(f"{m.group(3)} {m.group(4)}", '%B %Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass

    # Month–Month Year: "March-April 2020"
    m = re.match(r'(\w+)\s*[–-]\s*(\w+)\s+(\d{4})', dc)
    if m:
        try:
            dt = datetime.strptime(f"{m.group(2)} {m.group(3)}", '%B %Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass

    # Day ranges: "February 8–10, 2019", "April 3–6, 2019"
    m = re.match(r'(\w+)\s+(\d{1,2})\s*[–-]\s*(\d{1,2}),?\s*(\d{4})', dc)
    if m:
        try:
            dt = datetime.strptime(f"{m.group(1)} {m.group(3)}, {m.group(4)}", '%B %d, %Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass

    # Year–Year ranges: "1993–2015", "2020–2026"
    # Use Jan 1 of end year so specific dates in that year sort above ranges
    m = re.match(r'(\d{4})\s*[–-]\s*(\d{4})', dc)
    if m:
        return f"{m.group(2)}-01-01"

    # Year alone — treat as Jan 1 so specific months sort above it
    m = re.match(r'^(\d{4})$', dc.strip())
    if m:
        return f"{m.group(1)}-01-01"

    # Season + year
    m = re.match(r'(Spring|Summer|Fall|Winter|Late|Early)\s+(\d{4})', dc, re.IGNORECASE)
    if m:
        season_months = {'spring': '04', 'summer': '07', 'fall': '10', 'winter': '01', 'early': '03', 'late': '10'}
        month = season_months.get(m.group(1).lower(), '06')
        return f"{m.group(2)}-{month}-15"

    # Decade–Year: "1990s–2015"
    m = re.match(r'(\d{3})0s\s*[–-]\s*(\d{4})', dc)
    if m:
        return f"{m.group(2)}-01-01"

    # Decades: "1990s"
    m = re.match(r'(\d{3})0s', dc)
    if m:
        return f"{int(m.group(1)) * 10 + 5}-01-01"

    # Pre-YYYY
    m = re.match(r'Pre-(\d{4})', dc)
    if m:
        return f"{int(m.group(1)) - 1}-12-31"

    return '1900-01-01'


def get_phase_info(phase, tokens):
    """Get phase name and color"""
    phases = tokens.get('palette', {}).get('phase', {})
    phase_data = phases.get(phase, {})
    return {
        'color': phase_data.get('hex', '#A69070'),
        'name': phase_data.get('name', f'Act {phase}'),
    }

def resolve_banner_png(post_id, banners_dir, base_path='..'):
    """
    Resolve banner PNG path for a post.
    All banners are illustrated PNGs in banners/v3/.

    Supports v3 (B-prefix) post IDs:
    - B02 -> /images/banners/v3/banner_B02_banner.png

    base_path controls the relative prefix:
    - '..' for post pages (_site/posts/B02.html -> ../images/banners/v3/...)
    - '.' for homepage/tag pages (_site/index.html -> ./images/banners/v3/...)

    Returns path like ../images/banners/v3/banner_B02_banner.png or None if not found.
    """
    if not banners_dir.exists():
        return None

    v3_dir = banners_dir / 'v3'

    # v3 beat IDs (B01, B02, B47a, B47b, etc.)
    beat_match = re.match(r'B(\d+[a-z]?)', post_id)
    if beat_match:
        beat_id = beat_match.group(1)
        # Zero-pad pure numeric IDs (B1 -> B01), preserve alpha suffix (47a stays 47a)
        if beat_id.isdigit():
            beat_id = beat_id.zfill(2)
        else:
            # e.g. "47a" -> zero-pad the numeric prefix: "47a"
            num_part = re.match(r'(\d+)', beat_id).group(1).zfill(2)
            beat_id = num_part + beat_id[len(re.match(r'(\d+)', beat_id).group(1)):]
        fname = f"banner_B{beat_id}_banner.png"
        if v3_dir.exists() and (v3_dir / fname).exists():
            return f"{base_path}/images/banners/v3/{fname}"
        return None

    # Not found
    return None

def build_post_nav_chain(posts):
    """Build previous/next navigation for each post"""
    nav_map = {}
    for i, post in enumerate(posts):
        nav_map[post['id']] = {
            'prev': posts[i - 1] if i > 0 else None,
            'next': posts[i + 1] if i < len(posts) - 1 else None,
        }
    return nav_map

def get_related_posts(post, all_posts, limit=3):
    """Find related posts by tag and phase"""
    post_tags = set(post.get('tags', []))
    post_phase = post.get('phase')

    candidates = []
    for p in all_posts:
        if p['id'] == post['id']:
            continue

        # Phase match
        if p.get('phase') == post_phase:
            candidates.append((p, 2))  # Higher weight

        # Tag match
        p_tags = set(p.get('tags', []))
        common_tags = len(post_tags & p_tags)
        if common_tags > 0:
            candidates.append((p, 1 + common_tags * 0.5))

    # Deduplicate and sort by score
    seen = set()
    unique = []
    for p, score in candidates:
        if p['id'] not in seen:
            unique.append((p, score))
            seen.add(p['id'])

    unique.sort(key=lambda x: x[1], reverse=True)
    return [p for p, _ in unique[:limit]]

def group_posts_by_phase(posts, tokens):
    """Group posts by phase for homepage"""
    phase_order = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']
    grouped = {phase: [] for phase in phase_order}

    for post in posts:
        phase = post.get('phase', 'I')
        if phase in grouped:
            grouped[phase].append(post)

    # Convert to list with phase info
    result = []
    for phase in phase_order:
        if grouped[phase]:
            phase_info = get_phase_info(phase, tokens)
            result.append({
                'phase': phase,
                'name': phase_info['name'],
                'color': phase_info['color'],
                'posts': grouped[phase],
                'description': _get_phase_description(phase),
            })

    return result

def _get_phase_description(phase):
    """Get narrative description for phase"""
    descriptions = {
        'I': 'Russell\'s background and the Walsh family context before litigation.',
        'II': 'Russell meets Tara Walsh in 2015; the relationship begins.',
        'III': 'The alleged criminal events and immediate aftermath.',
        'IV': 'Tara Walsh leaves California and the custody dispute begins.',
        'V': 'Alleged cover-up actions and suppression of evidence.',
        'VI': 'Court-imposed gag orders and speech restrictions.',
        'VII': 'The jury trial and verdict.',
        'VIII': 'Civil rights litigation and constitutional claims.',
        'IX': 'The archive and the silence that remains.',
    }
    return descriptions.get(phase, f'Phase {phase}')

def _get_phase_date_range(phase):
    """Get date range for phase"""
    ranges = {
        'I': '1990s–2015',
        'II': '2015–2017',
        'III': '2017–2018',
        'IV': '2018–2019',
        'V': '2019–2020',
        'VI': '2020–2022',
        'VII': '2022–2023',
        'VIII': '2023–2024',
        'IX': '2024–2026',
    }
    return ranges.get(phase, '–')

def get_all_tags(posts):
    """Collect all unique tags and their counts, returns list of (tag, count, slug) tuples"""
    tag_counts = {}
    for post in posts:
        for tag in post.get('tags', []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Convert to list of tuples with slug
    tags_list = []
    for tag, count in sorted(tag_counts.items()):
        slug = tag.lower().replace(' ', '-').replace('/', '-')
        tags_list.append((tag, count, slug))

    return tags_list

def get_posts_by_tag(tag, posts):
    """Get all posts that have a specific tag"""
    return [p for p in posts if tag in p.get('tags', [])]

def tag_to_slug(tag):
    """Convert tag name to URL slug"""
    return tag.lower().replace(' ', '-').replace('/', '-')

def parse_front_matter(md_text):
    """Parse YAML front matter from Markdown file, return (metadata, body)"""
    if md_text.startswith('---'):
        parts = md_text.split('---', 2)
        if len(parts) >= 3:
            try:
                metadata = yaml.safe_load(parts[1])
                body = parts[2].strip()
                return metadata or {}, body
            except yaml.YAMLError:
                pass
    return {}, md_text


def load_markdown_content(post_id, md_dir):
    """
    Load expanded Markdown content for a post if it exists.

    Searches posts/md/ for files matching P##_*.md or B##_*.md pattern.
    Returns (front_matter, body_html, body_md, why_this_matters_html) or None.
    """
    if not md_dir.exists():
        return None

    # Find matching file — priority: _DRAFT > canonical > skip _BOOK/_ORIGINAL/_SUPERSEDED/.bak
    all_candidates = (
        list(md_dir.glob(f"{post_id}_*.md")) +
        list(md_dir.glob(f"{post_id.upper()}_*.md")) +
        [md_dir / f"{post_id}.md"]
    )
    # Filter out legacy/book variants
    skip_suffixes = ('_BOOK.md', '_ORIGINAL.md', '_SUPERSEDED.md', '_PRE_BORA_BORA.md', '.md.bak')
    filtered = [f for f in all_candidates if f.exists() and not any(str(f).endswith(s) for s in skip_suffixes)]
    # Sort: _DRAFT files first, then canonical
    candidates = sorted(filtered, key=lambda f: (0 if '_DRAFT' in f.name else 1, f.name))
    for md_file in candidates:
        if not md_file.exists():
            continue
        raw = md_file.read_text(encoding='utf-8')
        front_matter, body_md = parse_front_matter(raw)

        # Split body into main content and "Why This Matters" section
        why_section = ''
        why_md = ''
        main_md = body_md

        why_match = re.split(r'^## Why This Matters\s*$', body_md, flags=re.MULTILINE)
        if len(why_match) == 2:
            main_md = why_match[0].strip()
            why_md = why_match[1].strip()
            why_section = markdown.markdown(why_md, extensions=['smarty'])

        body_html = markdown.markdown(main_md, extensions=['smarty'])

        return {
            'front_matter': front_matter,
            'body_html': body_html,
            'body_md': body_md,
            'main_md': main_md,
            'why_html': why_section,
            'md_hash': hashlib.sha256(raw.encode()).hexdigest()[:16],
            'source_path': str(md_file),
            'provenance': front_matter.get('provenance', []),
        }

    return None


def render_post_html(post, template_env, all_posts, tokens, banners_dir, nav_map, md_dir=None, evidence_registry=None, v3_evidence_map=None, canonical_by_eid=None):
    """Render a single post to HTML"""
    standard_phases = {'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX'}
    post_phase = post.get('phase', 'I')
    phase_info = get_phase_info(post_phase, tokens)
    banner_image = resolve_banner_png(post.get('id'), banners_dir)

    # Set phase_name for template rendering
    if post_phase in standard_phases:
        post['phase_name'] = phase_info['name']
        post['phase_display'] = f"Act {post_phase} — {phase_info['name']}"
    else:
        # Special posts (Preface, Afterword, Back Cover, etc.)
        post['phase_name'] = post.get('act_name', post_phase)
        post['phase_display'] = post.get('act_name', post_phase)

    prev_post = nav_map[post['id']].get('prev')
    next_post = nav_map[post['id']].get('next')

    # Use curated cross_links from posts.json if available, fallback to dynamic
    cross_link_ids = post.get('cross_links', [])
    if cross_link_ids:
        # Build lookup dict
        posts_by_id = {p['id']: p for p in all_posts}
        related = [posts_by_id[cid] for cid in cross_link_ids if cid in posts_by_id][:6]
    else:
        related = get_related_posts(post, all_posts)

    # Add phase color to related posts
    for rel in related:
        rel['phase_color'] = get_phase_info(rel.get('phase', 'I'), tokens)['color']

    template = template_env.get_template('post.html')

    # Load expanded Markdown content if available, fallback to summary
    md_content = load_markdown_content(post['id'], md_dir) if md_dir else None

    if md_content:
        content = md_content['body_html']
        why_this_matters = md_content['why_html']
        provenance_badges = md_content['provenance']
        has_v3_content = True
        media_clips = md_content['front_matter'].get('media', [])
    else:
        content = f"<p>{post.get('summary', '')}</p>"
        why_this_matters = ''
        provenance_badges = []
        has_v3_content = False
        media_clips = []

    # Resolve evidence items with exhibit IDs and titles for footer
    # Hero items shown prominently, primary items shown as chips
    # Tertiary items are excluded entirely (internal only)
    evidence_items = []
    hero_evidence = []
    post_evidence = post.get('evidence', {})
    post_id = post.get('id', '')

    # Primary path: canonical evidence index via collected_files
    if evidence_registry and isinstance(post_evidence, dict) and post_evidence.get('collected_files'):
        for fpath in post['evidence']['collected_files']:
            if fpath in evidence_registry:
                entry = evidence_registry[fpath]
                tier = entry.get('tier', 'primary')
                if isinstance(tier, str):
                    tier = tier.lower()
                # Tertiary evidence is internal only — never shown in footer
                if tier == 'tertiary':
                    continue
                item_data = {
                    'exhibit_id': entry.get('exhibit_id', ''),
                    'title': entry.get('title', Path(fpath).stem),
                    'file_path': fpath,
                    'tier': tier,
                    'category': entry.get('category', '') or entry.get('exhibit_type', ''),
                    'reliability': entry.get('reliability', ''),
                    'description': entry.get('description', '') or entry.get('appendix_text', '')[:200] if entry.get('appendix_text') else '',
                }
                if tier == 'hero':
                    hero_evidence.append(item_data)
                evidence_items.append(item_data)
            else:
                fname = Path(fpath).stem
                evidence_items.append({
                    'exhibit_id': fname.split('_')[0] if '_' in fname else '',
                    'title': fname.replace('_', ' '),
                    'file_path': fpath,
                    'tier': 'primary',
                    'category': '',
                    'reliability': '',
                    'description': '',
                })

    # Curated path: use posts.json hero/primary/secondary arrays + evidence index lookup
    if not evidence_items and isinstance(post_evidence, dict):
        # Build exhibit_id → entry lookup from canonical index
        eid_lookup = {}
        if v3_evidence_map and post_id in v3_evidence_map:
            for entry in v3_evidence_map[post_id]:
                eid_lookup[entry.get('exhibit_id', '')] = entry

        # Process curated tiers from posts.json in order: hero, primary, secondary
        for tier_name, tier_list in [('hero', post_evidence.get('hero', [])),
                                      ('primary', post_evidence.get('primary', [])),
                                      ('secondary', post_evidence.get('secondary', []))]:
            for eid in tier_list:
                entry = eid_lookup.get(eid, {})
                rel_path = entry.get('rel_path', '')
                file_path = f"evidence/{rel_path}" if rel_path else ''
                item_data = {
                    'exhibit_id': eid,
                    'title': entry.get('title', eid.replace('_', ' '))[:80],
                    'file_path': file_path,
                    'tier': tier_name,
                    'category': entry.get('category', '') or entry.get('exhibit_type', ''),
                    'reliability': entry.get('reliability', 'Documented Record'),
                    'description': (entry.get('description', '') or entry.get('appendix_text', '') or entry.get('embed_text', ''))[:200] if entry else '',
                }
                if tier_name == 'hero':
                    hero_evidence.append(item_data)
                evidence_items.append(item_data)

    # Source exhibit auto-injection: for each hero item with a source_exhibit,
    # add the source to the primary tier if it's not already present.
    # This ensures readers can trace derivative hero evidence back to its primary source.
    if canonical_by_eid and hero_evidence:
        existing_eids = {item['exhibit_id'] for item in evidence_items}
        auto_injected = []
        for hero_item in hero_evidence:
            hero_entry = canonical_by_eid.get(hero_item['exhibit_id'], {})
            source_eid = hero_entry.get('source_exhibit')
            if source_eid and source_eid not in existing_eids:
                source_entry = canonical_by_eid.get(source_eid)
                if source_entry:
                    rel_path = source_entry.get('rel_path', '')
                    source_data = {
                        'exhibit_id': source_eid,
                        'title': source_entry.get('title', source_eid.replace('_', ' '))[:80],
                        'file_path': f"evidence/{rel_path}" if rel_path else '',
                        'tier': 'primary',
                        'category': source_entry.get('category', ''),
                        'reliability': source_entry.get('reliability', 'Documented Record'),
                        'description': (source_entry.get('description', '') or '')[:200],
                    }
                    evidence_items.append(source_data)
                    existing_eids.add(source_eid)
                    auto_injected.append(source_eid)
                else:
                    print(f"      \u26a0 source_exhibit '{source_eid}' for hero '{hero_item['exhibit_id']}' not found in canonical index")
        if auto_injected:
            print(f"      \u2139 Auto-injected {len(auto_injected)} source exhibit(s) into {post_id} primary tier: {', '.join(auto_injected)}")

    # Calculate total evidence count (hero + primary + secondary) for "explore all" link
    total_evidence_count = len(evidence_items)

    # Canonical URL for this post
    canonical_url = f"{SITE_URL}/posts/{post['id']}"

    html = template.render(
        post=post,
        evidence_items=evidence_items,
        hero_evidence=hero_evidence,
        total_evidence_count=total_evidence_count,
        content=content,
        why_this_matters=why_this_matters,
        provenance_badges=provenance_badges,
        has_v3_content=has_v3_content,
        media_clips=media_clips,
        phase_color=phase_info['color'],
        banner_image=banner_image,
        prev_post=prev_post,
        next_post=next_post,
        related_posts=related,
        site_title='Chappaqua Poison',
        site_url=SITE_URL,
        canonical_url=canonical_url,
        base_path='..',
    )

    return html, md_content

def get_featured_posts(posts, tokens, banners_dir=None):
    """Return curated featured posts for homepage carousel.
    Featured post IDs are maintained here for editorial control."""
    featured_ids = ['B35', 'B30', 'B09', 'B15']
    posts_by_id = {p['id']: p for p in posts}
    featured = []
    for fid in featured_ids:
        if fid in posts_by_id:
            post = dict(posts_by_id[fid])  # copy to avoid mutation
            if banners_dir:
                post['banner_image'] = resolve_banner_png(fid, banners_dir, base_path='.')
            # Get phase color
            phase_info = get_phase_info(post.get('phase', 'I'), tokens)
            post['phase_color'] = phase_info['color']
            post['phase_name'] = phase_info['name']
            featured.append(post)
    return featured

def render_index_html(template_env, posts, tokens, banners_dir=None):
    """Render homepage"""
    grouped_posts = group_posts_by_phase(posts, tokens)
    tags = get_all_tags(posts)

    # Resolve banner paths for each post in grouped_posts (for tile images)
    if banners_dir:
        for group in grouped_posts:
            for post in group['posts']:
                post['banner_image'] = resolve_banner_png(post.get('id', ''), banners_dir, base_path='.')

    # Featured posts for carousel
    featured_posts = get_featured_posts(posts, tokens, banners_dir)

    # Build flat post list sorted by post number descending (newest first)
    all_posts_flat = []
    grouped_ids = set()
    for group in grouped_posts:
        for post in group['posts']:
            p = dict(post)
            p['phase_color'] = group['color']
            p['phase_label'] = f"Act {group['phase']}"
            all_posts_flat.append(p)
            grouped_ids.add(p.get('id', ''))

    # Include ungrouped posts (phase X, None, etc.) so they appear on homepage
    for post in posts:
        if post.get('id', '') not in grouped_ids:
            p = dict(post)
            p['phase_color'] = '#A69070'
            p['phase_label'] = ''
            if banners_dir:
                p['banner_image'] = resolve_banner_png(p.get('id', ''), banners_dir, base_path='.')
            all_posts_flat.append(p)

    # Sort by number ascending (Chapter 1 first); sub-posts (same number) keep phase order via stable sort
    all_posts_flat.sort(key=lambda p: int(p.get('number', 0)), reverse=False)

    # Phase timeline info
    phases = []
    for phase in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']:
        phase_info = get_phase_info(phase, tokens)
        phases.append({
            'phase': phase,
            'name': phase_info['name'],
            'color': phase_info['color'],
            'date_range': _get_phase_date_range(phase),
            'description': _get_phase_description(phase),
        })

    template = template_env.get_template('index.html')

    # Canonical URL for homepage
    canonical_url = SITE_URL

    html = template.render(
        post_count=len(posts),
        grouped_posts=grouped_posts,
        all_posts_flat=all_posts_flat,
        featured_posts=featured_posts,
        phases=phases,
        tags=tags,
        site_title='Chappaqua Poison',
        canonical_url=canonical_url,
        base_path='.',
        active_nav='home',
    )

    return html

def render_static_page_html(static_page, template_env, tokens):
    """Render a static page with purpose as meta description"""
    # Create a minimal template that extends base.html with proper blocks
    template_str = """{% extends "base.html" %}
{% block title %}{{ page_title }} | {{ site_title }}{% endblock %}
{% block meta_description %}{{ meta_description }}{% endblock %}
{% block canonical %}<link rel="canonical" href="{{ canonical_url }}">{% endblock %}
{% block content %}
<div class="content-wrapper">
  <h1>{{ page_title }}</h1>
  <p>{{ page_purpose }}</p>
</div>
{% endblock %}"""

    template = template_env.from_string(template_str)

    page_id = static_page['id']
    filename = STATIC_PAGES_MAP.get(page_id, 'page.html')

    # Generate canonical URL
    canonical_url = f"{SITE_URL}/{filename.replace('.html', '')}"

    html = template.render(
        site_title='Chappaqua Poison',
        page_title=static_page['title'],
        page_purpose=static_page['purpose'],
        canonical_url=canonical_url,
        meta_description=static_page['purpose'],
        base_path='.',
    )

    return html

def load_evidence_registry(registry_path):
    """Load the canonical evidence_index_canonical.json.
    Returns a list of evidence items ready for template rendering,
    sorted by exhibit_id.

    Also returns a dict keyed by filename for post-footer lookups."""
    if not Path(registry_path).exists():
        print(f"  ⚠ evidence_index_canonical.json not found at {registry_path}")
        return []

    with open(registry_path, encoding='utf-8') as f:
        data = json.load(f)

    entries = data.get('entries', [])
    items = []
    for entry in entries:
        # Tertiary evidence is internal only — excluded from evidence.html
        if entry.get('tier', '').lower() == 'tertiary':
            continue
        # Suppress file links for entries flagged as missing
        file_missing = entry.get('file_missing', False)
        rel_path = entry.get('rel_path', '')
        file_path = '' if file_missing else (f"evidence/{rel_path}" if rel_path else '')
        item = {
            'exhibit_id': entry.get('exhibit_id', ''),
            'original_exhibit_id': entry.get('original_exhibit_id', ''),
            'title': entry.get('title', entry.get('filename', '')),
            'description': entry.get('description', ''),
            'category': entry.get('category', 'Other'),
            'category_key': entry.get('category_key', ''),
            'file_type': entry.get('file_type', '') or entry.get('extension', ''),
            'file_path': file_path,
            'phase': entry.get('phase'),
            'reliability': entry.get('reliability', 'Documented Record'),
            'related_posts': entry.get('posts', []),
            'post_titles': entry.get('post_titles', []),
            'sub_files': entry.get('sub_files', []),
            'thumbnail': entry.get('thumbnail', ''),
            'tier': entry.get('tier', 'secondary'),
            'evidence_text_preview': entry.get('evidence_text_preview', ''),
            'key_people': entry.get('key_people', []),
            'keywords': entry.get('keywords', []),
            'extracted_dates': entry.get('extracted_dates', []),
            # Editorial fields from evidence map
            'embed_text': entry.get('embed_text', ''),
            'appendix_text': entry.get('appendix_text', ''),
            'exhibit_type': entry.get('exhibit_type', ''),
            'exhibit_name': entry.get('exhibit_name', ''),
            'caption_voice': entry.get('caption_voice', ''),
            # Filename for cross-referencing
            'filename': entry.get('filename', ''),
        }
        items.append(item)

    # Sort: canonical A-H IDs first, then readable labels, then others
    def sort_key(item):
        eid = item['exhibit_id']
        if not eid:
            return ('zzz', 0, item['title'])
        # Canonical IDs like A-1, B-9 sort first
        canon = re.match(r'^([A-H])-(\d+)$', eid)
        if canon:
            return ('aaa', int(canon.group(2)), canon.group(1))
        # Everything else alphabetically
        return ('bbb', 0, eid)

    items.sort(key=sort_key)
    return items


def build_evidence_index(posts, output_dir, evidence_dir, template_env):
    """Build evidence index page from curated registry"""
    # Load canonical evidence index
    registry_path = Path(__file__).parent.parent / 'evidence_index_canonical.json'
    evidence_items = load_evidence_registry(registry_path)

    if not evidence_items:
        print("  ⚠ No evidence items loaded — skipping evidence page")
        return '', 0

    # Build post lookup for resolving related_posts → post_titles
    post_lookup = {p['id']: p.get('title', p['id']) for p in posts}
    valid_post_ids = set(post_lookup.keys())  # Only include posts that exist

    # Enrich evidence items: resolve related_posts IDs into post_titles objects
    for item in evidence_items:
        resolved = []
        for pid in item.get('related_posts', []):
            # Only include post reference if the post actually exists in the active posts list
            if pid and pid in valid_post_ids:
                resolved.append({'id': pid, 'title': post_lookup[pid]})
        item['post_titles'] = resolved

    # Collect unique categories and reliability tiers
    categories = sorted(set(item['category'] for item in evidence_items))
    reliability_tiers = sorted(set(item['reliability'] for item in evidence_items))
    phases_with_evidence = sorted(set(
        item['phase'] for item in evidence_items if item.get('phase')
    ))

    # Count files (including sub-files in grouped items)
    total_files = 0
    for item in evidence_items:
        if item.get('sub_files'):
            total_files += len(item['sub_files'])
        else:
            total_files += 1

    # Render template
    template = template_env.get_template('evidence.html')
    canonical_url = f"{SITE_URL}/evidence"

    html = template.render(
        evidence_items=evidence_items,
        total_entries=len(evidence_items),
        total_files=total_files,
        categories=categories,
        reliability_tiers=reliability_tiers,
        phases_with_evidence=phases_with_evidence,
        site_title='Chappaqua Poison',
        canonical_url=canonical_url,
        base_path='.',
    )

    return html, len(evidence_items)

def render_tag_page_html(tag, tag_slug, posts_with_tag, template_env, tokens):
    """Render a tag page showing all posts with that tag"""
    template = template_env.get_template('tag.html')

    # Group posts by phase for display
    phase_order = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']
    grouped = {phase: [] for phase in phase_order}

    for post in posts_with_tag:
        phase = post.get('phase', 'I')
        if phase in grouped:
            grouped[phase].append(post)

    # Convert to list with phase info
    grouped_posts = []
    for phase in phase_order:
        if grouped[phase]:
            phase_info = get_phase_info(phase, tokens)
            grouped_posts.append({
                'phase': phase,
                'color': phase_info['color'],
                'posts': grouped[phase],
            })

    # Canonical URL for tag page
    canonical_url = f"{SITE_URL}/tags/{tag_slug}"

    html = template.render(
        tag=tag,
        tag_slug=tag_slug,
        posts_count=len(posts_with_tag),
        grouped_posts=grouped_posts,
        site_title='Chappaqua Poison',
        canonical_url=canonical_url,
        meta_description=f"Posts tagged with '{tag}'",
        base_path='..',
    )

    return html

def ensure_directories(output_dir):
    """Create necessary output directories"""
    (output_dir / 'posts').mkdir(parents=True, exist_ok=True)
    (output_dir / 'tags').mkdir(parents=True, exist_ok=True)
    (output_dir / 'js').mkdir(parents=True, exist_ok=True)
    (output_dir / 'css').mkdir(parents=True, exist_ok=True)

def main():

    # Paths
    project_root = Path(__file__).parent.parent
    tokens_file = project_root / 'tokens.json'
    banners_dir = project_root / 'Images' / 'banners'
    templates_dir = project_root / 'templates'

    posts_file = project_root / 'posts.json'
    output_dir = project_root / '_site'
    md_dir = project_root / 'posts' / 'md'
    build_label = "v3 (beats)"
    print("=" * 60)
    print(f"ChappaquaPoison {build_label} — HTML Builder")
    print("=" * 60)

    # Load data
    print("\n1. Loading data...")
    all_posts = load_posts(posts_file)
    # Filter out hidden posts (hidden: true in posts.json)
    hidden_posts = [p for p in all_posts if p.get('hidden', False)]
    posts = [p for p in all_posts if not p.get('hidden', False)]
    static_pages = load_static_pages(posts_file)
    tokens = load_tokens(tokens_file)
    if hidden_posts:
        hidden_ids = ', '.join(p['id'] for p in hidden_posts)
        print(f"   ✓ Loaded {len(all_posts)} posts from {posts_file.name} ({len(hidden_posts)} hidden: {hidden_ids})")
    else:
        print(f"   ✓ Loaded {len(posts)} posts from {posts_file.name}")

    # ── B13 Guard (soft) ─────────────────────────────────────
    # B13 "The Painter of Cottages" has been accidentally dropped
    # from posts.json multiple times. This guard warns and auto-
    # restores the markdown from backup if possible.
    post_ids = {p.get('id') for p in posts}
    if 'B13' not in post_ids:
        print("\n   ⚠  WARNING: B13 'The Painter of Cottages' missing from posts.json!")
        print("     This chapter has been accidentally dropped before.")
        print("     Restore from posts/md_backup_pre_embeds/B13_the-painter-of-cottages.md")
        print("     BUILD CONTINUES — but the site will be incomplete.\n")
    b13_md = list(md_dir.glob('B13_*.md'))
    if not b13_md:
        _backup = project_root / 'posts' / 'md_backup_pre_embeds' / 'B13_the-painter-of-cottages.md'
        if _backup.exists():
            shutil.copy2(str(_backup), str(md_dir / 'B13_the-painter-of-cottages.md'))
            print("   ✓ B13 markdown auto-restored from backup")
        else:
            print("   ⚠  WARNING: B13 markdown missing and no backup found")
    # ── End B13 Guard ─────────────────────────────────────────
    print(f"   ✓ Loaded {len(static_pages)} static pages")

    # Check for Markdown sources
    glob_pattern = '*.md'
    md_count = len(list(md_dir.glob(glob_pattern))) if md_dir.exists() else 0
    print(f"   ✓ Found {md_count} Markdown source files in {md_dir.relative_to(project_root)}/")

    # Setup Jinja2
    print("2. Setting up templating engine...")
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    # Register custom filters
    env.filters['basename'] = lambda path: Path(path).name
    env.filters['slugify'] = lambda text: text.lower().replace(' ', '-').replace('/', '-')
    def clip_title_filter(path):
        """Turn clip filename into readable title, e.g.
        'Gavish_Aware_Encouraging_est1h20.mp4' -> 'Gavish — Aware Encouraging (est 1h20)'
        'Clip10_Moore_Representation_Fraud_opening.mp4' -> 'Clip 10 — Moore Representation Fraud (opening)'
        """
        import re as _re
        name = Path(path).stem  # strip extension
        # Split on first underscore group that separates the speaker/clip ID from the description
        # Handle "Clip##_..." pattern
        clip_match = _re.match(r'^(Clip)(\d+)_(.+?)(?:_(est\w+|opening|closing))?$', name)
        if clip_match:
            prefix = f"{clip_match.group(1)} {clip_match.group(2)}"
            desc = clip_match.group(3).replace('_', ' ')
            suffix = clip_match.group(4)
            if suffix:
                suffix = _re.sub(r'est(\d+)h(\d+)', r'est \1h\2', suffix)
                return f"{prefix} — {desc} ({suffix})"
            return f"{prefix} — {desc}"
        # Handle "Speaker_Desc_est##h##" pattern
        speaker_match = _re.match(r'^(\w+?)_(.+?)(?:_(est\w+))?$', name)
        if speaker_match:
            speaker = speaker_match.group(1)
            desc = speaker_match.group(2).replace('_', ' ')
            suffix = speaker_match.group(3)
            if suffix:
                suffix = _re.sub(r'est(\d+)h(\d+)', r'est \1h\2', suffix)
                return f"{speaker} — {desc} ({suffix})"
            return f"{speaker} — {desc}"
        return name.replace('_', ' ')
    env.filters['clip_title'] = clip_title_filter
    print("   ✓ Jinja2 environment ready")

    # Prepare directories
    print("3. Creating output directories...")
    ensure_directories(output_dir)
    print("   ✓ Directories created")

    # Copy static assets (Images, CSS, JS, favicon)
    print("3b. Copying static assets to _site/...")
    images_src = project_root / 'Images'
    images_dst = output_dir / 'images'
    if images_src.exists():
        images_dst.mkdir(exist_ok=True)
        copied = 0
        # Copy root-level image files (hero-banner.png, og-banner.svg, etc.)
        for src_file in images_src.iterdir():
            if src_file.is_file():
                dst_file = images_dst / src_file.name
                if not dst_file.exists() or src_file.stat().st_mtime > dst_file.stat().st_mtime:
                    try:
                        shutil.copy2(src_file, dst_file)
                        copied += 1
                    except PermissionError:
                        pass
        # Copy image subdirectories
        for subdir in ['banners', 'banners/v3', 'icons', 'inline', 'style_board', 'textures', 'thumbnails', 'thumbnails/evidence']:
            src_sub = images_src / subdir
            dst_sub = images_dst / subdir
            if src_sub.exists():
                dst_sub.mkdir(exist_ok=True)
                for src_file in src_sub.iterdir():
                    if src_file.is_file():
                        dst_file = dst_sub / src_file.name
                        if not dst_file.exists() or src_file.stat().st_mtime > dst_file.stat().st_mtime:
                            try:
                                shutil.copy2(src_file, dst_file)
                                copied += 1
                            except PermissionError:
                                pass  # Skip files we can't overwrite
        # Copy photos/ directory tree (evidence + narrative subdirectories)
        photos_src = images_src / 'photos'
        if photos_src.exists():
            for root, dirs, files in os.walk(photos_src):
                rel_root = Path(root).relative_to(images_src)
                dst_root = images_dst / rel_root
                dst_root.mkdir(parents=True, exist_ok=True)
                for fname in files:
                    src_file = Path(root) / fname
                    dst_file = dst_root / fname
                    if not dst_file.exists() or src_file.stat().st_mtime > dst_file.stat().st_mtime:
                        try:
                            shutil.copy2(src_file, dst_file)
                            copied += 1
                        except PermissionError:
                            pass
        banner_count = len(list((images_dst / 'banners' / 'v3').glob('*.png'))) if (images_dst / 'banners' / 'v3').exists() else 0
        inline_count = len(list((images_dst / 'inline').glob('*.svg'))) if (images_dst / 'inline').exists() else 0
        print(f"   ✓ images/ synced ({banner_count} banner PNGs, {inline_count} inline SVGs, {copied} updated)")
    else:
        print("   ⚠ Images/ source directory not found")

    # Copy Evidence directory into _site for local file:// viewing
    evidence_src = project_root / 'Evidence'
    evidence_dst = output_dir / 'Evidence'
    if evidence_src.exists():
        evidence_copied = 0
        for root, dirs, files in os.walk(evidence_src):
            rel_root = Path(root).relative_to(evidence_src)
            dst_root = evidence_dst / rel_root
            dst_root.mkdir(parents=True, exist_ok=True)
            for fname in files:
                src_file = Path(root) / fname
                dst_file = dst_root / fname
                if not dst_file.exists() or src_file.stat().st_mtime > dst_file.stat().st_mtime:
                    try:
                        shutil.copy2(src_file, dst_file)
                        evidence_copied += 1
                    except PermissionError:
                        pass
        print(f"   ✓ Evidence/ synced ({evidence_copied} files updated)")
    else:
        print("   ⚠ Evidence/ directory not found — evidence links will be broken")

    # Copy CSS and JS assets (tokens.css, plyr.css, search.js, plyr.min.js, etc.)
    for asset_dir in ['css', 'js']:
        src_dir = project_root / asset_dir
        dst_dir = output_dir / asset_dir
        if src_dir.exists():
            dst_dir.mkdir(exist_ok=True)
            asset_copied = 0
            for src_file in src_dir.iterdir():
                if src_file.is_file():
                    dst_file = dst_dir / src_file.name
                    if not dst_file.exists() or src_file.stat().st_mtime > dst_file.stat().st_mtime:
                        try:
                            shutil.copy2(src_file, dst_file)
                            asset_copied += 1
                        except PermissionError:
                            pass
            if asset_copied:
                print(f"   ✓ {asset_dir}/ synced ({asset_copied} files updated)")

    # Copy favicon
    favicon_src = project_root / 'favicon.svg'
    if favicon_src.exists():
        shutil.copy2(favicon_src, output_dir / 'favicon.svg')

    # Copy _redirects file
    redirects_src = project_root / '_redirects'
    if redirects_src.exists():
        shutil.copy2(redirects_src, output_dir / '_redirects')

    # Copy og-banner image
    og_banner_src = project_root / 'Images' / 'og-banner.png'
    if og_banner_src.exists():
        shutil.copy2(og_banner_src, images_dst / 'og-banner.png')

    # Copy Previous directory
    previous_src = project_root / 'Previous'
    if previous_src.exists():
        previous_dst = output_dir / 'Previous'
        try:
            if previous_dst.exists():
                shutil.rmtree(previous_dst)
            shutil.copytree(previous_src, previous_dst)
        except PermissionError:
            print("   ⚠ Could not update Previous/ directory (permission denied, skipping)")

    # Build navigation
    print("4. Building navigation chains...")
    nav_map = build_post_nav_chain(posts)
    print(f"   ✓ Navigation built for {len(posts)} posts")

    # Load canonical evidence index for post footers
    canonical_path = project_root / 'evidence_index_canonical.json'
    evidence_registry = {}  # keyed by file_path for collected_files lookup
    canonical_by_post = {}  # keyed by post_id → list of entries (replaces v3_evidence_map)
    if canonical_path.exists():
        with open(canonical_path, encoding='utf-8') as f:
            canonical_data = json.load(f)
        for entry in canonical_data.get('entries', []):
            # Build file-path lookup (matches evidence_metadata.json's old keying)
            rel_path = entry.get('rel_path', '')
            if rel_path:
                fpath_key = f"evidence/{rel_path}"
                evidence_registry[fpath_key] = entry
            # Also key by just filename for fallback
            fname = entry.get('filename', '')
            if fname:
                evidence_registry[fname] = entry
            # Build post→entries lookup (replaces v3_evidence_map)
            for pid in entry.get('posts', []):
                canonical_by_post.setdefault(pid, []).append(entry)
        print(f"   \u2713 Loaded canonical evidence index ({len(canonical_data.get('entries', []))} entries)")
    v3_evidence_map = canonical_by_post  # reuse the same parameter name downstream

    # Build global exhibit_id → entry lookup for source_exhibit resolution
    canonical_by_eid = {}
    for entry in canonical_data.get('entries', []) if canonical_path.exists() else []:
        eid = entry.get('exhibit_id') or entry.get('id', '')
        if eid:
            canonical_by_eid[eid] = entry

    # Render posts
    print("5. Rendering post pages...")
    v3_count = 0
    v2_count = 0
    build_manifest = {}
    for post in posts:
        html, md_info = render_post_html(post, env, posts, tokens, banners_dir, nav_map, md_dir, evidence_registry, v3_evidence_map, canonical_by_eid)
        post_file = output_dir / 'posts' / f"{post['id']}.html"
        post_file.write_text(html)

        if md_info:
            v3_count += 1
            html_hash = hashlib.sha256(html.encode()).hexdigest()[:16]
            build_manifest[post['id']] = {
                'md_hash': md_info['md_hash'],
                'html_hash': html_hash,
                'source': md_info['source_path'],
                'provenance': md_info['provenance'],
            }
        else:
            v2_count += 1

    print(f"   ✓ Generated {len(posts)} post pages ({v3_count} v3 expanded, {v2_count} v2 summary)")

    # ─── Post-render: expand evidence-to-post cross-links from inline embeds ───
    print("5b. Expanding evidence-to-post links from inline embeds...")
    eid_by_post = {}  # post_id → set of exhibit IDs found in HTML
    for post in posts:
        post_file = output_dir / 'posts' / f"{post['id']}.html"
        if post_file.exists():
            html_text = post_file.read_text(errors='replace')
            found_eids = set(re.findall(r'data-exhibit="([^"]+)"', html_text))
            if found_eids:
                eid_by_post[post['id']] = found_eids

    # Build exhibit_id → canonical entry lookup
    eid_to_entries = {}
    for entry in canonical_data.get('entries', []):
        eid = entry.get('exhibit_id', '')
        if eid:
            eid_to_entries.setdefault(eid, []).append(entry)

    links_added = 0
    for post_id, eids in eid_by_post.items():
        for eid in eids:
            if eid in eid_to_entries:
                for entry in eid_to_entries[eid]:
                    posts_list = entry.get('posts', [])
                    if post_id not in posts_list:
                        posts_list.append(post_id)
                        entry['posts'] = posts_list
                        links_added += 1

    if links_added > 0:
        # Write updated canonical index
        with open(canonical_path, 'w', encoding='utf-8') as f:
            json.dump(canonical_data, f, indent=2, ensure_ascii=False)
        print(f"   ✓ Added {links_added} new evidence-to-post cross-links")
        # Rebuild the post→entries lookup for evidence.html
        canonical_by_post = {}
        for entry in canonical_data.get('entries', []):
            for pid in entry.get('posts', []):
                canonical_by_post.setdefault(pid, []).append(entry)
        v3_evidence_map = canonical_by_post
    else:
        print("   ✓ All evidence-to-post links already up to date")

    # Write build manifest for v3 posts
    if build_manifest:
        manifest_path = project_root / 'audit' / 'build_manifest.json'
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, 'w') as f:
            json.dump(build_manifest, f, indent=2)
        print(f"   ✓ Build manifest written ({len(build_manifest)} entries)")

    # Render homepage
    print("6. Rendering homepage...")
    index_html = render_index_html(env, posts, tokens, banners_dir)
    (output_dir / 'index.html').write_text(index_html)
    print("   ✓ Generated index.html")

    # Render static pages
    print("7. Rendering static pages...")
    static_count = 0
    # Pages with dedicated templates (filename minus .html)
    DEDICATED_TEMPLATES = {'methodology.html', 'about.html', 'timeline.html', 'evidence.html', 'public-record-notice.html', 'falsifiability.html', 'how-to-read.html', 'search.html', 'timeline-guide.html', 'characters.html', 'legal.html', 'book.html'}

    # Map filenames to active_nav identifiers for header highlighting
    ACTIVE_NAV_MAP = {
        'about.html': 'about',
        'timeline.html': 'timeline',
        'evidence.html': 'evidence',
        'search.html': 'search',
        'methodology.html': 'about',
        'how-to-read.html': 'about',
        'public-record-notice.html': 'about',
        'falsifiability.html': 'about',
        'timeline-guide.html': 'timeline',
        'characters.html': 'about',
        'legal.html': 'legal',
        'book.html': 'book',
    }

    for static_page in static_pages:
        page_id = static_page['id']
        filename = STATIC_PAGES_MAP.get(page_id)

        # Skip S-1 (homepage, already generated)
        if page_id == 'S-1':
            continue

        if filename:
            active_nav = ACTIVE_NAV_MAP.get(filename, '')

            # Special handling for evidence.html
            if filename == 'evidence.html':
                evidence_dir = project_root / 'Evidence'
                html, evidence_count = build_evidence_index(posts, output_dir, evidence_dir, env)
                static_file = output_dir / filename
                static_file.write_text(html)
                static_count += 1
                print(f"   ✓ Generated evidence.html ({evidence_count} artifacts indexed)")
            elif filename == 'timeline.html':
                # Special handling for timeline — load timeline.json and pass events
                timeline_json_path = project_root / 'timeline.json'
                timeline_events = []
                if timeline_json_path.exists():
                    with open(timeline_json_path) as f:
                        timeline_data = json.load(f)
                    timeline_events = timeline_data.get('entries', [])

                # Build phase info list
                timeline_phases = []
                for phase in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']:
                    phase_info = get_phase_info(phase, tokens)
                    phase_events = [e for e in timeline_events if e.get('phase') == phase]
                    # Sort events by date
                    phase_events.sort(key=lambda e: e.get('date', ''))
                    timeline_phases.append({
                        'phase': phase,
                        'name': phase_info['name'],
                        'color': phase_info['color'],
                        'date_range': _get_phase_date_range(phase),
                        'description': _get_phase_description(phase),
                        'events': phase_events,
                    })

                # Build post title lookup for linking
                # Index by both B-id and source P-ids so timeline.json P-refs resolve
                post_lookup = {}
                for p in posts:
                    entry = {
                        'title': p.get('title', ''),
                        'url': f'./posts/{p["id"]}.html',
                        'summary': p.get('summary', ''),
                        'ecs': p.get('ecs'),
                    }
                    post_lookup[p['id']] = entry
                    # Also map legacy P-ids from source_posts
                    for sp in p.get('source_posts', []):
                        if sp and sp not in post_lookup:
                            post_lookup[sp] = entry

                template = env.get_template('timeline.html')
                canonical_url = f"{SITE_URL}/timeline"
                html = template.render(
                    site_title='Chappaqua Poison',
                    canonical_url=canonical_url,
                    base_path='.',
                    active_nav='timeline',
                    timeline_phases=timeline_phases,
                    post_lookup=post_lookup,
                    total_events=len(timeline_events),
                )
                static_file = output_dir / filename
                static_file.write_text(html)
                static_count += 1
                print(f"   ✓ Generated timeline.html ({len(timeline_events)} events across {len(timeline_phases)} phases)")
            elif filename in ('timeline-guide.html', 'characters.html', 'legal.html', 'book.html'):
                # Markdown-based reference pages — read markdown, convert to HTML, inject into template
                md_map = {
                    'timeline-guide.html': 'pages/timeline-canonical.md',
                    'characters.html': 'pages/characters-canonical.md',
                    'legal.html': 'pages/legal.md',
                    'book.html': 'pages/book.md',
                }
                md_path = project_root / md_map[filename]
                if md_path.exists():
                    md_text = md_path.read_text()
                    # Strip YAML front matter if present
                    if md_text.startswith('---'):
                        parts = md_text.split('---', 2)
                        if len(parts) >= 3:
                            md_text = parts[2].strip()
                    content_html = markdown.markdown(md_text, extensions=['smarty'])
                    template_name = filename.replace('.html', '') + '.html'
                    template = env.get_template(template_name)
                    canonical_url = f"{SITE_URL}/{filename.replace('.html', '')}"
                    html = template.render(
                        site_title='Chappaqua Poison',
                        canonical_url=canonical_url,
                        base_path='.',
                        active_nav=active_nav,
                        content=content_html,
                    )
                    static_file = output_dir / filename
                    static_file.write_text(html)
                    static_count += 1
                    print(f"   ✓ Generated {filename} (from {md_map[filename]})")
                else:
                    print(f"   ⚠ Skipped {filename}: source markdown not found at {md_path}")
            elif filename in DEDICATED_TEMPLATES:
                # Use dedicated template
                template_name = filename.replace('.html', '') + '.html'
                try:
                    template = env.get_template(template_name)
                    canonical_url = f"{SITE_URL}/{filename.replace('.html', '')}"
                    html = template.render(
                        site_title='Chappaqua Poison',
                        canonical_url=canonical_url,
                        base_path='.',
                        active_nav=active_nav,
                    )
                except Exception as e:
                    print(f"   ⚠ Dedicated template {template_name} failed: {e}, falling back")
                    html = render_static_page_html(static_page, env, tokens)
                static_file = output_dir / filename
                static_file.write_text(html)
                static_count += 1
            else:
                html = render_static_page_html(static_page, env, tokens)
                static_file = output_dir / filename
                static_file.write_text(html)
                static_count += 1
    print(f"   ✓ Generated {static_count} static pages")

    # Render 404 page
    print("7b. Rendering 404 page...")
    template_404 = env.get_template('404.html')
    html_404 = template_404.render(site_title='Chappaqua Poison', base_path='.')
    (output_dir / '404.html').write_text(html_404)
    print("   ✓ Generated 404.html")

    # Render tag pages
    print("8. Rendering tag pages...")
    tags = get_all_tags(posts)
    valid_slugs = {slug for _, _, slug in tags}
    # Clean up orphan tag pages from previous builds
    tags_dir = output_dir / 'tags'
    orphan_count = 0
    if tags_dir.exists():
        for existing in tags_dir.glob("*.html"):
            if existing.stem not in valid_slugs:
                try:
                    existing.unlink()
                    orphan_count += 1
                except (PermissionError, OSError):
                    # Overwrite with empty redirect to tags list
                    try:
                        existing.write_text('<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0;url=../"></head><body>Redirecting...</body></html>')
                        orphan_count += 1
                    except:
                        pass
    if orphan_count:
        print(f"   ✓ Cleaned {orphan_count} orphan tag pages")
    tag_count = 0
    for tag, count, slug in tags:
        posts_with_tag = get_posts_by_tag(tag, posts)
        html = render_tag_page_html(tag, slug, posts_with_tag, env, tokens)
        tag_file = output_dir / 'tags' / f"{slug}.html"
        tag_file.write_text(html)
        tag_count += 1
    print(f"   ✓ Generated {tag_count} tag pages")

    print("\n" + "=" * 60)
    print("✓ HTML generation complete!")
    print("=" * 60)
    print(f"\nOutput directory: {output_dir}")
    print(f"  - {len(posts)} posts in {output_dir / 'posts'}")
    print(f"  - 1 homepage at {output_dir / 'index.html'}")
    print(f"  - {static_count} static pages in {output_dir}")
    print(f"  - {tag_count} tag pages in {output_dir / 'tags'}")

    # Run post-build site integrity validation
    print("\n9. Running post-build integrity validation...")
    try:
        from validate_site import SiteValidator
        validator = SiteValidator(output_dir)
        validation_result = validator.run()
        report_path = project_root / 'Audits' / 'site_integrity_report.json'
        validator.save_report(report_path)
        if validation_result != 0:
            print(f"   ⚠ Site validation found issues — review Audits/site_integrity_report.json")
        else:
            print(f"   ✓ Site integrity check passed")
    except ImportError:
        print(f"   ⚠ validate_site.py not found — skipping integrity check")
    except Exception as e:
        print(f"   ⚠ Validation error: {e}")

    return 0

if __name__ == '__main__':
    sys.exit(main())
