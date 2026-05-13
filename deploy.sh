#!/bin/bash
# deploy.sh — Rebuild the site and prepare _site/ for Cloudflare Pages deployment
#
# Usage:
#   ./deploy.sh          # Rebuild _site/
#   ./deploy.sh --zip    # Rebuild and create a deployment zip
#
# Cloudflare Pages settings:
#   Build command: (none — static site)
#   Build output directory: _site
#   OR run this script as the build command: bash deploy.sh

set -e

echo "═══════════════════════════════════════════"
echo "  Chappaqua Poison — Site Build & Deploy"
echo "═══════════════════════════════════════════"
echo ""

# 1. Run the build
echo "→ Running build_html.py..."
python3 scripts/build_html.py

# 2. Verify Evidence/ was copied into _site/
if [ ! -d "_site/Evidence" ]; then
    echo "⚠ _site/Evidence/ missing — build script should copy it"
    echo "  (The build copies Evidence/ into _site/ automatically)"
    exit 1
fi

# 3. Remove full deposition videos from _site/ (too large for GitHub/Cloudflare)
echo ""
echo "→ Removing full deposition videos from _site/ (>100 MB each)..."
for f in _site/Evidence/media/video/ExMM_0{1,2,3,4}_*; do
    if [ -f "$f" ]; then
        echo "  Removed: $(basename "$f") ($(du -h "$f" | cut -f1))"
        rm "$f"
    fi
done

# 4. Verify no files exceed 100 MB
echo ""
echo "→ Checking for oversized files..."
oversized=$(find _site/ -type f -size +100M 2>/dev/null)
if [ -n "$oversized" ]; then
    echo "⚠ WARNING: Files over 100 MB found in _site/:"
    echo "$oversized"
else
    echo "  ✓ No files over 100 MB"
fi

# 5. Report size
echo ""
echo "→ Final _site/ size: $(du -sh _site/ | cut -f1)"
echo "  Files: $(find _site/ -type f | wc -l)"
echo ""

# 6. Optional: create zip
if [ "$1" = "--zip" ]; then
    ZIPNAME="chappaqua-poison-deploy-$(date +%Y%m%d).zip"
    echo "→ Creating deployment zip: $ZIPNAME"
    cd _site && zip -r "../$ZIPNAME" . -x "*.DS_Store" && cd ..
    echo "  ✓ Created: $ZIPNAME ($(du -h "$ZIPNAME" | cut -f1))"
fi

echo ""
echo "═══════════════════════════════════════════"
echo "  ✓ Build complete — _site/ ready to deploy"
echo "═══════════════════════════════════════════"
