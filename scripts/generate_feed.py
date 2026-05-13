#!/usr/bin/env python3
"""
Generate feed.xml (Atom format) for ChappaquaPoison v2.

Reads posts.json to generate a complete Atom feed with one entry per post.
Includes proper date parsing and staggered timestamps for same-day posts.
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring
from html import escape

SITE_URL = os.environ.get('SITE_URL', 'https://chappaquapoison.com')
FEED_UPDATED = '2026-02-15T12:00:00Z'


def parse_date_context(date_context, post_number):
    """
    Parse date_context string and return ISO 8601 timestamp.

    Handles formats like:
    - "1990s–2015"
    - "Jan 21, 2018"
    - "July 2018"
    - "2020"
    - "Fall 2016"
    - "~Late 2019"
    - "March 9, 2017"
    - etc.

    For date ranges, uses the end date.
    For vague dates, approximates to a reasonable date.
    Staggers same-day posts by adding (post_number * 1 hour) offset.
    """

    if not date_context or not isinstance(date_context, str):
        return FEED_UPDATED

    # Remove timeline references and extra notes
    date_context = re.sub(r'\s*\(Timeline.*?\)', '', date_context)
    date_context = re.sub(r'\s*\(Evidence.*?\)', '', date_context)
    date_context = re.sub(r'\s*\(Overt.*?\)', '', date_context)
    date_context = date_context.strip()

    # Try to parse exact dates first
    exact_formats = [
        '%B %d, %Y',  # "January 27, 2018"
        '%b %d, %Y',  # "Jan 21, 2018"
        '%B %d, %y',  # "January 27, 18"
        '%b %d, %y',  # "Jan 21, 18"
        '%B %Y',      # "January 2018"
        '%b %Y',      # "Jan 2018"
        '%m/%d/%Y',   # "01/27/2018"
        '%m/%d/%y',   # "01/27/18"
    ]

    for fmt in exact_formats:
        try:
            dt = datetime.strptime(date_context, fmt)
            # Add stagger based on post number (1 hour per post)
            dt = dt + timedelta(hours=post_number % 24)
            return dt.isoformat() + 'Z'
        except ValueError:
            continue

    # Handle date ranges: "1993–2015", "2013–2015", "2018–2025", etc.
    range_match = re.match(r'(\d{4})\s*[–-]\s*(\d{4})', date_context)
    if range_match:
        end_year = int(range_match.group(2))
        # Use end of year as date
        dt = datetime(end_year, 12, 31)
        dt = dt + timedelta(hours=post_number % 24)
        return dt.isoformat() + 'Z'

    # Handle "YYYY" alone
    year_match = re.match(r'^(\d{4})$', date_context.strip())
    if year_match:
        year = int(year_match.group(1))
        dt = datetime(year, 12, 31)
        dt = dt + timedelta(hours=post_number % 24)
        return dt.isoformat() + 'Z'

    # Handle "Fall", "Spring", "Summer", "Winter"
    season_match = re.match(
        r'(Spring|Summer|Fall|Winter|Late|Early)\s+(\d{4})',
        date_context,
        re.IGNORECASE
    )
    if season_match:
        season = season_match.group(1).lower()
        year = int(season_match.group(2))

        # Map season to approximate month
        season_months = {
            'spring': 4,
            'summer': 7,
            'fall': 10,
            'winter': 1,
            'early': 3,
            'late': 10,
        }
        month = season_months.get(season, 6)
        dt = datetime(year, month, 15)
        dt = dt + timedelta(hours=post_number % 24)
        return dt.isoformat() + 'Z'

    # Handle decades: "1990s", "2010s"
    decade_match = re.match(r'(\d{3})0s', date_context)
    if decade_match:
        decade = int(decade_match.group(1))
        year = decade * 10 + 9
        dt = datetime(year, 12, 31)
        dt = dt + timedelta(hours=post_number % 24)
        return dt.isoformat() + 'Z'

    # Handle "Pre-YYYY"
    pre_match = re.match(r'Pre-(\d{4})', date_context)
    if pre_match:
        year = int(pre_match.group(1)) - 1
        dt = datetime(year, 12, 31)
        dt = dt + timedelta(hours=post_number % 24)
        return dt.isoformat() + 'Z'

    # Default fallback
    return FEED_UPDATED


def create_feed(posts_data):
    """Create Atom feed element tree."""
    feed = Element('feed')
    feed.set('xmlns', 'http://www.w3.org/2005/Atom')

    # Feed metadata
    SubElement(feed, 'title').text = 'Chappaqua Poison'
    SubElement(feed, 'subtitle').text = 'Archive of curated evidence, reconstruction, and court records'
    SubElement(feed, 'updated').text = FEED_UPDATED

    link = SubElement(feed, 'link')
    link.set('href', f'{SITE_URL}/feed.xml')
    link.set('rel', 'self')

    link = SubElement(feed, 'link')
    link.set('href', SITE_URL)

    feed_id = SubElement(feed, 'id')
    feed_id.text = 'urn:chappaquapoison:feed'

    author = SubElement(feed, 'author')
    SubElement(author, 'name').text = 'Stephen Russell'

    # Get posts and sort by date (newest first)
    posts = posts_data.get('posts', [])

    # Parse dates and sort
    posts_with_dates = []
    for i, post in enumerate(posts):
        date_str = parse_date_context(post.get('date_context'), i)
        posts_with_dates.append((date_str, post, i))

    # Sort by parsed date (reverse chronological)
    posts_with_dates.sort(key=lambda x: x[0], reverse=True)

    # Create entries
    entry_count = 0
    for date_str, post, original_index in posts_with_dates:
        entry = SubElement(feed, 'entry')

        post_id = post.get('id')
        title = post.get('title', 'Untitled')
        summary = post.get('summary', '')
        tags = post.get('tags', [])

        # Title
        SubElement(entry, 'title').text = title

        # Link
        link = SubElement(entry, 'link')
        link.set('href', f'{SITE_URL}/posts/{post_id}')

        # ID (URN)
        entry_id = SubElement(entry, 'id')
        entry_id.text = f'urn:chappaquapoison:post:{post_id}'

        # Updated timestamp
        SubElement(entry, 'updated').text = date_str

        # Summary
        SubElement(entry, 'summary').text = summary

        # Categories (tags)
        for tag in tags:
            category = SubElement(entry, 'category')
            category.set('term', tag)

        # Content with summary and ECS badge info
        content = SubElement(entry, 'content')
        content.set('type', 'html')

        # Build HTML content
        html_content = f'<p>{escape(summary)}</p>\n'
        html_content += '<p><strong>Tags:</strong> '
        html_content += ', '.join([f'<code>{escape(tag)}</code>' for tag in tags])
        html_content += '</p>'

        content.text = html_content

        entry_count += 1

    return feed, entry_count


def main():
    """Generate and write feed.xml."""
    # Load posts.json
    with open('posts.json', 'r') as f:
        posts_data = json.load(f)

    # Create feed
    feed, entry_count = create_feed(posts_data)

    # Write to _site/feed.xml
    feed_path = Path('_site/feed.xml')
    feed_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to pretty-printed XML string
    xml_str = tostring(feed, encoding='unicode')

    # Add XML declaration
    xml_output = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str

    with open(feed_path, 'w') as f:
        f.write(xml_output)

    print(f"Generated feed.xml with {entry_count} entries")
    print(f"Written to: {feed_path}")

if __name__ == '__main__':
    main()
