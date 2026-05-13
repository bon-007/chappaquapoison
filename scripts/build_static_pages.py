#!/usr/bin/env python3
"""
ChappaquaPoison v3 — Static Pages Builder
Generates all 14 static pages (S-1 through S-14) from templates.
Author: Claude
Date: 2026-02-15
"""

import json
import os
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape


class StaticPageBuilder:
    """Builds all 14 static pages for the ChappaquaPoison archive."""

    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = str(Path(__file__).resolve().parent.parent)
        self.base_dir = Path(base_dir)
        self.templates_dir = self.base_dir / "templates"
        self.site_dir = self.base_dir / "_site"
        self.scripts_dir = self.base_dir / "scripts"

        # Ensure output directory exists
        self.site_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )

        # Load data files
        self.load_data()

    def load_data(self):
        """Load all required data files."""
        with open(self.base_dir / "posts.json", "r") as f:
            self.posts_data = json.load(f)

        # Load timeline entries
        timeline_md = self.base_dir / "TIMELINE.md"
        self.timeline_entries = self.parse_markdown_table(timeline_md)

        # Load person index
        person_md = self.base_dir / "PERSON_INDEX.md"
        self.people = self.parse_markdown_table(person_md)

        # Load court cases
        cases_md = self.base_dir / "COURT_CASE_INDEX.md"
        self.court_cases = self.parse_markdown_table(cases_md)

        # Read full markdown files for content
        with open(self.base_dir / "PROPOSED_POSTS_AND_EVIDENCE.md", "r") as f:
            self.proposed_posts = f.read()

        with open(self.base_dir / "ECS_METHODOLOGY.md", "r") as f:
            self.ecs_methodology = f.read()

    def parse_markdown_table(self, filepath):
        """Parse markdown table into list of dicts."""
        rows = []
        with open(filepath, "r") as f:
            lines = f.readlines()

        headers = None
        for line in lines:
            if line.startswith("|") and not headers:
                headers = [cell.strip() for cell in line.split("|")[1:-1]]
            elif line.startswith("|") and line.count("-") == 0 and headers:
                cells = [cell.strip() for cell in line.split("|")[1:-1]]
                if len(cells) == len(headers):
                    rows.append(dict(zip(headers, cells)))

        return rows

    def extract_section(self, markdown_text, section_title, end_marker=None):
        """Extract a section from markdown by title."""
        lines = markdown_text.split('\n')
        start_idx = None
        end_idx = None

        for i, line in enumerate(lines):
            if section_title.lower() in line.lower():
                start_idx = i
            elif start_idx and end_marker and end_marker.lower() in line.lower():
                end_idx = i
                break

        if start_idx:
            if end_idx:
                return '\n'.join(lines[start_idx:end_idx])
            else:
                return '\n'.join(lines[start_idx:])
        return ""

    def build_page(self, page_id, title, description, content_html, og_type="website"):
        """Build a static page using base template."""
        template = self.env.get_template("base.html")

        context = {
            "site_title": "ChappaquaPoison v2",
            "page_title": title,
            "page_description": description,
            "og_type": og_type,
            "content_block": content_html,
        }

        # Create a simplified block content structure
        page_content = f"""
        <div class="content-wrapper">
            <article>
                <header>
                    <h1 class="page-title">{title}</h1>
                    <p class="page-subtitle">{description}</p>
                </header>
                <div class="page-body">
                    {content_html}
                </div>
            </article>
        </div>
        """

        return template.render(
            site_title="ChappaquaPoison v2",
            block_title=title,
            block_description=description,
            block_content=page_content
        )

    def render_markdown_as_html(self, md_text):
        """Simple markdown to HTML conversion."""
        import re

        html = md_text

        # Headers
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # Bold
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)

        # Italic
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)

        # Code
        html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)

        # Blockquotes
        html = re.sub(r'^> (.*?)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)

        # Paragraphs
        html = re.sub(r'\n\n', '</p><p>', html)
        html = f'<p>{html}</p>'

        return html

    def table_to_html(self, rows, headers=None):
        """Convert list of dicts to HTML table."""
        if not rows:
            return "<p>No data available.</p>"

        if not headers:
            headers = list(rows[0].keys()) if rows else []

        html = '<table class="data-table">\n<thead>\n<tr>\n'
        for header in headers:
            html += f'  <th>{header}</th>\n'
        html += '</tr>\n</thead>\n<tbody>\n'

        for row in rows:
            html += '<tr>\n'
            for header in headers:
                value = row.get(header, "")
                html += f'  <td>{value}</td>\n'
            html += '</tr>\n'

        html += '</tbody>\n</table>'
        return html

    def s1_homepage(self):
        """S-1: Homepage / Index"""
        banner = """
        <div class="banner-statement">
            <p>These materials were published across three independent sources — the investigative project <em>ChappaquaPoison</em>, the family archive <em>StevieLovesEvie</em>, and the personal blog <em>ABrieGrowsInBrooklyn</em> — alongside the public court record. A court later ordered them deleted. They remain here. The public record is not a private possession. The law recognizes no proprietary interest in truth. No sealed records, confidential child medical records, or attorney-client communications are published here.</p>
        </div>

        <div class="archive-demonstrates">
            <h2>What This Archive Demonstrates</h2>
            <p>This archive demonstrates how procedural ambiguity, discredited expert reliance, and compelled speech restrictions can converge in family court proceedings. The materials presented here are not narrative. They are source-cited public records, sworn testimony, and filed pleadings.</p>
        </div>

        <div class="timeline-compression">
            <h2>The Case in Outline</h2>
            <ul>
                <li><strong>2018</strong> — Emergency custody granted in California.</li>
                <li><strong>2019</strong> — Permanent DVRO entered.</li>
                <li><strong>2022</strong> — Jury verdict for battery and domestic violence.</li>
                <li><strong>2023</strong> — Appeal affirmed.</li>
                <li><strong>2023</strong> — Portions of speech restriction struck by Appellate Division.</li>
                <li><strong>2026</strong> — Motion to vacate pending.</li>
                <li><strong>2026</strong> — Federal constitutional claims filed.</li>
            </ul>
            <p><em>The record spans eight proceedings in four jurisdictions. All documents cited.</em></p>
        </div>
        """

        return {
            "id": "S-1",
            "title": "ChappaquaPoison v2 — Archive Home",
            "content": banner
        }

    def s2_about(self):
        """S-2: About This Archive"""
        content = """
        <h2>About This Archive</h2>

        <h3>What This Archive Is</h3>
        <p>This is a public record archive compiled from three independent sources:</p>
        <ul>
            <li><strong>ChappaquaPoison</strong> — An investigative documentation project (2019–2020)</li>
            <li><strong>StevieLovesEvie</strong> — A family archive (2019–2021)</li>
            <li><strong>ABrieGrowsInBrooklyn</strong> — A personal blog with contemporaneous accounts (2010–2018)</li>
        </ul>
        <p>These materials were publicly available before any court order. A court later ordered them deleted. They remain here.</p>

        <h3>What This Archive Is Not</h3>
        <ul>
            <li>Not sealed court records (none are included)</li>
            <li>Not confidential child medical records (none are included)</li>
            <li>Not attorney-client communications (none are included)</li>
            <li>Not a narrative (it is a chronological archive of public records and sworn testimony)</li>
            <li>Not edited for sympathetic presentation (all source material is cited with Evidence Confidence Scores)</li>
        </ul>

        <h3>Source Provenance</h3>
        <p>Every document published here was public before any deletion order was entered. Public court records are not a private possession. The law recognizes no proprietary interest in truth.</p>

        <h3>Methodology Acknowledgment</h3>
        <p>This archive was compiled with AI assistance. Every claim is source-cited. Every source is either:</p>
        <ul>
            <li>A public court filing</li>
            <li>A sworn declaration or deposition transcript</li>
            <li>A discovery document (produced in litigation)</li>
            <li>A published blog post or media article</li>
            <li>A laboratory report or regulatory finding</li>
        </ul>
        <p>No sealed material is included. No confidential information regarding the minor child is published. The archive is transparent about which sources are direct court records and which are reconstructed from public sources.</p>

        <h3>Gag Order Acknowledgment</h3>
        <p>A court order entered in 2020 restricted public discussion of this case. Portions of that order were struck by the Appellate Division in 2023 (214 AD3d 890). This archive exists in part to transparently challenge the remaining restrictions and to preserve public court records that were ordered deleted.</p>
        """

        return {
            "id": "S-2",
            "title": "About This Archive",
            "content": content
        }

    def s3_how_to_read(self):
        """S-3: How to Read This Archive"""
        content = """
        <h2>How to Read This Archive</h2>

        <h3>Evidence Confidence Scores (ECS)</h3>
        <p>Every post includes an ECS rating (50–100) reflecting the reliability of its underlying sources. Court filings and sworn testimony score highest (90–100). Discovery materials and deposition transcripts score 75–89. Reconstructed accounts from published sources score 60–74. Secondary or contested sources score 50–59. The score is not an opinion. It is a transparency mechanism.</p>

        <h3>Reconstruction Notices</h3>
        <p>Posts sourced from non-public-record material include a Reconstruction Notice identifying the source type and limitations. This is how the archive marks the boundary between documented record and inferred narrative.</p>

        <h3>Source Tiers</h3>
        <ul>
            <li><strong>Tier 1:</strong> Court filings, judicial orders, sworn declarations (ECS 90–100)</li>
            <li><strong>Tier 2:</strong> Discovery materials, deposition transcripts, Bates-stamped documents (ECS 75–89)</li>
            <li><strong>Tier 3:</strong> Published blog posts, media coverage, public correspondence (ECS 60–74)</li>
            <li><strong>Tier 4:</strong> Reconstructed from secondary sources with noted limitations (ECS 50–59)</li>
        </ul>

        <h3>Why Some Posts Rely on Discovery Materials</h3>
        <p>Certain events in this record were never publicly reported. The only documentation exists in Bates-stamped discovery, sworn depositions, or filed declarations. These posts cite specific exhibit numbers. Readers should note the source tier when evaluating any claim.</p>

        <h3>Why No Sealed Material Is Included</h3>
        <p>This archive does not publish sealed court records, confidential child medical records, or attorney-client communications. Where a sealed record is relevant, the archive notes its existence without reproducing its content.</p>

        <h3>Cross-Links and Tags</h3>
        <p>Posts are connected by a cross-link system identifying evidentiary relationships across phases. The tag system allows thematic navigation. Tags are capped at 3–5 per post to maintain legibility.</p>
        """

        return {
            "id": "S-3",
            "title": "How to Read This Archive",
            "content": content
        }

    def s4_methodology(self):
        """S-4: Methodology & Sources"""
        content = """
        <h2>Methodology & Sources</h2>

        <h3>Evidence Confidence Score (ECS) Framework</h3>
        <p>The ECS is a transparency mechanism, not an opinion. It tells the reader how much independent verification underlies each claim.</p>
        <p>The ECS answers a specific question: <em>How much work would it take an adversary to discredit this source?</em></p>

        <h3>Tier 1: Verified (90–100)</h3>
        <p><strong>Sources requiring adversarial proof to challenge</strong></p>
        <ul>
            <li><strong>98–100:</strong> Jury verdicts and appellate judgments (final adjudication)</li>
            <li><strong>95–98:</strong> Appellate opinions and reversals (judicial review)</li>
            <li><strong>90–95:</strong> Court filings (petitions, orders, protective orders filed in open court)</li>
            <li><strong>90–95:</strong> OASAS regulatory findings and credential revocations</li>
            <li><strong>90–95:</strong> Laboratory reports with CLIA certification</li>
            <li><strong>90–95:</strong> Sworn testimony subject to cross-examination (at trial or deposition)</li>
        </ul>

        <h3>Tier 2: Caution (75–89)</h3>
        <p><strong>Sources requiring document-level challenge to discredit</strong></p>
        <ul>
            <li><strong>85–89:</strong> Sworn declarations filed in court (not cross-examined in court, but subject to perjury liability)</li>
            <li><strong>82–89:</strong> Deposition testimony (transcript-documented, sworn under oath)</li>
            <li><strong>78–89:</strong> Discovery materials with Bates stamps (authenticated through litigation process)</li>
            <li><strong>78–85:</strong> Police reports and incident records (official documentation)</li>
            <li><strong>75–85:</strong> Published media investigations by news organizations</li>
        </ul>

        <h3>Tier 3: Limited (60–74)</h3>
        <p><strong>Sources requiring credibility assessment</strong></p>
        <ul>
            <li><strong>70–74:</strong> Published blog posts and personal accounts (pre-litigation contemporaneous)</li>
            <li><strong>65–74:</strong> Reconstructed accounts from multiple published sources</li>
            <li><strong>60–70:</strong> Self-reported communications (emails, texts, messages)</li>
            <li><strong>60–70:</strong> Secondary source compilations and media summaries</li>
        </ul>

        <h3>Tier 4: Minimal (50–59)</h3>
        <p><strong>Sources requiring counter-evidence</strong></p>
        <ul>
            <li><strong>50–59:</strong> Contested claims with single-source attribution</li>
            <li><strong>50–59:</strong> Claims without corroboration from independent sources</li>
            <li><strong>50–59:</strong> Reconstructed chronology from indirect evidence</li>
            <li><strong>50–59:</strong> Statements recanted or contradicted by the source</li>
        </ul>

        <h3>Source Transparency</h3>
        <p>This archive was compiled with AI assistance. Every claim is source-cited. The archive is transparent about:</p>
        <ul>
            <li>Which sources are direct court records</li>
            <li>Which sources are reconstructed from public sources</li>
            <li>Which sources come from published blogs or media</li>
            <li>Which sources are discovery-produced documents</li>
            <li>Which sources are sealed or limited-access materials</li>
        </ul>
        """

        return {
            "id": "S-4",
            "title": "Methodology & Sources",
            "content": content
        }

    def s5_timeline(self):
        """S-5: Master Timeline"""
        timeline_html = """
        <h2>Master Timeline</h2>
        <p><strong>Entries:</strong> 64 | <strong>Span:</strong> 1990–2026 | <strong>Last Updated:</strong> 2026-02-15</p>
        """

        if self.timeline_entries:
            timeline_html += self.table_to_html(
                self.timeline_entries,
                headers=["#", "Date", "Event", "Posts", "Evidence", "ECS"]
            )

        return {
            "id": "S-5",
            "title": "Master Timeline",
            "content": timeline_html
        }

    def s6_evidence_index(self):
        """S-6: Evidence Index"""
        # Collect all evidence from posts.json
        all_evidence = []
        for post in self.posts_data.get("posts", []):
            if "evidence" in post and "collected_files" in post["evidence"]:
                for file in post["evidence"]["collected_files"]:
                    all_evidence.append({
                        "file": file,
                        "post": f"Post {post.get('number', '')}",
                        "title": post.get("title", "")
                    })

        evidence_html = "<h2>Evidence Index</h2>\n"
        evidence_html += f"<p><strong>Total Evidence Artifacts:</strong> {len(all_evidence)}</p>\n"

        if all_evidence:
            evidence_html += '<table class="evidence-table">\n<thead>\n<tr>\n'
            evidence_html += '<th>File</th>\n<th>Post</th>\n<th>Title</th>\n</tr>\n</thead>\n<tbody>\n'

            for item in sorted(all_evidence, key=lambda x: x["file"]):
                evidence_html += '<tr>\n'
                evidence_html += f'<td><code>{item["file"]}</code></td>\n'
                evidence_html += f'<td>{item["post"]}</td>\n'
                evidence_html += f'<td>{item["title"]}</td>\n'
                evidence_html += '</tr>\n'

            evidence_html += '</tbody>\n</table>'

        return {
            "id": "S-6",
            "title": "Evidence Index",
            "content": evidence_html
        }

    def s7_people_index(self):
        """S-7: Person Index"""
        people_html = "<h2>Person Index</h2>\n"
        people_html += f"<p><strong>Total Individuals:</strong> {len(self.people)}</p>\n"

        if self.people:
            people_html += self.table_to_html(
                self.people,
                headers=["Person", "Role", "Posts", "Evidence"]
            )

        return {
            "id": "S-7",
            "title": "Person Index",
            "content": people_html
        }

    def s8_court_cases(self):
        """S-8: Court Case Index"""
        cases_html = "<h2>Court Case Index</h2>\n"
        cases_html += f"<p><strong>Total Cases:</strong> {len(self.court_cases)}</p>\n"

        if self.court_cases:
            cases_html += self.table_to_html(
                self.court_cases,
                headers=["Case", "Court", "Docket", "Posts", "Evidence"]
            )

        return {
            "id": "S-8",
            "title": "Court Case Index",
            "content": cases_html
        }

    def s9_patterns(self):
        """S-9: Patterns"""
        content = """
        <h2>Patterns: Cross-Cutting Evidentiary Threads</h2>
        <p>Each thread is independently documented. Their convergence is not rhetorical. It is chronological.</p>

        <h3>1. Default Entries</h3>
        <p><strong>Posts 34, 35, 66C</strong> — The "default" characterization appears in at least three procedural contexts with inconsistent definitions. The archive tracks each instance and its documentary basis.</p>

        <h3>2. Supervisor Replacements</h3>
        <p><strong>Posts 41C, 48C</strong> — Neutral court-appointed supervisors and AFCs who filed reports favorable to Russell were systematically replaced. The archive documents each removal and the replacement sequence.</p>

        <h3>3. Police Incidents</h3>
        <p><strong>Posts 25, 26, 62</strong> — North Castle Police Department documentation became litigation leverage without adversarial testing. The archive maps each police report to its downstream use in custody proceedings.</p>

        <h3>4. Griffin Reliance</h3>
        <p><strong>Posts 15, 31, 41B, 60</strong> — A single forensic evaluation by a subsequently discredited evaluator persisted through multiple proceedings. The archive tracks the evaluation's influence from issuance through federal complaint.</p>

        <h3>5. Judicial Recusals</h3>
        <p><strong>Posts 48D</strong> — Three successive judges recused without public explanation. The archive documents the sequence and its temporal relationship to other events.</p>

        <h3>6. Speech Restrictions</h3>
        <p><strong>Posts 44, 45, 46, 61, 67</strong> — A progression from gag order to compelled deletion to constitutional challenge. The archive traces the escalation and its intersection with parental rights.</p>

        <h3>7. Coordinated Process Manipulation</h3>
        <p><strong>Posts 28, 41F, 43, 37, 41D</strong> — Five documented instances where private party objectives aligned with state-actor outputs. Each is independently documented. Their convergence is temporal.</p>

        <h3>Convergence Diagram</h3>
        <pre>
                    ┌─────────────────────┐
                    │   CUSTODY OUTCOME   │
                    │   (File No. 154703) │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
        ┌─────┴─────┐    ┌────────┴────────┐    ┌─────┴──────┐
        │  Default   │    │    Griffin      │    │   Speech   │
        │  Entries   │    │   Reliance      │    │Restrictions│
        │(34,35,66C) │    │(15,31,41B,60)   │    │(44-46,61,67│
        └─────┬─────┘    └────────┬────────┘    └─────┬──────┘
              │                    │                    │
        ┌─────┴─────┐    ┌────────┴────────┐    ┌─────┴──────┐
        │ Supervisor │    │    Police       │    │  Judicial   │
        │Replacement │    │  Incidents      │    │  Recusals   │
        │ (41C,48C)  │    │  (25,26,62)     │    │   (48D)     │
        └───────────┘    └────────────────┘    └────────────┘
        </pre>
        """

        return {
            "id": "S-9",
            "title": "Patterns",
            "content": content
        }

    def s10_falsifiability(self):
        """S-10: If This Archive Is Wrong"""
        content = """
        <h2>If This Archive Is Wrong</h2>
        <p>This archive invites correction. If any material claim is inaccurate, the following documents or clarifications would resolve the question. This page is not rhetorical — it is an open offer.</p>

        <h3>1. The Default Classification</h3>
        <p>If the proceeding in File No. 154703 was not entered on default, produce: the answer or responsive pleading filed by Plaintiff, the docket entry reflecting its filing, and the court minutes documenting a contested hearing on the merits. These records would resolve the procedural irregularity documented in Posts 34, 35, and 66C.</p>

        <h3>2. The Griffin Credential</h3>
        <p>If Andrew Griffin held a valid CASAC credential at the time his evaluation was relied upon in custody proceedings, produce: the OASAS credential record showing active status during the relevant period. This would resolve the claims in Posts 15, 31, 41B, and 60.</p>

        <h3>3. The Monell Claim</h3>
        <p>If Westchester County Family Court maintained a credential verification policy for court-appointed forensic evaluators, produce: the written policy, and any record of its application to the Griffin appointment. This would address the municipal liability theory in Post 60.</p>

        <h3>4. The Speech Restrictions</h3>
        <p>If the gag order issued in File No. 154703 was constitutionally valid as originally entered, produce: the appellate ruling affirming it. Note: the Appellate Division, Second Department struck portions of the order in 214 AD3d 890 (Mar. 2023). A subsequent ruling reinstating those provisions would resolve the question.</p>

        <h3>5. The Supervisor Replacement Pattern</h3>
        <p>If the removal of supervisors and AFCs who filed reports favorable to Russell was based on documented cause unrelated to those reports, produce: the written basis for each removal. This would resolve the pattern documented in Posts 41C and 48C.</p>

        <h3>6. The Police Documentation</h3>
        <p>If North Castle Police Department investigated Walsh family reports with the same rigor applied to reports against Russell, produce: the investigation file for each disputed report. This would resolve the "litigation leverage" characterization in Post 62.</p>

        <h3>7. The Timeline</h3>
        <p>If any dated event in the Master Timeline (234 entries) is inaccurately dated or described, identify the entry and provide the correcting document. The archive will publish the correction with the same prominence as the original entry.</p>

        <h3>8. The Evidentiary Hearing</h3>
        <p>If an evidentiary hearing was conducted before permanent custody orders were entered in File No. 154703 — with both parties present, witnesses called, exhibits admitted, and testimony subject to cross-examination — produce the transcript. This would resolve the procedural claims documented in Posts 35, 35B, 36, and 37.</p>

        <h3>Standing Offer</h3>
        <p>This archive will publish corrections, retractions, or clarifications for any claim that is demonstrably inaccurate. Corrections will appear at the top of the relevant post with full transparency about what changed and why.</p>
        <p><em>An archive that is afraid of correction is not an archive. It is propaganda. This is an archive.</em></p>
        """

        return {
            "id": "S-10",
            "title": "If This Archive Is Wrong",
            "content": content
        }

    def s11_public_record_notice(self):
        """S-11: Public Record Notice"""
        content = """
        <h2>Public Record Notice</h2>

        <h3>Standing Disclaimer</h3>
        <p>Everything published here was public before any order was entered.</p>
        <p>The public record is not a private possession. The law recognizes no proprietary interest in truth. No sealed records, confidential child medical records, or attorney-client communications are published here.</p>

        <h3>Source Provenance Shield</h3>
        <p>This archive is compiled from publicly available court filings, published media, and documents disclosed during litigation. All source materials are cited with their provenance.</p>

        <h3>What Is Included</h3>
        <ul>
            <li>Public court filings and orders</li>
            <li>Publicly published blog posts and media coverage</li>
            <li>Discovery materials disclosed in litigation</li>
            <li>Sworn declarations and testimony filed in court</li>
            <li>Laboratory reports and regulatory findings</li>
            <li>Police reports and incident documentation</li>
        </ul>

        <h3>What Is Not Included</h3>
        <ul>
            <li>Sealed court records</li>
            <li>Confidential child medical records</li>
            <li>Attorney-client communications</li>
            <li>Trade secrets or proprietary information</li>
            <li>Information obtained in violation of law</li>
        </ul>
        """

        return {
            "id": "S-11",
            "title": "Public Record Notice",
            "content": content
        }

    def s12_audit_log(self):
        """S-12: Audit Log"""
        content = f"""
        <h2>Audit Log</h2>
        <p><strong>Archive Launch:</strong> February 15, 2026</p>
        <p><strong>Current Version:</strong> v2.0 (Structured Archive with ECS, Cross-Linking, Evidence Index)</p>

        <h3>Version History</h3>
        <table class="audit-table">
            <thead>
                <tr>
                    <th>Version</th>
                    <th>Date</th>
                    <th>Changes</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>v1.0</td>
                    <td>2019–2020</td>
                    <td>Original ChappaquaPoison investigative project</td>
                </tr>
                <tr>
                    <td>v2.0</td>
                    <td>2026-02-15</td>
                    <td>Structured archive: 91 posts, 14 static pages, ECS scoring, cross-linking, evidence index, timeline integration, person index, court case index, methodology documentation</td>
                </tr>
            </tbody>
        </table>

        <h3>Artifact Count</h3>
        <ul>
            <li>Posts: 91</li>
            <li>Static Pages: 14</li>
            <li>Timeline Entries: 64</li>
            <li>People Index: 28 individuals</li>
            <li>Court Cases: 5 dockets</li>
            <li>Evidence Files: Indexed and catalogued</li>
        </ul>

        <h3>Correction Log</h3>
        <p>No corrections have been published to date. The archive invites readers to identify factual inaccuracies. See: <a href="/falsifiability">If This Archive Is Wrong</a>.</p>
        """

        return {
            "id": "S-12",
            "title": "Audit Log",
            "content": content
        }

    def s13_ten_documents(self):
        """S-13: The Case in 10 Documents"""
        content = """
        <h2>The Case in 10 Documents</h2>
        <p><strong>Format:</strong> Ten one-page document excerpts. No narrative. No commentary. The documents speak.</p>

        <h3>Document Catalog</h3>
        <table class="documents-table">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Document</th>
                    <th>Source</th>
                    <th>ECS</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>Emergency Custody Order (California Superior Court)</td>
                    <td>B-2</td>
                    <td>90</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>Walsh DV-120 Response — admits drugging</td>
                    <td>C-6</td>
                    <td>90</td>
                </tr>
                <tr>
                    <td>3</td>
                    <td>Tedla Declaration — nanny witnessed drugging</td>
                    <td>C-1</td>
                    <td>85</td>
                </tr>
                <tr>
                    <td>4</td>
                    <td>OASAS Credential Revocation — Griffin</td>
                    <td>B-14</td>
                    <td>90</td>
                </tr>
                <tr>
                    <td>5</td>
                    <td>DEFAULT 2 — Custody/Gag Order on Default</td>
                    <td>B-7</td>
                    <td>90</td>
                </tr>
                <tr>
                    <td>6</td>
                    <td>Appellate Division Ruling — gag order struck, "not on default"</td>
                    <td>B-12</td>
                    <td>95</td>
                </tr>
                <tr>
                    <td>7</td>
                    <td>SF Jury Verdict — battery, IIED, DV with malice</td>
                    <td>B-9</td>
                    <td>98</td>
                </tr>
                <tr>
                    <td>8</td>
                    <td>CA Court of Appeal — judgment affirmed</td>
                    <td>B-11</td>
                    <td>98</td>
                </tr>
                <tr>
                    <td>9</td>
                    <td>NY Domestication of CA Judgment</td>
                    <td>B-13</td>
                    <td>95</td>
                </tr>
                <tr>
                    <td>10</td>
                    <td>Motion to Vacate — cover page</td>
                    <td>H-6</td>
                    <td>90</td>
                </tr>
            </tbody>
        </table>

        <p><em>Each document rendered as a one-page excerpt with source attribution and ECS score. This file is designed for judges, journalists, and researchers who need to understand the case in under five minutes. Every page is independently verifiable through the cited court record.</em></p>
        """

        return {
            "id": "S-13",
            "title": "The Case in 10 Documents",
            "content": content
        }

    def s14_public_record_inventory(self):
        """S-14: Public Record Inventory"""
        content = """
        <h2>Public Record Inventory</h2>
        <p>A checkable inventory of every document type in the archive, with its public-record status, sealed status, and source.</p>

        <table class="inventory-table">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Document Type</th>
                    <th>Example</th>
                    <th>Source</th>
                    <th>Public Status</th>
                    <th>Sealed?</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>1</td><td>Appellate Division opinions</td><td>214 AD3d 890 (Mar. 2023)</td><td>Court records</td><td>Publicly filed</td><td>No</td></tr>
                <tr><td>2</td><td>Jury verdict and judgment</td><td>CGC-18-570137 (Feb. 2022)</td><td>Court records</td><td>Publicly filed</td><td>No</td></tr>
                <tr><td>3</td><td>OASAS credential revocation</td><td>Complaints #19-116, #19-196</td><td>State agency</td><td>Regulatory finding</td><td>No</td></tr>
                <tr><td>4</td><td>Court of Appeal opinion</td><td>A165356 (Sep. 2023)</td><td>Court records</td><td>Publicly filed</td><td>No</td></tr>
                <tr><td>5</td><td>Domestication filing</td><td>Westchester Supreme Court (Jan. 2023)</td><td>Court records</td><td>Publicly filed</td><td>No</td></tr>
                <tr><td>6</td><td>Sworn declarations</td><td>Filed in FPT-18-377425</td><td>Court records</td><td>Publicly filed</td><td>No</td></tr>
                <tr><td>7</td><td>Deposition transcripts</td><td>SF civil case discovery</td><td>Court-supervised</td><td>Produced in discovery</td><td>No</td></tr>
                <tr><td>8</td><td>Police reports</td><td>NC-001474-19</td><td>Law enforcement</td><td>Public records</td><td>No</td></tr>
                <tr><td>9</td><td>Published blog posts</td><td>ABrieGrowsInBrooklyn (2010–2018)</td><td>Internet</td><td>Publicly published</td><td>No</td></tr>
                <tr><td>10</td><td>Published investigative content</td><td>ChappaquaPoison (2019–2020)</td><td>Internet</td><td>Publicly published</td><td>No</td></tr>
                <tr><td>11</td><td>Published family archive</td><td>StevieLovesEvie (2019–2021)</td><td>Internet</td><td>Publicly published</td><td>No</td></tr>
                <tr><td>12</td><td>Media reporting</td><td>Journal News (Oct. 2020)</td><td>Published press</td><td>Publicly published</td><td>No</td></tr>
                <tr><td>13</td><td>DVRO petition and orders</td><td>FPT-18-377425</td><td>Court records</td><td>Publicly filed</td><td>No</td></tr>
                <tr><td>14</td><td>Motion to Vacate</td><td>File No. 154703 (Dec. 2025)</td><td>Court records</td><td>Publicly filed</td><td>No</td></tr>
                <tr><td>15</td><td>Federal civil rights complaints</td><td>S.D.N.Y. (Feb. 2026)</td><td>Court records</td><td>Publicly filed</td><td>No</td></tr>
                <tr><td>16</td><td>Criminal complaints (FBI/NYAG)</td><td>Filed ~Sep. 2025</td><td>Law enforcement</td><td>Filed complaints</td><td>No</td></tr>
                <tr><td>17</td><td>Attorney correspondence</td><td>Various (2018–2026)</td><td>Court filings</td><td>Filed as exhibits</td><td>No</td></tr>
                <tr><td>18</td><td>Text message evidence</td><td>Bates-stamped discovery</td><td>Court-supervised</td><td>Produced in discovery</td><td>No</td></tr>
                <tr><td>19</td><td>Laboratory reports</td><td>LabCorp, Redwood Toxicology</td><td>Medical labs</td><td>Court exhibits</td><td>No</td></tr>
                <tr><td>20</td><td>Billing records</td><td>AFC fee applications</td><td>Court records</td><td>Publicly filed</td><td>No</td></tr>
                <tr><td>21</td><td>Hearing transcripts</td><td>Various (2018–2026)</td><td>Court records</td><td>Publicly filed</td><td>No</td></tr>
            </tbody>
        </table>

        <h3>Attestation</h3>
        <p><strong>Every document cited in this archive is a public record, publicly filed, or publicly published.</strong> None have been sealed by any court. None contain confidential information regarding the minor child. No sealed records, confidential child medical records, or attorney-client communications are published here.</p>
        """

        return {
            "id": "S-14",
            "title": "Public Record Inventory",
            "content": content
        }

    def write_page(self, page_id, filename, title, description, content_html):
        """Write a static page to disk."""
        output_path = self.site_dir / filename

        # Build complete HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{description}">
  <meta name="og:title" content="{title} | ChappaquaPoison v2">
  <meta name="og:description" content="{description}">
  <meta name="og:image" content="/images/og-banner.jpg">
  <meta name="og:type" content="website">
  <meta name="theme-color" content="#0F1116">
  <meta name="color-scheme" content="dark">

  <title>{title} | ChappaquaPoison v2</title>

  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;600&family=Source+Serif+4:wght@400;600&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">

  <!-- Design Tokens CSS -->
  <link rel="stylesheet" href="/css/tokens.css">

  <style>
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      padding: 0;
      background-color: var(--color-deep-charcoal);
      color: var(--color-body-text-dark);
      font-family: var(--font-body);
      font-weight: 400;
      font-size: 17px;
      line-height: 1.7;
      -webkit-font-smoothing: antialiased;
    }}

    a {{
      color: var(--color-link-default);
      text-decoration: none;
      border-bottom: 1px solid currentColor;
      transition: color 0.2s ease-in-out;
    }}

    a:hover {{
      color: var(--color-link-hover);
    }}

    /* Header */
    header {{
      background-color: var(--color-deep-charcoal);
      border-bottom: 1px solid var(--color-slate-blue-gray);
      position: sticky;
      top: 0;
      z-index: 50;
      padding: 16px 0;
    }}

    .header-inner {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 40px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .site-title {{
      font-family: var(--font-heading);
      font-size: 20px;
      font-weight: 700;
      margin: 0;
      color: var(--color-body-text-dark);
    }}

    .site-title a {{
      color: inherit;
      border: none;
    }}

    .header-nav {{
      display: flex;
      gap: 32px;
      list-style: none;
      margin: 0;
      padding: 0;
    }}

    .header-nav a {{
      font-family: var(--font-ui);
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    /* Main Content */
    main {{
      min-height: calc(100vh - 200px);
      padding: 40px 20px;
    }}

    .content-wrapper {{
      max-width: 680px;
      margin: 0 auto;
      padding: 0 var(--layout-padding);
    }}

    article {{
      margin-bottom: 64px;
    }}

    .page-title {{
      font-family: var(--font-heading);
      font-size: clamp(32px, 5vw, 48px);
      font-weight: 700;
      margin: 0 0 16px 0;
      color: var(--color-body-text-dark);
    }}

    .page-subtitle {{
      font-size: 18px;
      color: var(--color-muted-caption);
      margin: 0 0 32px 0;
      font-style: italic;
    }}

    .page-body h2 {{
      font-family: var(--font-heading);
      font-size: 28px;
      font-weight: 600;
      margin: 32px 0 16px 0;
      color: var(--color-body-text-dark);
    }}

    .page-body h3 {{
      font-family: var(--font-heading);
      font-size: 20px;
      font-weight: 600;
      margin: 24px 0 12px 0;
      color: var(--color-body-text-dark);
    }}

    .page-body p {{
      margin: 0 0 1.2em 0;
    }}

    .page-body ul, .page-body ol {{
      margin: 16px 0;
      padding-left: 32px;
    }}

    .page-body li {{
      margin-bottom: 8px;
    }}

    .page-body code {{
      font-family: var(--font-mono);
      font-size: 14px;
      background-color: var(--color-code-docket);
      color: var(--color-body-text-dark);
      padding: 2px 6px;
      border-radius: 2px;
    }}

    .page-body pre {{
      background-color: var(--color-code-docket);
      padding: 16px;
      border-radius: 2px;
      overflow-x: auto;
      margin: 16px 0;
      font-family: var(--font-mono);
      font-size: 13px;
      line-height: 1.5;
    }}

    .page-body blockquote {{
      margin: 24px 0;
      padding-left: 20px;
      border-left: 3px solid var(--color-muted-amber);
      font-style: italic;
      color: var(--color-muted-caption);
    }}

    .page-body table {{
      width: 100%;
      border-collapse: collapse;
      margin: 24px 0;
      font-size: 15px;
    }}

    .page-body table thead {{
      background-color: var(--color-slate-blue-gray);
    }}

    .page-body table th {{
      padding: 12px;
      text-align: left;
      font-weight: 600;
      color: var(--color-body-text-dark);
      border-bottom: 1px solid var(--color-phase-divider);
    }}

    .page-body table td {{
      padding: 12px;
      border-bottom: 1px solid var(--color-phase-divider);
    }}

    .page-body table tr:hover {{
      background-color: var(--color-slate-blue-gray);
    }}

    /* Banner & Special Sections */
    .banner-statement, .archive-demonstrates, .timeline-compression {{
      background-color: var(--color-slate-blue-gray);
      border-left: 3px solid var(--color-muted-amber);
      padding: 24px;
      margin: 32px 0;
      border-radius: 2px;
    }}

    .banner-statement p, .archive-demonstrates p, .timeline-compression p {{
      margin: 0 0 16px 0;
    }}

    .timeline-compression ul {{
      margin: 16px 0;
      padding-left: 32px;
    }}

    .timeline-compression li {{
      margin-bottom: 8px;
    }}

    /* Footer */
    footer {{
      background-color: var(--color-slate-blue-gray);
      border-top: 1px solid var(--color-phase-divider);
      padding: 40px 20px;
      margin-top: 64px;
      color: var(--color-muted-caption);
      font-family: var(--font-ui);
      font-size: 13px;
    }}

    .footer-inner {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 40px;
    }}

    .footer-content {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 32px;
      margin-bottom: 32px;
    }}

    .footer-section h3 {{
      font-family: var(--font-ui);
      font-size: 13px;
      font-weight: 600;
      text-transform: uppercase;
      margin: 0 0 16px 0;
      color: var(--color-body-text-dark);
    }}

    .footer-section ul {{
      list-style: none;
      padding: 0;
      margin: 0;
    }}

    .footer-section li {{
      margin-bottom: 8px;
    }}

    .footer-section a {{
      font-size: 13px;
    }}

    .footer-bottom {{
      border-top: 1px solid var(--color-phase-divider);
      padding-top: 24px;
      font-size: 12px;
      text-align: center;
    }}

    @media (max-width: 768px) {{
      .header-inner {{
        padding: 0 20px;
        flex-direction: column;
        gap: 16px;
      }}

      .header-nav {{
        gap: 16px;
      }}

      .content-wrapper {{
        padding: 0 16px;
      }}

      main {{
        padding: 24px 0;
      }}

      .footer-inner {{
        padding: 0 20px;
      }}

      .page-body table {{
        font-size: 13px;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="header-inner">
      <h1 class="site-title">
        <a href="/">ChappaquaPoison v2</a>
      </h1>
      <nav>
        <ul class="header-nav">
          <li><a href="/">Home</a></li>
          <li><a href="/about.html">About</a></li>
          <li><a href="/how-to-read.html">How to Read</a></li>
          <li><a href="/methodology.html">Methodology</a></li>
          <li><a href="/timeline.html">Timeline</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <main id="main-content">
    <div class="content-wrapper">
      <article>
        <h1 class="page-title">{title}</h1>
        <p class="page-subtitle">{description}</p>
        <div class="page-body">
          {content_html}
        </div>
      </article>
    </div>
  </main>

  <footer>
    <div class="footer-inner">
      <div class="footer-content">
        <div class="footer-section">
          <h3>Archive</h3>
          <ul>
            <li><a href="/">Posts</a></li>
            <li><a href="/timeline.html">Master Timeline</a></li>
            <li><a href="/evidence.html">Evidence Index</a></li>
            <li><a href="/people.html">People Index</a></li>
          </ul>
        </div>
        <div class="footer-section">
          <h3>Information</h3>
          <ul>
            <li><a href="/about.html">About This Archive</a></li>
            <li><a href="/how-to-read.html">How to Read</a></li>
            <li><a href="/methodology.html">Methodology</a></li>
            <li><a href="/public-record-notice.html">Public Record Notice</a></li>
          </ul>
        </div>
        <div class="footer-section">
          <h3>Pages</h3>
          <ul>
            <li><a href="/patterns.html">Patterns</a></li>
            <li><a href="/falsifiability.html">If This Archive Is Wrong</a></li>
            <li><a href="/cases.html">Court Cases</a></li>
            <li><a href="/audit-log.html">Audit Log</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p><strong>Public Record Notice:</strong> This archive is compiled from publicly available court filings, published media, and documents disclosed during litigation. All source materials are cited with their provenance.</p>
        <p>&copy; 2026 ChappaquaPoison v2. Archival transparency project.</p>
      </div>
    </div>
  </footer>
</body>
</html>
"""

        with open(output_path, "w") as f:
            f.write(html)

        return output_path

    def build_all_pages(self):
        """Build all 14 static pages."""
        results = []

        # S-1: Homepage (special handling)
        s1 = self.s1_homepage()
        path = self.write_page(s1["id"], "index.html",
                               "ChappaquaPoison v2 — Archive Home",
                               "Public record archive of the Russell v. Walsh litigation",
                               s1["content"])
        results.append({"page": "S-1 (Home)", "path": path, "title": s1["title"]})

        # S-2 through S-14
        pages = [
            (self.s2_about(), "about.html"),
            (self.s3_how_to_read(), "how-to-read.html"),
            (self.s4_methodology(), "methodology.html"),
            (self.s5_timeline(), "timeline.html"),
            (self.s6_evidence_index(), "evidence.html"),
            (self.s7_people_index(), "people.html"),
            (self.s8_court_cases(), "cases.html"),
            (self.s9_patterns(), "patterns.html"),
            (self.s10_falsifiability(), "falsifiability.html"),
            (self.s11_public_record_notice(), "public-record-notice.html"),
            (self.s12_audit_log(), "audit-log.html"),
            (self.s13_ten_documents(), "ten-documents.html"),
            (self.s14_public_record_inventory(), "public-record-inventory.html"),
        ]

        for page_data, filename in pages:
            path = self.write_page(
                page_data["id"],
                filename,
                page_data["title"],
                page_data["id"],
                page_data["content"]
            )
            results.append({"page": page_data["id"], "path": path, "title": page_data["title"]})

        return results


def main():
    """Main execution."""
    print("ChappaquaPoison v3 — Static Pages Builder")
    print("=" * 60)

    builder = StaticPageBuilder()
    results = builder.build_all_pages()

    print(f"\nGenerated {len(results)} pages:\n")

    total_size = 0
    for result in results:
        size = result["path"].stat().st_size
        total_size += size
        size_kb = size / 1024
        print(f"  {result['page']:20} → {result['path'].name:30} ({size_kb:>8.1f} KB)")

    print(f"\n{'Total Size:':20} {total_size / (1024*1024):.2f} MB")
    print(f"\nAll pages generated successfully in {builder.site_dir}")


if __name__ == "__main__":
    main()
