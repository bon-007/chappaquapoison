# Orientation — ChappaquaPoison v3

**Last updated:** 2026-05-14 13:56 UTC (Session — **HONEYPOT v7 LIVE WITH CLASSIFIER FIXES.** v7 deployed after first-day data review showed 47 misclassified records (Tencent Lighthouse / RackNerd / JOY SERVICES VPS bots labeled "human"). Fixes: expanded DATACENTER_ASN list + regex fallback for generic hosting names (Fix A); new `looksLikeBrowserButLies()` function and `fake_browser` signal class — catches Mozilla-UA-with-no-Sec-Fetch-headers tooling (Fix B); smoke-test traffic routed to `tests/` partition with `test:true` flag, separate from real corpus (Fix C). Verified in production via three-test smoke pass. Source at `worker_v7.js`. Architecture doc updated. **Earlier 2026-05-14:** **HONEYPOT DEPLOYED.** Worker v6 live at `chappaquapoison.com/*` adding scanner-path bait + slow-404 friction layer on top of v5's visitor-cookie/classification/banner logic. WAF rules updated with high-priority skip rule (`http_request_firewall_custom` entrypoint `293bc3435d59...`) so honeypot paths bypass all managed WAF and reach the Worker. Credential paths (`.env*`, `.aws/*`, `.ssh/*`, `.git/*`, `database.*`, etc.) serve fake `.env`-style content (~2.8KB) with placeholder credentials — Phase C swaps in real canarytokens.org tokens next session. Reconnaissance paths (`wp-config.php`, `phpinfo.php`, `xmlrpc.php`, `phpmyadmin/*`, etc.) get 2-3s slow-404 friction. Every probe writes evidence-quality records to R2 (`chappaquapoison-logs`) at `scanner-probes/YYYY-MM-DD/` and `logs/YYYY-MM-DD/scanner-{informed?}/<visitor_id>/`. Records include Cloudflare ray_id for cross-reference with CF's authoritative logs under subpoena. L2/L3 detection via `informed_probe=true` flag set when scanner-class probe carries existing visitor cookie. **Smoke test:** 14 probes confirmed working — bait at `.env.production` returns 200/2855B, slow-404 at `wp-config.php` returns 404/336B after 2.93s. **Full architecture documented at `/Users/s/Claude/_pipeline_audit_backup_2026-05-13/HONEYPOT_ARCHITECTURE.md`.** Source code at `/Users/s/Claude/_pipeline_audit_backup_2026-05-13/honeypot/worker_v6.js`. Pending: canary token generation + swap (Phase C, next session).)

