#!/usr/bin/env python3
"""
Banner Generation — B37–B42
Chapters read. Scene canon consulted. Environmental/still-life compositions.
No identifiable faces. Institutions, documents, and spaces as protagonists.
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
# B37 — Erase, Deactivate, and Delete
# Court orders blog erased, all documentation destroyed. 146 posts.
# Scene canon: laptop screen fading from teal glow to black.
# NO courtroom, NO people. The digital destruction.
# =========================================================================
B37_PROMPTS = {
    "screen_fading": (
        "A laptop computer on a dark desk, its screen the only light source "
        "in the room. The screen glows oxidized teal, fading toward darkness. "
        "The glow illuminates a few stacked printed pages beside the laptop "
        "and the surface of the desk. The room behind is completely dark. "
        "The screen is going dark — the last light of a blog being erased. "
        "The glow reflected on the desk surface fades with it."
    ),
    "books_shelf_dark": (
        "A wooden bookshelf in a dark room holding rows of bound volumes — "
        "thick evidence books with tabs visible between pages. A single "
        "desk lamp illuminates them from the side, casting long shadows. "
        "One book has been pulled halfway out, its spine catching the light. "
        "The rest recede into shadow. An archive ordered into darkness. "
        "One hundred and forty-six posts, bound and shelved and silenced."
    ),
    "cursor_dark": (
        "A dark room with a single glowing laptop screen reflected on a "
        "polished wooden desk surface. The screen casts a pale teal-blue "
        "rectangle of light on the desk. Beside the laptop, a stack of "
        "photographs and printed pages sit in the fading light. The room "
        "is otherwise featureless and black. The moment before the screen "
        "goes dark. Documentation meeting its institutional end."
    ),
}

# =========================================================================
# B38 — Bora Bora
# Steve receives verdict by phone in paradise. Overwater bungalow.
# Mount Otemanu through window. Phone call delivers institutional loss.
# Scene canon: flat ambient daylight, ordinariness against magnitude.
# NO people, NO courtroom, NO dramatic reaction.
# =========================================================================
B38_PROMPTS = {
    "bungalow_phone": (
        "An overwater bungalow interior with teak wood floors and a glass "
        "panel in the floor showing turquoise water below. A phone lies "
        "face-up on the teak surface beside a bed. Through large windows, "
        "a volcanic mountain rises from a turquoise lagoon under pale "
        "afternoon sky. The room is beautiful and empty. The phone is the "
        "only object that connects this place to what is happening elsewhere."
    ),
    "lagoon_window": (
        "A window framing a turquoise tropical lagoon with a dark volcanic "
        "mountain in the distance. Inside the room, a small table holds "
        "a phone and an untouched drink in a glass. The table is teak. "
        "Afternoon light floods in but the room feels still. "
        "Paradise framing loss. The beautiful indifference of a place "
        "that does not know what the phone call contained."
    ),
    "glass_floor": (
        "Looking straight down through a glass floor panel in an overwater "
        "bungalow. Turquoise water is visible below — coral shapes and "
        "small fish. On the glass panel's edge, a phone lies face-down "
        "on the teak floor beside it. Warm afternoon light from a window "
        "casts across the floor. The phone has been set down. "
        "Beneath it, the water continues as if nothing happened."
    ),
}

# =========================================================================
# B39 — Orders as Weapons
# Court orders circulated to journalists, employers, investigators.
# The document becomes the weapon. Journalist threatened by name.
# SFPD investigation closed when order delivered to detective's desk.
# Scene canon: document on desk, office ambient, no faces.
# =========================================================================
B39_PROMPTS = {
    "document_desk": (
        "A court document with an official seal lying on a wooden office "
        "desk. A hand from the edge of the frame slides the document "
        "forward across the desk surface. A desk lamp illuminates the "
        "paper. An envelope lies open beside it. The desk has a coffee "
        "mug and a reporter's notebook. The document is the subject — "
        "institutional protection transformed into a weapon."
    ),
    "envelope_stack": (
        "A desk surface with multiple manila envelopes fanned out, each "
        "one containing identical documents. A single document is pulled "
        "halfway from one envelope, its official seal visible. A desk "
        "lamp lights the scene from one side. The envelopes are addressed "
        "but the addresses are not readable. The mass distribution of "
        "court orders to silence everyone who documented the truth."
    ),
    "detective_desk": (
        "A police detective's desk with a document lying on top of case "
        "files. A desk lamp. A coffee mug. A telephone. On the wall "
        "behind the desk, pamphlets and posters are visible but blurred. "
        "The document sits on top of an open case folder, covering it. "
        "The desk of someone whose investigation was killed by a piece "
        "of paper delivered from across the country."
    ),
}

# =========================================================================
# B40 — We Were Hit
# Brienne Walsh testifies under oath via Zoom deposition from Savannah.
# "We were hit." Camera recording light. Microphone.
# Scene canon: deposition room, fluorescent, red recording light.
# NO family confrontation, NO frightened expression.
# =========================================================================
B40_PROMPTS = {
    "microphone_light": (
        "A microphone on a conference table in an empty deposition room. "
        "Fluorescent light overhead. A water glass beside the microphone. "
        "A legal pad and pen. In the corner, a camera on a tripod with "
        "a small red recording light glowing. The room is clinical, "
        "institutional, beige walls. The microphone waits for testimony. "
        "The red light is already recording."
    ),
    "zoom_screen": (
        "A laptop screen on a conference table showing a video call "
        "interface — a single participant window visible but the face "
        "not detailed, just a silhouette against a bright window. "
        "Fluorescent light in the room. A microphone sits in front of "
        "the laptop. Recording equipment with a red light to the side. "
        "Testimony delivered through technology across state lines."
    ),
    "chair_testimony": (
        "A single chair at a conference table in a deposition room. "
        "The chair faces a camera on a tripod, its red recording light "
        "on. A microphone is centered on the table. A water glass, half "
        "empty. Fluorescent light from above makes everything flat and "
        "clinical. The chair holds the weight of what was said in it. "
        "Three words that confirmed a generational pattern."
    ),
}

# =========================================================================
# B41 — Less Than Genuine
# Four depositions at the Walsh compound. Coached denial.
# "I have no current recollection." Privacy invoked 47 times.
# Gavish slips: "They were aware of it. They were encouraging it, yeah."
# Scene canon: four chairs, three empty, recording equipment, fluorescent.
# =========================================================================
B41_PROMPTS = {
    "four_chairs": (
        "Four chairs arranged at a long conference table in a deposition "
        "room. Three chairs are empty, pushed back slightly from the table. "
        "The fourth chair is pulled forward, occupied only by implication. "
        "A microphone sits on the table. Recording equipment in the "
        "background with a red light on. Fluorescent overhead. "
        "Dark wood beams visible in the ceiling above. Coached silence."
    ),
    "chromebook_empty": (
        "A Chromebook laptop open on a conference table, its screen dark. "
        "No documents beside it — the table is deliberately bare except "
        "for a water glass and the laptop. A camera on a tripod faces "
        "the empty chair behind the table. Red recording light on. "
        "Fluorescent light. Exposed dark beams in the ceiling of a "
        "carriage house. The preparation of a performance."
    ),
    "water_glasses": (
        "A conference table with four water glasses arranged in a row. "
        "Three are full and untouched. The fourth is half empty, a "
        "condensation ring on the table beneath it. A microphone sits "
        "at the center of the table. Fluorescent light overhead. "
        "Dark ceiling beams of an old carriage house above. "
        "Four depositions. One unguarded moment of truth."
    ),
}

# =========================================================================
# B42 — The Kidnapping Case
# Five years of filings. 89 entries. Three rejected defaults.
# Procedural asymmetry as typography. Desk lamp against register.
# Scene canon: court register on desk, highlighted entries, no people.
# =========================================================================
B42_PROMPTS = {
    "register_desk": (
        "A long printed court register unrolled across a wooden desk "
        "under a warm desk lamp. The paper scrolls off both edges of "
        "the desk. A highlighter and pen lie across the paper. "
        "Three sections of the register are marked with yellow highlight. "
        "The rest is dense rows of institutional type. A coffee mug "
        "anchors one corner of the paper. The machinery of five years."
    ),
    "rejection_slips": (
        "Three identical court rejection notices arranged on a dark desk "
        "surface. Each notice is the same size, same format. A desk lamp "
        "illuminates them from one side. A highlighter lies between them. "
        "The repetition is the subject — three attempts, three identical "
        "rejections. The procedural machinery returning the same answer "
        "to three different questions."
    ),
    "filing_weight": (
        "A wooden desk buried under stacked court filings, rejection "
        "notices, and envelopes. A desk lamp illuminates the pile from "
        "one side. The stack is high — years of accumulated paperwork. "
        "A pen lies on top of the topmost filing. Through a window "
        "behind, bare winter trees. The weight of five years of "
        "procedural combat fought alone against institutional machinery."
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
    "B37": B37_PROMPTS,
    "B38": B38_PROMPTS,
    "B39": B39_PROMPTS,
    "B40": B40_PROMPTS,
    "B41": B41_PROMPTS,
    "B42": B42_PROMPTS,
}

if __name__ == "__main__":
    print("=" * 60)
    print("Banner Generation — B37–B42")
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

    print(f"\nDone — {ok} OK, {fail} failed out of 18")
