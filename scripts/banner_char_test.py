#!/usr/bin/env python3
"""
Banner Character Test — Session 181
Goal: Test the winning D suffix on scenes WITH characters.
Verify: simplified forms, small oval eyes, correct hair colors, proper silhouettes.

Three test scenes:
  1. Steve alone (B08-style: man with phone, ultrasound moment)
  2. Tara on boat (B02-style: blonde woman, corrected from old brunette error)
  3. Family group (B04-style: compound scene, multiple characters)
"""
import os
import sys
import json
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
import urllib.request

# Paths
BASE_DIR = Path(__file__).parent.parent
COVER_IMG = BASE_DIR / "Images/cover.png"
HERO_IMG = BASE_DIR / "Images/hero-banner.png"
OUTPUT_DIR = BASE_DIR / "Images/banners/test_session181_chars"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ===========================================================================
# WINNING D SUFFIX (from Session 180 style test)
# ===========================================================================
SUFFIX_D = (
    " Illustrated in the exact style of the attached cover art: bold black pen outlines "
    "over muted dark watercolor, simplified rounded character forms, small oval eyes, "
    "charcoal-navy shadows, oxidized teal midtones, warm amber only as lamplight accents. "
    "Foreground figures graphic and clean, background atmospheric and painterly. "
    "No text, no captions, no logos, no watermarks, no words anywhere in the image."
)

# ===========================================================================
# CHARACTER-FOCUSED SCENE PROMPTS
# ===========================================================================

SCENES = {
    "steve_ultrasound": {
        "label": "Steve alone — ultrasound moment (B08-style)",
        "prompt": (
            "A tall lean man around forty with dark blond hair and light stubble "
            "sits alone on a hospital waiting room chair, holding a phone. "
            "Harsh fluorescent light overhead, teal-green linoleum floor. "
            "His expression is still, looking down at the phone screen. "
            "Empty chairs on either side. A corridor recedes behind him into shadow. "
            "Muted hospital palette, isolated figure, quiet dread."
        ),
    },
    "tara_boat": {
        "label": "Tara on boat — golden hour (B02-style, corrected)",
        "prompt": (
            "An attractive poised woman with shoulder-length blonde hair stands "
            "at the bow of a small sailboat on calm water. Golden late-afternoon sun "
            "backlights her hair. She wears a white linen top. One hand rests on "
            "the railing. Behind her, low green hills and a hazy summer sky. "
            "The light is warm but the water is dark teal beneath the boat. "
            "Composed, confident, sunlit surface hiding deep water."
        ),
    },
    "family_compound": {
        "label": "Family at the compound — group scene (B04-style)",
        "prompt": (
            "A suburban backyard gathering at dusk. A tall lean man with dark blond hair "
            "holds a small blonde girl of about four on his hip — she wears a blue hair clip "
            "and yellow top. An older couple sits at a weathered picnic table nearby. "
            "String lights glow amber overhead. A dark-shingled house looms behind them. "
            "The adults smile but the shadows are long. Fireflies and fading daylight. "
            "Warmth and unease coexisting."
        ),
    },
}

# ===========================================================================
# GENERATION
# ===========================================================================

def generate_scene(scene_key, scene_data, variation_num=1):
    """Generate one image for a character scene with the D suffix."""
    full_prompt = scene_data["prompt"] + SUFFIX_D
    word_count = len(full_prompt.split())
    print(f"\n--- {scene_key} (v{variation_num}) ---")
    print(f"  {scene_data['label']}")
    print(f"  Total prompt: {word_count} words")

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
        output = replicate.run(
            "black-forest-labs/flux-2-pro",
            input=api_input,
        )
        img_url = output[0] if isinstance(output, list) else str(output)

        img_path = OUTPUT_DIR / f"char_{scene_key}_v{variation_num:02d}.png"
        urllib.request.urlretrieve(img_url, str(img_path))
        size_kb = img_path.stat().st_size / 1024
        print(f"  Saved: {img_path.name} ({size_kb:.0f} KB)")
        return str(img_path)
    except Exception as e:
        print(f"  ERROR: {e}")
        return None
    finally:
        for fh in style_refs:
            try:
                fh.close()
            except:
                pass


def main():
    print("=" * 60)
    print("Banner Character Test — Session 181")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Cover style ref: {'YES' if COVER_IMG.exists() else 'MISSING'}")
    print(f"Hero style ref: {'YES' if HERO_IMG.exists() else 'MISSING'}")
    print(f"Suffix: D (cover match)")
    print("=" * 60)

    results = {}
    for scene_key, scene_data in SCENES.items():
        path = generate_scene(scene_key, scene_data)
        if path:
            results[scene_key] = path

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    for name, path in results.items():
        print(f"  {name}: {path}")
    print(f"\nGenerated {len(results)}/{len(SCENES)} character scenes")
    print(f"View results in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
