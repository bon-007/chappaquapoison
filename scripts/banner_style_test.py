#!/usr/bin/env python3
"""
Banner Style Test — Session 180
Goal: Find the right style suffix that produces the cover art look
(bold ink outlines, simplified animation forms, dark teal/amber palette)
on Flux 2 Pro.

Test subject: B09 "The Brooklyn Apartment"
Scene direction (from regen plan): Brooklyn apartment doorway from inside —
the door closing, winter street visible through the narrowing gap.
A man's coat on a hook. A bassinet just visible in the dark interior.
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

# Paths
BASE_DIR = Path(__file__).parent.parent
COVER_IMG = BASE_DIR / "Images/cover.png"
HERO_IMG = BASE_DIR / "Images/hero-banner.png"
OUTPUT_DIR = BASE_DIR / "Images/banners/test_session180"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ===========================================================================
# STYLE SUFFIX VARIANTS TO TEST
# ===========================================================================

# Variant A: Explicit ink-outline animation style, dark palette
SUFFIX_A = (
    " Bold ink-outline illustration style matching the Chappaqua Poison book cover: "
    "clean black outlines on all figures and objects, flat muted color fills, "
    "simplified rounded character forms with small dark eyes, "
    "dark charcoal-navy and oxidized teal palette with restrained warm amber accents, "
    "cross-hatching in shadows, paper grain texture. "
    "No text, no captions, no logos, no watermarks, no words anywhere in the image."
)

# Variant B: Animation-forward, referencing the cover directly
SUFFIX_B = (
    " Animated storybook-noir illustration in the style of the Chappaqua Poison cover art: "
    "bold black ink outlines, simplified cartoon character features, muted watercolor washes, "
    "dark palette of charcoal navy and teal with amber only from practical light sources, "
    "deep atmospheric shadows filling forty percent of the frame. "
    "No text, no captions, no logos, no watermarks, no words anywhere in the image."
)

# Variant C: Shorter, more direct
SUFFIX_C = (
    " Dark storybook illustration with bold black ink outlines and flat color fills. "
    "Simplified animated characters with small eyes. Muted charcoal-teal-amber palette. "
    "Paper grain texture, deep shadows. Filling the entire frame edge to edge. "
    "No text, no captions, no logos, no watermarks, no words anywhere in the image."
)

# Variant D: Leaning into the cover comparison explicitly
SUFFIX_D = (
    " Illustrated in the exact style of the attached cover art: bold black pen outlines "
    "over muted dark watercolor, simplified rounded character forms, small oval eyes, "
    "charcoal-navy shadows, oxidized teal midtones, warm amber only as lamplight accents. "
    "Foreground figures graphic and clean, background atmospheric and painterly. "
    "No text, no captions, no logos, no watermarks, no words anywhere in the image."
)

# ===========================================================================
# SCENE PROMPT (short, scene-focused, <80 words)
# ===========================================================================

SCENE_PROMPT = (
    "A Brooklyn apartment doorway seen from inside. The door is closing, "
    "showing a narrow sliver of cold winter street and bare trees outside. "
    "A dark coat hangs on a hook by the door. A wooden bassinet sits in the dim interior, "
    "one small cream blanket visible. Late afternoon winter light through the gap. "
    "The warmth inside trapped, the cold outside encroaching. "
    "No people visible, environmental storytelling."
)

SUFFIXES = {
    "A_ink_outline": SUFFIX_A,
    "B_animation_noir": SUFFIX_B,
    "C_short_direct": SUFFIX_C,
    "D_cover_match": SUFFIX_D,
}


def generate_variant(suffix_name, suffix_text, variation_num=1):
    """Generate one image with the given suffix."""
    full_prompt = SCENE_PROMPT + suffix_text
    word_count = len(full_prompt.split())
    print(f"\n--- {suffix_name} (variation {variation_num}) ---")
    print(f"Total prompt: {word_count} words")

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

        import urllib.request
        img_path = OUTPUT_DIR / f"B09_test_{suffix_name}_v{variation_num:02d}.png"
        urllib.request.urlretrieve(img_url, str(img_path))
        print(f"  Saved: {img_path.name} ({img_path.stat().st_size / 1024:.0f} KB)")
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
    print("Banner Style Test — Session 180")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Cover style ref: {'YES' if COVER_IMG.exists() else 'MISSING'}")
    print(f"Hero style ref: {'YES' if HERO_IMG.exists() else 'MISSING'}")
    print("=" * 60)

    results = {}
    for suffix_name, suffix_text in SUFFIXES.items():
        path = generate_variant(suffix_name, suffix_text)
        if path:
            results[suffix_name] = path

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    for name, path in results.items():
        print(f"  {name}: {path}")
    print(f"\nGenerated {len(results)}/{len(SUFFIXES)} variants")
    print(f"View results in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
