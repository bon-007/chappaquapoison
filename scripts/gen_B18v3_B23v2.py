#!/usr/bin/env python3
"""
Banner Re-generation — B18 v3 (rage moment) + B23 v2 (tighter environmental)

B18: The moment of rage. A hand gripping a rod-style honing steel,
driving it downward into an iPhone screen. Nine asymmetric puncture
marks — scattered like a mad person made them, NOT symmetrical.
BPD splitting. "Bc Steve turned off the wifi."
The phone was trial evidence — Tara denied it, the jury saw the stab wounds.

B23: The Uber departure. Tighter environmental compositions that avoid
text on buses/signs. The open car door, the glass tower, morning light.
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
# B18 v3 — The Rage Moment
# A hand gripping a steel honing rod (knife sharpener) mid-stab,
# driving it downward onto an iPhone on a kitchen counter.
# The phone screen has scattered asymmetric puncture marks — nine of them,
# randomly placed like a person in uncontrolled rage made them.
# NOT a neat pattern. The violence is in progress, not aftermath.
# =========================================================================
B18_PROMPTS = {
    "rage_stab_v3": (
        "A woman's hand gripping a long steel honing rod high above an iPhone "
        "lying on a dark wooden kitchen counter, mid-swing downward. The rod's "
        "round tip aimed at the phone screen. The screen already has scattered "
        "asymmetric puncture marks — nine holes with starburst cracks, randomly "
        "placed across the glass in a pattern of uncontrolled rage. Under a "
        "single pendant kitchen light. The hand is white-knuckled. Motion blur "
        "on the descending rod."
    ),
    "impact_moment_v3": (
        "Close-up of a steel rod striking an iPhone screen on a wooden counter. "
        "The round tip of the honing steel meets cracked glass. Nine scattered "
        "puncture holes already mark the phone — asymmetric, chaotic, the marks "
        "of someone attacking the device in rage. Starburst fractures radiate "
        "from each hole. A fist clutches the rod handle above. Kitchen pendant "
        "light catches the steel. The violence of a moment. One more strike."
    ),
    "splitting_v3": (
        "An iPhone face-up on a kitchen counter with nine asymmetric puncture "
        "wounds in the glass — scattered chaotically, some close together, some "
        "at the edges, starburst cracks radiating wildly. A steel honing rod "
        "with a round tip rests beside the phone at an angle, as though just "
        "dropped. The rod has a dark handle and a long silver shaft. "
        "Under harsh pendant light. The counter around the phone is scratched "
        "and gouged. Domestic rage frozen in evidence."
    ),
}

# =========================================================================
# B23 v2 — The Uber (The Airport)
# Tighter environmental compositions. Avoid text on buses and signs.
# Focus on: the open car door, the glass tower, morning light,
# the geometry of departure. No people in frame or only silhouettes.
# =========================================================================
B23_PROMPTS = {
    "open_door_tower_v2": (
        "A black sedan parked at a curb in front of a tall glass apartment "
        "tower. The rear passenger door is wide open. Morning coastal light "
        "falls on the car and the tower's glass facade. The sidewalk is empty. "
        "No buses, no signs. Just the open door and the tower and the morning. "
        "The geometry of a departure. San Francisco pale sky."
    ),
    "rearview_mirror_v2": (
        "A view through the windshield of a sedan parked at a city curb. "
        "In the rearview mirror, a glass skyscraper's entrance is visible "
        "receding. Morning fog softens everything. The dashboard is visible "
        "in the foreground. An infant car seat is strapped in the back, "
        "glimpsed in the mirror. The car is about to pull away from the curb. "
        "San Francisco coastal morning, pale and ordinary."
    ),
    "tower_lobby_from_outside_v2": (
        "The glass lobby of a fifty-eight-story apartment tower seen from "
        "outside on a San Francisco morning. Through the glass, the security "
        "desk and elevator bank are visible but empty. On the sidewalk in front, "
        "a single stroller sits abandoned — no one near it. Morning fog diffuses "
        "the light. The lobby glows warm against the cool street. "
        "Something has just left. The absence is the subject."
    ),
}


def generate_image(prompt_text, output_path):
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


if __name__ == "__main__":
    print("=" * 60)
    print("Banner Re-gen — B18 v3 (rage) + B23 v2")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    all_prompts = {"B18": B18_PROMPTS, "B23": B23_PROMPTS}

    for banner_id, prompts in all_prompts.items():
        print(f"\n{'='*60}")
        print(f"  {banner_id}")
        print(f"{'='*60}")
        for variant_name, prompt_text in prompts.items():
            word_count = len((prompt_text + SUFFIX_D2).split())
            print(f"\n  [{variant_name}] ({word_count} words)")
            out_path = OUTPUT_DIR / f"{banner_id}_{variant_name}.png"
            result = generate_image(prompt_text, out_path)
            if "error" in result:
                print(f"    ERROR: {result['error']}")
            else:
                print(f"    OK: {result['size_kb']:.0f} KB")

    print("\nDone.")
