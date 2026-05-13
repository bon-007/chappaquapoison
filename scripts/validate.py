#!/usr/bin/env python3
"""
ChappaquaPoison v2 — Comprehensive Validation Script

Validates:
1. posts.json integrity (required fields, no empty titles)
2. ECS completeness (flags posts without ECS scores)
3. Evidence reference check (verify collected_files paths exist)
4. Tag consistency (flags tags used only once)
5. Cross-link symmetry (if A links to B, B should link to A)
6. Phase assignment (every post has a valid phase)
7. Banner coverage (check which posts have banner SVGs)
8. Timeline coverage (check posts.json dates vs timeline.json entries)

Outputs:
- Console report
- Markdown validation report saved to _build/validation_report.md
"""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# Color codes for console output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ValidationReport:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.issues = []
        self.warnings = []
        self.passes = []
        self.stats = {}

    def add_issue(self, category: str, message: str):
        self.issues.append({"category": category, "message": message})

    def add_warning(self, category: str, message: str):
        self.warnings.append({"category": category, "message": message})

    def add_pass(self, category: str, message: str):
        self.passes.append({"category": category, "message": message})

    def add_stat(self, key: str, value):
        self.stats[key] = value

    def print_console_report(self):
        """Print formatted report to console."""
        print(f"\n{Colors.HEADER}{Colors.BOLD}=== ChappaquaPoison v2 Validation Report ==={Colors.ENDC}\n")

        # Statistics
        print(f"{Colors.BOLD}STATISTICS{Colors.ENDC}")
        for key, value in self.stats.items():
            print(f"  {key}: {value}")
        print()

        # Passes
        if self.passes:
            print(f"{Colors.OKGREEN}{Colors.BOLD}✓ PASSES ({len(self.passes)}){Colors.ENDC}")
            for item in self.passes:
                print(f"  ✓ [{item['category']}] {item['message']}")
            print()

        # Warnings
        if self.warnings:
            print(f"{Colors.WARNING}{Colors.BOLD}⚠ WARNINGS ({len(self.warnings)}){Colors.ENDC}")
            for item in self.warnings:
                print(f"  ⚠ [{item['category']}] {item['message']}")
            print()

        # Issues
        if self.issues:
            print(f"{Colors.FAIL}{Colors.BOLD}✗ ISSUES ({len(self.issues)}){Colors.ENDC}")
            for item in self.issues:
                print(f"  ✗ [{item['category']}] {item['message']}")
            print()

        # Summary
        if not self.issues:
            print(f"{Colors.OKGREEN}{Colors.BOLD}All checks passed!{Colors.ENDC}\n")
        else:
            print(f"{Colors.FAIL}{Colors.BOLD}{len(self.issues)} issues found. Please review.{Colors.ENDC}\n")

    def save_markdown_report(self, output_path: str):
        """Save report to markdown file."""
        md_lines = [
            "# ChappaquaPoison v2 — Validation Report",
            f"**Generated:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Statistics",
            ""
        ]

        for key, value in self.stats.items():
            md_lines.append(f"- **{key}:** {value}")

        md_lines.extend(["", "## Validation Results", ""])

        # Passes
        if self.passes:
            md_lines.append(f"### ✓ Passes ({len(self.passes)})")
            md_lines.append("")
            for item in self.passes:
                md_lines.append(f"- `{item['category']}` — {item['message']}")
            md_lines.append("")

        # Warnings
        if self.warnings:
            md_lines.append(f"### ⚠ Warnings ({len(self.warnings)})")
            md_lines.append("")
            for item in self.warnings:
                md_lines.append(f"- `{item['category']}` — {item['message']}")
            md_lines.append("")

        # Issues
        if self.issues:
            md_lines.append(f"### ✗ Issues ({len(self.issues)})")
            md_lines.append("")
            for item in self.issues:
                md_lines.append(f"- `{item['category']}` — {item['message']}")
            md_lines.append("")

        # Summary
        md_lines.append("## Summary")
        md_lines.append("")
        if not self.issues:
            md_lines.append("✓ All checks passed.")
        else:
            md_lines.append(f"✗ **{len(self.issues)} issues** found.")
            md_lines.append(f"⚠ **{len(self.warnings)} warnings** found.")

        # Ensure _build directory exists
        build_dir = self.base_path / "_build"
        build_dir.mkdir(exist_ok=True)

        output_file = build_dir / "validation_report.md"
        with open(output_file, 'w') as f:
            f.write("\n".join(md_lines))

        print(f"\n{Colors.OKGREEN}Report saved to: {output_file}{Colors.ENDC}")