**Previous update:** 2026-05-13 (Session — **PIPELINE RECOVERED FROM DRIVE EVENT.** Source brought back into consistency with deployed live site (chappaquapoison.com). All 54 chapter bodies semantically match live; 23 of 26 sampled built pages now byte-identical. Reconciliation work: 8 chapter body fixes (7 Evie age corrections + B50 trim + B53 back-cover rewrite, all live-wins direction); 14 ` 2.md`/` 2.html` drive-event filename duplicates renamed; B49/B50/B51/B53 moved from `Drafts/test_draft_v2/` to `posts/md/`; templates restored (`falsifiability.html`, `404.html`) or rebuilt (`timeline-guide.html`, `contact.html`); `base.html` updated for SEO drift (Twitter Cards, og:url defaulting to canonical_url, og:site_name, absolute og:image, Contact nav link); JSON-LD Book schema added to index.html, CollectionPage schema added to evidence.html; `pages/legal.md` got Appellate citation upgrade + Case Filings section; `evidence/` → `Evidence/` path case fix in build script; missing source assets restored (book cover image, one evidence photo). Committed to source git as `4ca09ca`. **Three local-only edits remain pending future deploy:** D-31 → Don Ackerman tag rename (B09, B14, B15), 48 chapters' act_name renames, B48 ECS change. **Anchor preserved at `/Users/s/Claude/_anchor_origin_main_20260513/`** for future consistency comparisons. **Full recovery documentation at `/Users/s/Claude/_pipeline_audit_backup_2026-05-13/PIPELINE_CONSISTENCY_STATE.md`** including round-trip verification recipe. **Premise affirmed: live is canonical; pipeline is the measuring instrument; no deploy until substantive content work warrants it.** Earlier framing that "live > local with substantial chapter content drift" was quantitatively wrong — actual prose drift was tiny and scoped to specific edits; the bigger drift was in templates and SEO scaffolding.)

**Previous update:** 2026-04-11 (Session ~180 — **SITE REPOSITIONED.** Complete repositioning from "evidence archive" to "documentary narrative." All meta descriptions, og:tags, homepage hero text, book page, llms.txt updated and deployed. New positioning system with 6 outputs (1-sentence, 3-sentence, 3-paragraph, 5-paragraph, tease, taste) at `Planning/POSITIONING_DRAFT.md`. Book page rewritten with three-paragraph positioning + "Support This Work" CTA. PDF pipeline source updated: fifty-two → fifty-four, S. Grant Russell removed from copyright, "Evidence Archive Edition" replaces "Documentary edition." New `chappaqua-outreach` skill created for communications/outreach workflow. 54 per-post ai.txt files deployed for AI ingestion. **THE STANDARD (S177 author directive): This book is attempting to be one of the greatest nonfiction books of the last twenty years. That is the standard against which every craft decision is measured.** Next: direct outreach — witnesses, lawyers, activists, coalition partners via CloudPost.)
**Purpose:** Tell any new Claude instance where everything is, how it works, and what state the pipeline is in.

---

## What This Is

A documentary narrative about a custody case involving poisoning, institutional failure, and one father's fight to reach his daughter. Built from Markdown + JSON + Jinja2 templates, deployed as a static site to Cloudflare Pages at chappaquapoison.com. Also generates book-format DOCX → PDF (~521 pages, 6×9 trade paperback) via `scripts/generate_book.js` (Node.js, `docx` library) + LibreOffice conversion.

The user is **Steve Russell**, the author and subject.

---

## START HERE — SESSION SKILL

**Invoke the `chappaqua-session` skill first.** It presents four workflows (writing, banners, site optimization, and communications/outreach), the resources and learnings for each, and forces a conversation with the author before any work begins. It then routes to the deeper skills (`chappaqua-editorial`, `baldwin-voice`, `banner-generation`, `site-optimization`) based on which workflow is chosen. The communications workflow covers email infrastructure (cloudpost MTA, DKIM signing, Cloudflare Email Routing) and outreach — source verification and advocacy. State file: `~/Claude/Mail/cloudpost-session-state.yaml`.

> **For any writing/voice/craft session:** Before applying any voice rule from any Standards doc, read `Standards/VOICES_COMPS_MASTER.md` (the 19-author corpus) and `Standards/VOICE_EVOLUTION.md` (the five-era arc). The voice work has had five eras of correction, and Era 5 (The Felt Presence) qualifies every rule in every other voice doc — restraint without a felt human presence becomes airlessness. A session that loads only `VOICE_STANDARD.md` or `VOICE_TARGET_PROFILE.md` without reading the master docs will over-apply the discipline and produce the airless prose Era 5 was named to correct.

If the skill isn't installed, read it directly: `skills/chappaqua-session/SKILL.md`

After the skill loads, read this file (ORIENTATION.md) for current state and NEXT_SESSION_PROMPT.md for task context.

---

## PROJECT ROOT — AUTHORITATIVE FILES ONLY

The project root contains exactly four MD files. Only these are authoritative:
- **ORIENTATION.md** (this file) — current state, pipeline, file locations
- **NEXT_SESSION_PROMPT.md** — session history, deploy process, known issues, task context
- **EVIDENCE_EMBED_STANDARDS.md** — canonical embed CSS reference (857 lines, still live, referenced by template)
- **README.md** — standard project readme

Ten orphan MD files from earlier sessions (CORE_NARRATIVES.md, INSIGHTS.md, SESSION_LOG.md, V3_HUNT_LOG.md, etc.) were archived to `Archive/` in Session 157. They were superseded by the editorial skill, NARRATIVES_AND_THEMES.md, and NEXT_SESSION_PROMPT.md. Do not recreate root-level MD files — consolidate into NEXT_SESSION_PROMPT.md or the appropriate Standards/Indexes/Audits directory.

---

## READ FIRST: LESSON FROM THE REVIEW

**`Standards/LESSON_FROM_THE_REVIEW.md`** — Read this before any editorial, craft, or review work. It contains the distilled wisdom of the 157-finding adversarial review: the book is smarter than you are; trust the source, not the last session; don't explain what the reader can see; you are not the author.

---

## CRITICAL LESSONS — READ BEFORE DOING ANYTHING

These are hard-won lessons from 32 sessions. Every failure traces back to violating one of these:

**THE CARDINAL RULES: Always read. Never leap before you look. Never delegate. Never assume. Never stay inside one folder.**

1. **Read everything yourself. No shortcuts. No delegation.** Every session that has failed has failed because someone searched metadata instead of looking at things. A photograph of Tara on a boat was missed because the index entry said "Scanned page from Evie scrapbook." A previous session created 139 identical stub index entries and called it done. Do not use subagents for reading. Do not assume what an entry contains. Do not delegate evidence searches. Open the file. Read it. Describe what you actually see. The process works when you read everything. It breaks every time you don't.

6. **The blog's Evidence folder is a CURATED SUBSET, not the complete archive. (Added Session 22)** The full case archive lives at `~/Claude/CaseFiles/` — 19 case folders, including `02_SF_Civil_CGC-18-570137/` (the Battery case with trial transcripts), `01_SF_DVRO_FPT-18-377425/`, `04_NY_Family_Court_154703/`, and 16 more. The master evidence indexes and Evie Story Book PDFs live at `~/Claude/Indexes and Master Archives/`. Session 22 spent hours searching the blog's Evidence folder for Battery trial testimony that was sitting in CaseFiles the entire time. The blog folder contains ~1,263 curated files. CaseFiles contains 432K files. **Every evidence search must check both.** When you can't find something in the blog Evidence folder, the next step is CaseFiles — not declaring it missing.

7. **Start from the evidence, not from the markdown. (Added Session 22)** Session 22 produced a 250-word post for a scene that should have been 3,000 words because the editor started from the existing markdown and worked backward. The corrected process: read CHARACTERS, PLACES, and NARRATIVES first. Search the evidence archives (including CaseFiles). THEN read the markdown. Build the post from the story and the evidence outward, not from the existing text inward. Cleaning is not editing. Removing bad embeds is not the same as finding good ones.

2. **The Five Archives are characters, not filing systems.** Each has a voice, a purpose, and visual material that keyword searches miss. Kelly's Books use juxtaposition as argument. Tara's texts reveal the scheme through two registers (performed remorse vs. "it's soooooo easy"). Brienne's blog is the time machine into the Walsh family before the story began. Petrella's podcast carries the arc of a professional destroyed for supporting the truth. The Court Record speaks with institutional authority in both its worst and best forms. See VISUAL_EVIDENCE_STANDARD.md and VOICE_STANDARD.md for the full character descriptions.

3. **Visual evidence carries equal weight to evidentiary evidence.** Steve holding Evie at the window doesn't prove battery. But placed beside the Guttridge letter calling his bruise documentation "signs of instability," it makes the reader understand what the legal record cannot convey. The two-axis model in VISUAL_EVIDENCE_STANDARD.md exists because of the systematic bias toward text over images. Fight this bias.

4. **Contrast is the story's engine.** Not commentary, not argument — proximity. The "sweetest revenge" texts beside "I'm sorry I ruined everything." The lethal dose search beside the father kissing his newborn. Every editorial pass must search for contrast evidence. If the candidate list has no contrast pieces, the search is incomplete.

5. **Fix the index before doing editorial work.** When the index is broken, everything downstream fails. If an index entry doesn't describe what you'd actually see in the file, update it before proceeding.

---

## Current State (April 10, 2026 — Session 171 Close-Out)

**REAL DRAFT PHASE BEGINS. TEST DRAFTS COMPLETE.**

The test draft phase (Sessions 170-171) produced two full test drafts, built the harness infrastructure, discovered the B32 hallucinated staging scene, established the Quote Rule and Dramatized Staging category, and proved that delegation fails for craft work. The real draft process — documented in `Audits/REAL_DRAFT_OPERATIONAL_BRIEF.md` — rewrites production files in `posts/md/` one chapter at a time, with the author present, and runs pipeline QA to verify consistency across `_site/`, `_deploy/`, git, and the live site.

`Standards/CHAPTER_ENRICHMENT_GUIDE.md` is the **single-source living container** that feeds the rewrite. It now includes Section 0.15 (Quote Rule) and Section 0.16 (Dramatized Staging) — the two rules that emerged from the test draft failures.

Sessions 158-164 built the editorial infrastructure (voice analysis, writing plan, enrichment guide, reading layer). Sessions 165-167 executed enrichment samples across all 12 monotony-zone chapters — 37 enrichment actions across B19, B23, B25, B29, B32, B33, B35, B37, B39, B41, B45, B48. All passed QA-as-you-go. Phase 4 technical QA complete. Session 168 completed the arc-level sequential read but left architectural debt. **Session 169 resolved all Session 168 debt AND completed Phase 2 prep:**

- All seven Open Questions for Author answered (Q1 Horowitz residue, Q2 Kelly interior→external, Q3 Jackman overlap fix, Q4 B37 prolepsis strip, Q5 baseball-bat foreshadowing kept, Q6 vocabulary sub-tasks scoped, Q7 B39 closing payoff kept).
- ARC_READ_FINDINGS.md folded into per-chapter Section 7 entries and the orphaned file deleted. ARC_READ_PROTOCOL.md amended to prescribe in-guide finding integration. CHAPTER_ENRICHMENT_GUIDE.md "HISTORICAL" header removed.
- Step 1D research passes: ExTR_03 (January 26, 2021 Humphrey transcript) located and threaded through B32/B33 as the default-asymmetry receipts. Evie birthdate triangulated to January 27, 2018 (ExO_02 + B17 + B32) and B46 age correction ("Evie was five" at the September 2023 anchor, not seven) integrated into the guide. B48's late-2025 "Evie was seven, turning eight in January" protected on the Do Not Touch list as a separate moment. Missing SCREENSHOT_SGT_CARAWAY_COURT_ORDER restored from Blue_IMAGE_Archive. Vocabulary sweep executed across all 53 posts with concentration-adjusted decisions: B29-SYS-THIN (cut 6-8 of 15), B30-SYS-THIN (rework act-as-victim paragraph), ARC-SYS-PHRASING (cross-chapter "the system that ___" construction audit).
- Step 1E final read-through: B46 stale guide-status line fixed, six Success Feel Statement titles corrected against actual chapter titles (B19 "The Leaning Tower," B23 "The Uber," B25 "A Special Relationship," B29 "The Memo," B32 "Five O'Clock," B33 "Two Defaults"), four Success Feel descriptions rewritten where the old text described chapters that no longer exist in the current numbering (B23, B25, B29, B33 — B33 most severe: old description was about Paul Hymowitz forensic evaluation, a chapter that does not exist in the current arc at all), two minor AR-006 artifacts fixed ("51 chapters" → "53 posts", pre-sweep chapter list marked as superseded).

**Session 170 first actions (before any rewrite):**
1. **Prescription audit.** Read each of the twelve monotony-zone Section 7 entries (B19, B23, B25, B29, B32, B33, B35, B37, B39, B41, B45, B48) with the source voice analysis's six prescriptions in hand: Sebald counterweight (specifically called out for B32/B35/B37/B39/B41); per-chapter Steve-consciousness paragraph; Lyrical/Place restoration in the late chapters; Robinson strategic placement across the B25–B41 stretch; a B38 Bora-Bora-equivalent respite somewhere in B25–B35; and systematic use of `ChappaquaPoison Book/Planning/Scene_Candidate_List.md` (42 scene cards), `DIALOGUE_AND_SPEECH_REFERENCE.md` (144 speech units), and `Scene_Expansion_Opportunities.md` (15 opportunities). For each entry, confirm it (a) reflects current chapter content, (b) operationalizes whichever of the six prescriptions apply, and (c) cites at least one concrete planning-document resource where scene cards or speech units are available. Any entry that comes up short gets patched in the same pass. Special attention to B41 "Less Than Genuine" and B45 "What the Jury Found" — these slots held different chapter content in the April 8 diagnosis due to post-April-8 B40–B48 renumbering, so verify independently that their current content is still in the monotony zone rather than inherited positionally.
2. **Three-way drift check** across the twelve monotony-zone chapters: guide Section 7 entries vs. April 6 deploy commit `15c7b32` (`_deploy/.git` — "Fresh deploy: ChappaquaPoison v3 with corrected banners") vs. current `posts/md/` source. Verify line-number anchors still point at what the guide says they point at, verify verbatim quotes the guide leans on still exist in the posts verbatim, verify every Do Not Touch passage is present and unchanged, verify the four rewritten Success Feel descriptions match the actual chapters. Log drift to `Audits/PHASE2_PREP_DRIFT_LOG.md`, fix what's in-flight fixable, surface the rest.
3. Optional: WebFetch live site for a third comparison point (`chappaquapoison.com`). Ask Steve for the URL at the top of Session 170.
4. Once prescription audit and drift check clear, Steve picks the first chapter to rewrite and Phase 2 begins. The enrichment guide's Section 7 entries are the work orders.

**Remaining open items beyond Session 170's first actions:** Legal pass, Steve/Evie safety pass, broader 208-entry file_missing audit (Phase 2-adjacent), duplicate evidence index entries cleanup (B-7_02, ExTR_06 quadruple, ExTR_05 vs LEGAL-HUMPHREY-RECUSAL parallel). (The `chappaqua-editorial` skill THE NUMBERING line was corrected this session from "50 posts. B00–B47, B100, B101" to "53 posts. B00–B53, B13 dissolved" in the writable `skills/chappaqua-editorial/SKILL.md` — the read-only system copy at `.claude/skills/` still carries the old text and will need a separate cycle to pick up the correction.)

**THE READING LAYER — READ FIRST:**
- `Standards/BEFORE_YOU_WRITE.md` — **(Sessions 163-164, updated Session 167)** THE FIRST DOCUMENT A WRITING SESSION READS. Contains actual passages demonstrating each voice register (the book at its best AND worst), emotional spine written in the book's own register, character presences as felt rather than described, Do Not Touch manifest, 15 craft notes from cover-to-cover reading, **Section V-A: execution learnings from Sessions 165-167**, and the loading sequence for subsequent documents. The QA checklist now collapses three checks (scene/physical/Steve) into one: "Can the reader draw the room?" ~20 minutes. Not optional.

**Key files for writing work (load in this order after BEFORE_YOU_WRITE.md):**
- `Standards/CHAPTER_ENRICHMENT_GUIDE.md` — **THE LIVING REWRITE PREP CONTAINER.** Single-source file for research, refined recommendations, writing samples, and (going forward) arc-read findings that feed the eventual systematic rewrite. Thirteen per-chapter entries exist for all 12 monotony-zone chapters. Sessions 165-167 executed them as samples. The guide continues to grow. Header currently reads "HISTORICAL" (Session 167 error); correct after reading the guide in full.
- `Standards/EDITORIAL_QA_STANDARD.md` — Five process rules that prevent monotony + three self-interrogation questions (Am I hiding? Am I lecturing? Does the ending pull?).
- `Standards/WRITING_PLAN.md` — Maps all interventions to chapters. Updated Session 159.
- `Standards/ENRICHMENT_SESSION_NOTES.md` — FULLY SUPERSEDED for chapter-level work. All 12 chapters now have guide entries. Notes remain useful only for: Backstory Excursion Standard, cross-chapter patterns (5), research queue (9 targets).
- `Standards/VOICE_TARGET_PROFILE.md` — What "done" looks like per chapter.
- `Audits/VOICE_STYLE_ANALYSIS_2026-04-08.md` — Full diagnostic with charts.
- `Audits/WRITING_SESSION_LOG.md` — Session-by-session progress through Session 167.

**INDEPENDENT CONVERGENCE (Session 164):** Two different AI models (Claude and Gemini), working separately from the same 51-chapter source text, converged on five conclusions: (a) restraint is the book's power; (b) monotony zone cured by physicality; (c) archive built from desperation not competence; (d) two antagonists — Tara and the system; (e) system punishes nuance. These are structural properties of the text, not interpretive opinions. Embedded in BEFORE_YOU_WRITE.md Craft Notes 10, 14, 15 and Steve character description.

**Process correction (Session 160):** Robinson moment writing attempted then fully reverted after author critique. The fix: build the guide first, write only from a complete guide. All reverted chapters in `Backups/session160_pre_writing/`.

**⚠ NUMBERING TRAP (Session 159):** Scene_Candidate_List.md uses sequential chapter numbers that do NOT match B-numbers. Always cross-reference by CHAPTER TITLE.

**⚠ PROCESS RULE (Session 160):** Do not delegate evidence research to agents. Do not defer editorial decisions to author. The session reads evidence, makes judgments, resolves all open items in the guide.

**Next writing work:**
1. **Arc-level sequential read** (recommended dedicated session) — read all 12 enriched chapters in B-number order to verify pacing, information sequence, no prolepsis violations, no cross-chapter phrase/image repetition. This is the remaining Phase 4 work. **Follow `Standards/ARC_READ_PROTOCOL.md`** (created Session 167 — order, checklist, findings template, success criteria). Findings go to `Audits/ARC_READ_FINDINGS.md`.
2. **Legal pass** — review all legal claims, citations, and procedural descriptions for accuracy, currency, and risk.
3. **Steve and Evie safety pass** — review the entire book for anything that could compromise Steve's legal position or Evie's safety and wellbeing.
4. Read `Standards/BEFORE_YOU_WRITE.md` FIRST (~20 minutes) regardless of which task is chosen.
5. Open items: Evie age question in B46 (author judgment needed), TEXT_TARA_JURY_VERDICT_DISMISSAL exhibit not locatable, Humphrey courtroom transcript needs research, SCREENSHOT_SGT_CARAWAY_COURT_ORDER still missing, federal complaint Genovese correction, B52 DiFabio name, Fishman protocol.

**INTEGRATION DRAFT IN PROGRESS.** Session 146 began executing all 8 integration items from the review plus 2 CO reversals. Work is on the `integration-draft` git branch; the RC state is preserved on `master` at commit `5054346`. The old book PDF is intact in GumroadBundle.

**GIT BRANCH STRUCTURE:**
- **`master`** at `5054346`: RC baseline. All review-era changes (Sessions 122–145) committed. This is the revert point.
- **`integration-draft`**: All 10 changes applied. HTML build passes clean. PDF regeneration pending.

**INTEGRATION CHANGES APPLIED (Session 146):**
1. **CO-010 revert:** Whitespace dividers removed from B32 (after "He left Kelly in the hospital") and B35 (after "face my accuser" section).
2. **CO-019 revert:** Three editorial sentences restored to B37 Genovese passage ("The concern was not about Evie's safety...").
3. **B32 Humphrey expansion:** Two paragraphs added — Humphrey's spoken words from ExTR_03 ("she dismissed it because he defaulted"), Kelly hearing the history reduced to a file. Hearing's procedural housekeeping (Jackman fee, 18b attorney) described.
4. **B48 precision pass:** "fire on the property" → "threats and vandalism." Frozen accounts restored with Russell Declaration support.
5. **B36 Linda's compassion:** "Tara could be doing so much better too" added from ExO_06 PS, with narrative framing.
6. **B16/B17/B23 evidence de-duplication:** 4 repeated embeds (MSG-JESSE-001, MSG-MATAN-006, MSG-MATAN-005, MSG-JESSE-002) replaced with textual references on 2nd appearances. B16 keeps all originals. B17 and B23 use prose references.
7. **B35 closing:** Catalogue converted to observed scene — Kelly walking out of the Yonkers courthouse.
8. **B31 wine/urine inference:** Sentence added explaining ingestion→urine pathway and wine as delivery mechanism. Lab's abortifacient commentary cited with connection to Kelly's pregnancy.
9. **B47 record alteration:** Scene expanded — Bowman pulling up the case management system, discovering the field change, the implications spelled out.
10. **VE-001 running headers:** Part title pages now have explicit empty headers in generate_book.js. Page numbers retained.

**CURRENT PHASE: INTEGRATION DRAFT COMPLETE. PDF REGENERATION NEXT.** The review earned closure at Session 142 (three consecutive zero-CO test sessions). Session 145 produced the integration plan. Session 146 executed all items.

**ADVERSARIAL REVIEW STATUS:**
- **Phase 1 (Cold Read): COMPLETE.** Sessions 124–129. All 51 chapters read. 184 findings.
- **Refinement Pass 1: COMPLETE.** Session 130. 184 → 82 findings.
- **Phase 2 (Evidence Dive): COMPLETE.** Sessions 131–133. Full Standard sessions on B32, B35, B36, B37, B48, B49. EC-001 discovered (lab number discrepancy).
- **Phase 3 (Execution): COMPLETE.** Sessions 134–137. All 22 change orders resolved (17 EXECUTED, 5 CLOSED). EC-001 RESOLVED — 349.87→649.87 corrected across all files. Wine/urine language corrected. All 5 hypotheses assessed (H1–H3, H5: SUPPORTED; H4: CHALLENGED → SUPPORTED after CO-022).
- **Phase 3.5 (Session 35 Resolution + First VE): COMPLETE.** Session 138. All 4 Session 35 violations resolved. First Visual Editor pass: 5 findings, 80/521 pages examined.
- **Phase 3.5b (PDF Regeneration): COMPLETE.** Session 139. PDF regenerated from corrected markdown. 8/8 correction checks passed. VE-005 RESOLVED.
- **Phase 4 (Consecutive Zero-CO Test): COMPLETE.** Counter: **3/3.** Session 140 (B04+B05): 0 COs. Session 141 (B21+B22): 0 COs. Session 142 (B43+B44): 0 COs. **COMPLETION CRITERION MET.**
- **Phase 5 (Post-Closure): COMPLETE.** Session 143: Full VE pass (all 489 pages), author determinations (3 withdrawn, 6 demoted, 2 CO reversals flagged). Session 144: Comprehensive S1/S2 evidence review — all verifiable claims checked, B35 building passage fully verified (all 6 links), B48 revised (Russell Declaration supports forged filing + frozen accounts). Session 145: Integration plan produced.
- **Critique:** `Planning/THE_CRITIQUE.md` (157 findings — 154 active, 3 withdrawn. 22 COs all resolved, 7/7 editors with findings).
- **Integration Plan:** `Planning/INTEGRATION_PLAN.md` (8 actionable items remaining, prioritized with evidence ready).
- **State:** `Planning/REVIEW_STATE.json`.
- **Process:** `Planning/ADVERSARIAL_REVIEW_PROCESS.md`.
- **Skill:** `book-review` (load at start of every review session).

**PENDING (Session 147 Verified):**
- **Git commit on integration-draft** — All 10 changes + late-session files (Theme 12, Jon/Linda entries, LESSON_FROM_THE_REVIEW.md) are on disk but uncommitted. Commit as first action of next working session.
- **PDF regeneration** from integration-draft branch (DOCX → LibreOffice → PDF). The existing PDF in GumroadBundle is from the RC baseline, not the integration draft.
- **Author review** of all 10 changes in rendered PDF. See NEXT_SESSION_PROMPT.md for per-change review checklist.
- **VE-001 verification** — Part title pages should have empty running headers in the new PDF. Must be visually confirmed.
- **Merge decision:** If author approves, merge `integration-draft` → `master`. If not, `master` remains the RC. Individual changes can be reverted selectively with `git checkout master -- posts/md/B{XX}_*.md`.

**OPEN ITEMS:**
- **Design spec tests:** 6 queued from MEMO Item 5.
- **Process memo:** Overdue (was due at S137, went to execution instead).

**SESSION 147 NOTES:**
Session 147 verified all late-session S146 work on disk: Standards/LESSON_FROM_THE_REVIEW.md (new, untracked), Theme 12 in NARRATIVES_AND_THEMES.md (line 603), Jon Russell entry in CHARACTERS.md (line 996+), Linda Russell expansion (with "The Poison in the Family" in Connected To). All 9 modified post files + generate_book.js confirmed in git diff. Handoff documents strengthened for next session.

**SESSION 150 NOTES (April 6, 2026):**
Session 150 was a banner investigation and Replicate audit. Found that ALL banners currently deployed are wrong — Flux 2 Pro photorealistic style. Correct banners (hand-inked gpt-image-1 style) exist only in `~/Claude/Blogs/ChappaquaPoison_v3/Images/banners/v3_backup_20260328/`. Full findings documented in BANNER STATUS section above. Prior sessions also attempted chapter renumbering (B47a/B47b) which needs reconciliation with posts.json. See NEXT_SESSION_PROMPT.md for restoration plan.

**SESSION 155-157 NOTES (April 6-7, 2026):**
Session 155: `chappaqua-session` bootstrap skill created. Session 156: Email infrastructure operational (Cloudpost MTA, DKIM signing, Cloudflare Email Routing). Session 157: Advocacy Engine v2 — complete strategic rebuild of outreach from supplicant to asset positioning. Deep archive read of 9 chapters produced the positioning inversion. New files in `CaseFiles/17_Advocacy_Engine/`: STRATEGY.md, PIPELINE_v2.md, Advocacy_Engine_Master.xlsx, Westchester_Master_Contacts.xlsx. Skills updated with epistemological insight about reading chapters vs. indexes. FIJ grant deadline April 27, 2026. See NEXT_SESSION_PROMPT.md for full details.

**SESSION ~180 NOTES (April 11, 2026):**
Site repositioning: complete rewrite of all positioning touchpoints from "evidence archive" to "documentary narrative." Created positioning system with 6 reusable outputs at `Planning/POSITIONING_DRAFT.md`. Deployed: base.html meta/og, index.html meta/hero, book.md (three-paragraph positioning + CTA), llms.txt (three-sentence positioning + literary nonfiction framing), 54 per-post ai.txt files. PDF source updated: fifty-two → fifty-four, author name removed from copyright, "Evidence Archive Edition." Created `chappaqua-outreach` skill for communications/outreach workflow. Updated `chappaqua-session` skill with fourth workflow documentation. Key author directives: (1) Don't say we stand in opposition to the gag order — the art and commerce stand in opposition by existing. (2) The fall book is "a great work of American nonfiction." (3) Next phase is direct outreach — witnesses, lawyers, activists, coalition partners. (4) CTA architecture needed: hook → stay → support → amplify.

**NEXT SESSION IS OUTREACH.** The author has directed that the next phase is direct marketing and outreach via CloudPost. Invoke `chappaqua-outreach` skill. Read `~/Claude/CaseFiles/17_Advocacy_Engine/OUTREACH_ARCHITECTURE.md` — the intelligence layer (contact dossiers, voice guide, response protocols, legal/ethical boundaries). Then read cloudpost state file, STRATEGY.md, and PIPELINE_v2.md. Get status updates from Steve on: Marc Fishman call, FIJ grant, Wave 0 edits. The architecture document defines a multi-session build sequence and open questions Steve must answer before Track A sends.

**NEXT SESSION IS REAL DRAFT.** The test draft phase is complete as of Session 171. Invoke `chappaqua-session`, pick writing workflow, read `Audits/REAL_DRAFT_OPERATIONAL_BRIEF.md` first — it contains the five rules, four phases, pipeline QA process, and multi-session architecture. Then read `Standards/BEFORE_YOU_WRITE.md`. Phase 1 is a staging audit; Phase 2 is chapter-by-chapter rewrite.

**TWO WORKSPACE PATHS:** This project has files in two locations:
- `~/Blogs/ChappaquaPoison_v3/` — the author's source directory (read-write)
- `~/Claude/Blogs/ChappaquaPoison_v3/` — the working copy with source, build, and deploy
Changes made in one are NOT automatically reflected in the other. The git repo lives at `_deploy/.git/` inside the Claude workspace path. See "Stage 6: Deploy to GitHub Pages" in the Build Pipeline section for the full deploy process.

**51 posts total (B00–B51, B13 dissolved).** All have at least editorial-pass-1. All 51 posts voice-enriched and deployed to `posts/md/`. B00, B50, B51 are special (prologue, afterword, back cover) with no status field.

**BOOK PDF: CURRENT.** `GumroadBundle/ChappaquaPoison_BOOK_2026-04-02.pdf` — ~489 pages, 7.3 MB. Regenerated Session 139, all corrections verified. 8/8 checks passed.

**SITE IS LIVE AND FULLY DEPLOYED.** Deployed to chappaquapoison.com via GitHub Pages. All 51 chapters, working evidence system, clean navigation, corrected banners, real deposition clips. Git repo is `_deploy/.git/` — see Build Pipeline "Stage 6" for deploy process.

**Deferred (not blocking review):** Cloudflare R2 setup (Tier 2 video), "manifesto" language (unsourced), white supremacist calls (safety-deferred), AI vocabulary spot-clean, redundancy audit.

### BANNER STATUS (April 6, 2026 — Session 152 update)

**SIGNIFICANT PROGRESS MADE.** Session 151 restored gpt-image-1 banners from backup. Session 152 performed full QA against 4-module art direction, swapped 8 banners with better candidates, and generated 9 new banners via Flux Kontext Pro. All 3 exclusion violations (B07, B08, B27) are now fixed. 17 banners total improved. 7 still need regeneration. Full audit in `Audits/BANNER_QA_2026-04-06.md`.

**Current state of v3/ banners (51 files after orphan cleanup):**
- 10 PASS (original gpt-image-1): B05, B25, B26, B29, B33, B37, B40, B43, B44, B45, B46
- 17 IMPROVED (candidate swaps + Kontext Pro): B01, B03, B06, B07, B08, B09, B10, B12, B15, B17, B22, B27, B30, B38, B42, B50, B51
- 14 BORDERLINE (original gpt-image-1, scene partially captured): B04, B11, B14, B18, B19, B20, B21, B24, B28, B31, B32, B34, B35, B39, B41, B47
- 7 STILL NEEDS REGEN: B00, B02, B16, B23, B36, B48, B49

**New pipeline tool discovered:** `black-forest-labs/flux-kontext-pro` on Replicate ($0.04/image). Takes a style-reference image + text prompt → generates new scene in similar style. ~70% match to gpt-image-1 house style (crosshatch vs watercolor). Scripts: `scripts/kontext_test.py`, `scripts/kontext_batch.py`.

**Originals before all swaps backed up to:** `Images/banners/v3_pre_swap_backup/`

**Two banner styles exist — only ONE is correct:**

| Property | CORRECT (gpt-image-1) | WRONG (Flux 2 Pro) |
|----------|----------------------|---------------------|
| Style | Hand-inked suburban-noir storybook illustration | Photorealistic digital painting |
| Look | Bold graphic, woodcut-like linework, brush-and-pen outlines, muted watercolor-and-gouache washes over visible paper grain | Warm amber, thick brushstrokes, oil painting texture, cinematic lighting |
| Figures | Simplified human forms, small black oval eyes, minimal facial features, rounded adult proportions | Realistic faces, detailed features, photographic proportions |
| File size | 300–714 KB | 1.1–1.9 MB |
| Backend | `backend_openai` (gpt-image-1, size 1536×1024) | `backend_flux2pro` (Replicate black-forest-labs/flux-2-pro) |
| Match to site | Matches the book cover image in the hero banner | Does NOT match — looks like a different site entirely |

**Where the correct banners are:**
- **BACKUP:** `~/Claude/Blogs/ChappaquaPoison_v3/Images/banners/v3_backup_20260328/` — 49 files (B01–B49 in OLD numbering, before the B47a/B47b renumber), all 300–714KB, all created Mar 28 19:43 EST
- **Mapping from backup → current numbering:**
  - Backup B01–B47 = Current B01–B47 (direct 1:1)
  - Backup B48 = Current B50 "Where Are They Now"
  - Backup B49 = Current B51 "Back Cover"

**Where the wrong banners are (CURRENT STATE):**
- `~/Claude/Blogs/ChappaquaPoison_v3/Images/banners/v3/` — 54 files, all Flux 2 Pro photorealistic (1.1–1.8MB)
- `~/Claude/Blogs/ChappaquaPoison_v3/_site/images/banners/v3/` — same wrong banners
- `~/Claude/Blogs/ChappaquaPoison_v3/_deploy/images/banners/v3/` — same wrong banners
- `~/Blogs/ChappaquaPoison_v3/Images/banners/v3/` — 47 files, also wrong (1.1–1.9MB)
- The live site at chappaquapoison.com is serving the wrong banners

**Chapters that have NO correct banner in backup (need generation):**
- **B00** "Someone at the Gate" (Prologue) — not in backup
- **B48** "The Trap" (new chapter, was B47a) — didn't exist when backup was made
- **B49** "The Coward" (new chapter, was B47b) — didn't exist when backup was made
- **B52** "The Trap" / renumbered from old B50 — not in backup
- **B53** "The Coward" / renumbered from old B51 — not in backup

**WAIT — NUMBERING CLARIFICATION NEEDED:** The backup was made BEFORE the B47a/B47b renumber. The current posts.json shows B00–B51 (with B13 dissolved). But the git repo has commits referencing B52/B53 from a renumber that bumped B48–B51 to B50–B53. **The next session must reconcile the posts.json numbering with the banner filenames and the git repo state.** One of these numbering schemes is stale.

**Replicate prediction logs (confirmed Apr 6):**
- 149 total predictions on the chappaquapoison account
- 100% are `black-forest-labs/flux-2-pro` — no other model ever used
- Mar 28–29: ~136 predictions (the batch that produced the wrong photorealistic banners)
- Apr 6: 13 predictions (regeneration attempts from this session, also wrong style)
- Replicate API token: see `scripts/.env`

**To generate new banners in the correct style, you need:**
- An OpenAI API key (set as `OPENAI_API_KEY` in `scripts/.env`)
- Use `backend_openai` in `scripts/banner_pipeline.py`
- The STYLE_BLOCK in the pipeline is correct — it describes the hand-inked style
- The `copy_ready_prompts.json` has scene prompts for most chapters (51 keys: B00–B46, B49, B51, X102, X103)

**Banner pipeline files:**
- `scripts/banner_pipeline.py` — Main generation script (openai, replicate, comfyui, dry-run backends)
- `scripts/banner_steward.py` — Production process with color validation (PALETTE_FAMILIES)
- `scripts/copy_ready_prompts.json` — Proven scene prompts per chapter (keys are manifest site_codes)
- `Planning/PRODUCTION_PROCESS.md` — Governs banner production (4 phases, scoring rubric R1–R9/C1–C5/S1–S6/P1–P9/O1–O3)
- `Images/banners/v3_backup_20260328/` — THE CORRECT BANNERS (backup)
- `Images/banners/candidates/` — All Flux 2 Pro candidates (wrong style, for reference only)
- `Images/banners/SESSION_BRIEF.md` — Banner production session brief
- `Images/banners/production_log.json` — Production log (0 accepted via formal process)

**Art direction system (4 modules):**
- Module 1: House Style Constitution (`Planning/HOUSE_STYLE_CONSTITUTION.md`)
- Module 2: Character Anchor Canon (`Planning/CHARACTER_ANCHOR_CANON.md`)
- Module 3: Banner Scene Canon (`Planning/BANNER_SCENE_CANON.md`)
- Module 4: Color Constitution (`Planning/COLOR_CONSTITUTION.md`)

**CRITICAL LESSON:** Multiple sessions confused the two banner styles. The Flux 2 Pro banners look polished and professional but are WRONG for this site. The correct style matches the book cover in the hero banner — hand-inked, paper grain visible, muted palette, simplified figures. When in doubt, compare any banner to the hero image at the top of chappaquapoison.com. If it looks photorealistic, it's wrong.

### Editorial History (Sessions 11–137)

The detailed session-by-session editorial log has been archived. Key milestones for reference:

- **Sessions 11–68:** Evidence index built (2,191 entries), source exhibit linkage (421 linkages), evidence presentation overhaul (100+ embeds converted), book pipeline rewrite
- **Sessions 69–91:** Baldwin voice enrichment — 19 sessions, all 51 chapters enriched, 4 MAJOR narrator-editorializing passages fixed, 3 source prolepsis passages fixed
- **Sessions 95–105:** Reader feedback, character research, character pass (13 yarns), B41/B42 written, full chapter renumbering
- **Sessions 110–122:** Middle third editorial plan — 12 passes, B23–B39 raised to 9.0/10, book rebuilt
- **Session 123:** Adversarial review designed — 7 editors, 5 phases, hypothesis tests, process document written
- **Sessions 124–129:** Phase 1 Cold Read — 51 chapters, 184 findings, 3 S1 findings, evidence seal broken (EC-001)
- **Session 130:** First refinement pass — 184 → 82 findings, signal density 91%, critique compressed
- **Sessions 131–133:** Phase 2 Evidence Dive + Full Standard sessions (B32, B35, B36, B37, B48, B49). 132 total findings. Convergence mechanism added (Change Order system). 22 COs extracted.
- **Sessions 134–137:** Phase 3 Execution. All 22 COs resolved (17 EXECUTED, 5 CLOSED). EC-001 corrected (349.87→649.87 across all files). All 5 hypotheses assessed. Wine/urine language corrected. Completion criterion changed: author acceptance gate replaced by consecutive zero-CO test.

Reports: `Planning/MIDDLE_THIRD_PROGRESS_REPORT.md`, `Planning/PASS_12_INTEGRATION_REPORT.md`, `Enriched/qa_reports/`

**Canonical index:** 2,191 entries. 4 tiers (Hero: 202, Primary: 518, Secondary: 1,440, Tertiary: 21). `source_exhibit` field (421 non-null linkages). Build: 0 errors.

<details>
<summary>Full Session History (Sessions 11–122) — Click to expand</summary>

**Session 49 hero/inline final sweep:** Comprehensive audit of all 48 posts. Resolved ALL remaining hero/inline mismatches — 8 items demoted, 5 inline embeds added across B06, B12, B18, B21, B38. B05, B07, B09 also resolved (from Session 48/49 overlap). **0 hero/inline mismatches remain.**

**~~⚠ CRITICAL FINDING — Session 45: 558 Phantom Evidence IDs.~~** **RESOLVED Session 46.** The Session 45 extraction script used `id` instead of `exhibit_id` to query the canonical index, producing a false count of 558 phantoms. Actual count was **12 phantom IDs**, all resolved in Session 46 (13 entries added: 4 parent/umbrella, 3 naming aliases, 1 new real entry, 4 legacy/placeholder/missing). All 13 posts are now unblocked for curation.

**Session 52-53:** Tightened institutional middle blog posts (B19, B22, B36, B37, B38, B40). Generated Draft 52 (8,304 lines). Completed cover-to-cover read. Editorial recommendations saved to `Blogs/ChappaquaPoison Book/Drafts/Draft52_Editorial_Recommendations.md`.

**Session 54:** Added Author's Note on the Public Record to book front matter (litigation privilege framing from page one). Updated standalone `afterword.md` from "ready for filing" to filed tense — Monell + § 1983 claims, "He cannot fight Chappaqua alone. The record can." Fixed Crutcher Cast of Characters entry ("witnessed a pill" not "helped administer"). Generated Draft 53 (409 pages, 86,341 words) + PDF + EPUB. Created comprehensive editorial plan (`Blogs/ChappaquaPoison Book/Drafts/Editorial_Plan_Session54.md`) synthesizing three independent editorial assessments into 6 sequenced sessions (A-F): Kelly's arc → Tara's duality → inner-thought passages → Evie anchoring → front/back matter → final generation. Next work: Session A (Kelly's arc in B08, B30, B31).

