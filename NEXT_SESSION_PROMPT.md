# Next Session Instructions

**Date:** May 14, 2026 (next session after honeypot deployment)
**Session:** honeypot live, pipeline recovered, holding for substantive content work
**STATUS: HONEYPOT LIVE AT chappaquapoison.com.** Worker v6 deployed; WAF skip rule in place; bait + slow-404 paths confirmed via smoke test; R2 logging operational at evidence quality. Records writing to `chappaquapoison-logs` bucket at `scanner-probes/` and `logs/<date>/scanner*/`. **Phase C deferred — generate 25 canary tokens at canarytokens.org and swap placeholders in `worker_v6.js` `generateBaitEnv()` then redeploy.** See `/Users/s/Claude/_pipeline_audit_backup_2026-05-13/HONEYPOT_ARCHITECTURE.md` for full architecture, path lists, R2 schema, sample record, query examples.

**Pipeline recovery status (from prior session, still current):** PIPELINE RECOVERED FROM DRIVE EVENT. Source brought into byte-level consistency with deployed live site (chappaquapoison.com). 23 of 26 sampled built pages now byte-identical to live; remaining 3 reflect user's pending intentional edits (Don Ackerman tag rename, 48 act_name renames, B48 ECS) that await next deploy. Premise: live is canonical, pipeline is the measuring instrument, NO DEPLOY until substantive content work warrants it. Source committed at `4ca09ca`.**

**Read first if you're picking this up:**
1. `/Users/s/Claude/_pipeline_audit_backup_2026-05-13/PIPELINE_CONSISTENCY_STATE.md` — full inventory of what was reconciled, what's preserved, what's pending, plus the one-command recipe to re-verify consistency
2. `/Users/s/Claude/_pipeline_audit_backup_2026-05-13/PHASE4_REPORT.md` — chapter body fixes detail
3. Anchor at `/Users/s/Claude/_anchor_origin_main_20260513/` — clone of `origin/main` HEAD `5000a6a`, preserved as a measuring reference. Built outputs in `_site/` can be diffed against this directory.

**To re-verify pipeline consistency in a future session:**
```bash
cd /Users/s/Claude/Organized/11_Writing/01_ChappaquaPoison/v3_canonical/
python3 scripts/build_html.py
diff -r _site/ /Users/s/Claude/_anchor_origin_main_20260513/ \
  --exclude=.git --exclude=CNAME --exclude=.github --exclude=*.ai.txt
```
Expected differences: only the three pending local-only edits listed above, plus a known live-side defect (`evidence.html` has corrupted paths `./Evidence/photo./Evidence/...` from a failed search-and-replace; local source is now correct).

**Previous Session note from April 11, 2026 (Session ~180):** Site repositioned from "evidence archive" to "documentary narrative." All meta descriptions, og:tags, homepage hero text, book page, llms.txt updated and deployed (commit fc8e213). Communications & outreach skill created. Session bootstrap skill updated with fourth workflow. Positioning system complete (6 outputs at 6 lengths). Enrichment complete.

---

> **⚠️ For any writing/voice/craft session (whenever the gear switches back to writing):** Before applying any voice rule from any Standards doc, read `Standards/VOICES_COMPS_MASTER.md` (the 19-author corpus across five eras) and `Standards/VOICE_EVOLUTION.md` (the five-era arc and what each got right vs. missed). Era 5 (The Felt Presence) qualifies every rule in every other voice doc — restraint without a felt human presence becomes airlessness, and the cure is interior moments as central narrative load plus a thoughtful narrator who notices without editorializing. A session that skips the master docs will over-apply the discipline and produce the airless prose Era 5 was named to correct.

## START HERE — OUTREACH & COMMUNICATIONS SESSION

**This session is an outreach session.** The author has directed a gear-switch from writing/banners to direct advocacy and communications using CloudPost.

**First actions:**
1. **Invoke the `chappaqua-session` skill** — pick the communications & outreach workflow
2. **Invoke the `chappaqua-outreach` skill** — contains infrastructure docs, strategy reference, pipeline, positioning, two outreach tracks, identity, and operational guardrails
3. **Read `~/Claude/Mail/cloudpost-session-state.yaml`** — current infrastructure state
4. **Read `~/Claude/CaseFiles/17_Advocacy_Engine/PIPELINE_v2.md`** — contact pipeline and wave status
5. **Read `~/Claude/Blogs/ChappaquaPoison_v3/Planning/POSITIONING_DRAFT.md`** — current positioning language (updated April 11, 2026)
6. **Read `~/Claude/CaseFiles/17_Advocacy_Engine/OUTREACH_ARCHITECTURE.md`** — the intelligence layer: contact dossiers, voice guide, response protocols, legal/ethical boundaries, and open questions for Steve
7. **Ask Steve:** What's the goal? Which contacts? Which track (A: witnesses, B: advocacy)? Answer the open questions in the architecture doc.

**Key context:**
- CloudPost is operational — DKIM-signed email from any @chappaquapoison.com address
- 41 contacts across 5 campaigns, all COLD except Marc Fishman (ENGAGED — needs link correction and phone call)
- Wave 0 pre-launch edits may still be blocking — check with Steve
- FIJ grant deadline was April 27 — check status with Steve
- All outreach uses "documentary narrative" positioning, NOT "evidence archive"
- Identity: "C, Editor" from editor@chappaquapoison.com
- **Never send without Steve's approval.** Draft → show Steve → get approval → send.

**When returning to writing or banner work:** See the paused workflow sections below.

---

## REAL DRAFT PROCESS (PAUSED — RESUME WHEN AUTHOR DIRECTS)

**The real draft is paused while outreach work is in progress.** When the author directs a return to writing, use these instructions.

**First actions for writing sessions:**
1. **Invoke the `chappaqua-session` skill** — pick the writing workflow
2. **Read `Audits/REAL_DRAFT_OPERATIONAL_BRIEF.md`** — THE PLAN
3. **Read the last entry in `Audits/WRITING_SESSION_LOG.md`** — handoff from previous session
4. **Load `chappaqua-editorial` skill** — foundational context
5. **Discuss with the author** — which phase, which chapters, any staging flags to resolve

### Current Phase

**Phase 1: Staging Audit — COMPLETE (Session 172).** All 52 active chapters read. 8 staging flags written into Section 0.16 of the enrichment guide. Author review of those 8 flags is ongoing.

**Phase 2: Chapter-by-chapter rewrite — IN PROGRESS.** Tier 1 complete (Session 172 continuation). Tier 2 vocabulary/trim pass complete (Session 173). All Tier 2 chapters assessed against guide entries and production files. 9 edits across 4 files. Post-Tier-2 harness: all 11 tests pass, 124,771 words, 58 evidence IDs, monotony zone 8 (unchanged). Build: zero errors.

