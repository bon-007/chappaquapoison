#!/usr/bin/env python3
"""
Banner Generation — B04 Tara Knoll
Regenerating existing B04 composition in D2 style.
Current banner: Walsh Sr. in dark suit + sunglasses, Maura in dark clothing,
two adopted Korean sisters in matching white dresses, Walsh compound behind at dusk.
Chapter details: house called Tara Knoll, stone and wood, dark inside,
hedgerows ten feet high, seven acres, private drive, Easter dinner.
"""
import os
import urllib.request
from pathlib import Path
from datetime import datetime

env_path = Path(__file__).parent / ".env"
if env_path.exists():
    for line in env_path.read_text().strip().split("\n"):
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()

import replicate

BASE_DIR = Path(__file__).parent.parent
COVER_IMG = BASE_DIR / "Images/cover.png"
HERO_IMG = BASE_DIR / "Images/hero-banner.png"
OUTPUT_DIR = BASE_DIR / "Images/banners/pipeline_session181"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

# =========================================================================
# B04 — Tara Knoll
# Recreating the existing composition in D2 style:
# Walsh Sr. (silver hair, dark suit, dark sunglasses), Maura (gray hair,
# dark conservative clothing), two adopted Korean sisters (dark hair,
# matching white dresses). The Walsh compound behind — stone and wood,
# large, dark, curtains drawn, lamps never bright enough.
# Hedgerows, bare trees, dusk violet sky, ground fog.
# =========================================================================
B04_PROMPTS = {
    "family_compound": (
        "Four people standing on a dark lawn in front of a large stone "
        "and wood colonial house at dusk. Left: an older man with silver "
        "hair in a dark navy suit and dark sunglasses, rigid posture, "
        "hands at his sides. Right: an older woman with gray hair in "
        "dark austere clothing. Center front: two young Korean girls "
        "with straight dark hair in identical white pinafore dresses, "
        "standing close together. The house behind has warm amber "
        "light in windows but curtains partly drawn. Tall hedgerows "
        "ten feet high on both sides. Bare tree branches overhead. "
        "Purple dusk sky. Ground-level fog across the lawn. Rose "
        "bushes at the margins. The scene is formal and unsettling, "
        "wealth performing family."
    ),
    "family_compound_v2": (
        "A formal family group standing before a dark wealthy estate "
        "at evening. An older patriarch with silver hair wearing a "
        "dark suit and dark sunglasses stands stiffly at left. An "
        "older matriarch with gray hair in dark clothing stands at "
        "right. Between them, two young Asian girls in matching white "
        "dresses stand together, small against the adults. Behind "
        "them a large stone and wood house sits at the end of a "
        "curving driveway through old trees. The house is dark "
        "despite lit windows — curtains drawn, lamps dim. Tall "
        "hedgerows frame the property. Purple twilight sky. Low "
        "ground fog. The composition evokes American Gothic — "
        "controlled, prosperous, deeply wrong."
    ),
    "family_compound_v3": (
        "An older man in a dark suit and dark sunglasses with silver "
        "hair stands rigidly beside an older woman in dark conservative "
        "clothing with gray hair. In front of them stand two young "
        "girls with dark hair in identical white pinafore dresses. "
        "All four face the viewer. Behind them, a large dark colonial "
        "house on a hill with amber-lit windows behind drawn curtains. "
        "The driveway curves through tall trees. Hedgerows rise high "
        "on both sides of the property. Purple dusk sky. Ground fog "
        "drifting across the lawn. Rose bushes at the edges of the "
        "frame. The family is posed, controlled, the wealth visible "
        "but the warmth absent."
    ),
}


def generate(tag: str, prompt: str):
    full = prompt + SUFFIX_D2
    out_path = OUTPUT_DIR / f"B04_{tag}.png"
    if out_path.exists():
        print(f"  ⏭  {out_path.name} exists, skipping")
        return

    print(f"\n  ▸ Generating B04_{tag} …")
    cover_uri = open(str(COVER_IMG), "rb")
    hero_uri = open(str(HERO_IMG), "rb")

    try:
        output = replicate.run(
            "black-forest-labs/flux-2-pro",
            input={
                "prompt": full,
                "aspect_ratio": "16:9",
                "output_format": "png",
                "output_quality": 95,
                "safety_tolerance": 5,
                "input_images": [cover_uri, hero_uri],
            },
        )
        url = str(output)
        urllib.request.urlretrieve(url, str(out_path))
        print(f"  ✓ {out_path.name}  ({out_path.stat().st_size // 1024} KB)")
    except Exception as e:
        print(f"  ✗ B04_{tag} failed: {e}")
    finally:
        cover_uri.close()
        hero_uri.close()


if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"  B04 — Tara Knoll — D2 Style Regeneration")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")

    for tag, prompt in B04_PROMPTS.items():
        generate(tag, prompt)

    print(f"\n{'='*60}")
    print(f"  Done. Check {OUTPUT_DIR}/B04_*.png")
    print(f"{'='*60}\n")
