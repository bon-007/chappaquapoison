#!/usr/bin/env python3
"""
Banner Generation — B49–B53 (Final batch)
Chapters read. Scene canon consulted.
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
# B49 — The Coward
# Walsh Sr. portrait through absence. Wealthy dining room, empty chair.
# Car keys on polished table, untouched glass, amber table lamp.
# Scene canon: NO person visible. Vacancy IS the portrait.
# =========================================================================
B49_PROMPTS = {
    "dining_vacancy": (
        "A wealthy suburban dining room at evening. A polished wooden "
        "table with a single place setting — plate, wine glass half full "
        "but untouched, cloth napkin. The chair is pushed back and empty. "
        "A warm amber table lamp illuminates the setting. Through the "
        "window behind, cool blue evening sky. Car keys sit on the "
        "table beside the glass. The occupant has left the room."
    ),
    "empty_chair": (
        "A single upholstered dining chair at the head of a long "
        "polished wooden table in a wealthy home. The chair is empty. "
        "A warm amber lamp casts light across the polished surface. "
        "An untouched glass of wine stands on the table. Through tall "
        "windows, cool evening blue. The chair faces the viewer. "
        "The absence is the portrait. Cowardice as vacancy."
    ),
    "keys_table": (
        "Close-up of a polished wooden table surface in warm amber "
        "lamplight. A set of car keys lies on the polished wood beside "
        "an untouched wine glass. The reflection of the lamp glows in "
        "the wood grain. Beyond the table edge, an empty chair is "
        "visible, pushed back. Cool evening blue through a window "
        "in the background. The keys are the departure made physical."
    ),
}

# =========================================================================
# B50 — The Demand
# Conditioned contact via text. Phone screen as only light.
# Dark room. Cool blue-white phone glow. No faces. No readable text.
# Scene canon: phone screen IS the character. Transaction as cruelty.
# =========================================================================
B50_PROMPTS = {
    "phone_dark": (
        "A phone lying face-up on a dark surface in a completely dark "
        "room. The screen glows cool blue-white, illuminating the "
        "surface beneath it and a small radius around it. The screen "
        "shows a message thread — green and gray bubbles visible but "
        "not readable. Nothing else is visible in the room. The phone "
        "glow is the only light. A demand delivered in the dark."
    ),
    "screen_glow": (
        "A dark room where the only light comes from a phone screen "
        "lying on a nightstand beside a bed. The cool blue-white glow "
        "illuminates the edge of the nightstand and casts shadows. "
        "The screen is angled away so the content is not visible, "
        "just the glow. Complete darkness everywhere else. The cold "
        "light of conditions attached to a child."
    ),
    "message_void": (
        "A phone held in a hand in a dark room, screen facing toward "
        "the viewer. The screen glows blue-white showing message "
        "bubbles in green and gray — no readable words. The hand is "
        "anonymous, seen from behind. The phone light illuminates "
        "only the fingers holding it. Everything else is black. "
        "Contact reduced to transaction. Love weaponized as leverage."
    ),
}

# =========================================================================
# B51 — For Evie
# Warm house interior. Afternoon light through windows. Open door to
# prepared child's room. Shoes by door. The warmest banner.
# Scene canon: domestic warmth, lived-in, NOT institutional.
# Evening Light state: PRESENT.
# =========================================================================
B51_PROMPTS = {
    "house_light": (
        "Interior of a lived-in house on a quiet street. Warm afternoon "
        "golden light streams through front windows, falling across "
        "hardwood floors and a worn rug. Shoes sit by the front door. "
        "Mail on a small table. Bookshelves line one wall with red-spined "
        "bound volumes. Up a staircase visible in the background, a "
        "door is open with warm light beyond it. A home waiting."
    ),
    "open_door": (
        "Looking up a staircase in a warm house interior. At the top "
        "of the stairs, a bedroom door stands open. Warm afternoon "
        "golden light spills through the open doorway. The walls of "
        "the stairwell show framed photographs — small, their content "
        "not visible. Hardwood steps. A worn runner on the stairs. "
        "The room at the top is prepared for someone who has not arrived."
    ),
    "window_warmth": (
        "A living room interior with afternoon golden light pouring "
        "through large front windows. The light falls across a "
        "comfortable couch, a bookshelf with red-spined volumes, "
        "and hardwood floors with a worn rug. A baby toy sits on "
        "the floor near the couch. The room feels lived-in, warm, "
        "real. Not staged. The first purely domestic light in the story."
    ),
}

# =========================================================================
# B52 — Where Are They Now
# Split composition: institutional corridor (unchanged) on one side,
# federal workspace with desk lamp on the other.
# Fluorescent gray vs. warm amber working light.
# =========================================================================
B52_PROMPTS = {
    "split_light": (
        "A composition split down the middle. On the left, an "
        "institutional corridor stretches into distance under "
        "fluorescent light — gray walls, marble floor, empty, "
        "unchanged. On the right, a warm desk lamp illuminates "
        "a workspace with court filings, a pen, and a coffee mug. "
        "The two halves share a horizon line but different light. "
        "One system unchanged. One system building accountability."
    ),
    "corridor_desk": (
        "A long institutional corridor with fluorescent lighting "
        "stretching into distance on the left side of the frame. "
        "On the right, visible through an open doorway, a small "
        "office with a warm desk lamp illuminating papers and "
        "documents on a wooden desk. The corridor is gray and empty. "
        "The office is warm and working. The system that failed and "
        "the work that continues despite it."
    ),
    "federal_workspace": (
        "A wooden desk under a warm desk lamp at night. Court filings "
        "and papers spread across the surface. A pen rests on an open "
        "folder. A coffee mug sits at the edge. Through a window "
        "behind the desk, night sky. On the wall, a single framed "
        "photograph too small to see. The workspace of accountability. "
        "The federal case being built after every other system failed."
    ),
}

# =========================================================================
# B53 — Back Cover
# Single blue hair clip on dark surface. Maximum minimalism.
# Evening Gold directional light catching Ribbon Blue.
# The smallest object carrying the weight of eight years.
# Scene canon: NO people, NO institutional architecture.
# =========================================================================
B53_PROMPTS = {
    "blue_clip": (
        "A single small blue hair clip lying on a dark surface. Warm "
        "golden directional light from the left catches the clip, "
        "making it glow against the darkness. The surface is dark "
        "wood or dark fabric. Deep shadow on the right side. Nothing "
        "else in the frame — just the clip, the light, and the dark. "
        "The smallest object holding the weight of everything."
    ),
    "clip_light": (
        "Close-up of a tiny blue ribbon hair clip on a polished dark "
        "wooden surface. A single beam of warm evening golden light "
        "falls from the upper left, illuminating the clip and the "
        "wood grain beneath it. The rest of the frame is deep shadow. "
        "The clip catches the light and holds it. Ribbon blue against "
        "lampblack. The child as artifact. The evidence that remains."
    ),
    "dark_surface": (
        "A dark wooden desk surface seen from above. In the center, "
        "a small blue hair clip sits alone. Warm directional light "
        "from one side creates a long shadow from the clip across "
        "the dark surface. The light is warm gold. The shadow is "
        "long. Nothing else is on the surface. The record reduced "
        "to its smallest and most essential element."
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


ALL = {
    "B49": B49_PROMPTS,
    "B50": B50_PROMPTS,
    "B51": B51_PROMPTS,
    "B52": B52_PROMPTS,
    "B53": B53_PROMPTS,
}

if __name__ == "__main__":
    print("=" * 60)
    print("Banner Generation — B49–B53 (FINAL BATCH)")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Output: {OUTPUT_DIR}")
    print("=" * 60)

    ok = 0
    fail = 0
    for banner_id, prompts in ALL.items():
        print(f"\n{'='*60}")
        print(f"  {banner_id}")
        print(f"{'='*60}")
        for vname, prompt_text in prompts.items():
            wc = len((prompt_text + SUFFIX_D2).split())
            print(f"\n  [{vname}] ({wc} words)")
            out = OUTPUT_DIR / f"{banner_id}_{vname}.png"
            res = generate_image(prompt_text, out)
            if "error" in res:
                print(f"    ERROR: {res['error']}")
                fail += 1
            else:
                print(f"    OK: {res['size_kb']:.0f} KB")
                ok += 1

    print(f"\nDone — {ok} OK, {fail} failed out of 15")