def load_json(file_path: Path) -> dict:
    """Load JSON file safely."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"{Colors.FAIL}Error loading {file_path}: {e}{Colors.ENDC}")
        return {}


def validate_posts_json(report: ValidationReport, posts_data: dict) -> Tuple[int, dict]:
    """Validate posts.json integrity."""
    print(f"{Colors.OKCYAN}Validating posts.json...{Colors.ENDC}")

    issues_found = 0
    posts_by_id = {}

    static_pages = posts_data.get('static_pages', [])
    posts = posts_data.get('posts', [])

    report.add_stat("Total Static Pages", len(static_pages))
    report.add_stat("Total Posts", len(posts))

    # Check static pages
    for page in static_pages:
        if not page.get('id') or not page.get('title'):
            report.add_issue("posts.json", f"Static page missing id or title: {page}")
            issues_found += 1

    # Check posts
    required_fields = ['id', 'number', 'title', 'phase', 'phase_name', 'summary', 'tags']

    for post in posts:
        post_id = post.get('id')
        posts_by_id[post_id] = post

        # Check required fields
        for field in required_fields:
            if field not in post or post[field] is None:
                report.add_issue("posts.json", f"Post {post_id} missing or null field: {field}")
                issues_found += 1

        # Check for empty title
        if not post.get('title') or not post.get('title').strip():
            report.add_issue("posts.json", f"Post {post_id} has empty title")
            issues_found += 1

        # Check phase validity
        valid_phases = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']
        if post.get('phase') and post.get('phase') not in valid_phases:
            report.add_issue("posts.json", f"Post {post_id} has invalid phase: {post.get('phase')}")
            issues_found += 1

    if issues_found == 0:
        report.add_pass("posts.json", "All required fields present, no empty titles")

    return issues_found, posts_by_id


def validate_ecs_completeness(report: ValidationReport, posts_by_id: dict):
    """Check ECS score completeness."""
    print(f"{Colors.OKCYAN}Validating ECS completeness...{Colors.ENDC}")

    unscored = []
    scored = defaultdict(int)

    for post_id, post in posts_by_id.items():
        ecs = post.get('ecs')
        if ecs is None:
            unscored.append(post_id)
        else:
            # Categorize by tier
            if 90 <= ecs <= 100:
                scored['Tier 1 (90-100)'] += 1
            elif 75 <= ecs < 90:
                scored['Tier 2 (75-89)'] += 1
            elif 60 <= ecs < 75:
                scored['Tier 3 (60-74)'] += 1
            elif 50 <= ecs < 60:
                scored['Tier 4 (50-59)'] += 1

    report.add_stat("Posts with ECS scores", len(posts_by_id) - len(unscored))
    report.add_stat("Posts without ECS scores", len(unscored))

    for tier, count in sorted(scored.items()):
        report.add_stat(f"  {tier}", count)

    if unscored:
        report.add_warning("ECS", f"{len(unscored)} posts lack ECS scores: {', '.join(unscored[:10])}")
        if len(unscored) > 10:
            report.add_warning("ECS", f"... and {len(unscored) - 10} more")
    else:
        report.add_pass("ECS", "All posts have ECS scores")


def validate_evidence_references(report: ValidationReport, base_path: Path, posts_by_id: dict):
    """Check that collected_files paths exist on disk."""
    print(f"{Colors.OKCYAN}Validating evidence references...{Colors.ENDC}")

    missing_files = []
    found_files = 0
    referenced_files = set()

    for post_id, post in posts_by_id.items():
        evidence = post.get('evidence', {})
        collected_files = evidence.get('collected_files', [])

        for file_path in collected_files:
            referenced_files.add(file_path)
            full_path = base_path / file_path

            if not full_path.exists():
                missing_files.append((post_id, file_path))
            else:
                found_files += 1

    report.add_stat("Evidence files referenced", len(referenced_files))
    report.add_stat("Evidence files found on disk", found_files)
    report.add_stat("Evidence files missing", len(missing_files))

    if missing_files:
        report.add_warning("Evidence", f"{len(missing_files)} referenced files not found:")
        for post_id, file_path in missing_files[:10]:
            report.add_warning("Evidence", f"  {post_id} references: {file_path}")
        if len(missing_files) > 10:
            report.add_warning("Evidence", f"  ... and {len(missing_files) - 10} more")
    else:
        report.add_pass("Evidence", "All referenced evidence files exist")


def validate_tag_consistency(report: ValidationReport, posts_by_id: dict):
    """Flag tags used only once (potential typos)."""
    print(f"{Colors.OKCYAN}Validating tag consistency...{Colors.ENDC}")

    tag_counts = defaultdict(list)
    all_tags = set()

    for post_id, post in posts_by_id.items():
        for tag in post.get('tags', []):
            tag_counts[tag].append(post_id)
            all_tags.add(tag)

    report.add_stat("Total unique tags", len(all_tags))

    single_use_tags = {tag: posts for tag, posts in tag_counts.items() if len(posts) == 1}

    if single_use_tags:
        report.add_warning("Tags", f"{len(single_use_tags)} tags used only once (possible typos):")
        for tag, posts in sorted(single_use_tags.items())[:15]:
            report.add_warning("Tags", f"  '{tag}' (used in {posts[0]})")
        if len(single_use_tags) > 15:
            report.add_warning("Tags", f"  ... and {len(single_use_tags) - 15} more")
    else:
        report.add_pass("Tags", "No single-use tags detected")


def validate_cross_links(report: ValidationReport, posts_by_id: dict):
    """Check cross-link symmetry."""
    print(f"{Colors.OKCYAN}Validating cross-link symmetry...{Colors.ENDC}")

    asymmetric_links = []
    total_links = 0
    symmetric_links = 0

    for post_id, post in posts_by_id.items():
        cross_links = post.get('cross_links', [])
        total_links += len(cross_links)

        for linked_id in cross_links:
            if linked_id not in posts_by_id:
                report.add_issue("CrossLinks", f"Post {post_id} links to non-existent post {linked_id}")
                continue

            # Check if reverse link exists
            target_post = posts_by_id[linked_id]
            target_links = target_post.get('cross_links', [])

            if post_id in target_links:
                symmetric_links += 1
            else:
                asymmetric_links.append((post_id, linked_id))

    report.add_stat("Total cross-links", total_links)
    report.add_stat("Symmetric links", symmetric_links)
    report.add_stat("Asymmetric links", len(asymmetric_links))

    if asymmetric_links:
        report.add_warning("CrossLinks", f"{len(asymmetric_links)} asymmetric links (A→B but not B→A):")
        for source, target in asymmetric_links[:10]:
            report.add_warning("CrossLinks", f"  {source} → {target}")
        if len(asymmetric_links) > 10:
            report.add_warning("CrossLinks", f"  ... and {len(asymmetric_links) - 10} more")
    elif total_links > 0:
        report.add_pass("CrossLinks", "All cross-links are symmetric")


def validate_phase_assignment(report: ValidationReport, posts_by_id: dict):
    """Check phase assignment validity."""
    print(f"{Colors.OKCYAN}Validating phase assignment...{Colors.ENDC}")

    valid_phases = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']
    phase_distribution = defaultdict(int)
    invalid_phases = []

    for post_id, post in posts_by_id.items():
        phase = post.get('phase')
        if phase not in valid_phases:
            invalid_phases.append((post_id, phase))
        else:
            phase_distribution[phase] += 1

    report.add_stat("Posts with valid phases", len(posts_by_id) - len(invalid_phases))

    for phase in sorted(phase_distribution.keys()):
        report.add_stat(f"  Phase {phase}", phase_distribution[phase])

    if invalid_phases:
        report.add_issue("Phases", f"{len(invalid_phases)} posts with invalid phases:")
        for post_id, phase in invalid_phases:
            report.add_issue("Phases", f"  {post_id}: {phase}")
    else:
        report.add_pass("Phases", "All posts have valid phase assignments")


def validate_banner_coverage(report: ValidationReport, base_path: Path):
    """Check which posts have banner SVGs."""
    print(f"{Colors.OKCYAN}Validating banner coverage...{Colors.ENDC}")

    banners_path = base_path / "Images" / "banners"
    if not banners_path.exists():
        report.add_warning("Banners", "Images/banners directory not found")
        return

    banner_files = list(banners_path.glob("**/*.svg"))
    report.add_stat("Banner SVGs found", len(banner_files))

    if len(banner_files) == 0:
        report.add_warning("Banners", "No banner SVGs found in Images/banners/")
    else:
        report.add_pass("Banners", f"{len(banner_files)} banner SVGs available")


def validate_timeline_coverage(report: ValidationReport, base_path: Path, posts_by_id: dict):
    """Check posts.json dates vs timeline.json entries."""
    print(f"{Colors.OKCYAN}Validating timeline coverage...{Colors.ENDC}")

    timeline_path = base_path / "timeline.json"
    if not timeline_path.exists():
        report.add_warning("Timeline", "timeline.json not found")
        return

    timeline_data = load_json(timeline_path)
    timeline_entries = timeline_data.get('entries', [])

    report.add_stat("Timeline entries", len(timeline_entries))

    posts_with_dates = [p for p in posts_by_id.values() if p.get('date_context')]
    report.add_stat("Posts with date context", len(posts_with_dates))

    if len(posts_with_dates) > 0:
        report.add_pass("Timeline", f"{len(posts_with_dates)} posts have date context")


def main():
    """Run all validation checks."""
    base_path = Path(__file__).parent.parent

    print(f"\n{Colors.BOLD}ChappaquaPoison v2 Validation Script{Colors.ENDC}")
    print(f"Base path: {base_path}\n")

    report = ValidationReport(base_path)

    # Load main files
    posts_path = base_path / "posts.json"
    posts_data = load_json(posts_path)

    if not posts_data:
        print(f"{Colors.FAIL}Failed to load posts.json{Colors.ENDC}")
        sys.exit(1)

    # Run validations
    issues, posts_by_id = validate_posts_json(report, posts_data)
    validate_ecs_completeness(report, posts_by_id)
    validate_evidence_references(report, base_path, posts_by_id)
    validate_tag_consistency(report, posts_by_id)
    validate_cross_links(report, posts_by_id)
    validate_phase_assignment(report, posts_by_id)
    validate_banner_coverage(report, base_path)
    validate_timeline_coverage(report, base_path, posts_by_id)

    # Print reports
    report.print_console_report()
    report.save_markdown_report(str(base_path / "_build" / "validation_report.md"))

    # Exit code
    sys.exit(0 if not report.issues else 1)


if __name__ == "__main__":
    main()