**Session 55:** Executed all 6 sessions of the editorial prose plan (A-F). Session A: Kelly's emotional arc deepened in B08, B19, B30, B31 — added "Good Victim" hero embed (QUOTE-GOOD-VICTIM) in B19, Kelly's mirror observation in B30, grief-before-lab-results in B31, Kelly's cognitive quality in B08. Session B: Tara duality edits in B35-B39 — Walsh Sr custody threat, Tara-as-compound-not-individual framing. Session C: Inner-thought passages added to B21, B27, B28, B44, B45, B49 — italic trigger → reflection → unanswered possibility model. Session D: Evie anchoring hard-cuts in B25, B26, B32, B33, B43, B46 + delay-as-weapon framing + character introductions (Morales-Horowitz censure, Guttridge donations, Schauer ADA, Farquharson LCSW/councilwoman) + Contemporaneous Scene Rule fix in B29. Session E: Voice pass — pattern-naming removed (B28, B29, B48), rhythmic repetition trimmed (B30), legal name density reduced (B27), afterword grounded with federal filing scene. Session F: Draft 54 generated (87,742 words, 399 pages) + PDF + EPUB. All builds pass clean (0 errors, 1 pre-existing warning re: B-7_020).

**Session 56:** Publication prep. Fixed last build warning (B-7_020 canonical index entry pointed to wrong filename — corrected to match actual file on disk, also fixed corrupted `extension` field on related B-7_02 entry). Back cover (B51) sharpened: "walks into a relationship" → "moves in with," substance terminology matched to evidence language, weakest Pontius Pilate list item cut, "It is a story about..." paragraph cut (was arguing not witnessing). Spot-read 5 most heavily edited posts from Session 55 (B19, B27, B28, B30, B44, B45) — all clean, no graft marks or rhythm breaks. Subtitle confirmed: "An American Tragedy." Dedication confirmed: "For Evie." Draft 55 generated (87,707 words, 399 pages) + PDF + EPUB. Build: 0 errors, 0 warnings.

**Session 58:** Evidence presentation overhaul. Converted all 7 text message embeds in B17 from screenshot-in-phone-frame to typed CSS text bubbles (verified against evidence PNG files). Created `msg-secondary` class for right-aligned darker gray bubbles in non-Steve conversations (Tara=primary/left, other=secondary/right). Designed three new Ghost-style image formats: `photo-card` (inline photos), `document-card` (legal documents), `photo-gallery` (multi-image grids: 2up/3up/4up/9up). Converted 3 proof-of-concept image embeds (B18: EB1_P105, EB1_P107; B21: C-6_03). CSS added to `templates/post.html`. EVIDENCE_EMBED_STANDARDS.md updated to v1.2. **47 image embeds across 21 posts and 16 message embeds across 12 posts remain for conversion.**

**Session 58b (continued):** Fixed 7 CSS errors/corner cases in multi-up message template (media query ordering, font-size resets, continuation ellipsis scaling, caption max-width, border-radius protection at 480px). Created `_site/test-multiup.html` (message layout test page) and `_site/test-images.html` (image format test page with all 12 layout variants using real evidence). EVIDENCE_EMBED_STANDARDS.md updated to v1.3 with multi-up message documentation.

