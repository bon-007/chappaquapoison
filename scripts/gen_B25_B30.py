#!/usr/bin/env python3
"""
Banner Generation — B25–B30
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
# B25 — A Special Relationship
# Chapter: Court appoints supervisor Delia Farquharson. She promises integrity.
# Meets privately with Tara before first visit. $250/hr. Has "special
# relationship" with the judge. Handwritten court order.
# Scene canon: Institutional, fluorescent, spare room, clipboard.
# =========================================================================
B25_PROMPTS = {
    "clipboard_room": (
        "An empty supervised visitation room under flat fluorescent light. "
        "A small table with two chairs on one side and one on the other. "
        "A clipboard with papers lies on the table, a pen beside it. "
        "Municipal beige walls, scuffed linoleum floor, a clock on the wall. "
        "The room is cold, institutional, designed for observation. "
        "No people. The architecture of control."
    ),
    "handwritten_order": (
        "A handwritten document on a desk, the looping pen strokes of a "
        "judge's order. A wooden judge's gavel rests beside it. "
        "The ink is dark blue, the paper cream. Fluorescent light "
        "makes the page flat and clinical. A manila folder partially "
        "covers the next page. The machinery of family court — handwritten "
        "restrictions on a father's access to his child."
    ),
    "campaign_poster": (
        "A municipal building hallway — fluorescent lights, linoleum floor, "
        "a bulletin board with posted notices on the wall. A door marked "
        "only by a room number stands ajar, revealing a bare table and "
        "chairs inside. A woman's coat hangs on a hook by the door. "
        "The hallway is empty, institutional, Mount Vernon municipal. "
        "The architecture of backroom deals despite promises of integrity."
    ),
}

# =========================================================================
# B26 — Sixteen Visits
# Chapter: 16 supervised visits, 6 supervisors. Chappaqua cottage with
# playroom: white toy chest, Fisher-Price walker, baby piano, road playmat,
# activity cube. Milly the spaniel. Steve always had food ready.
# Every observer reports: Steve is attentive, Evie is happy.
# Then the visits stop for five months.
# =========================================================================
B26_PROMPTS = {
    "playroom_empty": (
        "A small playroom in a rented cottage. A white toy chest with "
        "stacking rings on top. A Fisher-Price walker, a baby piano, "
        "a road playmat on the floor. An activity cube sits by the window "
        "where afternoon light comes in. A small Cavalier King Charles "
        "spaniel lies on the couch nearby. Everything is set up, waiting. "
        "No child in the frame. The room a father builds for visits."
    ),
    "food_ready": (
        "A kitchen counter in a cream-walled cottage. Green sippy cup, "
        "small containers of yogurt melts, sliced mango, organic vegetable "
        "packets arranged in a row. An orange throw is visible on a sofa "
        "in the next room. A chandelier hangs over the breakfast bar. "
        "Everything prepared. The particular care of a father who cannot "
        "waste a single minute of the hours he is permitted."
    ),
    "sixteen_chairs": (
        "A supervised visitation room at a community center. A folding "
        "table with a clipboard and a pen. On the floor, scattered toys — "
        "blocks, a stuffed giraffe, a sippy cup. A window shows bare "
        "winter trees outside. The room is between institutional and "
        "domestic — trying to be warm, unable to escape fluorescence. "
        "The space where six supervisors all saw the same thing."
    ),
}

# =========================================================================
# B27 — The Bruises
# Chapter: Visit 15. Steve and two adults discover bruises on Evie.
# Both parents report them. Story migrates: concerning → normal → nonexistent.
# Court accepts final version. Months later, Tara's attorney recuses.
# Scene canon: NO visible bruises — "the system made them invisible."
# =========================================================================
B27_PROMPTS = {
    "camera_documenting": (
        "A phone camera held above a small child's dress laid flat on a "
        "table, photographing it. The dress is tiny, with a floral pattern, "
        "placed as though being documented as evidence. A supervisor's "
        "clipboard is visible at the edge of the frame. Fluorescent "
        "overhead light. The clinical precision of a parent who knows "
        "that what he documents will be made to disappear."
    ),
    "three_reports": (
        "Three manila folders on a desk, spread in a row. The first folder "
        "is thick with papers. The second is thinner. The third is empty, "
        "its pages missing. A desk lamp casts warm light across the folders. "
        "The progression is visible — the story migrating from full "
        "to absent. Documentation disappearing in plain sight."
    ),
    "exam_table_empty": (
        "A pediatric examination table in a doctor's office, empty. "
        "A thin paper sheet covers the surface, slightly crumpled. "
        "Overhead fluorescent light. A blood pressure cuff sized for a "
        "toddler hangs on the wall. A stethoscope on the counter. "
        "The room is clinical, prepared for an examination that the "
        "system decided did not need to happen."
    ),
}

# =========================================================================
# B28 — The Ambush
# Chapter: Last supervised visit. September 21 2019. Dark road in Chappaqua,
# no streetlights. Walsh compound gate. A blacked-out SUV parked behind
# bushes. Two men in camouflage (Brendan Walsh and Brian Meenan).
# Steve never sees his daughter again.
# =========================================================================
B28_PROMPTS = {
    "dark_road_suv": (
        "A dark country road at dusk with no streetlights. Dense trees "
        "line both sides. An iron gate is visible at the end of a driveway "
        "climbing uphill. Parked behind bushes on the right, a black SUV "
        "with tinted windows sits with its lights off, barely visible in "
        "the shadows. September canopy still full overhead. The darkness "
        "is total beneath the trees. Chappaqua at nightfall."
    ),
    "gate_closing": (
        "A large electronic iron gate on a Chappaqua estate at dusk, "
        "seen from the road. The gate is closing — halfway shut. "
        "A driveway climbs a quarter mile through dense trees to a "
        "compound at the top of the hill, barely visible. Amber dusk light "
        "fades in the sky above the trees. The gate's metalwork is dark "
        "and heavy. A car's taillights glow red through the closing gap."
    ),
    "headlights_bushes": (
        "A dark suburban road at night. Headlights suddenly illuminate "
        "from behind a row of hedges — a vehicle that was hidden, now "
        "turning on its lights. The beams cut through darkness, catching "
        "the leaves of overhanging trees. A second vehicle is visible on "
        "the road ahead, stopped. No streetlights. The ambush geometry "
        "of a custody exchange turned into something else."
    ),
}

# =========================================================================
# B29 — The Memo
# Chapter: Steve puts it all in one document. Rented house in Westchester,
# winter 2019, bare trees. Sits at table for hours. Nearly 500 pages.
# The act of documentation as resistance.
# Scene canon: desk lamp, pages spread, exhibits, photographs, night.
# =========================================================================
B29_PROMPTS = {
    "desk_evidence": (
        "A desk covered with stacked documents, court filings, printed "
        "photographs, and exhibit pages spread in organized rows. A warm "
        "desk lamp illuminates the papers. A coffee mug sits among the "
        "pages. Through a window behind, bare winter trees and a dark "
        "Westchester night. The labor of making a record when every "
        "institution has declined to look. Nearly five hundred pages."
    ),
    "pages_lamplight": (
        "A man's hands arranging pages on a wooden table under lamplight. "
        "The hands are placing a photograph alongside a printed document. "
        "Stacks of exhibits surround the work area. A legal pad with "
        "handwritten notes is visible. The lamp casts a warm cone of light "
        "against the dark room. Bare tree branches are visible through "
        "a window. Winter. The archive building itself."
    ),
    "table_from_above": (
        "A wooden dining table seen from above, completely covered with "
        "documents. Legal filings, printed text messages, photographs of "
        "a child, court orders, medical records. The papers are organized "
        "into sections with colored tabs. A desk lamp sits at the edge. "
        "An empty coffee mug. The table of someone who believed that if "
        "he arranged the evidence clearly enough, someone would read it."
    ),
}

# =========================================================================
# B30 — Aunt K
# Chapter: Kelly Turnure. Dark hair, straight, with bangs. She built the
# blog (StevieLovesEvie.com), compiled evidence books, wrote letters to
# three judges in three months. She met Evie, became Aunt K.
# Scene canon: Home desk at night, evidence books, laptop, letters, desk lamp.
# Character: Kelly — dark-haired, straight black hair with bangs.
# =========================================================================
B30_PROMPTS = {
    "desk_night": (
        "A woman seen from behind at a home desk late at night. She has "
        "straight dark hair with bangs, silhouetted against a glowing "
        "laptop screen. Stacks of evidence books surround the laptop. "
        "Printed letters are arranged beside the keyboard. A warm desk "
        "lamp on one side, the cool laptop glow on the other. "
        "The archive-tech glow of truth-building. Domestic workspace."
    ),
    "evidence_books": (
        "A desk surface covered with evidence. Three thick evidence books "
        "with numbered tabs and photographs visible between pages. A laptop "
        "screen glows with a blog layout. Printed letters addressed to "
        "judges are stacked beside the books. A pen lies across an open "
        "notebook. Night outside the window. The labor of documentation "
        "as survival. A warm desk lamp lights the work."
    ),
    "letters_stack": (
        "A stack of typed letters on a home desk, each addressed to a "
        "different judge. The paper is crisp. A pen rests on the top "
        "letter. Evidence books with colored tabs stand upright behind "
        "the letters like a wall. A mug of tea, a desk lamp casting "
        "warm amber. Night outside. Three judges. Three months. "
        "The particular persistence of a woman who built the record."
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
    "B25": B25_PROMPTS,
    "B26": B26_PROMPTS,
    "B27": B27_PROMPTS,
    "B28": B28_PROMPTS,
    "B29": B29_PROMPTS,
    "B30": B30_PROMPTS,
}

if __name__ == "__main__":
    print("=" * 60)
    print("Banner Generation — B25–B30")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Output: {OUTPUT_DIR}")
    print("=" * 60)

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
            else:
                print(f"    OK: {res['size_kb']:.0f} KB")

    print("\nDone — 18 images for B25-B30")
