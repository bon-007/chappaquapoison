#!/usr/bin/env python3
"""
insert_hero_embeds.py — Insert MISSING hero evidence embed HTML blocks into post markdown.
Checks what embeds already exist and only adds the ones that are missing.
"""

import json
import os
import re
import html as html_mod
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
MD_DIR = PROJECT / 'posts' / 'md'
INDEX_PATH = PROJECT / 'evidence_index_canonical.json'
POSTS_PATH = PROJECT / 'posts.json'

FORMAT_CLASS_MAP = {
    'pull-quote': 'embed-quote', 'photo-frame': 'embed-photo',
    'photo-frame-embed': 'embed-photo', 'social-card': 'embed-social',
    'email-screenshot': 'embed-email', 'email-screenshot-embed': 'embed-email',
    'blog-card': 'embed-blog', 'legal-snippet': 'embed-legal',
    'legal-snippet-embed': 'embed-legal', 'imessage': 'embed-message',
    'imessage-embed': 'embed-message', 'video-clip': 'embed-media',
    'video-clip-embed': 'embed-media', 'audio-transcript': 'embed-audio',
    'text-embed': 'embed-text', 'image': 'embed-photo', '': 'embed-text',
}
CATEGORY_FORMAT_MAP = {
    'Text Message / Chat Record': 'embed-message', 'Sworn Declaration': 'embed-legal',
    'Correspondence': 'embed-email', 'Photograph': 'embed-photo',
    'Document': 'embed-text', 'Deposition & Testimony': 'embed-legal',
    'Court Filing': 'embed-legal', 'Video Evidence': 'embed-media',
    'Court Order / Judgment': 'embed-legal', 'Audio Recording': 'embed-audio',
    'Media Coverage': 'embed-blog', 'Laboratory Analysis': 'embed-text',
    'Blog Archive': 'embed-blog',
}

def get_format_class(entry):
    fmt = entry.get('display_format', '')
    if fmt and fmt in FORMAT_CLASS_MAP:
        return FORMAT_CLASS_MAP[fmt]
    return CATEGORY_FORMAT_MAP.get(entry.get('category', ''), 'embed-text')

def safe_escape(text):
    """Escape HTML but preserve apostrophes as literal characters."""
    return html_mod.escape(text).replace('&#x27;', "'")

def get_body_html(entry, fc):
    desc = safe_escape(entry.get('description', entry.get('title', '')))
    et = entry.get('embed_text', '')
    rp = entry.get('rel_path', '')
    title = safe_escape(entry.get('title', ''))
    if fc == 'embed-photo' and rp:
        return f'    <img src="../evidence/{html_mod.escape(rp)}" alt="{title}" loading="lazy">\n    <p class="photo-description">{desc}</p>'
    elif fc == 'embed-media' and rp:
        return f'    <video controls preload="metadata" class="evidence-video-player">\n      <source src="../evidence/{html_mod.escape(rp)}" type="video/mp4">\n    </video>\n    <p class="media-description">{desc}</p>'
    elif fc == 'embed-message':
        return f'    <div class="message-narrative">\n      <blockquote><p>{html_mod.escape(et or desc)}</p></blockquote>\n    </div>'
    elif fc == 'embed-quote':
        return f'    <blockquote><p>{html_mod.escape(et or desc)}</p></blockquote>'
    else:
        body = f'    <div class="document-text"><p>{html_mod.escape(et or desc)}</p></div>'
        if fc == 'embed-audio' and rp:
            body = f'    <audio controls preload="metadata">\n      <source src="../evidence/{html_mod.escape(rp)}">\n    </audio>\n' + body
        return body

