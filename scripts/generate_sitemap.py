#!/usr/bin/env python3
"""
Generate sitemap.xml for ChappaquaPoison v2.

Reads posts.json and scans _site/tags/ to generate a complete sitemap.xml
covering all posts, static pages, tag pages, and special pages.
"""

import json
import os
import re
from pathlib import Path
from urllib.parse import quote
from xml.etree.ElementTree import Element, SubElement, tostring

# Static page mapping
# Only pages with real content are included in the sitemap.
# Thin/empty pages are excluded until populated.
STATIC_PAGES = {
    'S-2': 'about',
    'S-4': 'methodology',
    'S-5': 'timeline',
    'S-10': 'falsifiability',
    'S-11': 'public-record-notice',
    # EXCLUDED (thin/empty stubs — add back when populated):
    # 'S-3': 'how-to-read',
    # 'S-6': 'evidence',
    # 'S-7': 'people',
    # 'S-8': 'cases',
    # 'S-9': 'patterns',
    # 'S-12': 'audit-log',
    # 'S-13': 'ten-documents',
    # 'S-14': 'public-record-inventory',
}

SITE_URL = os.environ.get('SITE_URL', 'https://chappaquapoison.com')
LASTMOD_DATE = '2026-02-15'

def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def get_tag_slugs():
    """Scan _site/tags/*.html and extract tag slugs."""
    tags_dir = Path('_site/tags')
    slugs = []

    if tags_dir.exists():
        for html_file in sorted(tags_dir.glob('*.html')):
            slug = html_file.stem
            slugs.append(slug)

    return slugs

def create_sitemap(posts_data):
    """Create sitemap.xml element tree."""
    urlset = Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')

    url_count = 0

    # Homepage
    url = SubElement(urlset, 'url')
    SubElement(url, 'loc').text = f'{SITE_URL}/'
    SubElement(url, 'priority').text = '1.0'
    SubElement(url, 'lastmod').text = LASTMOD_DATE
    url_count += 1

    # Search page
    url = SubElement(urlset, 'url')
    SubElement(url, 'loc').text = f'{SITE_URL}/search'
    SubElement(url, 'priority').text = '0.4'
    SubElement(url, 'lastmod').text = LASTMOD_DATE
    url_count += 1

    # Static pages
    for page_id, slug in STATIC_PAGES.items():
        url = SubElement(urlset, 'url')
        SubElement(url, 'loc').text = f'{SITE_URL}/{slug}'
        SubElement(url, 'priority').text = '0.6'
        SubElement(url, 'lastmod').text = LASTMOD_DATE
        url_count += 1

    # All posts
    posts = posts_data.get('posts', [])
    for post in posts:
        post_id = post.get('id')
        if post_id:
            url = SubElement(urlset, 'url')
            SubElement(url, 'loc').text = f'{SITE_URL}/posts/{post_id}'
            SubElement(url, 'priority').text = '0.8'
            SubElement(url, 'lastmod').text = LASTMOD_DATE
            url_count += 1

    # All tag pages
    tag_slugs = get_tag_slugs()
    for slug in tag_slugs:
        url = SubElement(urlset, 'url')
        SubElement(url, 'loc').text = f'{SITE_URL}/tags/{slug}'
        SubElement(url, 'priority').text = '0.5'
        SubElement(url, 'lastmod').text = LASTMOD_DATE
        url_count += 1

    return urlset, url_count

def main():
    """Generate and write sitemap.xml."""
    # Load posts.json
    with open('posts.json', 'r') as f:
        posts_data = json.load(f)

    # Create sitemap
    urlset, url_count = create_sitemap(posts_data)

    # Write to _site/sitemap.xml
    sitemap_path = Path('_site/sitemap.xml')
    sitemap_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to pretty-printed XML string
    xml_str = tostring(urlset, encoding='unicode')

    # Add XML declaration
    xml_output = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str

    with open(sitemap_path, 'w') as f:
        f.write(xml_output)

    print(f"Generated sitemap.xml with {url_count} URLs")
    print(f"Written to: {sitemap_path}")

if __name__ == '__main__':
    main()