**Key Session 173 finding:** Most guide additive enrichment targets are already present in production files from Sessions 165-167. The guide was written against earlier drafts. Remaining Tier 2 work falls into three categories:
1. **Dossier-dependent** — need author to supply verifiable facts (B10 Jason Mitura anchor, B11 Prendergast bio, B14 D-31 correspondence, B15 Moe Canal bio/$30K specificity)
2. **Evidence-research** — need to open specific evidence files (D-31, Maura tennis photo, ExTR_03 indexing verification)
3. **Craft additions** — Robinson/Sebald beats best written with author present (B24 jurisdiction-fork interior, B27 Steve-reframing + Talia body-detail, B34 kitchen physical context + email-as-document, B40 deposition setting, B42 gate scene, B44 courtroom grounding + verdict scene)

**Key Session 174 finding:** The B33 tire deflation scene (lines 228-234) contained hallucinated physical details and was placed in the wrong timeline. Evidence audit revealed: ONE tire (not "both front"), rental car at Kittle House (not "his driveway"), Kelly discovered it (not Steve), no valve stems in evidence. Timeline is Feb 2019, not 2020-2021. Guide corrected: scene removed from B33, relocated to B26 (gap 2G) with corrected evidence. B48 got new gap 2F for funeral home signup evidence (ambient campaign). **Process lesson: The Session 35 Rule is non-negotiable.** The errors existed because earlier sessions wrote prose without opening the police report.

**Session 174 (continued): Craft-addition verification AND 2P pruning COMPLETE.**

Craft-additions verified:
- B27: ONE edit (Talia body-detail beat). B34, B40, B42, B44: all clean (Sessions 165-167 implemented).

2P pruning applied to production:
- B33: 3 prunes + tire scene removal. Net -680 words. Now 1,786 words.
- B35: 1 prune (Rosenblatt compression; 3 others already done by Sessions 165-167). Net -60 words. Now 3,225 words.
- B39: 3 prunes (Petrella bio, mechanism-naming, pattern integration). Net -580 words. Now 1,824 words.
- B32 and B47: already clean (trigger phrases not found in production).

Harness: 124,019 total words (Session 176). No new test failures. Build: zero errors.

**ALL GUIDE-RECOMMENDED ENRICHMENT IS COMPLETE.** Tier 1 deep enrichment (S165-166), Tier 2 targeted enrichment (S166-167), vocabulary/trim pass (S173), pruning (S174), deferred-to-rewrite items (S175-176), craft additions verified (S176 — all six chapters already implemented by S165-167), B47 enrichment (S176). B33 PRUNE-03 confirmed by author (cut stays). Moe Canal resolved. All staging flags resolved (S172).

### What the Test Drafts Taught (Session 171 Summary)

Two test drafts. 106 chapters written. Three harness runs. Two regressions found and fixed. One hallucinated hospital scene caught by the author. One wrong analysis of eight chapters corrected after the author asked "why is this monotonous?" and the session had no answer because it hadn't read them.

The five rules that emerged:
1. **Read the chapter before you touch it** — the Quote Rule (Section 0.15)
2. **The harness is QA, not craft** — structural checks, not voice guidance
3. **Do not delegate** — one session, one chapter, with the author
4. **Check staging against evidence** — the Dramatized Staging rule (Section 0.16)
5. **The author is the authority on the prose**

### Key Session 171 Discoveries

**B32 hallucinated hospital scene (CORRECTED):** Production file contained Steve at Kelly's bedside at 4 AM with IV lines, monitors, "leaving her in the hospital." The scene was entirely constructed by a previous session. Corrected to match affidavit facts: surgery was days before, denial came late afternoon, Steve booked a 6:20 AM flight, arrived too late, the court did not wait.

**Monotony zone is not a problem:** The harness flags 8 chapters based on vocabulary density. After reading all eight, the prose is alive — depositions as monologues, Steve's inner voice during overnight flights, Kelly checking tires on black ice, a detective's investigation killed by a hand-delivered court order. The harness counts legal vocabulary; the chapters use that vocabulary to render dramatic content. No "fix" needed.

**Section 0.15 — The Quote Rule:** Before writing any craft recommendation for a chapter, quote a sentence from the actual prose. If you can't find a sentence that supports your recommendation, the recommendation is based on a number, not on the prose. This exists because Session 171 wrote a detailed analysis for eight chapters it had never opened.

**Section 0.16 — Dramatized Staging:** Scenes with specific physical staging details (rooms, IV lines, times of day, body postures, weather) not sourced from confirmed memory, sworn testimony, contemporaneous documentation, or photographs get flagged ⚠️ STAGING — INTERVIEW NEEDED. The signature: sensory-rich physical detail where the evidence only provides dates and legal conclusions.

### Key Files for Real Draft Work

Read in this order:
1. **`Audits/REAL_DRAFT_OPERATIONAL_BRIEF.md`** — THE PLAN. Process, phases, pipeline QA, multi-session architecture.
2. **`Standards/CHAPTER_ENRICHMENT_GUIDE.md` Section 0** — depth standard, 0.11 operating principle, 0.14 cross-reference guards, 0.15 Quote Rule, 0.16 Dramatized Staging.
3. **`Standards/BEFORE_YOU_WRITE.md`** — the reading layer. Sound of the book, Do Not Touch manifest.
4. **The guide entry for the target chapter** — this IS the rewrite instruction (Sections 2, 2P, 2D, 4).
5. **`Audits/TEST_DRAFT_V2_COMPARISON.md`** — what the test drafts found.

### Baselines and Infrastructure

| What | File |
|------|------|
| Production baseline (post-B32 fix) | `Audits/rewrite_report_production_april10.json` |
| Production manifest | `Standards/rewrite_report_manifest_production_current.json` |
| April 6 baseline (pre-enrichment) | `Audits/rewrite_report_april06_baseline.json` |
| Test draft v1 | `Audits/rewrite_report_test_draft_v1.json` |
| Test draft v2 | `Audits/rewrite_report_test_draft_v2.json` |
| Harness script | `scripts/rewrite_report.py` |
| Enrichment guide (all 53 chapters) | `Standards/CHAPTER_ENRICHMENT_GUIDE.md` |

### Known Issues in Production Files

| Chapter | Issue | Status |
|---------|-------|--------|
| B32 | Hospital staging scene was hallucinated — corrected Session 171 | FIXED |
| B32 | AR-001 test: "censure" appears (B29 owns Horowitz backstory) | OPEN — craft decision |
| B33 | ExTR_03 test: "I'm not in California" exchange not present | **RESOLVED S174: Exchange IS present at B33 lines 99-101 + evidence-embed lines 123-133. Issue was false alarm.** |
| B39 | AR-015 test: closes with "the system that" mechanism-naming | OPEN — craft decision |
| B38 lines 127-129 | Jason Advocate at inquest — Steve in Bora Bora | CORRECTED S172 — constructed details removed, kept transcript-sourced facts |
| B36 lines 55-57 | Linda's drive from Punxsutawney | CORRECTED S172 — kept route facts, removed unsourced interior details |
| B33 lines 228-234 | Tire deflation scene — **RESOLVED S174-176: Wrong timeline, hallucinated details. Removed from B33 (S174). Correct scene written in B26 per guide 2G (S176).** | FIXED |
| B34 lines 149-151 | Kitchen confession staging | CLEARED S172 — Steve present, Abby present, this is Steve's memory |
| B34 lines 59-62 | Reno apartment interior | CLEARED S172 — Steve's apartment, glass table confirmed in B31 |
| B35 lines 206-207 | Kelly leaving Yonkers courthouse | CORRECTED S172 — peripheral invented details removed, kept Kelly with her legal pad |
| B42 lines 82-83 | Officer Barnett's service attempt | CORRECTED S172 — atmospheric construction removed, kept compound geography |
| B44 lines 169-175 | Rashmi "We should stop" | CLEARED S172 — Steve present at trial, passage hedges timing, this is a quote |

