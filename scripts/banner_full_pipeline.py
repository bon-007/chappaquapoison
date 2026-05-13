#!/usr/bin/env python3
"""
Banner Full Pipeline — Session 181
===================================
For each chapter:
  1. Read the chapter markdown (first 200 lines for key scenes/images)
  2. Look up the scene canon entry
  3. Generate 4 prompt variants with different compositional approaches
  4. Download all 4
  5. Log results for QA review

Refined suffix (D2): Stronger anti-anime eye directives, dot eyes, minimal faces.
"""
import os
import sys
import json
import re
import urllib.request
from pathlib import Path
from datetime import datetime

# Load API token
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    for line in env_path.read_text().strip().split("\n"):
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()

import replicate

# Paths
BASE_DIR = Path(__file__).parent.parent
COVER_IMG = BASE_DIR / "Images/cover.png"
HERO_IMG = BASE_DIR / "Images/hero-banner.png"
OUTPUT_DIR = BASE_DIR / "Images/banners/pipeline_session181"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
WINNERS_DIR = BASE_DIR / "Images/banners/winners_session181"
WINNERS_DIR.mkdir(parents=True, exist_ok=True)

# ===========================================================================
# REFINED D2 SUFFIX — stronger eye/face control
# From House Style Constitution: "small black oval eyes, minimal facial
# features" and "No anime eye logic, no glossy rendering"
# From cover.png observation: eyes are tiny black dots/ovals, no iris detail
# ===========================================================================
SUFFIX_D2 = (
    " Hand-inked suburban-noir storybook illustration in the exact style of the "
    "attached cover art. Bold black pen outlines over muted dark watercolor washes "
    "on visible paper grain. Simplified rounded character forms with tiny black dot "
    "eyes and minimal facial features — no iris detail, no anime eyes, no large "
    "expressive eyes. Charcoal-navy shadows, oxidized teal midtones, warm amber "
    "only as practical lamplight. Foreground figures graphic and clean, background "
    "atmospheric and painterly. Adults must look like adults, not children. "
    "No text, no captions, no logos, no watermarks, no words anywhere in the image."
)

WORD_LIMIT = 145  # Total prompt + suffix should stay under this


def read_chapter_opening(banner_id):
    """Read the first ~150 lines of a chapter to get key scenes and imagery."""
    md_dir = BASE_DIR / "posts/md"
    matches = list(md_dir.glob(f"{banner_id}_*.md"))
    if not matches:
        return None
    text = matches[0].read_text(encoding="utf-8")
    lines = text.split("\n")
    # Return first 150 lines (frontmatter + opening scenes)
    return "\n".join(lines[:150])


def read_scene_canon(banner_id):
    """Extract the scene canon entry for a given banner ID."""
    canon_path = BASE_DIR / "Planning/BANNER_SCENE_CANON.md"
    if not canon_path.exists():
        return None
    text = canon_path.read_text(encoding="utf-8")
    # Find the section for this banner
    pattern = rf"## {banner_id} —.*?\n(.*?)(?=\n## B\d|$)"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(0)
    return None


def generate_image(prompt_text, output_path):
    """Generate a single image via Replicate Flux 2 Pro."""
    full_prompt = prompt_text + SUFFIX_D2
    word_count = len(full_prompt.split())

    style_refs = []
    if COVER_IMG.exists():
        style_refs.append(open(str(COVER_IMG), "rb"))
    if HERO_IMG.exists():
        style_refs.append(open(str(HERO_IMG), "rb"))

    api_input = {
        "prompt": full_prompt,
        "aspect_ratio": "16:9",
        "output_format": "png",
        "output_quality": 95,
        "safety_tolerance": 5,
    }
    if style_refs:
        api_input["input_images"] = style_refs

    try:
        output = replicate.run("black-forest-labs/flux-2-pro", input=api_input)
        img_url = output[0] if isinstance(output, list) else str(output)
        urllib.request.urlretrieve(img_url, str(output_path))
        size_kb = output_path.stat().st_size / 1024
        return {"path": str(output_path), "size_kb": size_kb, "words": word_count}
    except Exception as e:
        return {"error": str(e)}
    finally:
        for fh in style_refs:
            try:
                fh.close()
            except:
                pass


def run_banner(banner_id, prompts_dict):
    """Generate all variants for a single banner."""
    print(f"\n{'='*60}")
    print(f"  {banner_id}")
    print(f"{'='*60}")

    results = {}
    for variant_name, prompt_text in prompts_dict.items():
        word_count = len((prompt_text + SUFFIX_D2).split())
        print(f"\n  [{variant_name}] ({word_count} words)")
        out_path = OUTPUT_DIR / f"{banner_id}_{variant_name}.png"
        result = generate_image(prompt_text, out_path)
        if "error" in result:
            print(f"    ERROR: {result['error']}")
        else:
            print(f"    OK: {result['size_kb']:.0f} KB")
        results[variant_name] = result

    return results


if __name__ == "__main__":
    # Accept banner IDs as command line args, or run all
    if len(sys.argv) > 1:
        banner_ids = sys.argv[1:]
    else:
        print("Usage: python banner_full_pipeline.py B00 B01 B02 ...")
        print("  or:  python banner_full_pipeline.py ALL")
        sys.exit(0)

    print(f"Banner Full Pipeline — Session 181")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Winners: {WINNERS_DIR}")
    print(f"Suffix: D2 (dot eyes, anti-anime)")

    for bid in banner_ids:
        canon = read_scene_canon(bid)
        chapter = read_chapter_opening(bid)
        print(f"\n--- {bid} ---")
        print(f"  Scene canon: {'Found' if canon else 'Missing'}")
        print(f"  Chapter text: {'Found' if chapter else 'Missing'}")