def generate_embed_html(entry):
    eid = entry['exhibit_id']
    cat = entry.get('category', 'Evidence')
    rel = entry.get('reliability', '')
    date_text = ''
    dates = entry.get('extracted_dates', [])
    if dates:
        date_text = dates[0] if isinstance(dates[0], str) else str(dates[0])

    fc = get_format_class(entry)
    body = get_body_html(entry, fc)
    caption = html_mod.escape(entry.get('title', entry.get('description', '')))

    hdr = [f'<span class="embed-type">{html_mod.escape(cat)}</span>']
    if date_text:
        hdr.append(f'<span class="embed-date">{html_mod.escape(date_text)}</span>')
    if rel:
        hdr.append(f'<span class="embed-source">{html_mod.escape(rel)}</span>')

    return f'''
<div class="evidence-embed {fc}" data-exhibit="{html_mod.escape(eid)}">
  <div class="embed-header">
      {chr(10).join("      " + h if i > 0 else h for i, h in enumerate(hdr))}
  </div>
  <div class="embed-body">
{body}
  </div>
  <div class="embed-caption">{caption} &mdash; <em>{html_mod.escape(eid)}</em></div>
</div>
'''

def find_insertion_points(md_text):
    points = []
    lines = md_text.split('\n')
    in_fm = False
    fm_end = 0
    for i, line in enumerate(lines):
        if i == 0 and line.strip() == '---':
            in_fm = True
            continue
        if in_fm and line.strip() == '---':
            fm_end = i
            in_fm = False
            break
    
    char_pos = 0
    in_html_block = False
    for i, line in enumerate(lines):
        char_pos += len(line) + 1
        if i <= fm_end:
            continue
        s = line.strip()
        # Track HTML blocks to avoid inserting inside them
        if s.startswith('<div') or s.startswith('<section'):
            in_html_block = True
        if s.startswith('</div>') or s.startswith('</section>'):
            in_html_block = False
            continue
        if in_html_block:
            continue
        if s in ('---', '***', '___'):
            points.append(('section', char_pos))
        elif s == '' and i > 0 and lines[i-1].strip() and lines[i-1].strip() not in ('---', '***', '___'):
            points.append(('para', char_pos))
    return points

def main():
    with open(INDEX_PATH) as f:
        ev = json.load(f)
    with open(POSTS_PATH) as f:
        pd = json.load(f)

    lookup = {e['exhibit_id']: e for e in ev['entries']}
    total = 0
    modified = 0

    for post in pd['posts']:
        pid = post['id']
        hero_ids = post.get('evidence', {}).get('hero', [])
        if not hero_ids:
            continue

        mds = [f for f in os.listdir(MD_DIR) if f.startswith(pid + '_') and f.endswith('.md') and 'PRE-SESSION' not in f]
        if not mds:
            continue
        md_file = MD_DIR / mds[0]
        md_text = md_file.read_text(encoding='utf-8')

        # Find which hero embeds already exist
        existing = set(re.findall(r'data-exhibit="([^"]+)"', md_text))
        missing = [h for h in hero_ids if h not in existing]
        if not missing:
            continue

        # Generate embeds only for missing heroes
        blocks = []
        for hid in missing:
            entry = lookup.get(hid)
            if entry:
                blocks.append(generate_embed_html(entry))
        if not blocks:
            continue

        # Find insertion points
        pts = find_insertion_points(md_text)
        if not pts:
            # Append at end
            md_text += '\n' + '\n'.join(blocks)
        else:
            # Distribute evenly
            n = len(blocks)
            step = max(1, len(pts) // (n + 1))
            placements = []
            for i, blk in enumerate(blocks):
                idx = min((i + 1) * step, len(pts) - 1)
                placements.append((pts[idx][1], blk))
            for pos, blk in reversed(placements):
                md_text = md_text[:pos] + '\n' + blk + '\n' + md_text[pos:]

        md_file.write_text(md_text, encoding='utf-8')
        total += len(blocks)
        modified += 1
        print(f"  + {pid}: +{len(blocks)} embeds ({len(existing)} existed, {len(hero_ids)} heroes)")

    print(f"\n{'='*60}")
    print(f"  Posts modified:  {modified}")
    print(f"  Embeds inserted: {total}")

if __name__ == '__main__':
    main()
