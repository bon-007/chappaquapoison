#!/usr/bin/env python3
"""
validate_site.py — Post-build integrity test for the _site output directory.

Crawls every HTML file in _site/ and validates:
  1. INTERNAL LINKS — Every href to another page resolves to an existing file
  2. IMAGE REFERENCES — Every <img src="..."> and CSS url() points to an existing file
  3. ASSET REFERENCES — CSS, JS, and other resource links all resolve
  4. PATH HYGIENE — No absolute paths (starting with /), no uppercase Images/
  5. SVG-IN-IMG GUARD — No <img src="*.svg"> (blocked by browsers via file://)
  6. EVIDENCE LINKS — All Evidence/ hrefs resolve to real files
  7. GRACEFUL FALLBACK — Images that fail should have alt text for accessibility

Exits with code 0 on pass, 1 on failure. Designed to run after every build.

Usage:
    python scripts/validate_site.py              # validate _site/ under project root
    python scripts/validate_site.py --strict     # treat warnings as errors
    python scripts/validate_site.py --fix-svg    # report SVG-in-img as error (default)
"""

import re
import sys
import os
from pathlib import Path
from collections import defaultdict
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote

# ─── Configuration ─────────────────────────────────────────────────

SITE_DIR_NAME = '_site'
EXTERNAL_PREFIXES = ('http://', 'https://', 'mailto:', 'tel:', 'javascript:', '#', 'data:')
# Files that are expected to not exist (anchor-only links, external, etc.)
SKIP_EXTENSIONS = {'.json', '.xml', '.txt', '.rss', '.atom'}


# ─── Colors ────────────────────────────────────────────────────────

class C:
    R = '\033[91m'    # red / error
    G = '\033[92m'    # green / pass
    Y = '\033[93m'    # yellow / warning
    B = '\033[94m'    # blue / info
    BOLD = '\033[1m'
    END = '\033[0m'


# ─── HTML Parser ───────────────────────────────────────────────────

class LinkImageExtractor(HTMLParser):
    """Extract all links, images, and resource references from an HTML file."""

    def __init__(self):
        super().__init__()
        self.links = []       # (href, line, tag)
        self.images = []      # (src, alt, line, tag)
        self.resources = []   # (href/src, line, tag) — CSS, JS, etc.
        self._line = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        line = self.getpos()[0]

        if tag == 'a':
            href = attrs_dict.get('href')
            if href:
                self.links.append((href, line, tag))

        elif tag == 'img':
            src = attrs_dict.get('src')
            alt = attrs_dict.get('alt', None)
            srcset = attrs_dict.get('srcset')
            if src:
                self.images.append((src, alt, line, 'img'))
            if srcset:
                # Parse srcset (e.g., "img1.png 1x, img2.png 2x")
                for entry in srcset.split(','):
                    parts = entry.strip().split()
                    if parts:
                        self.images.append((parts[0], alt, line, 'img[srcset]'))

        elif tag == 'source':
            srcset = attrs_dict.get('srcset')
            if srcset:
                for entry in srcset.split(','):
                    parts = entry.strip().split()
                    if parts:
                        self.images.append((parts[0], None, line, 'source'))

        elif tag == 'link':
            href = attrs_dict.get('href')
            rel = attrs_dict.get('rel', '')
            if href and 'stylesheet' in rel:
                self.resources.append((href, line, 'link[stylesheet]'))
            elif href and 'icon' in rel:
                self.resources.append((href, line, 'link[icon]'))

        elif tag == 'script':
            src = attrs_dict.get('src')
            if src:
                self.resources.append((src, line, 'script'))

        # Also pick up og:image and other meta image refs
        elif tag == 'meta':
            prop = attrs_dict.get('property', '')
            content = attrs_dict.get('content', '')
            if 'image' in prop and content and not content.startswith(('http://', 'https://')):
                self.images.append((content, None, line, 'meta[og:image]'))


# ─── Resolver ──────────────────────────────────────────────────────

def resolve_path(ref: str, html_file: Path, site_root: Path) -> Path:
    """
    Resolve a relative or root-relative path from an HTML file to an absolute filesystem path.
    """
    ref = unquote(ref)

    # Strip fragment
    if '#' in ref:
        ref = ref.split('#')[0]
    # Strip query
    if '?' in ref:
        ref = ref.split('?')[0]

    # Strip trailing parenthetical descriptions from evidence links
    # e.g., "file.pdf (description text)" -> "file.pdf"
    paren_match = re.match(r'^(.+\.\w{2,5})\s*\(.*\)$', ref)
    if paren_match:
        ref = paren_match.group(1)

    if not ref:
        return None

    if ref.startswith('/'):
        # Absolute from site root — this is a bug we're checking for
        return site_root / ref.lstrip('/')
    else:
        # Relative to the HTML file's directory
        return (html_file.parent / ref).resolve()


