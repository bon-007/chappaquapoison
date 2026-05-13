#!/usr/bin/env python3
"""
Banner Re-generation — B17 and B18
B17: Completely new prompts based on actual chapter reading.
  Chapter is about the scheme — text threads at midnight, exit clause,
  "pretending" calculation. NOT about the jet ride itself.
B18: Rod-style honing steel in stabbing motion onto phone screen.
  The round tip of the rod creates bullet-hole punctures.
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
# B17 — The Jet (RE-GEN)
# Chapter: NOT about a jet ride. It's about the scheme:
# - Tara's 11 conditions (Rules List) sent to Jesse
# - "I'm better pretending I want to be with him" sent to Matan
# - "Maybe you can kidnap me and Evie" at midnight
# - Walsh Sr. asking for Evie's SSN while Tara is in the cab
# - The exit planned before the entry
# The jet is the instrument of a calculated move, not a family trip.
# =========================================================================
B17_PROMPTS = {
    "teterboro_empty": (
        "A small private jet sits on an empty tarmac at Teterboro Airport "
        "in pale morning light. The stairs are down but no one is boarding. "
        "The jet is white and sleek against gray tarmac. Chain link fence "
        "in the background. A single car parked nearby with its door open. "
        "Cold New Jersey morning, bare trees beyond the fence. "
        "The plane waits. The scheme is already in motion."
    ),
    "midnight_phone": (
        "A phone screen glowing in a dark bedroom at midnight. "
        "The phone lies on rumpled sheets, its screen the only light. "
        "The clock shows very late. A packed suitcase sits on the floor "
        "beside the bed. Through a window, the outline of a suburban "
        "estate is visible against a dark sky. "
        "Plans made at midnight before the morning departure."
    ),
    "rules_list": (
        "A marble kitchen counter with a phone face-up and a legal pad "
        "beside it. The pad has lines of handwriting — a numbered list, "
        "unreadable but structured, eleven items visible. A pen lies across "
        "the pad. A coffee cup sits nearby, cold. Morning light from a window. "
        "The architecture of demands written before an arrival. "
        "Calculated, domestic, the exit clause written first."
    ),
}

# =========================================================================
# B18 — Save This, I've Got Him (RE-GEN)
# The key detail: a rod-style honing steel (knife sharpener) being
# thrust downward in a stabbing motion onto an iPhone screen.
# The round tip of the steel rod creates bullet-hole-like punctures.
# Nine starburst marks on the phone glass.
# =========================================================================
B18_PROMPTS = {
    "steel_stab": (
        "A close-up of a steel knife-sharpening rod being thrust downward "
        "onto an iPhone lying on a wooden kitchen counter. The round tip "
        "of the rod meets the phone screen. Starburst cracks radiate from "
        "the point of impact like bullet holes. The rod is held in a fist "
        "from above in a stabbing grip. Kitchen pendant light overhead. "
        "Violence made domestic. Nine puncture marks on glass."
    ),
    "phone_aftermath": (
        "An iPhone lying on a dark wooden kitchen counter under a pendant "
        "light. The phone screen has nine round puncture marks with "
        "starburst cracks radiating outward — holes made by a pointed rod. "
        "A steel honing rod lies beside the phone, its round tip visible. "
        "The marks look like bullet holes in glass. Kitchen shadows around "
        "the pool of light. Evidence of a deliberate act."
    ),
    "counter_evidence": (
        "A wooden kitchen counter under a single hanging lamp. On the left, "
        "an iPhone with its screen punctured — nine starburst holes in the "
        "glass. On the right, a second phone propped up, screen lit, "
        "photographing something. Between them, a steel honing rod with "
        "a round tip. The lamplight creates a cone of light on the counter. "
        "Everything outside the cone is dark. The evidence factory."
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
    print("Banner Re-gen — B17 + B18")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    all_prompts = {
        "B17": B17_PROMPTS,
        "B18": B18_PROMPTS,
    }

    for banner_id, prompts in all_prompts.items():
        print(f"\n{'='*60}")
        print(f"  {banner_id}")
        print(f"{'='*60}")
        for variant_name, prompt_text in prompts.items():
            word_count = len((prompt_text + SUFFIX_D2).split())
            print(f"\n  [{variant_name}] ({word_count} words)")
            out_path = OUTPUT_DIR / f"{banner_id}_{variant_name}_v2.png"
            result = generate_image(prompt_text, out_path)
            if "error" in result:
                print(f"    ERROR: {result['error']}")
            else:
                print(f"    OK: {result['size_kb']:.0f} KB")

    print("\nDone.")