**Session 59:** Hero image deep review. Opened and visually inspected every hero evidence item across all 49 posts (150+ items) plus searched Master Photos (399 images across 4 Evie Story Books) and blog Evidence folder (715 images). **Key finding: only 16 of 49 posts have a genuine photograph or screenshot as hero evidence.** 30 posts run exclusively on documents, legal filings, audio/video, quotes, or messages. Identified 10 high-priority posts with strong photo candidates ready for hero promotion (B00, B06, B12, B21, B28, B32, B34, B40, B45, B49). Found 11 PHOTO_ entries in canonical index with empty `rel_path` (files not yet copied to Evidence folder). Identified 7 category mismatches (genuine photos categorized as "Document" and vice versa). Full report: `Hero_Image_Review_Session59.md`.

**Session 60:** Source Exhibit Linkage — architecture and planning. Identified the fundamental provenance gap: hero evidence rendered inline (typed iMessage bubbles, pull quotes, photo cards, legal text blocks) are derivative presentations of primary source artifacts, but those source artifacts don't appear in the evidence footer or book endnotes. Designed the `source_exhibit` field — a nullable string on each canonical index entry pointing to the `exhibit_id` of the parent artifact. Classified all 150 hero items across 8 relationship types: self_sourcing (26), page_of_parent (1+), extraction_from_archive (16), text_from_transcript (23), text_from_declaration (17), quote_no_file (13), blog_excerpt (12), media (1+). Authored `Standards/SOURCE_EXHIBIT_SPEC.md` v1.1 defining the schema, all 8 relationship types with specific exhibit mappings, pipeline changes for both web (`build_html.py` footer auto-injection) and book (`blog_to_book.py` endnote enrichment), 5-phase implementation sequence, and the Provenance Principle (readers see institutional language — case names, filings, archives — not internal file names). Established Source Archives vs. Source Exhibits distinction: iMessage DB and Bates-stamped discovery are source archives (too large for per-item parents but NOT tertiary); conversation PDFs are the most specific usable parent for `source_exhibit`. Identified new work needed: court document facsimile CSS (Times New Roman), email rendering CSS, Evie Story Book page spread extraction, evidence hunt for 13 file_missing items. Created pre-revision backup (commits `6b62bbd` + `3221702`). Wrote phased implementation plan into ORIENTATION.md and NEXT_SESSION_PROMPT.md. **This revision supersedes the previous cluster-based style overhaul plan — source exhibit linkage must be established BEFORE the per-post conversion passes.**

**Session 61:** Source Exhibit Linkage — Phase 1 (schema + automated linkage). Added `source_exhibit` field to all 2,188 canonical index entries. Wrote `scripts/link_source_exhibits.py` with deterministic linkage rules for 6 relationship patterns: MSG-numbered→full conversation (71 items), LEGAL-INQUEST-*→transcript (20), LEGAL-DVRO-*→transcript (17), TRIAL-BATTERY-*→transcript (1), suffixed items→parent (299), plus self-sourcing classification for standalone exhibits, court filings, photos, audio/video, blog excerpts, emails, documents (1,305 confirmed null). **Key finding:** SOURCE_EXHIBIT_SPEC v1.1 listed MSG-JESSE-008 as the full conversation document, but the actual data shows the unsuffixed entries (MSG-JESSE, MSG-MATAN, etc.) are the full conversations — used unsuffixed as source parents. **Results:** 408 items linked automatically, 1,305 confirmed self-sourcing (null), 20 hero items left as needs_manual (all file_missing — deferred to Phase 6 evidence hunt), 475 non-hero unclassified (default null). Validation: 0 errors, 0 invalid references. Build: 0 errors, all checks passed. Report: `Audits/source_exhibit_linkage_report_20260321.md`.

**Session 62:** Source Exhibit Linkage — Phases 2+3. **Phase 2:** Added court document facsimile CSS (~145 lines) and email facsimile CSS (~130 lines) to `templates/post.html`. Court facsimile: Times New Roman, cream background, Q&A format with witness blocks and optional line numbers. Email facsimile: system font header block, Georgia body, attachment indicator. Created test page `_site/test-legal-email.html` with 6 real evidence examples (3 court, 3 email). Updated EVIDENCE_EMBED_STANDARDS.md to v1.4: Section 2b (court facsimile docs with decision guide), Section 3b (email facsimile docs with decision guide), Section 9 (Provenance Pairing Rules — auto-injection spec, relationship type → footer behavior table, reader-facing language patterns, book endnote provenance). Deprecation notes on old Sections 2 and 3. **Phase 3:** Identified 3 EB_ hero items needing page spread extraction (EB1_P107, EB3_MASTER_002, EB3_MASTER_024). Analyzed Evidence Index PDFs (Books 1-4) with PyMuPDF to determine page structure (alternating image/caption pages). Visually inspected all hero pages and adjacent pages to identify Kelly Russell's deliberate juxtapositions. Created 3 composite spread images using Pillow: EB1_SPREAD_P105-107 (father holding baby → shattered iPhone), EB3_SPREAD_IMG001-002 (Evie in Elsa dress → Evie in clawfoot tub), EB3_SPREAD_IMG023-024 (Brienne CPS confession → Walsh compound porch). Indexed 3 new entries, linked 3 hero items to their spreads. Build: 0 errors, 0 warnings.

**Session 63:** Phase 5 — Post-by-Post Conversion. ALL old-format evidence embeds converted across all 50 posts (~100+ conversions). 9 old format classes eliminated → 6 new CSS formats. Build: 0 errors.

**Session 64:** Phase 6 — Evidence Hunt. All 13 `file_missing` hero items resolved: 10 linked to source documents, 3 confirmed self-sourcing. 2 files copied to Evidence from CaseFiles. 1 duplicate entry removed. `rel_path` set for all 13. Build: 0 errors.

