#!/usr/bin/env python3
"""
Banner Generation — B31–B36
Read all chapters + scene canon. Environmental/still-life compositions.
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
# B31 — The Reno Bottle
# Chapter: Wine bottle from SF liquor cabinet opened in Reno apartment.
# Steve and Kelly both become severely ill. Lab results: mycophenolic acid.
# Kelly loses her pregnancy. Desert afternoon light, sparse apartment.
# =========================================================================
B31_PROMPTS = {
    "bottle_shadow": (
        "A single green glass wine bottle standing on a bare kitchen counter "
        "in a sparse apartment. Desert afternoon light streams through a "
        "window, casting the bottle's long shadow across the counter. "
        "Two empty wine glasses beside it. The counter is bare otherwise. "
        "Reno dry light, bone-white and dusty amber. The bottle as "
        "evidence. The poison delivered in vintage glass."
    ),
    "two_glasses": (
        "Two wine glasses on a glass table in a sparse apartment. "
        "One glass has red wine remaining, the other is empty. Desert "
        "light comes through blinds, casting horizontal stripes across "
        "the table. A green wine bottle stands between them, opened. "
        "The scene is quiet, domestic, the moment before the body "
        "recognizes what the wine contained."
    ),
    "cabinet_reno": (
        "A small liquor cabinet in a sparse apartment, its door open. "
        "Inside, a few bottles of wine from a previous life. One bottle "
        "is missing from the row, its absence marked by a gap. "
        "Dry desert light through a nearby window. The cabinet carried "
        "from San Francisco to Reno. What traveled with it was invisible."
    ),
}

# =========================================================================
# B32 — The Default (Five O'Clock)
# Chapter: Airport gate, 5 PM, phone shows court denial. Overnight red-eye.
# Kelly in surgery in SF. Judge enters default next day granting permanent
# custody and 5-year protection order.
# =========================================================================
B32_PROMPTS = {
    "airport_gate": (
        "An airport terminal gate at night. Rows of empty seats, "
        "a large window looking out onto a dark tarmac with a plane. "
        "Fluorescent overhead light, cold and flat. A single carry-on bag "
        "sits on a seat. A phone lies face-up on the seat beside it, "
        "its screen glowing with a notification. The particular solitude "
        "of a person about to board a red-eye alone."
    ),
    "departure_board": (
        "An airport departure board seen from below, amber digits showing "
        "flight times against black. A figure stands beneath it, seen from "
        "behind, small against the board's scale. A carry-on bag hangs "
        "from one hand. The terminal is mostly empty — late evening. "
        "Fluorescent light makes everything clinical. "
        "The moment before an overnight flight east."
    ),
    "window_tarmac": (
        "Floor-to-ceiling airport windows looking out onto a tarmac at "
        "night. A plane is being loaded, its interior lights glowing. "
        "Inside the terminal, a phone lies on the armrest of a seat, "
        "screen illuminated. A carry-on bag on the floor. "
        "No people visible. The gate area is empty except for the bag "
        "and the phone. Night departure. Five o'clock denial."
    ),
}

# =========================================================================
# B33 — The Double Default
# Chapter: Tara fails to appear twice at evidentiary hearing.
# Empty defendant bench. Judge announces rule but doesn't apply it.
# Then recuses himself. The institutional vacancy.
# =========================================================================
B33_PROMPTS = {
    "empty_bench": (
        "An empty wooden bench in a family courtroom. The bench where "
        "the defendant and her attorneys should sit is vacant. "
        "Fluorescent light overhead. A judge's elevated bench is visible "
        "in the background, distant. A court reporter's desk with "
        "recording equipment sits to one side. The emptiness is the "
        "subject — the absence that the court chose not to punish."
    ),
    "courtroom_vacancy": (
        "A family courtroom seen from the back of the room. Rows of "
        "wooden benches, all empty. The judge's bench at the front is "
        "elevated and dark. A window casts a pattern of light across "
        "the empty floor. The American flag stands in the corner. "
        "The room is ready for a hearing that no one came to. "
        "Institutional, fluorescent, silent."
    ),
    "nameplate_empty": (
        "A courtroom table with a nameplate holder, empty — no name card "
        "inserted. A legal pad and pen sit untouched. The chair behind "
        "the table is pushed back, as though someone was expected but "
        "never arrived. Fluorescent light. Wood paneling. "
        "The seat of the person who defaulted twice and paid nothing."
    ),
}

# =========================================================================
# B34 — Four Discoveries
# Chapter: Synthesis of four poisoning discoveries across four years.
# Lithium (2017), Seroquel (2018), Abby's confession (2018),
# Reno wine / mycophenolic acid (2020). The single pattern revealed.
# =========================================================================
B34_PROMPTS = {
    "forensic_still_life": (
        "Four objects arranged on a dark surface under clinical overhead "
        "light. An amber medical vial. A white pill bottle. A wine glass "
        "with residue. A laboratory test strip. Each object is lit "
        "individually, casting its own shadow. The dark surface between "
        "them connects the evidence. Four discoveries across four years. "
        "The pattern made visible in arrangement."
    ),
    "four_specimens": (
        "A dark laboratory table with four items in a row, each under "
        "its own cone of light: an amber vial, a crushed white tablet, "
        "a small specimen container, and a fragment of a green wine "
        "bottle. The spaces between them are dark. The arrangement is "
        "deliberate, forensic, each item a different year's discovery. "
        "Evidence timeline on a table."
    ),
    "timeline_desk": (
        "A desk lamp illuminates four photographs arranged in "
        "chronological order on a dark desk. Each photograph shows a "
        "different piece of evidence — a medical test, a pill bottle, "
        "a wine bottle, a lab report. The photographs are connected by "
        "a single line drawn between them on the desk surface. "
        "The pattern that took four years to see."
    ),
}

# =========================================================================
# B35 — Equal Threats
# Chapter: Judge Schauer vacates default but issues mutual temporary
# orders against BOTH Steve and Tara — treating poisoner and poisoned
# as symmetrical threats. Two identical documents.
# =========================================================================
B35_PROMPTS = {
    "two_orders": (
        "Two identical documents placed side by side on a courtroom bench. "
        "The papers are the same size, same format, mirror images of "
        "each other. Fluorescent light from above makes them flat and "
        "clinical. The bench is dark wood. The symmetry of the documents "
        "is the subject — two equal restraining orders, one for the "
        "poisoner, one for the poisoned."
    ),
    "glass_partition": (
        "A courtroom seen through a glass partition. On the other side "
        "of the glass, an empty judge's bench and two tables. The glass "
        "reflects a ghostly silhouette of a man standing on this side, "
        "looking through. Fluorescent light makes the reflection faint. "
        "The partition between a father and the court that treats him "
        "as an equal threat to the woman who poisoned him."
    ),
    "balance_scale": (
        "A brass balance scale on a courtroom desk, both pans level, "
        "each holding an identical folded document. The scale is perfectly "
        "balanced. Behind it, an empty courtroom stretches to a distant "
        "judge's bench. Fluorescent overhead. The false symmetry of "
        "justice that weighs a poisoner and her victim on the same scale."
    ),
}

# =========================================================================
# B36 — Grandma's Letter
# Chapter: Linda Russell drives 13 hours from Pennsylvania to Chappaqua.
# Walsh Sr. turns her away at door. She persists. Gets visits. Writes
# letter to Judge Schauer about what she observed.
# Winter, rural Pennsylvania Interstate 80, long drive.
# =========================================================================
B36_PROMPTS = {
    "highway_winter": (
        "A long straight highway stretching into the distance through "
        "a winter Pennsylvania landscape. Bare trees line both sides. "
        "A single car drives toward the vanishing point. Pale winter "
        "morning light, gold and cold. The road is empty except for "
        "the one car. Thirteen hours ahead. A grandmother driving "
        "to see her granddaughter."
    ),
    "steering_wheel": (
        "A car interior seen from the passenger side. An elderly woman's "
        "hands grip the steering wheel, seen from behind. Through the "
        "windshield, a winter highway stretches ahead with bare trees "
        "and pale morning light. The dashboard clock is not readable. "
        "The rearview mirror shows the road behind, already long. "
        "Six and a half hours each way. A retired nurse's steady hands."
    ),
    "door_turned_away": (
        "The front door of a large suburban estate in Chappaqua. "
        "The door is closed. A woman stands on the front step, seen from "
        "behind, her coat pulled tight against the cold. The house is "
        "stone and timber, expensive, quiet. The door has been closed "
        "in her face. She has not turned to leave. Winter afternoon "
        "light. The persistence of a grandmother."
    ),
}


def generate_image(prompt_text, output_path):
    full_prompt = prompt_text + SUFFIX_D2
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
        return {"path": str(output_path), "size_kb": size_kb}
    except Exception as e:
        return {"error": str(e)}
    finally:
        for fh in style_refs:
            try: fh.close()
            except: pass


ALL = {"B31": B31_PROMPTS, "B32": B32_PROMPTS, "B33": B33_PROMPTS,
       "B34": B34_PROMPTS, "B35": B35_PROMPTS, "B36": B36_PROMPTS}

if __name__ == "__main__":
    print(f"B31-B36 Generation — {datetime.now():%Y-%m-%d %H:%M}")
    ok = fail = 0
    for bid, prompts in ALL.items():
        print(f"\n  {bid}")
        for vn, pt in prompts.items():
            wc = len((pt + SUFFIX_D2).split())
            print(f"    [{vn}] ({wc}w) ", end="", flush=True)
            r = generate_image(pt, OUTPUT_DIR / f"{bid}_{vn}.png")
            if "error" in r:
                print(f"ERR: {r['error']}")
                fail += 1
            else:
                print(f"OK {r['size_kb']:.0f}KB")
                ok += 1
    print(f"\nDone — {ok}/{ok+fail}")