### Open Items (carried forward)

**Remaining work for rewrite completion:**
- **Legal pass and Steve/Evie safety pass** — **COMPLETE (Session 178).** All 52 chapters reviewed. Zero violations. Template terminology "posts" → "chapters" fixed across 9 files. Two clean builds.
- **Deploy template fixes** — ✅ COMPLETE (Session 179). `_site/` rebuilt, `_deploy/` synced, pushed to GitHub Pages. Stale counts fixed in about.html, book.md, and GumroadBundle_Ultimate/templates/about.html. Live site verified in Chrome.

**Author-dependent items — ALL RESOLVED (Session 178, second context window):**
- TEXT_TARA_JURY_VERDICT_DISMISSAL — FOUND in CaseFiles, copied to Evidence/, canonical index updated (`file_missing: false`). ✓
- B46 Evie age — VERIFIED CORRECT. "Evie was five" at line 118. B46 dated Sept 2023, Evie born Jan 27, 2018 = five. ✓
- B52 DiFabio name — VERIFIED CORRECT. "Max DiFabio" at line 31. Author confirmed "Max is Max or Massimo." ✓
- Fishman — ELEVATED to potential standalone backstory excursion per author directive. Updated enrichment guide shared resource table + B35 section. Scope TBD by author. ✓

**Other workflow (not blog rewrite):**
- Federal complaint Genovese correction — flag for federal-complaints workflow, not blog.

