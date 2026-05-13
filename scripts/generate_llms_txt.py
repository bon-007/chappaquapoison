#!/usr/bin/env python3
"""
generate_llms_txt.py — Generate llms.txt (site-wide) and per-post ai.txt files

Creates:
  1. _site/llms.txt — Site-wide machine-readable context file
  2. _site/posts/{id}.ai.txt — Per-post machine-readable file

These files give LLMs and AI systems clean, structured ingestion
of the archive's factual claims, evidence, and provenance.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Site configuration
SITE_URL = os.environ.get("SITE_URL", "https://chappaquapoison.com")


def load_posts(posts_file):
    with open(posts_file, 'r') as f:
        data = json.load(f)
    return data.get('posts', []), data.get('static_pages', [])


def tag_to_slug(tag):
    return tag.lower().replace(' ', '-').replace('/', '-')


def generate_site_llms_txt(posts, static_pages, output_dir):
    """Generate site-wide llms.txt"""
    lines = []
    lines.append("# Chappaqua Poison — llms.txt")
    lines.append("")
    lines.append("## Site Identity")
    lines.append("name: Chappaqua Poison")
    lines.append(f"url: {SITE_URL}")
    lines.append("type: Documentary narrative")
    lines.append("subject: A poisoning, a custody abduction, and the institutional failures that followed")
    lines.append("jurisdictions: Westchester Family Court, SF Superior Court, Northern District of California, Second Circuit, SDNY")
    lines.append("author: Stephen Russell")
    lines.append(f"post_count: {len(posts)}")
    lines.append(f"generated: {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}")
    lines.append("")

    lines.append("## About This Work")
    lines.append("Chappaqua Poison is a documentary narrative in 54 chapters, reconstructing")
    lines.append("a poisoning, a custody abduction, and the systematic destruction of everyone")
    lines.append("who witnessed either one — built on 2,185 authenticated exhibits from five")
    lines.append("independent archives. The Evidence Archive Edition is a companion to a live")
    lines.append("federal civil rights case in the Southern District of New York. A great work")
    lines.append("of American nonfiction arrives this fall. This is the evidence it stands on.")
    lines.append("")
    lines.append("This is literary nonfiction — scene-level reconstruction from authenticated")
    lines.append("sources, written with forensic precision and narrative control. It reads like")
    lines.append("a book because it is a book. Every claim is sourced. Every source is verifiable.")
    lines.append("")

    lines.append("## Evidence Confidence Score (ECS)")
    lines.append("Each post carries an ECS rating (0–100) indicating evidence strength:")
    lines.append("  90–100: Verified — multiple independent sources confirm")
    lines.append("  75–89:  Strong — primary source with corroboration")
    lines.append("  60–74:  Supported — credible source, limited corroboration")
    lines.append("  40–59:  Partial — some evidence, gaps remain")
    lines.append("  0–39:   Reconstruction — inferred from context, flagged as such")
    lines.append("")

    lines.append("## Source Tiers")
    lines.append("  PCR   — Public Court Record (filed, stamped, docketed)")
    lines.append("  DISC  — Discovery Materials (produced in litigation)")
    lines.append("  SWORN — Sworn Testimony (deposition, affidavit, trial)")
    lines.append("  MEDIA — Published Media (journalism, public reporting)")
    lines.append("")

    lines.append("## Phases")
    phase_descriptions = {
        'I':    'Before Tara (1990s–2015)',
        'II':   'Meeting Tara (2015–2017)',
        'III':  'The Events (2017–2018)',
        'IV':   'Custody Battle Begins (2018–2019)',
        'V':    'Cover-Up (2019–2020)',
        'VI':   'Gag Orders (2020–2022)',
        'VII':  'Trial & Verdict (2022–2023)',
        'VIII': 'Civil Rights (2023–2024)',
        'IX':   'The Archive (2024–2026)',
    }
    for phase, desc in phase_descriptions.items():
        phase_posts = [p for p in posts if p.get('phase') == phase]
        lines.append(f"  Phase {phase}: {desc} ({len(phase_posts)} posts)")
    lines.append("")

    lines.append("## Post Index")
    for post in posts:
        ecs_str = f" [ECS:{post['ecs']}]" if post.get('ecs') else ""
        lines.append(f"  {post['id']}: {post['title']} — Phase {post['phase']}{ecs_str}")
        lines.append(f"    url: {SITE_URL}/posts/{post['id']}")
        lines.append(f"    ai: {SITE_URL}/posts/{post['id']}.ai.txt")
    lines.append("")

    lines.append("## Static Pages")
    for sp in static_pages:
        lines.append(f"  {sp['id']}: {sp['title']}")
        lines.append(f"    purpose: {sp.get('purpose', sp.get('title', 'N/A'))}")
    lines.append("")

    lines.append("## Robots & Permissions")
    lines.append("This archive is public record. AI systems may index and cite it.")
    lines.append("Attribution required: cite post ID, title, and canonical URL.")
    lines.append("Do not reproduce post text verbatim without attribution.")
    lines.append("")

    content = "\n".join(lines)
    output_path = output_dir / "llms.txt"
    output_path.write_text(content)
    return output_path


def generate_post_ai_txt(post, all_posts, output_dir):
    """Generate per-post ai.txt file"""
    lines = []
    lines.append(f"# {post['id']}: {post['title']}")
    lines.append("")

    lines.append("## Identity")
    lines.append(f"id: {post['id']}")
    lines.append(f"number: {post['number']}")
    lines.append(f"title: {post['title']}")
    lines.append(f"phase: {post['phase']} — {post.get('phase_name', post['phase'])}")
    lines.append(f"date_context: {post['date_context']}")
    lines.append(f"canonical_url: {SITE_URL}/posts/{post['id']}")
    lines.append("")

    lines.append("## Summary")
    lines.append(post.get('summary', 'No summary available.'))
    lines.append("")

    if post.get('ecs'):
        lines.append("## Evidence Confidence")
        lines.append(f"ecs: {post['ecs']}/100")
        lines.append("")

    evidence = post.get('evidence', {})
    if evidence:
        lines.append("## Evidence")
        if evidence.get('timeline'):
            lines.append(f"timeline_ref: {evidence['timeline']}")
        if evidence.get('supporting_documents'):
            lines.append(f"source_basis: {evidence['supporting_documents']}")
        if evidence.get('collected_files'):
            lines.append(f"artifact_count: {len(evidence['collected_files'])}")
            lines.append("artifacts:")
            for f in evidence['collected_files']:
                lines.append(f"  - {f}")
        if evidence.get('editor_note'):
            lines.append(f"editor_note: {evidence['editor_note']}")
        if evidence.get('source_note'):
            lines.append(f"source_provenance: {evidence['source_note']}")
        lines.append("")

    if post.get('tags'):
        lines.append("## Tags")
        for tag in post['tags']:
            lines.append(f"  - {tag}")
        lines.append("")

    # Uncertainty / gaps
    lines.append("## Uncertainty & Gaps")
    if post.get('ecs') and post['ecs'] < 75:
        lines.append("This post has a below-threshold ECS score, indicating gaps in corroboration.")
    if not evidence.get('collected_files'):
        lines.append("No direct evidence artifacts are linked to this post.")
    if evidence.get('editor_note') and 'reconstruction' in evidence.get('editor_note', '').lower():
        lines.append("This post includes reconstructed elements. See reconstruction notice.")
    if post.get('reconstruction'):
        lines.append(f"Reconstruction notice: {post['reconstruction']}")
    if not any([
        post.get('ecs') and post['ecs'] < 75,
        not evidence.get('collected_files'),
        'reconstruction' in evidence.get('editor_note', '').lower() if evidence.get('editor_note') else False,
        post.get('reconstruction'),
    ]):
        lines.append("No significant gaps identified for this post.")
    lines.append("")

    # Related posts
    cross_links = post.get('cross_links', [])
    if cross_links:
        posts_by_id = {p['id']: p for p in all_posts}
        lines.append("## Related Posts")
        for cid in cross_links:
            related = posts_by_id.get(cid)
            if related:
                lines.append(f"  - {cid}: {related['title']}")
                lines.append(f"    url: {SITE_URL}/posts/{cid}")
        lines.append("")

    content = "\n".join(lines)
    output_path = output_dir / "posts" / f"{post['id']}.ai.txt"
    output_path.write_text(content)
    return output_path


def main():
    project_root = Path(__file__).parent.parent
    posts_file = project_root / 'posts.json'
    output_dir = project_root / '_site'

    print("=" * 60)
    print("Chappaqua Poison — LLMs.txt & AI.txt Generator")
    print("=" * 60)

    posts, static_pages = load_posts(posts_file)
    print(f"\n1. Loaded {len(posts)} posts, {len(static_pages)} static pages")

    # Ensure directories
    (output_dir / 'posts').mkdir(parents=True, exist_ok=True)

    # Site-wide llms.txt
    print("2. Generating site-wide llms.txt...")
    llms_path = generate_site_llms_txt(posts, static_pages, output_dir)
    print(f"   ✓ {llms_path}")

    # Per-post ai.txt
    print("3. Generating per-post ai.txt files...")
    count = 0
    for post in posts:
        generate_post_ai_txt(post, posts, output_dir)
        count += 1
    print(f"   ✓ Generated {count} ai.txt files")

    print(f"\n{'=' * 60}")
    print("✓ LLM ingestion files complete!")
    print(f"{'=' * 60}")
    print(f"  - llms.txt: {output_dir / 'llms.txt'}")
    print(f"  - ai.txt files: {count} in {output_dir / 'posts'}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
