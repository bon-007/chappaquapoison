#!/usr/bin/env python3
"""
ChappaquaPoison v3 QA Test Harness
===================================
Validates the built site against all vision documents.
Outputs a structured report with PASS/FAIL for every check.
"""
import json, os, re, sys
from pathlib import Path
from collections import defaultdict

PROJECT = Path(__file__).parent.parent
SITE = PROJECT / '_site'
# V2 reference removed — all assets now in v3

class QA:
    def __init__(self):
        self.results = []
        self.failures = 0
        self.passes = 0

    def check(self, category, name, passed, detail=""):
        status = "PASS" if passed else "FAIL"
        if not passed:
            self.failures += 1
        else:
            self.passes += 1
        self.results.append((category, name, status, detail))

    def report(self):
        print("\n" + "=" * 70)
        print("  CHAPPAQUAPOISON V3 — QA TEST HARNESS REPORT")
        print("=" * 70)

        cats = defaultdict(list)
        for cat, name, status, detail in self.results:
            cats[cat].append((name, status, detail))

        for cat, items in cats.items():
            fails = sum(1 for _, s, _ in items if s == "FAIL")
            passes = sum(1 for _, s, _ in items if s == "PASS")
            icon = "❌" if fails else "✅"
            print(f"\n{icon} {cat} ({passes} pass, {fails} fail)")
            print("-" * 60)
            for name, status, detail in items:
                marker = "  ✓" if status == "PASS" else "  ✗"
                line = f"{marker} {name}"
                if detail and status == "FAIL":
                    line += f" — {detail}"
                print(line)

        print(f"\n{'=' * 70}")
        print(f"  TOTAL: {self.passes} passed, {self.failures} failed")
        if self.failures == 0:
            print("  🎉 ALL CHECKS PASSED")
        else:
            print(f"  ⚠️  {self.failures} issues need fixing")
        print("=" * 70)
        return self.failures

qa = QA()

# ============================================================
# 1. STRUCTURAL CHECKS — Does _site exist with right shape?
# ============================================================
qa.check("STRUCTURE", "_site directory exists", SITE.exists())
qa.check("STRUCTURE", "posts/ directory exists", (SITE / 'posts').exists())
qa.check("STRUCTURE", "tags/ directory exists", (SITE / 'tags').exists())
qa.check("STRUCTURE", "css/ directory exists", (SITE / 'css').exists())
qa.check("STRUCTURE", "js/ directory exists", (SITE / 'js').exists())
qa.check("STRUCTURE", "images/ directory exists", (SITE / 'images').exists())
qa.check("STRUCTURE", "Evidence/ directory exists", (SITE / 'Evidence').exists())

# ============================================================
# 2. POST COMPLETENESS — All 46 beats + 2 interstitials present?
# ============================================================
if (SITE / 'posts').exists():
    post_files = sorted((SITE / 'posts').glob('B*.html'))
    post_ids = [f.stem for f in post_files]
    expected_beats = set(f'B{i:02d}' for i in range(1, 47))
    expected_interstitials = {'B12A', 'B14A'}
    expected_all = expected_beats | expected_interstitials
    qa.check("POSTS", f"48 post HTML files exist ({len(post_files)} found)",
             len(post_files) == 48,
             f"Missing: {expected_all - set(post_ids)}" if len(post_files) != 48 else "")

    for i in range(1, 47):
        bid = f"B{i:02d}"
        qa.check("POSTS", f"{bid}.html exists", (SITE / 'posts' / f'{bid}.html').exists())

    # Interstitial posts
    for inter in ['B12A', 'B14A']:
        qa.check("POSTS", f"{inter}.html exists", (SITE / 'posts' / f'{inter}.html').exists())

# ============================================================
# 3. BANNER CHECKS — 46 beats
# ============================================================
banner_dir = SITE / 'images' / 'banners' / 'v3'

gaps = []
svg_beats = []
png_beats = []
missing_beats = []

