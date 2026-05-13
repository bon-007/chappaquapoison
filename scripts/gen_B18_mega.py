#!/usr/bin/env python3
"""
B18 — Save This, I've Got Him — MEGA VARIANT GENERATION (10 versions)

The scene: Tara is enraged, has lost all control. BPD splitting.
She takes a knife sharpener — a long even rod with a blunt round tip,
like a steel dowel — and stabs it repeatedly into Steve's iPhone screen.
Nine asymmetric puncture marks. The whole phone holds the scars of
her state of mind. This phone was trial evidence.

The sharpener is NOT a block with slots. It's a single long steel rod
with a handle on one end and a blunt round tip on the other.
Think: fencing foil shape but with a round blunt end.

10 different compositional approaches to find the one that works.
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

PROMPTS = {
    # --- STABBING IN PROGRESS variants ---
    "rage_overhead_v4": (
        "A woman's fist raised high above her head, gripping a long thin steel "
        "rod by its dark handle, about to bring it down onto a phone lying on "
        "a kitchen counter. Her body is tense, arm fully extended upward. "
        "The steel rod is straight and even, the length of a forearm, with a "
        "small round blunt tip. The phone screen below already has scattered "
        "puncture marks. Kitchen pendant lamp. Dark shadows. Fury in motion."
    ),
    "downstroke_v4": (
        "A hand driving a long steel rod straight downward in a violent "
        "stabbing motion. The rod is a kitchen honing steel — thin, straight, "
        "with a round blunt tip at the end. The tip is making contact with "
        "a phone screen lying on a dark wooden counter. Impact radiates from "
        "the point of contact. Scattered starburst cracks already cover the "
        "screen. Overhead pendant light catches the steel. Pure rage."
    ),
    "blur_stab_v4": (
        "Motion blur of a steel rod being swung repeatedly at a phone on a "
        "counter. The rod is a long straight kitchen honing steel with a round "
        "tip. Multiple exposures suggest the repeated striking — the rod "
        "appears in several positions at once, blurred with violence. The phone "
        "screen is destroyed — nine asymmetric puncture wounds scattered "
        "across the glass. Kitchen darkness around a single lamp."
    ),
    "fist_grip_v4": (
        "Extreme close-up of a woman's white-knuckled fist gripping the black "
        "handle of a steel honing rod. The rod extends downward out of frame "
        "toward an unseen phone below. Tendons visible in the wrist. The grip "
        "is a stabbing grip — overhand, violent, not a cooking grip. "
        "Dark kitchen behind, pendant light above. The hand of someone who "
        "has lost all control."
    ),

    # --- AFTERMATH with rage energy variants ---
    "scattered_chaos_v4": (
        "An iPhone on a kitchen counter completely destroyed. Nine puncture "
        "holes scattered chaotically across the screen — some clustered in "
        "rage, some flung to the edges, each surrounded by wild starburst "
        "cracks. The pattern is asymmetric, random, the marks of someone "
        "who kept going after the screen was already dead. A long steel "
        "honing rod with a round tip lies beside it, dropped mid-rage. "
        "Pendant light. Scratched wooden counter."
    ),
    "counter_gouged_v4": (
        "A dark kitchen counter covered in scratch marks and gouges "
        "surrounding an iPhone. The phone screen has nine puncture holes "
        "with wild radiating cracks. The counter itself is scarred — long "
        "scratches from the steel rod missing the phone, divots in the wood "
        "where the blunt tip struck beside the device. A steel honing rod "
        "lies at an angle across the scene. The whole surface tells the "
        "story of uncontrolled violence. Pendant lamp overhead."
    ),
    "dropped_rod_v4": (
        "A steel honing rod lying on a kitchen floor, having just been "
        "dropped. The rod is long and straight with a dark handle and round "
        "blunt tip. Above on the counter, an iPhone with nine asymmetric "
        "holes in its screen is visible at the edge of the frame. The rod "
        "on the floor catches the pendant light. Kitchen tile. "
        "The aftermath of a rage that exhausted itself."
    ),
    "phone_face_v4": (
        "Extreme close-up of an iPhone screen with nine puncture marks. "
        "Each mark is a round hole surrounded by radiating starburst cracks. "
        "The holes are scattered wildly — three near the center, two at the "
        "top left, one in the bottom right corner, three along the edge. "
        "No symmetry. The glass between the holes is crazed with fracture "
        "lines. The screen of a phone that someone attacked with a pointed "
        "rod until their arm got tired. Black kitchen behind."
    ),

    # --- ENVIRONMENTAL / NARRATIVE variants ---
    "second_phone_v4": (
        "Two phones on a kitchen counter under pendant light. On the left, "
        "an iPhone with nine wild puncture holes in its screen, destroyed. "
        "On the right, a second phone propped upright, its camera lens "
        "aimed at the destroyed phone — photographing the evidence. Between "
        "them, a long steel honing rod with a round tip and dark handle. "
        "The juxtaposition: destroy, then document. The evidence factory."
    ),
    "wine_rod_phone_v4": (
        "A kitchen counter still life under harsh pendant light. A wine glass "
        "knocked over, red wine pooling. An iPhone with nine asymmetric "
        "puncture holes in its screen. A long steel honing rod with a round "
        "blunt tip lying diagonally across the scene. The wine has spread "
        "to the phone's edge. The domestic wreckage of a moment of complete "
        "loss of control. Charcoal-navy kitchen shadows."
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
    print("B18 MEGA — 10 variants")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    ok = 0
    fail = 0
    for vname, prompt_text in PROMPTS.items():
        wc = len((prompt_text + SUFFIX_D2).split())
        print(f"\n  [{vname}] ({wc} words)")
        out = OUTPUT_DIR / f"B18_{vname}.png"
        res = generate_image(prompt_text, out)
        if "error" in res:
            print(f"    ERROR: {res['error']}")
            fail += 1
        else:
            print(f"    OK: {res['size_kb']:.0f} KB")
            ok += 1

    print(f"\nDone — {ok} OK, {fail} failed out of 10")
