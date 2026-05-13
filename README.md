# ChappaquaPoison v3 — Quick Reference

**Read `ORIENTATION.md` for full context. Read `Indexes/CORE_NARRATIVES.md` before any editing.**

## Folder Map

| Folder | What's In It | When to Use |
|--------|-------------|-------------|
| **Indexes/** | 12 core reference docs (characters, places, evidence, narratives, posts, timeline) | Before editing any post or index |
| **Standards/** | 6 writing/quality rules (voice, revision, evidence style, thematic) | Before any prose editing |
| **Process/** | 7 tracking files (status, hunt logs, convergence, audit) | To check progress or history |
| **Planning/** | 10 planning docs (ending architecture, interior moments, book editorial notes) | When planning new work |
| **posts/** | Blog markdown source files (posts/md/) | When editing or reading post content |
| **scripts/** | Build pipeline (build_html.py is main) | When rebuilding the site |
| **Evidence/** | 270 curated evidence files | When verifying evidence |
| **Archive/** | Old skill versions, backups, historical reports | Only for archaeology |

## Session Startup Checklist

1. Read `ORIENTATION.md`
2. Read `Indexes/CORE_NARRATIVES.md`
3. Read `Indexes/V3_THEMATIC_MEMORY.md`
4. Check `Process/STATUS_REPORT.md` for current state
5. Check `Process/FOUNDATION_STATUS.md` for known issues

## Build

```bash
make all                          # Full rebuild
python3 scripts/build_html.py     # Just HTML
```

## Current State (March 2026)

- 51 chapters (B00-B51, no B13), including B41 Less Than Genuine and B42 The Kidnapping Case
- All chapters written, voice-enriched, and deployed
- Evidence integration complete (2,181 entries in canonical index)
- posts.json is the single source of truth