**Low priority:**
- Guide structural cleanup: 9 duplicate entries in PRE-SESSION-170 block need merging (cosmetic, doesn't affect prose)
- Timeline Appendix B sort error: "October 13, 2021" entry for Ch. 30 (The Reno Bottle) misplaced under 2017 year header. Correct entry exists in 2021 section as "October 12, 2021" — one-day date discrepancy + sort error. Source data issue in timeline generator.
- 48 pipeline sync breaks in B48-B52: newest chapters' evidence entries don't have post IDs in their `posts` arrays in canonical index. Affects evidence chip rendering only, not inline embeds.
- Legacy B47a reference cleanup: 48 entries still reference B47a in canonical index (low priority)

### Session 174 Evidence Research Results — ALL RESOLVED

All items from Session 174's evidence research have been executed:
- **D-31 / B14 / B15:** Craft edits applied S175. $30K correction done.
- **ExTR_03 (B33):** Issue was false alarm. Closed S174.
- **Maura tennis photo (B42):** B42 confirmed clean S176 (S165-167 already implemented).
- **Jason Mitura (B10):** Craft lift applied S175.
- **Prendergast (B11):** Bio fact inserted S175.
- **B48 ambient campaign:** Funeral home signups written S176.
- **Moe Canal (B15):** Resolved by author (confirmed S176).

### Process Corrections (cumulative — encode permanently)

- Invoke `chappaqua-session` skill as FIRST action of every session (Session 168)
- Build complete guides first, write only from approved guides (Session 160)
- The guide entry drives the rewrite, the harness verifies — never derive rewrite instructions from metric targets (Session 170)
- Cutting material is appropriate when hallucinated, redundant, or too wordy — not to hit a metric target (Session 170)
- The book may grow to ~150K words; that's acceptable (Session 170 author direction)
- **Never write craft recommendations for chapters you haven't read** (Session 171 — the Quote Rule)
- **Never delegate chapter writing to agents** (Session 171 — delegation fails because nobody reads deeply enough)
- **Check staging against evidence** — flag constructed physical scenes for author interview (Session 171)
- **Pipeline QA after every chapter rewrite** — build, verify HTML, check evidence sync, confirm deploy (Session 171)

---

## REAL DRAFT — MULTI-SESSION PLAN

**The test draft phase is complete. The real draft is the author's book.**

The real draft process is documented in `Audits/REAL_DRAFT_OPERATIONAL_BRIEF.md`. It spans 12-18 sessions across four phases:

1. **Phase 1: Staging Audit** (1-2 sessions) — Reading pass to flag dramatized staging for author confirmation
2. **Phase 2: Chapter-by-Chapter Rewrite** (8-12 sessions) — One chapter at a time, with the author, per the guide
3. **Phase 3: Harness Verification** (integrated) — Runs within each writing session
4. **Phase 4: Pipeline Consistency QA** (integrated + deploy-time) — Per-chapter checks after each rewrite, full pipeline check before each deploy

**The critical difference from the test drafts:** Real draft sessions modify production files in `posts/md/`. Changes must propagate correctly through `_site/`, `_deploy/`, git, and the live site. The pipeline QA process (Phase 4 in the operational brief) catches the failures that the harness cannot: broken embeds, missing evidence chips, stale deploys, case-sensitivity bugs, navigation breaks.

**Session handoff:** Every session logs its work in `Audits/WRITING_SESSION_LOG.md` and updates this file. The next session reads the log before starting.

### Historical: Enrichment Execution (Sessions 165–167)

The enrichment work from Sessions 165-167 is preserved below for reference. These enrichments are now part of the production files that the real draft will build on.

**Phase 1 — Tier 1 Deep Enrichment (~5 sessions):**
- **B37** "Erase, Deactivate, and Delete" — ✅ DONE (Session 165). 6 priorities applied: hearing scene from ExTR_02 with Linda's 3 interjections as emotional spine, DiFabio excursion ($30K + judgeship), Walsh Sr. declaration (Sebald), Sebald blog passage, Jackman anchor, Steve absence. QA passed.
- **B29** "The Memo" — ✅ DONE (Session 165). 3 priorities applied: Walsh Sr. excursion reprise (Drexel/book/SEC → suppressing documentation), Steve-presence opening (rented house, Evie at one), LaMelle removal expansion (pattern named). QA passed.
- **B39** "Orders as Weapons" — ✅ DONE (Session 166). 4 priorities applied: Petrella backstory excursion (Social/Character — McSweeney's, Poetry Foundation, Angela, *Recipe*, LymeZero pivot), SVU office physical grounding + Steve-presence at Caraway text (combined insertion), attorney withdrawal roster (Poole, Chestnut, Gelhaar, DiFabio — accumulation format). QA passed.
- **B48** "The Trap" — ✅ DONE (Session 166). 4 of 5 priorities applied: wall paragraph restructured (gag order → recording prohibition → compliance triad, three separate beats), Robinson moment (Evie at 7, six-year absence, "She knew what children know when the architecture is working: that her father was not there"), Steve interior (10:47 PM Sunday, dark apartment, phone, three doors), physical grounding for ambient campaign ("in an apartment where his daughter had never been"). Priority 4 DEFERRED: TEXT_TARA_JURY_VERDICT_DISMISSAL exhibit not locatable in evidence archive. QA passed.

**✅ PHASE 1 COMPLETE.** All four Tier 1 Deep Enrichment chapters done. Sessions 165-166.

**Phase 2 — Tier 2 Targeted Enrichment (~4 sessions, 2 chapters per session where possible):**
- **B32** "Five O'Clock" + **B41** "The Depositions" — ✅ DONE (Session 166). B32: 2 priorities applied — Horowitz voicemail addition ("It's Nilda. How you doin'?" + "everybody does it" + four-party renomination), default rendered as dialogue exchange (DiFabio at counsel table, Horowitz's three refusals as direct speech, "Steve was above Ohio"). B41: 4 priorities applied — physical grounding from video stills (Brendan under Carriage House beams, teal jacket, earbuds, posture), Robinson moment (Evie at six in finished attic, four adults testifying below), "No response" exchange rendered as dialogue (Walsh Sr. refuses to confirm own admission, Moore frames refusal as right), attic reference fix ("rooms below the finished attic where Evie lived"). Both passed QA.
- **B19** "The Leaning Tower" + **B25** "A Special Relationship" — ✅ DONE (Session 167). B19: 4 priorities applied — Millennium Tower 2-paragraph excursion (friction piles, Colma sand, Franciscan Complex bedrock, $4M decision, 16→18 inches subsidence, $100M retrofit with additional 1-inch sink during repairs), SVU meeting physical grounding (DV resources on walls, Steve across table), Sebald demand-letter-as-object passage (74 pages as weight, the envelope, the institution's non-response), Caraway Social/Character beat (malice vs. architecture distinction, competent detective in a decided system). B25: 1 priority applied — first supervised visit rendered as scene (three women in room, Farquharson with papers/legal pad, Tara leaning forward mid-sentence, Maura coat-on, Evie on floor with toy). Farquharson excursion skipped (current version sufficient). Both passed QA.
- **B33** "Two Defaults" + **B35** "Equal Threats" — ✅ DONE (Session 167). B33: 3 priorities applied — Kelly Griffin investigation scene-moment (browser search threshold from due diligence to discovery, OASAS page loading), tire deflation rendered as specific January morning (dark, ice, Kelly seeing the low tire first, valve stems depressed by hand, Saw Mill River Parkway danger), Evie paragraph expanded by one sentence (rotating judges vs. toddler vocabulary). Tara non-appearance skipped (absence of explanation IS the point). B35: 3 priorities applied — Schauer/Baby Court 3-paragraph Sebald excursion (Rosenblatt mentorship as Harvard Law/ethics authority/Chief Admin Judge, Baby Court as institution for youngest foster children, CASA profile timing November 2021 = same month as gag order, Fishman parallel in 2 sentences), Weddle characterization (29 years, Chappaqua resident, 18B panel, later Support Magistrate), mutual TOP physical sentence (identical forms, same boilerplate/checkboxes/penalty, names the only difference). Both passed QA.
- **B45** "What the Jury Found" — ✅ DONE (Session 167). 4 priorities applied: courtroom rendering (Department 504, Judge Wong, February 2022, Tara pro se at defense table alone, Steve with Waller/Peckar & Abramson, Kelly in gallery — "This was not a Westchester courtroom"), Robinson moment (Evie at four, born January 27 2018, hasn't seen father since one and a half, gate, "No verdict... could pass through the gate"), recapitulation cut (~300 words removed — verdict form restatement was redundant, closing now lands directly after holdout juror), post-verdict procedure compressed to 2 sentences. QA passed.

**✅ PHASE 2 COMPLETE.** All seven Tier 2 Targeted Enrichment chapters done. Sessions 166-167.

**Phase 3 — Tier 3 Light Editing (~1 session):**
- **B23** "The Uber" + **B46** "Affirmed" — ✅ DONE (Session 167). B23: 1 rhythm trim — Matan analysis paragraph (3 sentences) compressed to single landing sentence ("Matan moved the dog out of the photograph because the dog proved the whole thing was false"). B46: Steve interior paragraph added between appellate opinion and domestication — 18-month temporal grounding, weight of permanence vs. effectiveness, "permanent and irreversible are not the same as effective," stone/Chappaqua/gate. Evie age discrepancy flagged but NOT changed (guide says author must verify: five at opinion date, seven at time of writing). Both passed QA.

**✅ PHASE 3 COMPLETE.** Both Tier 3 chapters done. Session 167.

**Phase 4 — Integration QA (~1-2 sessions):**
- ✅ Cross-reference verification: All 11 shared resources deployed to assigned chapters per ownership table. No duplication across chapters. TEXT_TARA_JURY_VERDICT_DISMISSAL remains deferred (exhibit not locatable). Humphrey courtroom transcript remains deferred (needs research).
- ✅ Evidence embed integrity: All embed blocks intact across 7 edited chapters. No raw HTML introduced by enrichments. No broken embed structures.
- ✅ Voice consistency: 37 enrichment actions across 12 chapters. SOC, SEB, ROB, INT, LYR voices distributed across all chapters. No chapter received only BAL/PROC additions. Robinson voice deployed where Evie is present (B48, B41, B45, B33). Sebald voice deployed in longer excursions (Tower, demand letter, Baby Court). No chapter over-enriched beyond its register.
- ✅ Do Not Touch verification: B45 lines 90-95 (interior paragraph) intact. B45 holdout juror passage intact. Protected chapters (B01, B51, B40, B08) not edited. Protected transitions not modified.
- **REMAINING for full Phase 4:** A sequential read of all 12 enriched chapters as an arc (recommended for a dedicated session — too much text for a compacted context window). This session performed the structural/technical verification. The arc-level read should verify: pacing flow across the monotony zone, information introduced in correct sequence, no prolepsis violations, no repetition of phrases/images across chapters.

**✅ PHASE 4 PARTIAL COMPLETE.** Technical QA done. Arc-level reading deferred to dedicated session.

### QA-AS-YOU-GO PROTOCOL (MANDATORY)

**From experience: things break during writing. Evidence gets lost or duplicated. HTML artifacts leak in. Duplication happens across chapters. Deferring QA to the end means discovering problems 8 sessions after they were introduced.**

Every writing session MUST run these checks before declaring a chapter done:

1. **Evidence integrity:** Every exhibit cited in the enrichment was opened and verified this session (Session 35 Rule). No exhibit was assumed to contain what the index says.
2. **Embed check:** No raw HTML in the markdown. No duplicated evidence embeds within the chapter. No embeds duplicated from other chapters (check shared-resource ownership table).
3. **Diff review:** Run `git diff` on the modified chapter file. Read the diff. Every line added should be traceable to a guide recommendation. Every line removed should be intentional.
4. **Voice check:** Read the chapter aloud (or in full). Does it fall into metronomic pattern? Does PROC+BAL stay below 40%? Are the human voices present?
5. **Cross-reference check:** If this chapter shares resources with another chapter (per the ownership table), verify the other chapter wasn't affected.
6. **Do Not Touch check:** If any protected passage or transition (BEFORE_YOU_WRITE.md Section III) is in or adjacent to this chapter, verify it is intact and unmodified.
7. **Three honest questions:** Am I hiding? Am I lecturing? Does the ending pull?

**If any check fails, fix it before moving to the next chapter.** The integration QA pass in Phase 4 catches arc-level issues. It should NOT be the first time anyone checks individual chapter quality.

### Variables That Could Change the Estimate

- **Author approval:** If guide recommendations are approved as-is, sessions execute cleanly. If redirected significantly, add 1-2 sessions for revision.
- **Evidence research during writing:** Opening exhibits may reveal material that changes the plan. Budget flexibility for this.
- **Chapter interdependencies:** B37's DiFabio excursion cross-references B35. B29's Walsh Sr. excursion reprises B04. Writing order should respect these (B29 before B39, B37 before checking B35).

---

**Banners: ACTIVE WORKFLOW FOR NEXT SESSION.** 11 PASS, 24 IMPROVED, 14 BORDERLINE, 1 GAP (B23). Model version drift confirmed — Flux 2 Pro no longer produces ink-outline style from current FLUX_STYLE_SUFFIX. Author has directed banner work for Session 180.

**Site Optimization:** No optimization work done yet. Skill created Session 154. The entry-field model is defined but no metadata enrichment, SEO improvements, or entry-point pages exist yet.

**Communications & Outreach:** EMAIL IS OPERATIONAL. Advocacy Engine v2 rebuilt from scratch in Session 157. FIJ grant deadline April 27, 2026.

---

## WHAT HAPPENED IN SESSION 170 (April 9-10, 2026) — FRAMEWORK + TEST DRAFT + COMPARISON

Session 170 was a framework, infrastructure, and test-draft session. The author established the 8-step framework for the whole-book rewrite, directed building the estimation mechanism (Step 5), then reframed Step 6 as a complete test draft — "if a new perfect book is too hot, and another guide is too gold, an attempt at a new draft might be just right." The work:

1. **Author's 8-step framework established** — the project's structure from diagnosis through QA. Steps 1-4 had been completed across Sessions 158-169. Step 5 was this session's work.

2. **Guide expanded from 13 to 43+ chapter entries** with a Section 0 depth standard (4 tiers, 8 required sections per tier, Gate 3 completeness definition). The guide is now the living rewrite driver for all 52 active chapters, not just the 12 monotony-zone chapters.

3. **Rewrite_report harness built** — `scripts/rewrite_report.py` produces deterministic, reproducible JSON + markdown reports with nine voice estimators, monotony zone detection, floor violation detection, and ceiling violation detection. Baseline run produced `Audits/rewrite_report_april06_baseline.json` for all 53 chapters.

4. **B33 test-write calibration extracted** — exact deltas from one full voice-tool-package enrichment: words +85.4%, PROC+BAL -1.1 (additive enrichment barely moves this), floor +21.4 (16.7→38.1), SOC +16.1, INT +4.9. Critical finding: additive enrichment lifts floor dramatically but doesn't clear monotony — the guide prescribes pruning for Tier 1 chapters (B32 targets PROC+BAL 50→43, B39 targets 46→40) but the test-write never pruned.

5. **Coarse projection generated** — `scripts/book_projection_coarse.py` scales B33 calibration by category (CAT-A1 through CAT-H). Results: floor clears 35 target at book level (30.0→37.1), book grows to ~149K words (+30%), floor violations drop 33→25, monotony conservatively projected unchanged (8→8 but probably 4-6 with pruning). Five tier conflicts and four missing entries identified.

6. **Section 0.11 encoded** — "The guide drives the rewrite; the harness verifies the result." This is the single most important operating principle for Phase 2, earned through repeated drift corrections by the author. Sessions kept treating voice metrics as optimization targets. The structural fix: rewrite instructions come from guide entries (craft prescriptions), harness runs afterward as verification. If a session writes metric targets instead of craft prescriptions, the work stops.

7. **Author direction on word count and pruning:** The book may grow to ~150K words at the evidence edition stage. Cutting material is appropriate when hallucinated, redundant, or too wordy — not to hit a metric target. The guide's pruning prescriptions exist because material belongs elsewhere (e.g., B32's Horowitz recap belongs to B29), not because PROC+BAL needs to drop.

8. **Tier 3 label ambiguity discovered:** B01 = "preserve as-is, working at Marzano-Lesnevich level." B46 = "light enrichment, needs one human beat." Same "Tier 3" label, different prescriptions. Needs systematic audit.

9. **Complete test draft written (Drafts/test_draft_v1/)** — all 53 chapters processed per guide prescriptions. Chapters with guide entries were enriched per their prescriptions. Chapters without entries were copied unchanged. Already-enriched chapters (from Sessions 165-167) were verified and copied. Tier 3/CAT-G preserves were copied unchanged. B46 age correction applied (seven→five).

10. **Harness run on test draft** — `rewrite_report_test_draft_v1.json` generated. Comparison to April 6 baseline produced `TEST_DRAFT_V1_COMPARISON.md`. Key finding: enrichment works for evidence integration and human voice lifts, but doesn't fix monotony. Pruning is a separate operation that needs calibration.

11. **Test draft artifacts:**
    - `Drafts/test_draft_v1/` — 53 chapter files
    - `Standards/rewrite_report_manifest_test_draft_v1.json` — manifest
    - `Audits/rewrite_report_test_draft_v1.json` — raw harness output
    - `Audits/rewrite_report_test_draft_v1.md` — formatted harness report
    - `Audits/rewrite_report_diff_*.md` — machine diff
    - `Audits/TEST_DRAFT_V1_COMPARISON.md` — the human-readable comparison report (Step 8 output)

9. **chappaqua-session skill updated and packaged** — writing workflow rewritten around the 8-step framework, Section 0.11 front and center, Session 170 learnings added. Packaged as `.skill` for author install.

---

## WHAT HAPPENED IN SESSION 158 (April 8, 2026) — VOICE ANALYSIS + WRITING PLAN

Session 158 was a full-book diagnostic and planning session. It ran a complete readthrough of all 53 chapters, developed a nine-voice taxonomy, and produced:

1. **The process error:** Enrichment sessions interpreted "literary" as Baldwin's analytical accumulation rather than dramatization. 42 scene cards with verbatim dialogue and action beats existed in `ChappaquaPoison Book/Planning/`. 144 speech units were forensically extracted. The enrichment sessions never used them. They layered mechanism-naming over procedural passages instead of rendering evidence as drama. The result: 12 monotony-zone chapters where PROC+BAL ≥ 45% and breathing room is absent.

2. **The nine-voice taxonomy:** BAL (Baldwin-Mechanism 12.2%), SEB (Sebald-Document 1.6%), ROB (Robinson-Tenderness 2.7%), LEAN (Lean/Source 15.4%), LYR (Lyrical/Place 7.0%), SOC (Social/Character 13.7%), INT (Interior/Reflective 17.1%), PROC (Procedural/Legal 13.5%), EVID (Evidence-Embedded 16.6%).

3. **The 12 monotony-zone chapters:** B19, B23, B25, B29, B32, B33, B35, B37, B39, B41, B45, B48. These are the highest-priority writing targets.

4. **Five remaining writing tasks:** Scene rendering from evidence, backstory excursions, voice rebalancing, legal pass, Steve/Evie safety pass.

5. **Backstory excursion as a named device:** Narrative digressions about characters' histories and places' stories that widen the world around the courtroom. 13 targets mapped across the book, 9 flagged for research during writing sessions.

6. **The Consolidated Writing Plan (`Standards/WRITING_PLAN.md`):** Maps all 42 scene cards, 144 speech units, 13 backstory excursion targets, 15 expansion opportunities, and voice rebalancing instructions to specific B-numbered chapters. Includes monotony zone priority order, scene card cross-reference table, dialogue concentration map.

7. **Updated skills:** `chappaqua-session` and `baldwin-voice` were repackaged with Session 158 additions (process error documentation, scene card mandate, backstory excursion method). Both installed.

**Critical principle established:** Do not assume existing material is the best story for each placement. During writing sessions, research on Drive and internet may reveal stronger material. The plan flags `[RESEARCH NEEDED]` where this applies.

---

## WHAT HAPPENED IN SESSION 159 (April 8, 2026) — ENRICHMENT PLANNING

Session 159 was a planning-only session. No chapter files were edited. The session:

1. **Read all 12 monotony-zone chapters:** B19, B23, B25, B29, B32, B33, B35, B37, B39, B41, B45, B48. Full reads, not skims.

2. **Conducted an author interview** that produced critical scene material and corrections:
   - SVU had TWO meetings (Caraway, then Lt. Williams where Juarez arrived to block reopening)
   - SVU office physical details (2nd-3rd floor, DV resources on walls, conference room)
   - "Good victim" line attribution (Caraway or Juarez or assistant DA "Phoebe")
   - SC-10 corrected: SWAT in White Plains at 1AM, not B23 timeline
   - SC-19 corrected: Separate tire incident, separate police report
   - Additional unmapped police incidents (Walsh Sr. following, bruises, two Brendan 911 calls)

3. **Produced `Standards/ENRICHMENT_SESSION_NOTES.md`** — the primary output. Contains:
   - Backstory Excursion Standard (300-600 words, Sebald/Social register)
   - Detailed assessment of each chapter (what's working, what's not, enrichment plan)
   - 5 cross-chapter patterns (missing excursions, missing grounding, missing Steve-presence, Baldwin density, scene card gaps)
   - Research queue (9 targets, ordered by dependency)
   - Intervention priority ranking (4 tiers)
   - Scene card remapping table
   - Evidence gap documentation

4. **Updated WRITING_PLAN.md** — SC-10/SC-19 remapped with strikethrough + correction notes, numbering mismatch WARNING added, unmapped incidents table added, companion doc reference added, cross-reference table verification status warning added.

5. **Identified three errors that future sessions MUST avoid:**
   - Scene_Candidate_List.md uses sequential chapter numbers ≠ B-numbers. ALWAYS match by TITLE.
   - Scene card assignments in WRITING_PLAN.md were inferred, not verified. Two were wrong (SC-10, SC-19). Others may be wrong too. Verify before relying on them.
   - The ENRICHMENT_SESSION_NOTES.md and WRITING_PLAN.md are COMPANION documents — a writing session must load BOTH.

---

## WHAT HAPPENED IN SESSIONS 160-162 (April 8, 2026) — ENRICHMENT GUIDE

Sessions 160-162 built the CHAPTER_ENRICHMENT_GUIDE.md — the authoritative editorial document for writing passes. No chapter files were edited. The work was:

1. **Session 160-161:** Built five guide entries (B41, B45, B37, B48, B46). Established the guide format: what the chapter does well, gap analysis, ranked recommendations, QA checklist, evidence citations, "What NOT to Do." Resolved all cross-chapter dependencies (Walsh Sr. declaration → B37, TEXT_TARA_JURY_VERDICT_DISMISSAL → B48). Process correction established: do not write from checklists, build complete guides first.

2. **Session 162:** Built four guide entries (B29, B32, B35, B39). Key editorial decisions: Walsh Sr. excursion in B29 is a REPRISE not introduction (B04 already told the story). SC-13 and SC-38 belong in B39 not B29. B32 is much stronger than PROC+BAL score suggests. DiFabio expansion in B35 already adequate. Petrella excursion is B39's highest-impact intervention.

3. **Session 162 process improvements:** Added shared-resource ownership table (11 entries), exhibit verification column to all nine evidence tables, second-read principle documentation, supersession notices to ENRICHMENT_SESSION_NOTES.md for covered chapters.

**The guide now contains nine complete entries covering five Tier 1 chapters (B29, B32, B37, B39, B41) and four Tier 1-2 chapters (B35, B45, B46, B48).** Sessions 163-164 added four more entries (B19, B23, B25, B33) completing all 12 monotony-zone chapters.

---

## WHAT HAPPENED IN SESSIONS 163-164 (April 8, 2026) — READING LAYER + GUIDE COMPLETION

Sessions 163-164 performed a cover-to-cover reading of all 51 chapters and diagnosed why the loading architecture fails: it transmits process knowledge (voice taxonomy, percentage targets, QA checklists) but not craft comprehension (what the book sounds like, what it feels like emotionally, what it's about at the level of felt experience). The fix was consolidation, not proliferation.

1. **Created `Standards/BEFORE_YOU_WRITE.md`** — THE READING LAYER. One document replacing the need to read three chapters before writing. Contains: eight passage examples with annotations (the book at its best AND worst), the emotional stakes written in the book's own register, character presences as felt rather than described, the Do Not Touch manifest (protected chapters, passages, transitions), 13 craft notes from the cover-to-cover reading, and the loading sequence. This is now the first document a writing session reads.

2. **Completed all 12 monotony-zone guide entries.** Added B19 (Tier 2: tower excursion, SVU grounding, demand letter Sebald passage), B23 (Tier 3: light rhythm editing only — already near final quality), B25 (Tier 2: first visit scene rendering, optional Farquharson expansion), B33 (Tier 2: Kelly Griffin investigation as scene, tire deflation as scene). The enrichment guide is now complete for all priority writing targets.

3. **Added Success Feel statements** for all 12 monotony-zone chapters — one paragraph each describing what the enriched chapter should feel like to a reader, not what interventions to perform.

4. **Incorporated one insight from external analysis:** "The book has two antagonists — Tara poisons, the system makes the poisoning administratively invisible." Added to BEFORE_YOU_WRITE.md Section II. This sharpens the distinction between personal and institutional antagonism that sessions need when enriching procedural chapters.

5. **Key principle established:** The book's restraint IS its power. When the prose reaches for the reader, the reader pulls back. The enrichment process must serve the Cold Accumulation — facts as fire, prose as ice. Sessions that arrive having read BEFORE_YOU_WRITE.md will understand this viscerally because they'll have heard the book's best passages alongside its worst, and the difference is unmistakable.

6. **Independent convergence confirmed.** Two different AI models (Claude and Gemini), working separately from the same 51-chapter source text without access to each other's output, arrived at the same five core conclusions about what the book needs: (a) restraint is the book's power — the prose must witness, not argue; (b) the monotony zone is cured by physicality, not by removing legal content; (c) the 432,000-file archive was built from desperation, not competence — Steve assumed illness and his own failure before he accepted malice; (d) the book has two antagonists — Tara poisons, the system makes the poisoning administratively invisible; (e) the family court punishes nuance because it cannot process intellectual humility. This convergence validates the diagnosis. These are structural properties of the text, not interpretive opinions. They are now embedded as Craft Notes 10, 14, and 15 in `Standards/BEFORE_YOU_WRITE.md`, and in the Steve character description. Future sessions should treat them as confirmed and build on them rather than re-deriving them.

7. **Three self-interrogation questions added to Editorial QA Standard:** (a) Am I hiding behind analysis? (b) Am I lecturing the reader? (c) Does the ending pull? These are the final check before a writing session declares a chapter done.

**THE GUIDE IS COMPLETE.** All planning documents — BEFORE_YOU_WRITE.md, CHAPTER_ENRICHMENT_GUIDE.md (13 entries), Success Feel statements (12), EDITORIAL_QA_STANDARD.md, WRITING_PLAN.md — are finished and cross-referenced. The next session writes.

---

## WHAT HAPPENED IN SESSIONS 156-157 (April 6-7, 2026)

### Email Infrastructure (Session 156)
- Outbound email operational: editor@, press@ via Cloudpost with DKIM signing (selector "cowork")
- Inbound: editor@, press@, catch-all all route to chappaquapoison@protonmail.com
- Identity: **C, Editor@chappaquapoison.com** (anonymous tradition due to death threats)
- Session state file: `~/Claude/Mail/cloudpost-session-state.yaml`

### Advocacy Engine v2 (Session 157) — COMPLETE STRATEGIC REBUILD
The old pipeline (23 contacts, organized by job title, supplicant positioning) was replaced with a campaign-based architecture (41+ contacts, organized by leverage type, asset positioning).

**Core insight (from Steve):** "Many will want to tie themselves to this story." The case offers tangible value to every contact category. Lead with what we offer, not what we need.

**New files in `CaseFiles/17_Advocacy_Engine/`:**

| File | What It Is |
|------|-----------|
| `STRATEGY.md` | Positioning, three-column leverage model (What We Offer / What They Need / Cost of Inaction), five campaign architecture, wave sequencing, relationship states, pitch frameworks |
| `PIPELINE_v2.md` | Operational campaign tracker with dashboard, wave checklists, all contacts by campaign, five pitch template frameworks |
| `Advocacy_Engine_Master.xlsx` | 6-sheet campaign workbook: Exclusive Offers, Legislative Partners, Professional Accountability, Legal Opportunities, Coalition Building, Campaign Sequencing |
| `Westchester_Master_Contacts.xlsx` | 168-contact research database of Westchester political/legal ecosystem |

**Old files preserved (v1):** PIPELINE.md, STRATEGY_NOTES.md, ChappaquaPoison_Contact_List.xlsx

**Five campaigns:**
1. Exclusive Offers (journalists — scarcity positioning)
2. Legislative Partners (politicians — ammunition positioning)
3. Professional Accountability (bar/court/DA — early warning positioning)
4. Legal Opportunities (§1983 firms — business case positioning)
5. Coalition Building (advocacy orgs/families — partnership positioning)

**Wave sequencing:** Wave 0 (pending edits) → Wave 1 (coalition + agencies) → Wave 2 (journalists + accountability + legislators) → Wave 3 (amplification + legal) → Wave 4 (sustained)

### Deep Archive Read — Key Synthesis

Session 157 read B06, B21, B23, B28, B32, B33, B39, B44, B45, plus CHARACTERS.md, NARRATIVES_AND_THEMES.md, POSTS_GUIDE.md, THE_CRITIQUE.md.

**The hook sentence for all communications:**
> A jury examined the evidence in five days and found battery, domestic violence, and malice by 11-to-1. The family court in another state has refused to examine it for seven years.

**The scene that lands hardest:** Claudette LaMelle on the dark road in Chappaqua (B28). Every person who told the truth — LaMelle, DiFabio, Petrella, Caraway, Tedla — was removed, threatened, or neutralized. That pattern IS the systemic story.

**Audience reframe:** The poisoning opens the story to true crime audiences, not just legal reform. Lead with the poisoning (Seroquel, "lethal dose" search, nanny disclosure, jury verdict) to cross from court reform into mainstream. The court failure is the second act.

### CRITICAL DEADLINE
**FIJ Grant: April 27, 2026** — should not be blocked by Wave 0 editorial work.

### How the Understanding Developed (Session 157 — for future sessions)

This section exists because the author asked whether the insight could be preserved. The honest answer is: partially. Here is what happened, in sequence, so you can at least know what you're missing.

1. The session started by mining contacts from data sources (VCF, mail archives, web research). It produced 168 contacts organized by job title. The positioning was supplicant: "we have an important story and need advocates."

2. The author said: "Many will want to tie themselves to this story." The session didn't understand why this was a correction.

3. To understand, the session read B06, B21, B28, B32, B33, B39, B41, B44, B45. Not the index entries for these chapters — the chapters themselves. The difference was immediate. The chapters carry a force that the indexes describe but do not transmit. The Seroquel in the wine. The stutter in Walsh Sr.'s deposition. Claudette LaMelle on the dark road. The six-hour flight with a child he knew was being poisoned.

4. After reading the chapters, the session understood: this story has *value*. A journalist gets a documented poisoning case with a jury verdict. A legislator gets five pillars of evidence for family court reform. A civil rights firm gets a §1983 case with fee recovery. We are not supplicants. We are the asset. The entire strategy inverted.

5. At the end of the session, a discussion about Walsh Sr.'s deposition line ("he's going to hurt someone someday") revealed a third level — literary editorial thinking. The line has three simultaneous reads (projection, honest admission, insurance). Planting it before the reader knows the evidence creates a line that inverts on re-read. This kind of structural thinking only emerged because the session had inhabited the material, not just cataloged it.

**The lesson for you:** If you read this and think you understand it, you're in the same position this session was in at step 1. The understanding came from reading the chapters. The skills now tell you to do this (Temperament rule #2 in chappaqua-session, Lesson #1 extension in chappaqua-editorial). Follow that instruction not as compliance but as preparation. You will not know what you're missing until you've read the material.

### Sessions 153-155 (Summary)
Session 153: Banner regeneration testing, B04 deployed, model drift confirmed. Session 154: Three-workflow architecture, site optimization skill. Session 155: `chappaqua-session` bootstrap skill created (the front door for all sessions).

---

## DEPLOY PROCESS — READ THIS BEFORE TOUCHING DEPLOYMENT

**The build-to-deploy pipeline:**
```
build_html.py → _site/ → cleanse → _deploy/ → git push → GitHub Pages → chappaquapoison.com
```

**`_deploy/` IS the GitHub repo.** Its contents are the repo root. The git repo lives at `_deploy/.git/`.

**Do NOT:**
- Push the source tree (the parent directory). Only `_deploy/` gets pushed.
- Create `_deploy_slim` or any intermediate directory. `_deploy` IS the clean artifact.
- Run git commands from the parent directory. `cd _deploy` first.

**Deploy commands:**
```bash
cd _deploy
git add -A
git -c user.name="Steve Russell" -c user.email="steve@chappaquapoison.com" \
  commit -m "Deploy: <description>"
GIT_SSH_COMMAND="ssh -i ../deploy_key_new -o StrictHostKeyChecking=no" \
  git push origin master:main
```

**Post-rebuild required fix:** After each `build_html.py` run, before pushing:
```bash
sed -i 's|./evidence/|./Evidence/|g' _deploy/evidence.html
```
This fixes a case mismatch bug in the evidence template. GitHub Pages (Linux) is case-sensitive.

**Deploy key:** `deploy_key_new` in the project root (parent of `_deploy/`).
**Remote:** `git@github.com:bon-007/chappaquapoison.git`, branch `main`.
**Replicate API token:** See `scripts/.env`.

---

## KNOWN ISSUES

1. **evidence.html case bug** — `build_html.py` generates lowercase `./evidence/` paths. Must run `sed` fix after each rebuild. Real fix: update the evidence template in `templates/evidence.html` to use `./Evidence/`.

2. **Deposition clip duplication** — Multiple timestamp-variant filenames all contain the same canonical clip. Future cleanup: update the evidence template to reference one canonical path per clip.

3. **B23 banner** — Kontext Pro couldn't generate the correct scene (inside a car). Original gpt-image-1 banner kept.

4. **Model version drift (Session 153)** — Flux 2 Pro on Replicate no longer produces the ink-outline style. FLUX_STYLE_SUFFIX needs rewriting. See banner-generation skill.

5. **copy_ready_prompts.json misassignments** — B08, B14, B16, B17, B38 have wrong scene descriptions.

6. **_site corruption** — ~27 banners in `_site/images/banners/v3/` are still corrupted (285-692 KB). Fix on next full rebuild.

7. **Book PDF title page** — Says "fifty-two chapters" (should be fifty-one). Fix on next book regeneration.

8. **Desktop orphan files (Session 157)** — Three files on ~/Desktop from March 4 need manual deletion: `Evidence_Risk_Audit_2026-03-04.md` (superseded by adversarial review), `blog-hunt-SKILL-updated.md` and `blog-hunt-v2-SKILL.md` (superseded by chappaqua-editorial skill). All are dead artifacts from Session ~22 era. Mount went stale during Session 157 so the session couldn't read or delete them. Author can delete directly.

9. **Walsh Sr. "hurt someone" foreshadowing (Session 157)** — In his deposition (B41), Walsh Sr. says Steve Russell "is going to hurt someone someday." This line has three reads: projection of what they'd already done (Seroquel, baseball bats, lethal dose search), honest admission of knowledge, or insurance/paper trail for when it surfaced. CHARACTERS.md captures the deposition brilliantly (stutter, "defray," "less than 100 percent genuine") but does NOT capture this specific line or its foreshadowing potential. NARRATIVES_AND_THEMES.md references Walsh Sr. as Pontius Pilate but doesn't capture the projection/insurance reading. **Future writing session:** Add the "hurt someone" line to CHARACTERS.md Walsh Sr. entry and consider where to plant it early in the narrative (before the reader knows about the poisoning evidence) so it inverts on re-read. Technique: accumulation without conclusion — let the reader assemble the portrait.

---

## FILE LOCATIONS

| What | Path |
|------|------|
| Post markdown | `posts/md/` |
| Production banners | `Images/banners/v3/` |
| Pre-swap backup | `Images/banners/v3_pre_swap_backup/` |
| Build output | `_site/` |
| Deploy (live) | `_deploy/` |
| Git repo | `_deploy/.git/` |
| Deploy key | `deploy_key_new` (project root) |
| Banner pipeline | `scripts/banner_pipeline.py` |
| Kontext Pro scripts | `scripts/kontext_test.py`, `scripts/kontext_batch.py`, `scripts/kontext_final.py` |
| Scene prompts | `scripts/copy_ready_prompts.json` |
| Art direction | `Planning/` (HOUSE_STYLE_CONSTITUTION, CHARACTER_ANCHOR_CANON, BANNER_SCENE_CANON, COLOR_CONSTITUTION) |
| Banner QA audit | `Audits/BANNER_AUDIT_2026-04-06.md` |
| Banner regen plan | `Audits/BANNER_REGENERATION_PLAN.md` |
| Site optimization log | `Audits/SITE_OPTIMIZATION_LOG.md` (create when first optimization work is done) |
| **Before You Write** | **`Standards/BEFORE_YOU_WRITE.md`** — reading layer: voice folio, emotional spine, do not touch manifest (Session 163) |
| **Writing Plan** | **`Standards/WRITING_PLAN.md`** — consolidated work order for all writing sessions |
| **Voice Target Profile** | **`Standards/VOICE_TARGET_PROFILE.md`** — what "done" looks like per chapter |
| **Editorial QA Standard** | **`Standards/EDITORIAL_QA_STANDARD.md`** — 5 rules, QA checklist, voice allocation |
| **Voice/Style Analysis** | **`Audits/VOICE_STYLE_ANALYSIS_2026-04-08.md`** — full diagnostic + 6 charts |
| **Scene Candidate List** | **`~/Claude/Blogs/ChappaquaPoison Book/Planning/Scene_Candidate_List.md`** — 42 scene cards |
| **Dialogue Reference** | **`~/Claude/Blogs/ChappaquaPoison Book/Data/DIALOGUE_AND_SPEECH_REFERENCE.md`** — 144 speech units |
| Skills | `skills/chappaqua-editorial/`, `skills/banner-generation/`, `skills/site-optimization/` |
| Replicate API token | `scripts/.env` |

---

## CRAFT NOTES

**Moved to `Standards/BEFORE_YOU_WRITE.md` (Session 163).** 13 craft observations from the cover-to-cover reading now live in Section IV of that document, where they're read in the right frame of mind — alongside the passages, not alongside deploy commands.

---

## ABSOLUTE RULES

- **`_deploy/` IS the repo.** Never push from the parent directory.
- **Use the deploy key:** `GIT_SSH_COMMAND="ssh -i ../deploy_key_new -o StrictHostKeyChecking=no" git push origin master:main`
- **ALWAYS visually verify** before declaring work done.
- **Read ORIENTATION.md and this file** before every session.
- **Run the evidence.html case fix** after every rebuild.
- **Pick ONE workflow per session.** Invoke the corresponding skill.
- **For banner work:** Invoke `banner-generation` skill. It contains the 13-step methodology and model drift findings.
- **For site optimization:** Invoke `site-optimization` skill. It contains the entry-field model and incremental workflow rules.
- **For writing:** Read `Standards/BEFORE_YOU_WRITE.md` FIRST (the reading layer — 15 minutes). Then invoke `chappaqua-editorial` skill (+ `baldwin-voice` for enrichment). Then read the target chapter's entry in `Standards/CHAPTER_ENRICHMENT_GUIDE.md` including its Success Feel statement. Then `Standards/WRITING_PLAN.md` for the intervention map. Check scene cards and dialogue reference for the chapter you're working on BEFORE writing.