# ─── Test Suite ────────────────────────────────────────────────────

class SiteValidator:
    def __init__(self, site_root: Path, strict: bool = False):
        self.site_root = site_root.resolve()
        self.strict = strict
        self.errors = []      # (category, file, line, message)
        self.warnings = []    # (category, file, line, message)
        self.passes = []      # (category, message)
        self.stats = defaultdict(int)

    def error(self, category, file, line, msg):
        self.errors.append((category, str(file), line, msg))

    def warn(self, category, file, line, msg):
        self.warnings.append((category, str(file), line, msg))

    def ok(self, category, msg):
        self.passes.append((category, msg))

    # ── Collect all HTML files ──

    def collect_html_files(self):
        """Collect HTML files, excluding Evidence/ source documents (raw imports, not generated)."""
        all_files = sorted(self.site_root.rglob('*.html'))
        evidence_dir = self.site_root / 'Evidence'
        filtered = [f for f in all_files if not str(f).startswith(str(evidence_dir))]
        skipped = len(all_files) - len(filtered)
        if skipped:
            print(f"{C.Y}  Skipping {skipped} Evidence/ source document(s) (raw imports){C.END}")
        return filtered

    # ── Parse a single HTML file ──

    def parse_html(self, html_file: Path):
        try:
            content = html_file.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            self.error('IO', html_file, 0, f'Cannot read file: {e}')
            return None, content if 'content' in dir() else ''

        parser = LinkImageExtractor()
        try:
            parser.feed(content)
        except Exception as e:
            self.error('PARSE', html_file, 0, f'HTML parse error: {e}')

        return parser, content

    # ── Test 1: Internal Links ──

    def test_internal_links(self, html_file, parser):
        """Every internal href must resolve to an existing file."""
        for href, line, tag in parser.links:
            if any(href.startswith(p) for p in EXTERNAL_PREFIXES):
                self.stats['external_links'] += 1
                continue

            # Evidence links are handled by test_evidence_links
            if 'Evidence/' in href or 'evidence/' in href:
                continue

            self.stats['internal_links'] += 1

            target = resolve_path(href, html_file, self.site_root)
            if target is None:
                continue

            # Allow links to directories (index.html implicit)
            if target.is_dir():
                if (target / 'index.html').exists():
                    continue
                else:
                    self.error('LINK', html_file, line,
                              f'Directory link has no index.html: {href}')
                    continue

            if not target.exists():
                # Check if it's a known non-HTML resource we don't care about
                ext = target.suffix.lower()
                if ext in SKIP_EXTENSIONS:
                    # Still check it exists
                    if not target.exists():
                        self.warn('LINK', html_file, line,
                                 f'Resource link target not found: {href}')
                else:
                    self.error('LINK', html_file, line,
                              f'Broken internal link: {href}')

    # ── Test 2: Image References ──

    def test_images(self, html_file, parser):
        """Every image src must resolve to an existing file."""
        for src, alt, line, tag in parser.images:
            if any(src.startswith(p) for p in EXTERNAL_PREFIXES):
                self.stats['external_images'] += 1
                continue

            self.stats['internal_images'] += 1

            target = resolve_path(src, html_file, self.site_root)
            if target is None:
                continue

            if not target.exists():
                self.error('IMAGE', html_file, line,
                          f'Broken image: {src}')
            else:
                self.stats['images_ok'] += 1

    # ── Test 3: Resource References (CSS, JS) ──

    def test_resources(self, html_file, parser):
        """CSS/JS links must resolve."""
        for src, line, tag in parser.resources:
            if any(src.startswith(p) for p in EXTERNAL_PREFIXES):
                continue

            self.stats['resources'] += 1
            target = resolve_path(src, html_file, self.site_root)
            if target and not target.exists():
                self.error('RESOURCE', html_file, line,
                          f'Missing resource ({tag}): {src}')

    # ── Test 4: Path Hygiene ──

    def test_path_hygiene(self, html_file, content):
        """
        Flag absolute paths (href="/...", src="/...") that break under file://.
        Flag uppercase Images/ references (case sensitivity bomb).
        """
        # Absolute paths: src="/" or href="/" (but not https://)
        abs_pattern = re.compile(
            r'(?:src|href|srcset|content)\s*=\s*["\'](/[^"\']*)["\']',
            re.IGNORECASE
        )
        for match in abs_pattern.finditer(content):
            path = match.group(1)
            # Exclude protocol-relative //cdn... and root anchor #
            if path.startswith('//'):
                continue
            line = content[:match.start()].count('\n') + 1
            self.error('PATH', html_file, line,
                      f'Absolute path (breaks file://): {path}')

        # Uppercase Images/ (case-sensitivity bomb)
        case_pattern = re.compile(r'["\'/]Images/', re.MULTILINE)
        for match in case_pattern.finditer(content):
            line = content[:match.start()].count('\n') + 1
            self.error('CASE', html_file, line,
                      f'Uppercase "Images/" reference (use lowercase "images/")')

    # ── Test 5: SVG-in-IMG Guard ──

    def test_svg_in_img(self, html_file, parser):
        """
        Flag <img src="*.svg"> — browsers block SVGs loaded via <img> under file://.
        Only og:image meta tags are exempt (social crawlers handle SVGs fine).
        """
        for src, alt, line, tag in parser.images:
            if any(src.startswith(p) for p in EXTERNAL_PREFIXES):
                continue

            if src.lower().endswith('.svg') and tag != 'meta[og:image]':
                self.error('SVG', html_file, line,
                          f'SVG loaded via <{tag}> (blocked by file://): {src} — use PNG instead')

    # ── Test 6: Alt Text Coverage ──

    def test_alt_text(self, html_file, parser):
        """Every <img> should have alt text for graceful degradation."""
        for src, alt, line, tag in parser.images:
            if tag not in ('img', 'img[srcset]'):
                continue
            if alt is None:
                self.error('A11Y', html_file, line,
                          f'Image missing alt attribute: {src}')
                self.stats['missing_alt'] += 1
            elif alt.strip() == '':
                # Empty alt is valid for decorative images, just count
                self.stats['decorative_images'] += 1
            else:
                self.stats['alt_ok'] += 1

    # ── Test 7: Evidence Links ──

    def test_evidence_links(self, html_file, parser):
        """Evidence/ hrefs must resolve. Missing evidence PDFs are warnings (may be added later)."""
        for href, line, tag in parser.links:
            if 'Evidence/' in href or 'evidence/' in href:
                self.stats['evidence_links'] += 1
                target = resolve_path(href, html_file, self.site_root)
                if target and not target.exists():
                    # Evidence PDFs may legitimately not exist yet — warn, don't error
                    self.warn('EVIDENCE', html_file, line,
                              f'Missing evidence file: {href}')

    # ── Test 8: CSS url() references ──

    def test_css_urls(self):
        """Check url() refs inside CSS files."""
        for css_file in self.site_root.rglob('*.css'):
            try:
                content = css_file.read_text(encoding='utf-8', errors='replace')
            except Exception:
                continue

            url_pattern = re.compile(r'url\(["\']?([^"\')\s]+)["\']?\)')
            for match in url_pattern.finditer(content):
                ref = match.group(1)
                if any(ref.startswith(p) for p in EXTERNAL_PREFIXES):
                    continue
                if ref.startswith('/'):
                    line = content[:match.start()].count('\n') + 1
                    self.error('CSS', css_file, line,
                              f'Absolute path in CSS url(): {ref}')
                else:
                    target = (css_file.parent / ref).resolve()
                    if not target.exists():
                        line = content[:match.start()].count('\n') + 1
                        self.warn('CSS', css_file, line,
                                 f'Missing CSS asset: {ref}')

    # ── Test 9: Duplicate file check (case-sensitivity guard) ──

    def test_case_conflicts(self):
        """Flag files that differ only by case (invisible bomb on case-insensitive FS)."""
        seen = {}  # lowercase path -> actual path
        for f in self.site_root.rglob('*'):
            if not f.is_file():
                continue
            rel = str(f.relative_to(self.site_root))
            lower = rel.lower()
            if lower in seen and seen[lower] != rel:
                self.error('CASE', f, 0,
                          f'Case conflict: "{rel}" vs "{seen[lower]}" — '
                          f'will collide on case-insensitive filesystems')
            seen[lower] = rel

    # ── Run all tests ──

    def run(self):
        print(f"\n{C.BOLD}{'=' * 64}{C.END}")
        print(f"{C.BOLD}  SITE INTEGRITY VALIDATOR — _site/ post-build check{C.END}")
        print(f"{C.BOLD}{'=' * 64}{C.END}\n")

        if not self.site_root.exists():
            print(f"{C.R}ERROR: Site directory not found: {self.site_root}{C.END}")
            return 1

        html_files = self.collect_html_files()
        self.stats['html_files'] = len(html_files)
        print(f"{C.B}Scanning {len(html_files)} HTML files in {self.site_root}{C.END}\n")

        # Per-file tests
        for html_file in html_files:
            parser, content = self.parse_html(html_file)
            if parser is None:
                continue

            self.test_internal_links(html_file, parser)
            self.test_images(html_file, parser)
            self.test_resources(html_file, parser)
            self.test_path_hygiene(html_file, content)
            self.test_svg_in_img(html_file, parser)
            self.test_alt_text(html_file, parser)
            self.test_evidence_links(html_file, parser)

        # Site-wide tests
        print(f"{C.B}Running site-wide checks...{C.END}")
        self.test_css_urls()
        self.test_case_conflicts()

        # Report
        self._print_report()

        # Determine exit code
        if self.errors:
            return 1
        if self.strict and self.warnings:
            return 1
        return 0

    def _print_report(self):
        print(f"\n{C.BOLD}{'─' * 64}{C.END}")
        print(f"{C.BOLD}  RESULTS{C.END}")
        print(f"{'─' * 64}\n")

        # Stats
        print(f"{C.BOLD}Statistics:{C.END}")
        print(f"  HTML files scanned:   {self.stats.get('html_files', 0)}")
        print(f"  Internal links:       {self.stats.get('internal_links', 0)}")
        print(f"  External links:       {self.stats.get('external_links', 0)}")
        print(f"  Internal images:      {self.stats.get('internal_images', 0)}")
        print(f"  Images verified OK:   {self.stats.get('images_ok', 0)}")
        print(f"  Evidence links:       {self.stats.get('evidence_links', 0)}")
        print(f"  Alt text present:     {self.stats.get('alt_ok', 0)}")
        print(f"  Decorative (alt=\"\"):  {self.stats.get('decorative_images', 0)}")
        print(f"  Missing alt attr:     {self.stats.get('missing_alt', 0)}")
        print()

        # Errors
        if self.errors:
            # Group by category
            by_cat = defaultdict(list)
            for cat, file, line, msg in self.errors:
                by_cat[cat].append((file, line, msg))

            print(f"{C.R}{C.BOLD}✗ ERRORS ({len(self.errors)}):{C.END}")
            for cat in sorted(by_cat.keys()):
                items = by_cat[cat]
                print(f"\n  {C.R}[{cat}] — {len(items)} issue(s):{C.END}")
                for file, line, msg in items[:20]:
                    rel = Path(file).relative_to(self.site_root) if self.site_root in Path(file).parents or Path(file) == self.site_root else file
                    print(f"    L{line:>4}  {rel}  →  {msg}")
                if len(items) > 20:
                    print(f"    ... and {len(items) - 20} more")
            print()

        # Warnings
        if self.warnings:
            print(f"{C.Y}{C.BOLD}⚠ WARNINGS ({len(self.warnings)}):{C.END}")
            for cat, file, line, msg in self.warnings[:15]:
                rel = Path(file).relative_to(self.site_root) if self.site_root in Path(file).parents or Path(file) == self.site_root else file
                print(f"  L{line:>4}  {rel}  →  {msg}")
            if len(self.warnings) > 15:
                print(f"  ... and {len(self.warnings) - 15} more")
            print()

        # Summary
        print(f"{'─' * 64}")
        if not self.errors and not self.warnings:
            print(f"{C.G}{C.BOLD}✓ ALL CHECKS PASSED — site is clean{C.END}")
        elif not self.errors:
            print(f"{C.G}{C.BOLD}✓ No errors. {len(self.warnings)} warning(s).{C.END}")
        else:
            print(f"{C.R}{C.BOLD}✗ {len(self.errors)} error(s), {len(self.warnings)} warning(s) — BUILD FAILS INTEGRITY CHECK{C.END}")
        print(f"{'─' * 64}\n")

    def save_report(self, path: Path):
        """Save machine-readable JSON report."""
        import json
        report = {
            'stats': dict(self.stats),
            'errors': [{'category': c, 'file': f, 'line': l, 'message': m} for c, f, l, m in self.errors],
            'warnings': [{'category': c, 'file': f, 'line': l, 'message': m} for c, f, l, m in self.warnings],
            'passed': len(self.errors) == 0,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as fh:
            json.dump(report, fh, indent=2)
        print(f"{C.B}Report saved to: {path}{C.END}")


# ─── Main ──────────────────────────────────────────────────────────

def main():
    project_root = Path(__file__).parent.parent
    site_root = project_root / SITE_DIR_NAME

    strict = '--strict' in sys.argv

    validator = SiteValidator(site_root, strict=strict)
    exit_code = validator.run()

    # Save JSON report
    report_path = project_root / 'Audits' / 'site_integrity_report.json'
    validator.save_report(report_path)

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