for beat_num in range(1, 47):
    bid = f"B{beat_num:02d}"
    png = banner_dir / f"banner_{bid}_banner.png"
    svg = banner_dir / f"banner_{bid}_banner.svg"

    if png.exists():
        png_beats.append(beat_num)
        # Check it's not tiny (< 10KB suggests placeholder)
        size = png.stat().st_size
        qa.check("BANNERS", f"{bid} banner is PNG ({size//1024}KB)",
                 size > 10000, f"Only {size} bytes — likely placeholder")
    elif svg.exists():
        svg_beats.append(beat_num)
        qa.check("BANNERS", f"{bid} banner is PNG (not SVG placeholder)",
                 False, "SVG placeholder — needs real PNG banner")
    else:
        missing_beats.append(beat_num)
        qa.check("BANNERS", f"{bid} banner exists", False, "No banner file at all")

qa.check("BANNERS", f"Total PNG banners: {len(png_beats)}/46", len(png_beats) >= 40,
         f"SVG placeholders: {svg_beats}, Missing: {missing_beats}")

# Check banner references in HTML actually resolve
if (SITE / 'index.html').exists():
    idx_html = (SITE / 'index.html').read_text()
    banner_refs = re.findall(r'images/banners/v3/banner_B\d+_banner\.\w+', idx_html)
    for ref in set(banner_refs):
        ref_path = SITE / ref
        qa.check("BANNERS", f"Homepage banner ref resolves: {Path(ref).name}",
                 ref_path.exists(), f"Missing: {ref}")

# ============================================================
# 4. HERO IMAGE
# ============================================================
if (SITE / 'index.html').exists():
    idx_html = (SITE / 'index.html').read_text()
    hero_match = re.search(r'src="([^"]*hero[^"]*)"', idx_html)
    if hero_match:
        hero_path = hero_match.group(1).lstrip('./')
        hero_file = SITE / hero_path
        qa.check("HERO", f"Hero image exists: {hero_path}", hero_file.exists(),
                 "Hero image referenced in HTML but file is missing")
    else:
        qa.check("HERO", "Hero image referenced in HTML", False, "No hero image src found")

# ============================================================
# 5. CSS & ASSETS
# ============================================================
for css_file in ['tokens.css', 'print.css', 'plyr.css']:
    qa.check("CSS", f"{css_file} exists in _site/css/",
             (SITE / 'css' / css_file).exists())

qa.check("ASSETS", "favicon.svg exists", (SITE / 'favicon.svg').exists())
qa.check("ASSETS", "plyr.min.js exists", (SITE / 'js' / 'plyr.min.js').exists())
qa.check("ASSETS", "_redirects exists", (SITE / '_redirects').exists())

# ============================================================
# 6. STATIC PAGES
# ============================================================
REQUIRED_PAGES = [
    'index.html', 'about.html', 'timeline.html', 'evidence.html',
    'search.html', 'methodology.html', 'how-to-read.html',
    'falsifiability.html', 'cases.html', 'patterns.html', 'people.html',
    'public-record-notice.html', 'public-record-inventory.html',
    'audit-log.html', 'ten-documents.html', '404.html'
]
for page in REQUIRED_PAGES:
    exists = (SITE / page).exists()
    size = (SITE / page).stat().st_size if exists else 0
    qa.check("PAGES", f"{page} exists ({size//1024}KB)", exists and size > 500,
             f"Missing or empty" if not (exists and size > 500) else "")

# ============================================================
# 7. ABOUT PAGE CONTENT — Check against v3 narrative
# ============================================================
if (SITE / 'about.html').exists():
    about = (SITE / 'about.html').read_text()
    # Should reference 45 beats / 9 acts (not 50 scenes)
    has_45 = '45' in about or 'forty-five' in about.lower()
    has_50 = 'fifty narrative scenes' in about.lower() or 'fifty scenes' in about.lower()
    qa.check("ABOUT", "References 45 beats (not 50 scenes)",
             has_45 or not has_50,
             "Still says 'fifty scenes' — needs update to 45 beats")

    # Should reference the spine
    has_spine = 'custody order remain' in about.lower() or 'why does the' in about.lower()
    qa.check("ABOUT", "Contains the dramatic spine question", has_spine,
             "Missing: 'why does the custody order remain?'")

    # Should reference 9 acts
    has_9_acts = '9 acts' in about.lower() or 'nine acts' in about.lower()
    qa.check("ABOUT", "References 9 acts", has_9_acts,
             "Should reference 9-act structure")

# ============================================================
# 8. EVIDENCE INDEX COMPLETENESS
# ============================================================
if (SITE / 'evidence.html').exists():
    ev_html = (SITE / 'evidence.html').read_text()
    ev_rows = ev_html.count('evidence-row')
    qa.check("EVIDENCE", f"Evidence index has entries ({ev_rows} found)",
             ev_rows > 200, f"Only {ev_rows} evidence rows — expected 280+")