**Sessions 67-68:** Book pipeline overhaul. Complete rewrite of `scripts/generate_book.js` implementing BOOK_STYLE_GUIDE.md: five evidence treatments (A-E) with distinct visual styling, date-based output naming, built-in cover/copyright/title pages, three appendices (Cast of Characters, Timeline, Evidence Index). Jury vs. Reader Rule implemented (cleanEvidenceBody strips legal line numbers, metadata, digital exhaust; truncateEvidenceLines caps at 15 lines). Timeline appendix fully scrubbed — all quoted content (HTML/CSS dumps, court filing boilerplate, OCR artifacts, transcript headers) removed, leaving clean chronological date+post-reference list. B50 factual correction (Steve's bio). Cover-to-cover PDF readthrough found and fixed 5 issues: Parts II/III ordering (swapped due to Phase metadata sequence — fixed with pre-scan scheduling), leaked `<cite>` HTML tag (added catch-all HTML strip), spaced-out heading artifacts (reduced characterSpacing from 80→40), broken compound hyphens at line breaks (non-breaking hyphen U+2011 for compound words). Book page updated: ePub option removed, PDF download linked directly. **Current book: ChappaquaPoison_BOOK_2026-03-22.pdf — 429 pages, 95,524 words.** Site build: 0 errors.

**Session 65:** Phase 7 — Verification + Draft Generation. Wrote and ran `scripts/audit_phase7.py` (6 checks: source_exhibit target validity, hero auto-injection simulation, posts.json↔canonical sync, hero file_missing, chain detection, tier consistency). Initial run found 30 errors: 16 hero items with `file_missing` still true (Session 64 resolved them but didn't flip the boolean), 5 lowercase tier values, 9 null-ID stub entries. All fixed: 14 `file_missing` flags set to false, 5 tier values title-cased, 9 null stubs removed. Re-run: 0 errors, 0 warnings. Full site build: 273 HTML, 746 images, 0 errors. Rendered HTML spot-check of 7 posts (B17, B18, B21, B24, B34, B40, B44): all "Explore all N" counts correct, source exhibits auto-injected where expected (B17: 5 sources, B18: 3, B21: 1, B34: 1), zero broken images, institutional provenance language in all footer chips. Draft 58 generated (89,413 words, 404 pages) + PDF (1.4MB) + EPUB (0.7MB). Book endnotes verified: source provenance with ibid. deduplication working correctly.

**Session 66:** Visual QA + iMessage conversion sweep. Fixed B25 image overflow (CSS `.embed-body img { max-width: 100% }` added to template). Fixed 3 PDF-as-img rendering bugs (B27 ExX_01 → document-text, B47 ExG_01 → court-facsimile, B47 ExJJ_05 → court-facsimile). Converted 11 message exhibits across 7 posts from old `embed-document` format to new `imessage-embed` CSS bubble style: B16 (4: SCREENSHOT_TARA_WALSH_HOUSEHOLD_ABUSE, TEXT_TARA_JUL21_MISCARRIAGE_CONDITIONAL, MSG-MATAN-006, MSG-JESSE-001), B18 (1: MSG-JESSE-008), B23 (2: MSG-JESSE-002, MSG-MATAN-005), B29 (1: QUOTE-TARA-FAMILY-CUSTODY-THREAT), B48 (2: ExOO_54, F-053), B49 (1: F-053). B21 LEGAL-DVRO-GOPAL-TEXT correctly kept as embed-document (court transcript, not iMessage). Full programmatic QA: 0 issues across 46 posts. Full visual QA in Chrome: 0 issues. Build: 273 HTML, 738 images, 0 errors, 0 warnings.

**Session 69:** Baldwin Voice Enrichment — skill convergence and rewrite planning. Converged two independent AI assessments (local Opus 4.6 + external Opus 4.6) of the three-voice enrichment system into a single production skill. Five substantive divergences resolved: (1) narrator constraint locked to third-person omniscient (no "I," no "you," no direct address — moral weight via juxtaposition and Contemporaneous Scene Rule); (2) prolepsis absolutely prohibited (no forward references of any kind); (3) literary allusions prohibited (factual legal context for comprehension only); (4) ratio revised from 60/40 → 30/70 (30% enriched, 70% preserved); (5) Sebald replacement principle (Parts V/VII: Sebald replaces dense procedure, doesn't add layers). Calibration examples in `Enriched/references/voice-system.md` rewritten to show clean versions as primary, borderline versions as teaching notes. QA diagnostic updated (prolepsis = CRITICAL, narrator editorializing = CRITICAL, literary allusions = CRITICAL). Backup/restore protocol added to skill (Step 1.5): per-chapter source snapshots, per-session directory snapshots, never-patch-revert-and-rerun. Created 19-session rewrite plan (`Local AI/BALDWIN_REWRITE_PLAN.md`): 11 enrichment sessions (grouped by part/arc for voice coherence), 6 QA sessions, 1 revision, 1 compilation. Created `Enriched/` directory structure (backups/, snapshots/, qa_reports/, handoffs/). NEXT_SESSION_PROMPT.md rewritten for Session 1 of 19: tier classification (all 49 chapters) + Prologue enrichment (B0). Skill packaged and installed as `baldwin-voice`.

**Session 70:** Baldwin Voice Enrichment — Session 1 of 19 (tier classification + Prologue). Classified all 49 chapters into enrichment tiers: 8 Tier 1 (deep: B06, B12, B25, B29, B31, B35, B43, B46), 20 Tier 2 (targeted), 15 Tier 3 (threshold), 6 Tier 4 (untouched: B38, B45, B47, B49, B50, B51). Classification based on full chapter reads — prose quality vs. evidence density, procedural compression, interior moment protection. Output: `Enriched/TIER_ASSIGNMENTS.md`. Enriched B00 "Someone at the Gate" (Prologue) as production test — 5 targeted additions, ~185 words (source 775w → enriched 960w, ~24% enrichment). Additions: court order gap (Baldwin), compound self-interruption (Sebald), La Melle role context, mechanism accumulation ("steady accumulation of small accommodations"), gate motif plant. Inline QA: PASS, 0 CRITICAL/MAJOR, 1 MINOR. Relocated Baldwin reference files from `~/Claude/TOBESORTED/` to `Enriched/references/`. Updated NEXT_SESSION_PROMPT and ORIENTATION with correct paths. Handoff: `Enriched/handoffs/HANDOFF_SESSION_1.md`. Prolepsis flags identified in B05 and B06 for future sessions.

**Session 72:** Baldwin Voice Enrichment — Skill revision and restart. Editor review of Sessions 1–4 output identified a 10x enrichment gap: 2.7% average enrichment vs 30% design parameter. Root cause: the skill listed evidence_index mining, physiological research, and place grounding as optional enrichment types, and the model defaulted to mechanism-naming (the only type requiring no external queries). Three structural deficiencies: (1) evidence_index never queried, (2) physiological research never done, (3) environmental/place detail absent. Revised the `baldwin-voice` skill with a mandatory content layer (Step 3: Mine the Content Layer) containing three sequential sub-steps: 3A evidence_index query, 3B physiology web search, 3C place grounding web search. Removed "The default is restraint" closing line (identified as key contributor to over-conservatism). Added concrete enrichment-rate benchmarks (Tier 1: 10%+ delta, Tier 2: 3%+ delta). Added "identify → fix → verify" QA loop and contemporaneous-scene check. Test-enriched B06 with revised skill: +499 words (+23.9%) with all three content sub-steps executed. Editor validated: "The skill revision worked." Two fixes applied: prolepsis in closing paragraph, contemporaneous-scene violation in Tara registers paragraph. **All Sessions 1–4 enrichment output superseded.** Enrichment restarts from B00 with revised skill. Tier classification retained. Before/after comparison of old work preserved in `Enriched/BALDWIN_ENRICHMENT_COMPARISON.md`.

**Session 73:** Baldwin Voice Enrichment — Session 1 of 19 (restart with revised skill v2). Enriched B00 "Someone at the Gate" (Prologue): +2 words (0.3%) — editorial direction established Prologue/Chapter structural principle (B00 = sensation, B28 = understanding; same event, two readers). All mechanism-naming from old Sessions 1-4 enrichment removed; only "heavy iron" added from LaMelle affidavit. Then enriched B28 "The Ambush": upgraded from Tier 3 → Tier 1, +173 body words (15.0%), 9 additions including opening mechanism ("Observe, document, remove"), Sebald on Provision 4, September environment, ambush photo detail, Evie front seat self-interruption, wind motif return bridging B00, prior stalking from police report. Constructed-innocence register (911 call, trial testimony) preserved untouched. Tier assignments updated. Handoffs: `Enriched/handoffs/HANDOFF_SESSION_1_v2.md`, `Enriched/handoffs/HANDOFF_SESSION_1_B28.md`.

**Session 74:** Baldwin Voice Enrichment — Session 2 of 19, B01–B05 (Part I first half). B01 "The Fool" (+4.0%, 2 additions: professional identity at passport control plants documentation/records motif, Baldwin pattern at Red Square). B02 and B03 zero enrichment (Tier 3, source at peak). B04 "Tara Knoll" (+4.4%, 2 additions: Chappaqua environmental detail plants enclosure motif, embodied physiological detail in football scene). B05 "Nothing Stolen" (+3.4%, prolepsis fix + intrusion mechanism). All Tier 2 chapters above 3% target. 0 CRITICAL, 0 MAJOR. Handoff: `Enriched/handoffs/HANDOFF_SESSION_2.md`.

**Session 75:** Baldwin Voice Enrichment — Session 3 of 19, B06–B10 (Part I second half) + Evie naming motif capture. Created `Enriched/references/MOTIF_EVIE_NAMING.md` documenting the Evelyn/"light of evening" naming motif, Tara's Gracie counter-operation, integration plan (both beats in B12), dusk echo map (B00/B28/B47/B49), and cover resonance. Enrichment: B06 "The Illness" (Tier 1, +198w/+11.3%: cognitive delay physiology, Nantucket place detail + register break, surveillance-illness convergence, prolepsis fix, "important→necessary" Baldwin, "He told himself he was grateful"). B07 "The Wine Bottle" (Tier 2, +67w/+5.1%: Sebald DV-120 examination — drugging operation in bureaucratic language). B08 "The Ultrasound" (Tier 2, +30w/+2.6%: Baldwin false pregnancy mechanism, under threshold but tier work complete). B09 "The Brooklyn Apartment" (Tier 2, +93w/+4.3%: Sebald psychiatric intake form — "The form does not ask: Is someone hurting you?"). B10 "The Builder" (Tier 2, +104w/+5.0%: Jamie irony — choosing child over deal, architecture-betrayal naming, builder motif). QA: All 5 PASS, 0 CRITICAL, 0 MAJOR. Architecture/building metaphor at 3 uses — deploy sparingly going forward. Handoff: `Enriched/handoffs/HANDOFF_SESSION_3.md`.

**Session 80:** Baldwin Voice Enrichment — Session 8 of 19, B26–B30 (Part V second half + Part VI opening). B26 "Sixteen Visits" (Tier 2 light, +42w/+1.4%: blog-sourced register break, self-interruption on delay-as-weapon, Visit 6 drop-off detail). B27 "The Bruises" (Tier 2, +86w/+3.0%: Sebald examination of Jackman double-negative, self-interruption on Guttridge "instability"). B28 verified only (already enriched Session 1 v2, MODEL POST). B29 "The Walsh Abuse Memo" (Tier 1, +232w/+16.0%: Walsh Sr. letter to Gordon-Oliver as Sebald artifact, family/perimeter self-interruption, hospitalization register break). B30 "Aunt K" (Tier 2, +87w/+5.2%: evidence books expansion with juxtaposition principle, self-interruption on legal standing). All PASS QA. Handoff: `Enriched/handoffs/HANDOFF_SESSION_8.md`.

**Session 81:** Baldwin Voice Enrichment — Session 9 of 19, B31–B35 (Part VI The Pattern continued + Part VII The Courts II). B31 "The Reno Bottle" (Tier 1, +443w/+28.6%: Reno loft place detail, cooking register break, formal Sebald form-examination of MPA lab report, researched MPA physiology — immunosuppressant + antiproliferative pregnancy mechanism, Robinson for Kelly's grief, self-interruption on "presence"). B32 "Five O'Clock" (Tier 3, prolepsis fix only). B33 "The Double Default" (Tier 3, zero enrichment — peak quality). B34 "Four Discoveries" (Tier 3, prolepsis fix only). B35 "The Mutual Order" (Tier 1, +234w/~13% prose: Yonkers courthouse place detail, mutual TOP legal context, Weddle register break, Sebald "scattered gunshot" examination with self-interruption, two prolepsis fixes). All PASS QA. Handoff: `Enriched/handoffs/HANDOFF_SESSION_9.md`.

**Session 82:** Baldwin Voice Enrichment — Session 10 of 19, B36–B39 (Part VII The Courts II remainder + Part VII/VIII bridge). B36 "Grandma's Letter" (Tier 3, -3w/-0.3%: prolepsis fix — removed forward reference to silencing, replaced with contemporaneous blog description). B37 "Erase, Deactivate, and Delete" (Tier 3, -60w/-5.7%: two prolepsis fixes — removed appellate forward reference, removed Schauer jail quote from B38's inquest). B38 "The Inquest" (Tier 4, 0%: direct copy, rare beauty, untouched). B39 "Orders as Weapons" (Tier 2, +126w/+12.0%: Baldwin mechanism-naming of how default orders gain authority without process, self-interruption using "or rather" cascade, prolepsis fix removing "Steve would later describe her," multiplication mechanism naming across journalist/detective/attorney deployments). All PASS QA. Handoff: `Enriched/handoffs/HANDOFF_SESSION_10.md`.

**Session 84:** Baldwin Voice Enrichment — Session 12 of 19 (FINAL ENRICHMENT SESSION), B45–B49 + B50/B51 (Part VIII remainder + Part IX + Part X / Afterword). B45 "What the Jury Found" (Tier 4, 0%: direct copy, verdict scene and Steve's interior voice at peak). B46 "Affirmed" (Tier 2, +125w/+10.2%: negation-reversal self-interruption on appellate waiver principle, Sebald examination of consent argument precedent gap — "there is no body of case law recognizing implied consent to being covertly poisoned by an intimate partner," register break on appellate naming convention). B47 "The Record Is Open" (Tier 2 — reassessed from Tier 4, +68w/+3.9%: Sebald on record alteration mechanism — invisible bureaucratic correction, parenthetical-revision self-interruption on "true" in database rewriting context). B48 "The Demand" (Tier 4 — promoted from Tier 3, 0%: framing and landing already at peak, text messages carry their own weight). B49 "For Evie" (Tier 4, 0%: strongest opening in book, interior moments are the chapter, dusk/Evelyn motif already present — "The afternoon light comes through the front windows at an angle that changes with the season"). B50/B51 (Tier 4, 0%: untouched). All PASS QA, 0 CRITICAL/MAJOR/MINOR. Two new self-interruption formats: negation-reversal, parenthetical revision. **ALL 12 ENRICHMENT SESSIONS COMPLETE.** Next: Session 13 (first of five QA passes). Handoff: `Enriched/handoffs/HANDOFF_SESSION_12.md`.

**Session 83:** Baldwin Voice Enrichment — Session 11 of 19, B40–B44 (Part VIII The Trial, first half). Part VIII marks Baldwin dominant, prophetic register. Sebald form-examination formally redeployed in B43 after resting Sessions 9-10. B40 "We Were Hit" (Tier 2, +249w/+16.6%: Sebald blog-as-artifact examination of ABrieGrowsInBrooklyn — lifestyle blog that accidentally produced testimony more specific than formal discovery, Baldwin mechanism-naming with "except that" self-interruption naming circles of removal pattern applied to Brienne, "stained glass" register break). B43 "The Appellate Reversal" (Tier 1, +318w/+21.9%: Sebald form-examination of "the default did not occur" — examining what the sentence does not say vs. what it says, verb self-correction "had not erred, exactly — to err implies a miscalculation," legal context for default mechanism and prior restraint standard, Baldwin mechanism for Family Court's non-response to reversal, prolepsis fix "a jury would later find" → "a California jury had found," "design and use are not the same thing" register break). B44 "What Twelve People Saw" (Tier 2, +105w/+5.8%: Baldwin neutrality mechanism for jury, Tedla testimony detail from evidence_index — "To calm him down," two prolepsis fixes removing forward appellate references, self-interruption on "labored" — "though labored implies effort, and what the jury heard was not effort but collapse"). All PASS QA, 0 CRITICAL/MAJOR/MINOR. Three new self-interruption formats: "except that" redirect, verb self-correction, adjective self-correction. Handoff: `Enriched/handoffs/HANDOFF_SESSION_11.md`.

**Session 85:** Baldwin Voice Enrichment — Session 13 of 19 (QA Pass 1: Factual + Prolepsis Sweep). Independent QA session (separate from enrichment sessions). Automated diff + prolepsis regex scan across all 47 enriched chapters, followed by manual factual review of every addition in all 8 Tier 1 chapters and all high-delta Tier 2 chapters. **Results: 0 CRITICAL, 0 MAJOR, 7 MINOR (human review items).** Enrichment is factually clean — no fabricated events, no altered testimony, no wrong attributions. Prolepsis sweep: 0 new violations introduced; 8 source prolepsis correctly FIXED by enrichment (B05, B06, B32, B34, B36, B37, B43, B44); ~52 source-inherited instances preserved (author editorial decisions). Fixed 2 missing enriched files (B18, B21 — 0% enrichment chapters not previously copied to Enriched/). 7 MINOR flags are all verification requests for human review (B08 Rashmi testimony, B10 Crutcher credentials, B12 Gracie motif evidence, B14 Walsh Sr. doorway scene, B29 Walsh Sr. letter details, B35 Genovese forward claim). Retroactive blog archive review flagged B04, B09, B12 for Session 18 (enriched pre-Step-3D). Full report: `Enriched/qa_reports/QA_SESSION_13_FACTUAL.md`. **Manuscript cleared for QA Pass 2 (Voice Diagnostic).**

**Session 86:** Baldwin Voice Enrichment — Session 14 of 19 (QA Pass 2: Voice Diagnostic). Independent QA session. All 49 enriched chapters analyzed with 7 voice diagnostic checks: monotone, Baldwin accumulation, Sebald landing, interior moment integrity, register diversity, preservation ratio, VOICE_STANDARD. Tier 1 chapters read directly (8); Tier 2 chapters analyzed via parallel agents (23); Tier 3/4 quick-passed (18). **Results: 0 CRITICAL, 8 MAJOR, 14 MINOR.** Primary finding: narrator editorializing pattern in 6–8 Parts II–III Tier 2 chapters (B11, B14, B15, B16, B19, B22) where enrichment added sentences stepping outside the contemporaneous scene to explain mechanisms. Secondary: 3 Tier 1 chapters (B06, B12, B25) have preservation ratios slightly above 85%. Key strength: all 8 Tier 1 chapters pass (4 clean, 4 with MINOR only). Interior moments intact across all tiers. Three-voice system tracks the arc correctly. Sebald landings strong throughout. 8 MAJOR flags concentrated in a specific failure mode (narrator editorializing) correctable with targeted sentence-level revision in Session 18. Full report: `Enriched/qa_reports/QA_SESSION_14_VOICE.md`. **Manuscript cleared for QA Pass 3 (Machine-Signature Scan).**

**Session 87:** Baldwin Voice Enrichment — Session 15 of 19 (QA Pass 3: Machine-Signature Scan). Independent QA session. All 49 enriched chapters scanned for 6 machine-signature checks: forbidden phrases, construction repetition, metaphor domain collisions, self-interruption presence, register break presence, literary allusions. Combined programmatic scanning (forbidden phrase regex across all 49 files, construction counting, allusion detection) with direct reading (all 8 Tier 1 + 7 Tier 2 chapters read in full, 4 more Tier 2 carried forward from Session 14 verification). **Results: 0 CRITICAL, 0 MAJOR, 11 MINOR.** 10 MINOR for "the kind of X that Y" construction appearing 3-5× in individual chapters (B02, B04, B06, B08, B11, B12, B15, B18, B20, B31) — all verified as source-author construction present equally in Tier 3/4 zero-enrichment chapters, NOT machine signatures. 1 MINOR for architecture metaphor domain breadth (12 chapters) — verified as literal/analytical vocabulary, not decorative metaphor. All "weight of" instances concrete (paper, institutional authority, criminal, urgency), not the forbidden emotional pattern. All chapters confirmed to have self-interruptions and register breaks. Programmatic scan produced one false negative (B27 self-interruption — subtler patterns not caught by em-dash regex, verified present by direct read). **Manuscript clean of machine-signature contamination. No revisions needed from Pass 3.** Full report: `Enriched/qa_reports/QA_SESSION_15_MACHINE.md`. **Manuscript cleared for QA Pass 4 (Arc Check).**

**Session 88:** Baldwin Voice Enrichment — Session 16 of 19 (QA Pass 4: Arc Check). Independent QA session. All 49 enriched chapters read directly (no agents) for 4 cross-manuscript checks: motif continuity, information redundancy, prolepsis spot-check, tier match. **Results: 0 CRITICAL, 4 MAJOR, 6 MINOR, 3 INFO.** 4 MAJOR flags all confirmed narrator editorializing (verifying Session 14's unverified agent-sourced flags): B07 ×1 ("The form does not name...what it does not name, no one is asked to answer" — argues rather than witnesses), B09 ×1 ("A police report can hold an incident...It cannot hold a scheme" — steps outside scene to editorialize), B19 ×2 (L112 "A police report cannot hold a scheme" + L145-149 "The incident, on its own, could be explained away...None of this was visible"). Session 14 MAJOR flags fully resolved: B07 CONFIRMED, B09 CONFIRMED, B11 DISMISSED (false positive — Baldwin mechanism-naming, not editorializing), B40 DISMISSED (false positive — Sebald blog-as-artifact examination, not editorializing), B47 DISMISSED (false positive — Sebald record alteration examination, not editorializing). 3 of 8 agent-sourced flags were false positives, confirming the no-agents rule. Motif continuity: all 9 motifs tracked across full manuscript — shah-pah-ka clean (B00→B28), gate/driveway pervasive (21 chapters), documentation-as-love embodied (B05→B27→B30), fog concentrated SF chapters (correct), performance-of-family planted/echoed/referenced (B04→B24→B27), circles-of-removal active B25–B40 with B50 deliberate summary, architecture/building literal across 12 chapters (not decorative — confirmed Session 15), Evelyn/dusk echo map intact (B12→B00/B28/B47/B49). Information redundancy: 2 MINOR (EMAIL_9330 appears in both B19 and B20 captions; "scheme was circular" phrasing shared B20/B22). Prolepsis: all Session 13 fixes verified holding (B05, B06). Tier match: B35 delta 8.8% below 10% threshold noted as MINOR (carried forward from Session 13 — justified by thin evidence for this chapter). Arc-level modulation structurally sound across all 10 Parts. Full report: `Enriched/qa_reports/QA_SESSION_16_ARC.md`. **Manuscript cleared for QA Pass 5 (Read-Aloud Test).**

**Session 89:** Baldwin Voice Enrichment — Session 17 of 19 (QA Pass 5: Read-Aloud Test + MAJOR fixes). Final QA pass before revisions. **Phase 1:** Fixed all 4 confirmed MAJOR narrator-editorializing passages: B07 (cut DV-120 form editorial clause — "Filed under penalty of perjury, in the language of someone explaining a household routine" now the landing), B09 (cut psychiatric intake form editorial — "He was poisoned." as three-sentence close), B19 ×2 (cut "A police report cannot hold a scheme" + explanatory paragraph; cut "A police report could hold a pill in a wine glass" + framing sentence). All fixes verified in context — passages land through witnessing. **Phase 2:** Read-aloud test on 5 arc transition openings (B06, B12, B25, B35, B44) — all register shifts audible and correctly modulated. No stumbles. **Phase 3:** Graft test on 4 highest-delta chapters (B29 +16.0%, B31 +28.6%, B43 +21.9%, B40 +16.6%) — no audible seams, enrichment additions serve the material. B43 "default did not occur" Sebald examination identified as strongest enrichment passage in manuscript. **Phase 4:** Spot-checked 6 MINOR flags from Pass 4: 3 not audible (EMAIL_9330 dual usage justified, "scheme was circular" echo not found in B20, B35 delta justified), 3 audible source prolepsis flagged for Session 18 (B10 L180 "Years later, the depositions would reveal...", B24 L207-209 "But that is B25" + prolepsis paragraph, B26 L219 "is a story that belongs to the next chapter"). **Result: PASS — manuscript ready for Session 18 (Revisions).** Full report: `Enriched/qa_reports/QA_SESSION_17_READALOUD.md`.

**Session 90:** Baldwin Voice Enrichment — Session 18 of 19 (Revisions: Source Prolepsis Fixes). All 3 source-inherited prolepsis/meta-reference passages fixed: B10 L180 ("Years later, the depositions would reveal...") → rewritten as contemporaneous ("Beneath the surface of the family Steve was trying to build, the denials had already taken shape"), also fixed L201 "testified under oath" → "had known all along" (evidence embeds carry provenance); B24 L207-209 (Farquharson prolepsis paragraph + "But that is B25" meta-reference) → cut entirely, section ends on "casual efficiency of a courthouse" landing; B26 L219 ("is a story that belongs to the next chapter" blog voice) → cut entirely, creating devastating juxtaposition: "The bruises had not been there the day before. / The Walsh family allowed no further visits until September." All 3 re-read in context and verified — no new problems. Additional observation: B24 closing (L229-234 post-edit) contains additional prolepsis ("The custody situation would not sort itself out. It would deepen and harden...") not flagged in read-aloud test — noted for author awareness, not revised. Full report: `Enriched/qa_reports/QA_SESSION_18_REVISIONS.md`. **ALL REVISION WORK COMPLETE.** Next: Session 19 (Final Book Compilation).

**Session 91:** Baldwin Voice Enrichment — Session 19 of 19 (Final Book Compilation). Pre-compilation verification: all 49 enriched files confirmed present, all 7 Session 17-18 edits spot-checked and verified (revisions present, surrounding text intact), build passes clean. Backed up `posts/md/` (`posts/md_pre_enrichment_backup_20260325.tar.gz`). Copied all 49 enriched files to `posts/md/` — 0 frontmatter mismatches. Regenerated `_site/full_site.md` (8,261 lines, 97,966 words) — previous version was stale (March 22). Generated book: `ChappaquaPoison_BOOK_2026-03-25.docx` → PDF (437 pages, 2.3 MB). Whitespace-normalized PDF verification: all 4 MAJOR fix passages present, all 3 prolepsis fix passages present, all removed content absent. Enriched content verified in both HTML and PDF (B31 MPA physiology, B43 appellate examination, B29 Walsh Sr. letter). Appendices present (Cast of Characters, Timeline). Full report: `Enriched/qa_reports/COMPILATION_SESSION_19.md`. **BALDWIN VOICE ENRICHMENT PROJECT COMPLETE.**

**Session 95:** Reader Feedback Process — Character Research Deep Dive. First reader feedback (Laureanna B.) diagnosed three fixable problems: (1) redundancy (same descriptions reused across posts, e.g., Vermont Street, Millennium Tower), (2) AI vocabulary tells ("architecture" used 52× — mostly earned but some decorative; "framework" 3×), (3) weak character introductions (institutional characters introduced by role not as people). AI vocabulary audit found 14 of 19 classic AI-tell words completely absent (0 hits); remaining hits mostly natural usage. Character problem diagnosed as research failure: CHARACTERS.md tracks narrative function but contains zero physical descriptions, zero professional backstory, zero Westchester power-structure context. Created `Indexes/CHARACTER_RESEARCH.md` with deep web research on 10+ characters: **Schauer** (jailed disabled father Marc Fishman — 45 days, arrested during supervised visitation, ADA violations, FERPA rights stripped; career entirely inside court system since 1984), **Horowitz** (censured 2005 for fixing cases — "everybody does it"; re-nominated by 4 political parties; cocaine allegations; DiFiore connection; court staff nickname "NMH"), **Humphreys** (bow tie; 22 years Westchester County Attorney's Office — same pipeline as Guttridge), **Farquharson** (Columbia MSW, trauma specialist, foster care director, Mount Vernon councilwoman, mayoral candidate — AND $250/hr captured supervisor with "special relationship with the judge"; "rude and nasty" to Supreme Court judge), **Guttridge** (County Attorney pipeline, fired LaMelle, Frank Report allegations of judge intimidation), **Jackman** (5 years child welfare prosecutor, DelBello Donnellan firm; wrote bruise report pathologizing documentation), **Faedda** (wrote "Parenting a Bipolar Child," clinic named after ECT inventor, medicated Tara from age 12), **Faith Miller** (law assistant to Administrative Judge Gagliardi, County Attorney's Office, firm employs Jackman — the ultimate pipeline position). Also documented: Wagon-Circling Dynamic (how self-protection accelerated exposure), Chappaqua Architecture (Clinton/Crabtree's convergence — same building hosted Hillary's 2016 nomination speech and Steve's supervised visits), racial dynamics (LaMelle's observation of the club, whisper campaign), County Attorney pipeline, patronage protection system. **Remaining from feedback remediation:** redundancy audit across posts, AI vocabulary spot-clean, READER_FEEDBACK_PLAN.md, Steve's interview (deferred — strategic).

**COMPLETED PROJECT: BALDWIN VOICE ENRICHMENT — Full Book Rewrite (revised skill v2).** 19-session selective enrichment pass using the two-layer model: content layer (evidence_index, physiology, place, blog archive) + voice layer (Baldwin/Sebald/Robinson). Enriched output at `Enriched/`. Tier classification: `Enriched/TIER_ASSIGNMENTS.md` (8 Tier 1, 20 Tier 2, 15 Tier 3, 6 Tier 4). **ALL 19 SESSIONS COMPLETE.** 12 enrichment sessions + 5 QA passes + revisions + final compilation. 4 MAJOR narrator-editorializing passages fixed. 3 source prolepsis passages fixed. All 49 original chapters deployed to `posts/md/`. B41 and B42 voice-enriched Session 105 (Tier 2). Build and book generation verified clean.

**Canonical index:** 2,191 entries. 4 tiers (Hero: 202, Primary: 518, Secondary: 1,440, Tertiary: 21). `source_exhibit` field (421 non-null linkages). Build passes clean (0 errors, 0 warnings). **Current book:** ChappaquaPoison_BOOK_2026-03-28.docx (51 chapters, 130 evidence embeds, 109,506 words, 11.3 MB).

### Issues Found in Session 44 Audit

**1. ~~Posts needing editorial expansion (SHORT — under 800 words):~~ RESOLVED Sessions 48-49.**

**2. Posts needing editorial attention (THIN — remaining):**
- ~~B05, B07, B09, B10, B16~~ — RESOLVED Sessions 48-49.
- ~~B35 "The Mutual Order"~~ — RESOLVED Session 50. Expanded from ~1,941w to ~2,766w with new June 1 hearing scene (ExTR_10_03 promoted to hero).

**3. ~~Frontmatter format inconsistencies:~~ RESOLVED Session 46.**

**4. ~~posts.json ↔ frontmatter sync mismatches:~~ RESOLVED Session 46.**

**5. ~~Inline embeds misclassified as primary (not hero):~~ RESOLVED Session 49.**

**6. ~~Orphan markdown files:~~ RESOLVED Session 46 (renamed with _orphan_ prefix).**

### Session History (Compressed — Sessions 11-51)

| Sessions | Focus | Key Accomplishments |
|----------|-------|-------------------|
| 11-12 | Evidence index overhaul | 139 stubs replaced, 4 Evie Story Books read page by page, 400 Master Photos copied, SLE archive (146 files) fully indexed, canonical index: 2,037 entries |
| 13-15 | Message archive reading | 11 of 31 conversation PDFs read cover to cover (~660 pages), Seven-Register System confirmed, Inherited Scheme discovered (Kiara/Seroquel), Pontius Pilate Pattern documented, 42 new MSG- entries |
| 16-17 | Legal archive evidence hunt | 312 pages across 4 case documents, 39 new entries (22 Hero), DVRO hearing (Seroquel admission), Inquest transcript (full Tara testimony), Battery verdict forms |
| 18 | Index structural completion | 89 category fixes, 70 stubs eliminated, 106 page-level artifacts extracted, 26 duplicates archived |
| 19-22 | Editorial passes + arc work | Jesse/Matan/Walsh arcs completed, B02 editorial pass, evidence hunt processes codified |
| 23-32 | Full editorial rewrites | 15 posts rewritten from primary sources (see NEXT_SESSION_PROMPT.md for details), 100+ evidence embeds added |
| 33-43 | Evidence footer curation | ~27 of 48 posts curated with file inspection |
| 44 | Comprehensive audit | SHORT/THIN posts identified, 6 priority categories created |
| 45-47 | Pass 2 | Blog-wide editorial tightening (~2,800 words cut), "witnessing not arguing" enforced |
| 48-49 | Hero/inline alignment | All 48 posts audited, 0 mismatches remaining, 6 posts expanded |
| 50 | B35 expansion + housekeeping | B35: 830→2,772 words, frontmatter format sweep, MSG-BRIENNE warnings resolved |
| 51 | Book pipeline fixes | All 16 Draft 50 issues fixed, Draft 51 generated (405 pages, 101,600 words) |
| 52-53 | Draft 52 read + recs | Cover-to-cover read, editorial recommendations, institutional middle tightened |
| 54 | Federal updates + plan | Author's Note added, Afterword filed tense, Crutcher fix, Draft 53 (409pp), editorial plan created |
| 55 | Editorial prose plan (A-F) | All 6 sessions executed: Kelly arc, Tara duality, inner-thought, Evie anchoring, voice pass, final gen. 20+ posts edited. Draft 54 (87,742w, 399pp) + PDF + EPUB |
| 56 | Publication prep | Build warning fixed (B-7_020), back cover sharpened, 5 most-edited posts spot-read (clean). Draft 55 (87,707w, 399pp) + PDF + EPUB |
| 57 | Cover-to-cover read + title fix | Full cover-to-cover read of Draft 55 — no issues. B43 title unified ("The Appellate Reversal" everywhere). Draft 56 (87,707w, 410pp) + PDF + EPUB. Build: 0/0 |
| 58 | Evidence presentation overhaul | B17: 7 text embeds → typed CSS bubbles. msg-secondary class for L/R differentiation. 3 new Ghost-style image formats (photo-card, document-card, photo-gallery). 3 image embeds converted (B18, B21). 47 image + 16 message embeds remaining |
| 58b | CSS fixes + test pages | 7 multi-up CSS fixes (media query ordering, font-size resets, continuation ellipsis, caption width, border-radius). test-multiup.html + test-images.html created. EMBED_STANDARDS v1.3 |
| 59 | Hero image deep review | Every hero visually inspected (150+ items). Only 16/49 posts have photo heroes. 10 posts identified for photo hero promotion. 11 missing PHOTO_ files, 7 category mismatches. Hero_Image_Review_Session59.md |
| 60 | Source exhibit linkage planning | Provenance gap identified + architectured. `source_exhibit` field designed. 150 heroes classified (8 types). SOURCE_EXHIBIT_SPEC v1.1. Pipeline changes planned. Pre-revision backup committed. 7-phase implementation plan |
| 61 | Source exhibit Phase 1 | `source_exhibit` field added to all 2,181 entries. `scripts/link_source_exhibits.py` written. 408 auto-linked, 1,305 confirmed self-sourcing, 20 hero needs_manual (file_missing → Phase 6). Unsuffixed MSG entries confirmed as full conversations. Build: 0/0 |
| 62 | Source exhibit Phases 2-4 | **Phase 2:** Court facsimile + email facsimile CSS. EMBED_STANDARDS v1.4 + Provenance Pairing Rules. **Phase 3:** 3 EB_ hero spread images created/indexed/linked. **Phase 4:** `build_html.py` footer auto-injection (14 posts). `blog_to_book.py` endnote enrichment + ibid. dedup. Both builds: 0/0. Draft 57: 88,614w. Index: 2,191 entries, 411 source_exhibit |
| 63 | Phase 5 — Post-by-Post Conversion | ALL old-format embeds converted across all 50 posts (~100+ conversions). 9 old formats → 6 new CSS formats. Build: 0/0 |
| 64 | Phase 6 — Evidence Hunt | All 13 `file_missing` hero items resolved: 10 linked, 3 self-sourcing. 2 files copied to Evidence. 1 duplicate removed. Index: 2,190 entries, 421 source_exhibit. Build: 0/0 |
| 65 | Phase 7 — Verification | `audit_phase7.py` (6 checks), 30 errors found+fixed, Draft 58 (89,413w, 404pp). Source exhibit auto-injection verified across 7 posts |
| 66 | Visual QA + iMessage sweep | B25 image overflow fixed, 3 PDF-as-img bugs fixed, 11 message embeds converted across 7 posts. Full QA: 0 issues. Build: 0/0 |
| 67-68 | Book pipeline overhaul | `generate_book.js` rewrite: 5 evidence treatments, jury/reader rule, timeline scrub, cover-to-cover PDF readthrough. Book: 429pp, 95,524w. Build: 0/0 |
| 69 | Baldwin voice enrichment setup | Converged two independent AI assessments into production skill. 5 substantive divergences resolved. 19-session rewrite plan. Enriched/ directory created. Skill installed |
| 70-72 | Baldwin Sessions 1-3 (old skill) | Original skill produced avg 2.7% enrichment (vs 30% design). Tier classification created. B00–B10 enriched. Editor identified three deficiencies: evidence_index never queried, physiology never researched, place detail absent. **All output superseded by revised skill** |
| 73 | Baldwin Session 1 (revised) | B00 (+0.3%, "heavy iron" gate only — Prologue = pure scene) + B28 upgraded Tier 1 (+15.0%, 9 additions incl. ambush photo detail, compound geography, wind motif return). Skill revised with mandatory content layer. B06 proof-of-concept: +23.9% |
| 74 | Baldwin Session 2 | B01–B05: B01 (+4.0%, documentation motif planted), B02 (0%), B03 (0%), B04 (+4.4%, enclosure motif), B05 (+3.4%, prolepsis fixed, intrusion mechanism named). Total +152w |
| 75 | Baldwin Session 3 | B06–B10: B06 (+11.3%, cognitive delay physiology, Nantucket register break, surveillance-illness convergence), B07 (+5.1%→16.6% after re-enrichment), B08 (+2.6%→7.6%), B09 (+4.3%), B10 (+5.0%→7.3%). Evie naming motif captured. Total +492w |
| 76 | Baldwin Session 4 | B07/B08/B10 re-enrichment (timidity fix) + B11–B14: B11 (+8.5%, Brooklyn cold, preeclampsia cuff), B12 (+12.4%, **Evie naming motif planted** — Robinson aibhilín + Baldwin Gracie), B14 (+6.4%, Walsh Sr. coat, Pontius Pilate scene). Seroquel pharmacology researched |
| 77 | Baldwin Session 5 | B15–B17 (Part II complete): B15 (+1.9%, Baldwin mechanism-naming, author Sheraton detail), B16 (+7.1%, Vermont Street grounding from author, three-movements-of-a-negotiation, self-interrupting two-register), B17 (0%, peak quality). **New: `PLACE_DETAIL_AUTHOR.md`** — author primary-source place descriptions for 6 locations |
| 78 | Baldwin Session 6 | B18–B21 (Part III complete): B18 (0%, Tier 3, source at peak — kitchen scene, knife sharpener already vivid), B19 (+4.6%, ball-rolling-toward-sinking-corner from author, Salesforce LED register break, Lieutenant self-interruption), B20 (+7.2%, niacin TRPV1 physiology "body's own response to what it mistook for burning," room porousness, supplement-vs-weapon Baldwin), B21 (0%, Tier 3, source at peak — "She had needed only to be loved" already Baldwin). New metaphor domains: architecture/sinking (B19), body/heat (B20). All 5 construction patterns now available for Session 7. Fog motif echoed in B19 (different register from B06). Total +150w |
| 79 | Baldwin Session 7 + Blog Archive Integration | **Session 7:** B22–B25 (Part IV + Part V first half): B22 (+4.1%), B23 MODEL POST (0% — do not touch), B24 (+4.6%), B25 (+10.7%, tripartite Sebald examination, Tier 1). **Blog Archive Discovery:** Found and indexed the StevieLovesEvie blog archive (`Evidence/html/media/Perfectly_Formatted_Blogs_source.txt` — 48,350 lines, 215 unique posts, ~142,000 words). Created `Enriched/references/BLOG_DETAIL_INDEX.md` mapping blog posts to chapters with line numbers, extracting nanny quotes (Nicole, Ashley, Franceska), Evie behavior details, Walsh handoff choreography. Created Step 3D skill patch (`Enriched/references/SKILL_PATCH_3D.md`). Updated `baldwin-voice` skill with Step 3D (blog archive mining) and blog archive QA check in Step 7. Skill repackaged and reinstalled. **Editorial notes:** First line of book: `*People always tell you what they fear.*` (italics, Steve's interior voice, B00). Last line: `People always tell you what they fear.` (plain text, narrator voice, B49). Updated NEXT_SESSION_PROMPT.md with blog archive integration for Sessions 8-19. |
| 80 | Baldwin Session 8 | B26–B30 (Part V second half + Part VI opening): B26 (+1.4%, Tier 2 light — blog-sourced gate quip, delay-as-weapon self-interruption, Visit 6 drop-off thread), B27 (+3.0%, Sebald Jackman double-negative, Guttridge "instability" self-interruption), B28 verified (MODEL POST, do not touch), B29 (+16.0%, **Tier 1** — Walsh Sr. letter to Gordon-Oliver from EB3_MASTER_055 brought into prose as Sebald examination, family/perimeter self-interruption, hospitalization register break), B30 (+5.2%, evidence books expansion with four titles + juxtaposition principle, legal standing self-interruption). Blog archive mined for B26 (13 posts) and B27 (2 posts). Evidence_index deep mining for B29 (19 entries, EB3_MASTER_055 and ExU_01 opened). Pattern note: "in the letter's usage" self-interruption construction used twice (B27, B29) — vary in Session 9. Total +447w. All 5 PASS QA. |
| 81-83 | Baldwin Sessions 9-11 | See Session entries above. B31–B44 enriched. Sebald form-examination deployed B43. Three new self-interruption formats. Multiple prolepsis fixes across B32, B34, B35, B36, B37, B39, B43, B44 |
| 84 | Baldwin Session 12 (FINAL) | B45–B49 + B50/B51. B46 (+10.2%), B47 (+3.9%), all others Tier 4 untouched. Tier reassessments: B47 (4→2), B48 (3→4). Two new self-interruption formats (negation-reversal, parenthetical revision). **ALL ENRICHMENT COMPLETE** |
| 85-88 | Baldwin QA Sessions 13-16 | Pass 1 Factual (0 CRITICAL), Pass 2 Voice (8 MAJOR — agent-sourced), Pass 3 Machine-Signature (0 MAJOR, 11 MINOR source-inherited), Pass 4 Arc Check (4 MAJOR confirmed from Session 14 verification: B07×1, B09×1, B19×2 — all narrator editorializing). 3 of 8 agent flags dismissed as false positives. All 9 motifs tracked. Arc modulation sound. **4 MAJOR passages queued for Session 18 revision** |
| 95 | Reader Feedback Deep Dive | First reader feedback (Laureanna B.). AI vocabulary audit. CHARACTER_RESEARCH.md created (10+ characters). Wagon-circling dynamic, Chappaqua architecture, racial dynamics, County Attorney pipeline documented |
| 101-103 | Character Pass + New Chapters | All 13 yarns executed. B41 (The Depositions, 3,360w) + B42 (The Kidnapping Case, ~2,847w) written. 3 forward-evidence embeds placed |
| 104 | Evidence Embeds + Curation | 14 evidence embeds across B41/B42. Full footer curation: B41=32 total (6H/8P/18S), B42=27 total (8H/8P/11S) |
| 105 | Renumbering + Baldwin B41/B42 | Full chapter renumbering: B40b→B41, B40c→B42, cascade through B51. 253 canonical index entries, 60+ files updated. Baldwin enrichment: B41 (+302w/7.5%), B42 (+165w/5.1%). Book regenerated: 109,506 words |

</details>

### Model Posts — Read Before Writing

**B23 "The Uber"** and **B28 "The Ambush"** are the quality standard. Read one before starting any new post. Details in NEXT_SESSION_PROMPT.md.

### Longer-Horizon Work (Not Blocking Review)

- **Message archive:** 20 of 31 conversation PDFs unread (Kiara Walsh highest priority)
- **file_missing:** ~220 entries in canonical index (external storage)
- **Secondary tier:** Many entries still unassigned to posts
- **Court compilations:** ExBCD_01, ExBCD_03, ExC_01, ExSS_07 unread


---

## The Numbering Standard

**51 posts. B00-B51. B13 dissolved. Contiguous numbering (no suffixes, no B100/B101).**

**⚠ NUMBERING CONFLICT (April 6, 2026):** A session attempted to renumber B47a/B47b into B48/B49 and bump subsequent chapters to B50–B53, creating commits in the git repo. However, posts.json still shows the canonical B00–B51 scheme. **The next session must reconcile.** The posts.json scheme (B00–B51) is authoritative; any B52/B53 references in git are from the aborted renumber and should be corrected.

| Range | Role |
|-------|------|
| B00 | Prologue — "Someone at the Gate" |
| B01-B12 | Acts I-II |
| B13 | **DISSOLVED** — content redistributed; excluded from HTML build |
| B14-B40 | Acts III-VII + Trial opening |
| B41 | Less Than Genuine (new Session 103 as "The Depositions", renumbered from B40b Session 105, retitled to "Less Than Genuine") |
| B42 | The Kidnapping Case (new Session 103, renumbered from B40c Session 105) |
| B43-B47 | Acts VIII-IX (renumbered from B41-B47 Session 105) |
| B48 | The Demand (Act IX — "The Record") |
| B49 | For Evie (Act X) |
| B50 | Afterword — "Where Are They Now" (renumbered from B100 Session 105) |
| B51 | Back Cover (renumbered from B101 Session 105) |

**posts.json** is the source of truth for post IDs, titles, slugs, acts, and metadata (including static_pages array).

**Act structure (from posts.json — 10 acts, consolidated to 5 in book PDF):**

| Act (posts.json) | Chapters | Name | Book Act |
|-----|----------|------|----------|
| Preface | B00 | Prologue | Preface |
| I | B01-B10 | The Fool | Act 1: The Fool |
| II | B11-B17 | The Evidence | Act 1: The Fool |
| III | B18-B22 | The Household | Act 2: The Household |
| IV | B23 | The Kidnapping | Act 2: The Household |
| V | B24-B29 | The Courts | Act 3: The Courts |
| VI | B30-B31 | The Pattern | Act 3: The Courts |
| VII | B32-B39 | The Courts II | Act 3: The Courts |
| VIII | B40-B46 | The Trial | Act 4: The Courts (cont.) |
| — | B41 | Less Than Genuine | Act 4 (inserted between B40 and old B41→B43) |
| — | B42 | The Kidnapping Case | Act 4 (inserted between B41 and old B41→B43) |
| IX | B47-B48 | The Record | Act 5: The Record |
| X | B49 | For Evie | Act 5: The Record |

---

## Directory Structure

### Root — Build Data & Entry Points

```
ChappaquaPoison_v3/
├── ORIENTATION.md              ← YOU ARE HERE — read this first
├── NEXT_SESSION_PROMPT.md      ← Paste into next session for clean instance startup
├── README.md                   ← Quick reference map
├── INSIGHTS.md                 ← Pattern recognition, editorial instincts — READ EARLY
├── posts.json                  ← Source of truth for all posts AND static_pages array
├── evidence_index_canonical.json ← **CANONICAL** evidence index (2,191 entries, 4 tiers, 15 categories)
├── ChappaquaPoison_v3_FULL.md  ← Mirror of _site/full_site.md
├── ChappaquaPoison_v3_BOOK.docx ← Generated book (DOCX)
├── banner_scenes.json          ← Banner image generation data
├── timeline.json               ← Timeline data (115 entries)
├── tokens.json                 ← CSS design tokens (phase colors, typography, spacing)
├── Makefile                    ← Build commands: make all, make html, make search
├── deploy.sh                   ← Rebuild + optional zip for Cloudflare Pages
├── package.json                ← Node dependencies
├── EVIDENCE_EMBED_STANDARDS.md ← Canonical HTML patterns for all 9 evidence embed types
```

### posts/ — Source Markdown (54 files)

```
├── posts/
│   └── md/                        ← 54 markdown source files (B00-B51 contiguous + variants)
│       ├── B00_someone-at-the-gate.md
│       ├── B01_the-fool.md
│       ├── ...
│       ├── B41_less-than-genuine.md     ← NEW Session 103 (as "The Depositions"), renumbered Session 105, retitled Session 169
│       ├── B42_the-kidnapping-case.md   ← NEW Session 103, renumbered Session 105
│       ├── ...
│       ├── B49_for-evie.md
│       ├── B50_where-are-they-now.md
│       └── B51_back-cover.md
```

Each post has YAML frontmatter (title, subtitle, date, act, phase, tags, evidence, ecs) + markdown body with optional HTML evidence embed blocks.

### templates/ — Jinja2 Templates (13 files)

```
├── templates/
│   ├── base.html                  ← Master layout: nav, footer, CSS/JS, meta tags
│   ├── post.html                  ← Post template (ALL 9 Hero CSS formats live here ~lines 1474-1780)
│   ├── index.html                 ← Homepage: post feed, phase nav, tag cloud
│   ├── tag.html                   ← Tag archive pages
│   ├── about.html                 ← About This Archive (255 lines)
│   ├── methodology.html           ← Methodology & Sources (374 lines)
│   ├── how-to-read.html           ← Reader orientation (303 lines)
│   ├── falsifiability.html        ← If This Archive Is Wrong (239 lines)
│   ├── evidence.html              ← Evidence Index (auto-generated from canonical JSON)
│   ├── timeline.html              ← Master Timeline (auto-generated from timeline.json)
│   ├── public-record-notice.html  ← Standing disclaimer (117 lines)
│   ├── search.html                ← Search interface
│   └── 404.html                   ← Error page
```

**IMPORTANT:** 6 pages registered in posts.json have NO dedicated template and render as bare stubs. See "Static Pages Architecture" below.

### Audits/ — Quality Control & Evidence Planning

```
├── Audits/
│   ├── Evidence_Style_Guide_v1.docx      ← Formal 8-section style guide for 4-tier evidence system
│   ├── master_evidence_plan.json         ← Per-post Hero/Primary evidence selection (49 posts)
│   ├── EVIDENCE_REVIEW_SESSION1-3.md     ← Deep editorial evidence analysis (3 sessions)
│   ├── EVIDENCE_INDEX_RECONCILIATION.md  ← Index vs. filesystem reconciliation
│   ├── EVIDENCE_PIPELINE_AUDIT.md        ← Pipeline integrity checks
│   ├── EMBED_AUDIT_REPORT.md             ← Current embed status per post
│   ├── hallucination_scan_2026-03-16.json ← Automated factual claim verification
│   ├── site_integrity_report.json        ← Link/image/evidence validation
│   └── (batch analysis files, QA reports, etc.)
```

### Indexes/ — The Editorial Brain

```
├── Indexes/
│   ├── CORE_NARRATIVES.md          ← 12 narrative rules
│   ├── POSTS_GUIDE.md              ← Master post-by-post reference
│   ├── CHARACTERS.md               ← 30+ characters with arcs
│   ├── PLACES.md                   ← 20 locations
│   ├── EVIDENCE_INDEX.md           ← Evidence index (markdown companion to canonical JSON)
│   ├── NARRATIVES_AND_THEMES.md    ← Narrative arcs indexed across posts
│   ├── TAGS.md                     ← Canonical tag taxonomy
│   ├── V3_THEMATIC_MEMORY.md       ← 11 interpretive lenses
│   ├── V3_BANNER_MAP.md            ← Banner image assignments
│   ├── v3_Master_Timeline.md       ← 750+ dated events
│   └── EVIDENCE_TRIAGE.md          ← Evidence audit per post
```

### Standards/ — Writing & Quality Rules

```
├── Standards/
│   ├── EVIDENCE_TAGGING_GUIDE.md   ← Consolidated evidence classification
│   ├── CAPTION_VOICE_GUIDE.md      ← 10 archive voice registers
│   ├── VOICE_STANDARD.md           ← Contemporaneous Scene Rule, Cold Accumulation
│   ├── THEMATIC_STANDARD.md        ← Three principles, Ozymandias frame
│   ├── WRITER_BRIEF.md             ← Compact orientation for writer/editor sessions
│   ├── REVISION_STANDARDS.md       ← 10 structural rules
│   ├── EXPANSION_PROTOCOL.md       ← Guidelines for expanding posts
│   ├── ENDNOTE_STANDARD.md         ← Endnote formatting rules
│   └── EVIDENCE_BOOK_STANDARD.md   ← Book-specific evidence formatting
```

### scripts/ — Build & Utility Scripts (37 files)

```
├── scripts/
│   ├── build_html.py              ← PRIMARY BUILD SCRIPT (Jinja2 + posts.json + MD → _site/)
│   ├── build_search_index.py      ← Search index generator
│   ├── generate_full_site_md.py   ← Concatenate all posts into single MD
│   ├── generate_book.js           ← MD → DOCX (Node/docx-js)
│   ├── validate_site.py           ← Site integrity checker (links, images, evidence)
│   ├── generate_sitemap.py        ← XML sitemap
│   ├── generate_feed.py           ← RSS/Atom feed
│   ├── generate_thumbnails.py     ← Evidence thumbnail generator
│   ├── build_canonical_evidence_index.py ← Rebuild canonical JSON from filesystem
│   ├── insert_hero_embeds.py      ← Insert Hero HTML blocks into post MD files
│   └── (30+ other utility scripts)
```

### Evidence/ — Source Evidence Files (~1,263 files)

```
├── Evidence/
│   ├── interviews/                ← Author interview .md files (INT-001 through INT-003)
│   ├── media/
│   │   ├── audio/                 ← 10 audio files (voicemails, Uber recordings, 911 call)
│   │   ├── video/                 ← 9 evidence videos (gas from light fixture, etc.)
│   │   └── clips/                 ← 42 deposition clips across 4 deponents:
│   │       ├── stephen/           ← Stephen Walsh Sr. deposition clips
│   │       ├── gavish/            ← Matan Gavish deposition clips (22 clips)
│   │       ├── maura/             ← Maura Walsh deposition clips
│   │       └── brendan/           ← Brendan Walsh deposition clips
│   ├── photos/                    ← ~87 evidence photographs
│   ├── pdf/                       ← Court filings, lab reports, declarations
│   ├── html/, docs/, imports/     ← Other evidence formats
│   └── _removed_2026-03-04/       ← 41 archived duplicates
```

### Generated Output

```
├── _site/
│   ├── posts/*.html               ← 46 HTML posts with evidence footers + Hero embeds
│   ├── index.html                 ← Homepage
│   ├── about.html                 ← About (from template)
│   ├── methodology.html           ← Methodology (from template)
│   ├── how-to-read.html           ← Reader orientation (from template)
│   ├── falsifiability.html        ← Falsifiability (from template)
│   ├── evidence.html              ← Evidence Index (auto-generated)
│   ├── timeline.html              ← Timeline (auto-generated from timeline.json)
│   ├── public-record-notice.html  ← Disclaimer (from template)
│   ├── search.html                ← Search (from template)
│   ├── 404.html                   ← Error page (from template)
│   ├── people.html                ← **STUB** — needs template
│   ├── cases.html                 ← **STUB** — needs template
│   ├── patterns.html              ← **STUB** — needs template
│   ├── audit-log.html             ← **STUB** — needs template
│   ├── ten-documents.html         ← **STUB** — needs template
│   ├── public-record-inventory.html ← **STUB** — needs template
│   ├── full_site.md               ← All posts concatenated
│   ├── search_index.json          ← 49 documents indexed
│   ├── tags/*.html                ← Tag archive pages
│   └── Evidence/, css/, js/, images/
```

### GumroadBundle/ — Companion Archive Projects (Active as of Session 92)

```
├── GumroadBundle/
│   ├── BUNDLE_PLAN.md                  ← Gumroad bundle plan (7 items, 6 ready)
│   ├── ARCHIVE_PROJECTS_PLAN.md        ← Master plan for Evie's Story + The Lies ← START HERE
│   ├── EVIE_STORY_DEDUP_AUDIT.md       ← Image deduplication audit (19 duplicate groups)
│   └── LIES_CROSSCUT_WORKING.md        ← Cross-cut sequences by 8 patterns (12 confirmed, strength-ranked)
```

**Current work (Session 92+):** Two companion archive editions in progress:
- **Evie's Story (Definitive Edition):** Kelly Turnure's 4 Evie Story Books — cleaned, deduplicated, enriched with SLE blog writing. Dedup audit and SLE mapping complete; chapter outline and production pending.
- **The Lies (iMessage Edition):** Curated cross-cut of Tara Walsh's iMessage conversations organized by 8 forensic behavioral patterns. Rashmi and Linda threads fully read; Steve, Brienne, Rita/Dr. Rhodes threads pending. 12 cross-cut sequences confirmed.

---

## The Build Pipeline

### Stage 1: Source MD → HTML (Blog)
```
posts/md/*.md + templates/*.html + posts.json → scripts/build_html.py → _site/
```
**Command:** `make all` or `python3 scripts/build_html.py`

This is the primary build. It:
1. Reads posts from `posts/md/*.md` (YAML frontmatter + markdown body)
2. Reads post metadata from `posts.json`
3. Renders posts using `templates/post.html` (Jinja2)
4. Renders static pages via two paths (see below)
5. Generates `evidence.html` from `evidence_index_canonical.json`
6. Generates `timeline.html` from `timeline.json`
7. Generates tag pages using `templates/tag.html`
8. Runs `validate_site.py` for integrity checks
9. Runs `build_search_index.py` for search

### Static Pages Architecture

Static pages in `posts.json` have an `id` (S-1 through S-15) mapped to filenames via `STATIC_PAGES_MAP` in build_html.py. Two rendering paths:

**Path A — Dedicated Templates** (in `DEDICATED_TEMPLATES` set): The build looks for a template file matching the filename (e.g., `about.html` → `templates/about.html`). These templates extend `base.html` and contain full page content as HTML/Jinja2. Currently 10 pages use this path: index, about, methodology, how-to-read, falsifiability, evidence, timeline, public-record-notice, search, 404.

**Path B — Fallback Renderer** (`render_static_page_html()`): Pages without a dedicated template get a bare stub: `<h1>{{ title }}</h1><p>{{ purpose }}</p>`. Currently 6 pages use this path and need dedicated templates: people (S-7), cases (S-8), patterns (S-9), audit-log (S-12), ten-documents (S-13), public-record-inventory (S-14).

**To add a new static page:** Create `templates/{name}.html` extending `base.html`, add the filename to `DEDICATED_TEMPLATES` in build_html.py, and ensure the corresponding entry exists in `posts.json` `static_pages` array.

### Stage 2: Source MD → full_site.md
```
posts/md/*.md → scripts/generate_full_site_md.py → _site/full_site.md
```
**Command:** `python3 scripts/generate_full_site_md.py`

### Stage 3: full_site.md → DOCX
```
_site/full_site.md → scripts/generate_book.js → ChappaquaPoison_v3_BOOK.docx
```
**Command:** `node scripts/generate_book.js` (requires `npm install`)

### Stage 4: Custom PDF generation (reportlab)
```
_site/full_site.md → custom Python script → _site/ChappaquaPoison_v3_BOOK.pdf
```
6x9 trade paperback format. 184 pages. Script was run inline during pipeline rebuild.

### Stage 5: Custom EPUB generation (ebooklib)
```
_site/full_site.md → custom Python script → _site/ChappaquaPoison_v3_BOOK.epub
```
EPUB3 format. Script was run inline during pipeline rebuild.

### Full rebuild command sequence:
```bash
make all
python3 scripts/generate_full_site_md.py
node scripts/generate_book.js
# PDF and EPUB scripts were run inline — need to be saved as permanent scripts
```

**Note:** The PDF and EPUB generation scripts were created and run inline during the March 15 pipeline rebuild session. They should be saved as `scripts/generate_pdf.py` and `scripts/generate_epub.py` for reproducibility.

### Stage 6: Deploy to GitHub Pages

```
_site/ → cleanse → _deploy/ → git push → GitHub Actions → GitHub Pages → chappaquapoison.com
```

**THIS IS CRITICAL — READ BEFORE TOUCHING DEPLOYMENT:**

1. `build_html.py` generates `_site/` — the full local site with all evidence, media, everything.
2. `_site/` gets cleansed into `_deploy/` — stripping files that are too large or would break a git push (full depositions, raw movies, book PDFs, etc.).
3. **`_deploy/` IS the GitHub repo.** Its contents are the repo root. The git repo lives at `_deploy/.git/`. There is no source code in the GitHub repo — only the deployment-ready static site.
4. Push `_deploy/` to `main` on `git@github.com:bon-007/chappaquapoison.git` → triggers GitHub Actions workflow → deploys the repo root to GitHub Pages.
5. CNAME (`chappaquapoison.com`) and `.nojekyll` live inside `_deploy/`.

**Do NOT:**
- Push the source tree (the parent directory) to GitHub. Only `_deploy/` gets pushed.
- Create `_deploy_slim` or any other intermediate directory. `_deploy` IS the clean artifact.
- Use `git add -A` from the parent directory. The git repo is inside `_deploy/`.
- Add full depositions (700MB MP3s), sorted_movies (2.1GB), or Evidence/pdf (853MB) to the repo. These are excluded by `_deploy/.gitignore`.

**Deploy commands:**
```bash
cd _deploy
git add -A
git -c user.name="Steve Russell" -c user.email="steve@chappaquapoison.com" \
  commit -m "Deploy: <description>"
GIT_SSH_COMMAND="ssh -i ../deploy_key_new -o StrictHostKeyChecking=no" \
  git push origin master:main
```

**Deploy key:** `deploy_key_new` in the project root (parent of `_deploy/`).

**What's in _deploy/.gitignore:**
```
Evidence/sorted_movies/    # 2.1GB full movies
Evidence/pdf/              # 853MB raw PDFs
Evidence/_removed_*/       # Stale evidence
Evidence/media/video/      # Full deposition videos (LFS pointers, not real files)
Previous/                  # Old site versions
ChappaquaPoison_BOOK_*.pdf # Book PDFs
*.mov                      # Video files
.DS_Store
```

**What IS deployed (and must stay):** Deposition clips (Evidence/media/clips/, 304MB real MP4s), audio evidence (Evidence/media/audio/, 21MB), evidence photos (Evidence/photos/, 215MB), banner images (images/banners/v3/, 61MB), all HTML/CSS/JS.

**Known issue:** `build_html.py` generates `evidence.html` with lowercase `./evidence/` paths but the directory is `Evidence/` (capital E). GitHub Pages is case-sensitive (Linux). After each rebuild, run: `sed -i 's|./evidence/|./Evidence/|g' _deploy/evidence.html` before pushing. The real fix is in the evidence template.

---

## Evidence System — Current State

### Canonical Evidence Index

| Metric | Count |
|--------|-------|
| Canonical JSON entries | **2,181** |
| Physical evidence files | ~1,263 |
| Hero tier | 184+ |
| Primary tier | 510+ |
| Secondary tier | 1,435+ |
| Tertiary tier | 19 |
| Deposition video clips | 42 (across 4 deponents) |
| Audio files | 10 (voicemails, Uber recordings, 911 call) |
| Evidence videos | 9 |

### 4-Tier Evidence System

| Tier | Where it renders | Count | Purpose |
|------|-----------------|-------|---------|
| **Hero** | Inline in post body as visual embed | 58 | Key visual evidence that adds to the narrative |
| **Primary** | Post footer as clickable chips | 141 | Important evidence cited in body text |
| **Secondary** | evidence.html search page | 1,008 | Available for reader exploration |
| **Tertiary** | Internal only — filtered from public site | 20 | Background/working materials |

### 9 Hero Display Formats (CSS in templates/post.html)

| Format | CSS Class | Use |
|--------|-----------|-----|
| pull-quote | .pull-quote-embed | Devastating one-liners with amber rule, large italic text |
| photo-frame | .photo-frame-embed | Photos, screenshots, lab reports with polaroid-style frame |
| social-card | .social-card-embed | Blog posts, social media with header image + excerpt |
| email-screenshot | .email-screenshot-embed | Emails with header bar, sender/recipient, body text |
| blog-card | .blog-card-embed | Blog text quotes with featured image |
| legal-snippet | .legal-snippet-embed | Court documents with jurisdiction header, serif type |
| imessage | .imessage-embed | iMessage/text exchanges with blue/green bubbles |
| video-clip | .video-clip-embed | Playable video with thumbnail, play overlay, key quote caption |
| audio-transcript | .audio-transcript-embed | Audio with transcript snippet, speaker label, native player |

### Evidence Selection Governance

Per the Evidence Style Guide (Audits/Evidence_Style_Guide_v1.docx):

**Hero Slot System:** Every post (except B01 The Fool, B49 For Evie, B50, B51) has a minimum 3 Hero items — one Pull Quote, one Image/Screenshot/Video, one Styled Text Block (message, email, legal snippet, or audio). Posts may add 1-2 additional Heroes for a maximum of 5.

**Source Bias Priority:** Tara's discovery (device forensics, search history, messages) > Social media / Brienne's blog > Laboratory results > Court filings > Sworn testimony. This reflects the gag order constraint.

**Primary Cap:** 8-12 items per post. Footer should feel like a scannable, clickable slideshow.

### Interview Methodology

Three rounds of author interviews:
- **INT-001** — Early session, basic questions
- **INT-002** — Sessions 3-4, 25 questions across 2 rounds
- **INT-003** — Session 6, 12 entries (INT-003-001 through INT-003-012)

### Voice Standards

- **"Is the prose witnessing, or is it arguing?"** Witnessing is the work.
- **Contemporaneous Scene Rule** — Third-person omniscient, in the moment. No forward time jumps.
- **Cold Accumulation** — Evidence density increases across acts.
- **Evidence lane / narrative lane separation** — Evidence embeds are distinct from narrative prose.
- **The narrator's fundamental stance is admiration that survives betrayal** — governs tone for Tara, Kelly, Brienne, Petrella.
- **The commitment attempts (not the poisoning) were the worst events** — per Steve's interview.
- **The Fool Principle is deliberate, not naive** — Steve was aware of the risk and chose trust with preparation.
- **First/last line of the book:** `*People always tell you what they fear.*` (italics, Steve's interior voice, B00) / `People always tell you what they fear.` (plain text, narrator voice, B49). Same sentence, different speakers — the book's structural bookend.

---

## Connected Project: The Book

The blog feeds into a standalone book manuscript at `../ChappaquaPoison Book/`. That project has its own pipeline (`blog_to_book.py` → `book_to_pdf.py` → `book_to_epub.py`), its own orientation, and its own drafts directory (currently at Draft 30). The v3 blog also generates its own book outputs (DOCX, PDF, EPUB) directly.

---

## Key Patterns and Principles

Documented fully in INSIGHTS.md. Quick reference:

- **The Asymmetric Standard** — Steve is held to the highest standard; no standard on the other side.
- **The Story Changes Depending on Who's Watching** — Bruises migrate, aggression collapses before witnesses.
- **The Family Operates as a Unit** — Coordinated, not individual.
- **Juxtaposition over Argument** — Place evidence side by side, let the reader do the work.
- **Cold Accumulation** — Evidence density increases across acts.
- **Pontius Pilate Pattern** — People who could intervene but didn't.

---

## What NOT to Do

- Do NOT restructure the evidence system or change the index schema EXCEPT as defined in `Standards/SOURCE_EXHIBIT_SPEC.md` (the `source_exhibit` field addition approved Session 60).
- Do NOT rewrite posts without checking the Pass 2 state AND the evidence plan first.
- Do NOT assume what Steve remembers. Ask. His memory is the evidence.
- Do NOT soften the narrative. This is documentary nonfiction. The evidence speaks.
- Do NOT ask Steve questions the archives can answer. Search first.
- Do NOT use the old Body Rule. The Contemporaneous Scene Rule replaced it.
- Do NOT add narrator editorializing. Pass 2 specifically removed it.
- Do NOT add forward time jumps. The Contemporaneous Scene Rule forbids them.

---

## Master Archives (Outside the Blog Directory)

The v3 blog sits inside a larger workspace. Key paths relative to workspace root:

```
├── _AI_SYSTEM/
│   ├── ORIENTATION.md              ← Master orientation for ALL projects
│   └── Guides/Archive_Navigation_Guide.md  ← How to search the 313K-line archive
│
├── Indexes and Master Archives/
│   ├── Master_Evidence_Archive.md  ← 313,568 lines. PRIMARY research tool.
│   ├── Messages/                   ← 31 iMessage conversation PDFs
│   └── Photos/                     ← ~400 source images
│
├── Timelines/Master_Timeline.md    ← 4,925 lines
│
├── CaseFiles/                      ← 432,585 files, 280GB
│
└── Blogs/ChappaquaPoison_v3/       ← THE BLOG (you are here)
    ├── Evidence/html/media/
    │   └── Perfectly_Formatted_Blogs_source.txt  ← StevieLovesEvie blog archive (48,350 lines, 215 posts)
    └── Enriched/                   ← Baldwin voice enrichment outputs
        ├── backups/                ← per-chapter source snapshots
        ├── snapshots/              ← per-session directory snapshots
        ├── qa_reports/             ← QA session outputs
        ├── handoffs/               ← session handoff notes
        └── references/
            ├── BLOG_DETAIL_INDEX.md      ← Blog-to-chapter mapping with line numbers, nanny quotes, Evie detail
            ├── SKILL_PATCH_3D.md         ← Step 3D patch documentation (applied to skill Session 79)
            ├── voice-system.md           ← Baldwin/Sebald/Robinson calibration examples
            ├── MOTIF_EVIE_NAMING.md      ← Evelyn/"light of evening" naming motif tracking
            └── PLACE_DETAIL_AUTHOR.md    ← Author primary-source place descriptions (6 locations)
```

---

---

**Session 92 (March 26, 2026):** Evidence Archive Edition initiated. Two companion projects: Evie's Story (Definitive Edition) and The Lies (iMessage Edition). Image dedup audit (23 cross-book duplicates), SLE blog mapping (147 entries by voice type), Lies cross-cut working doc (12 sequences from Rashmi + Linda threads). Brendan Walsh thread identity corrected (was labeled "Brienne" but is actually the journalist brother).

**Session 93 (March 26, 2026):** All primary threads now read (Rita complete, Dr. Rhodes complete, Brendan complete, Steve complete from S92). CRITICAL FINDING: Adderall is Tara's prescription (Dr. Rhodes prescribing record), not Steve's — Rita (therapist) was told the reverse. Professional feedback loop documented. Lies cross-cut updated to 16 sequences + Adderall cross-cut, 3-tier ranking. Evie's Story chapter outline complete (12 chapters, 2 volumes). Kelly foreword drafted. Extracted image filenames found unreliable (auto-generated, don't match content). Core purpose established: protecting Steve and Evie through structural evidence.

*Orientation — Version 82 — April 8, 2026*
*Canonical evidence index: 2,191 entries. Book: 437 pages, 97,966 words. Build: 0 errors, 0 warnings. CHAPTER ENRICHMENT GUIDE: 5/5 priority entries complete (B41, B45, B37, B48, B46). No chapter files edited — guide work only. Process: guide first, evidence-grounded, write last.*