# Check Evidence files on disk
if (SITE / 'Evidence').exists():
    ev_files = list((SITE / 'Evidence').rglob('*'))
    ev_files = [f for f in ev_files if f.is_file()]
    qa.check("EVIDENCE", f"Evidence files in _site ({len(ev_files)} found)",
             len(ev_files) >= 900, f"Only {len(ev_files)} — v2 has 935")

    # Check for extensionless files
    no_ext = [f for f in ev_files if '.' not in f.name]
    qa.check("EVIDENCE", f"No extensionless evidence files ({len(no_ext)} found)",
             len(no_ext) == 0,
             f"Files without extensions: {[f.name[:40] for f in no_ext[:5]]}")

# Spot-check key evidence series
ev_dir = SITE / 'Evidence'
if ev_dir.exists():
    for series, expected_min in [('A-', 8), ('B-', 10), ('C-', 11), ('D-', 30), ('K-', 50)]:
        count = len([f for f in ev_dir.iterdir() if f.name.startswith(series)])
        qa.check("EVIDENCE", f"{series}series files ({count} found, need {expected_min}+)",
                 count >= expected_min, f"Only {count}")

# ============================================================
# 9. POSTS.JSON INTEGRITY
# ============================================================
posts_file = PROJECT / 'posts.json'
if posts_file.exists():
    data = json.loads(posts_file.read_text())
    posts = data.get('posts', [])
    visible_posts = [p for p in posts if not p.get('hidden', False)]
    qa.check("INDEX", f"posts.json has 48 visible entries (46 beats + 2 interstitials) ({len(visible_posts)} found)", len(visible_posts) == 48)

    # Check each post has required fields
    required_fields = ['id', 'title', 'slug', 'act', 'tags', 'summary']
    for post in posts:
        pid = post.get('id', '?')
        for field in required_fields:
            if field not in post or not post[field]:
                qa.check("INDEX", f"{pid} has '{field}' field", False, f"Missing or empty")
                break

# ============================================================
# 10. MARKDOWN SOURCE CHECKS
# ============================================================
md_dir = PROJECT / 'posts' / 'md'
if md_dir.exists():
    md_files = sorted(md_dir.glob('B*_*.md'))
    qa.check("MARKDOWN", f"48 beat markdown files ({len(md_files)} found, includes interstitials)",
             len(md_files) >= 48)

    short_beats = []
    for md_file in md_files:
        content = md_file.read_text()
        word_count = len(content.split())
        if word_count < 300:
            short_beats.append((md_file.stem, word_count))

    qa.check("MARKDOWN", f"No critically short beats (<300 words)",
             len(short_beats) == 0,
             f"Short: {short_beats}" if short_beats else "")

# ============================================================
# 11. NAVIGATION & INTERNAL LINKS
# ============================================================
if (SITE / 'posts').exists():
    # Check first and last posts have correct nav
    b01 = SITE / 'posts' / 'B01.html'
    b46 = SITE / 'posts' / 'B48.html'
    if b01.exists():
        b01_html = b01.read_text()
        qa.check("NAV", "B01 has next link to B02", 'B02.html' in b01_html)
    if b46.exists():
        b46_html = b46.read_text()
        qa.check("NAV", "B48 has prev link to B47", 'B47.html' in b46_html)

# ============================================================
# 12. TAG PAGES
# ============================================================
if (SITE / 'tags').exists():
    tag_count = len(list((SITE / 'tags').glob('*.html')))
    qa.check("TAGS", f"Tag pages generated ({tag_count} found)", tag_count > 100)

# ============================================================
# REPORT
# ============================================================
failures = qa.report()

# Write JSON report
report_path = PROJECT / 'Audits' / 'qa_report.json'
report_path.parent.mkdir(exist_ok=True)
report_data = {
    'total_checks': qa.passes + qa.failures,
    'passed': qa.passes,
    'failed': qa.failures,
    'results': [{'category': c, 'name': n, 'status': s, 'detail': d}
                for c, n, s, d in qa.results]
}
report_path.write_text(json.dumps(report_data, indent=2))
print(f"\nJSON report: {report_path}")

sys.exit(1 if failures else 0)
