#!/usr/bin/env python3
"""
Banner Generation — B43–B48
Chapters read. Scene canon consulted. Environmental/still-life compositions.
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
# B43 — The Remnant
# Appellate Division strikes gag order as unconstitutional prior restraint.
# A beam of light through a high window falls across a page on a desk.
# Scene canon: NO courtroom, NO judges, NO celebration.
# Light = institutional conscience. Paper Bone + Evening Gold beam.
# =========================================================================
B43_PROMPTS = {
    "light_on_page": (
        "A single beam of golden light falls through a high window onto "
        "a document lying on a dark wooden desk. The beam illuminates "
        "the page and the desk surface around it. The rest of the room "
        "is in deep shadow. A pen rests beside the document. The light "
        "is warm and clarifying, falling from above like institutional "
        "conscience. One moment of correction in a dark room."
    ),
    "opinion_desk": (
        "A desk in a shadowed room with a single bound legal volume "
        "lying open under a shaft of pale golden light from a high "
        "window. The light catches the open pages and the wood grain "
        "of the desk. A reading lamp sits unlit beside the volume. "
        "The beam is narrow and precise, illuminating only the open "
        "book. The rest of the room recedes into charcoal shadow."
    ),
    "window_beam": (
        "A high arched window in a dark institutional room. A single "
        "beam of warm afternoon light streams through, falling across "
        "a desk below where papers lie. The window is the only source "
        "of light. Dust motes float in the beam. The walls are dark "
        "stone or plaster. The light reaches the papers like a verdict "
        "reaching the record. Warm gold against institutional shadow."
    ),
}

# =========================================================================
# B44 — What Twelve People Saw
# Civil battery trial in San Francisco Superior Court. Twelve jurors.
# Natural California courtroom light — warmer than Westchester fluorescent.
# Scene canon: jury box silhouettes, natural light, NO TV drama aesthetic.
# =========================================================================
B44_PROMPTS = {
    "jury_box": (
        "A courtroom jury box with twelve empty wooden chairs arranged "
        "in two rows. Natural light from tall windows on the left fills "
        "the courtroom with warm California afternoon light. The chairs "
        "cast shadows. The witness stand is visible beyond the jury box, "
        "empty. Wood paneling. The warmth of a courtroom where evidence "
        "is tested by strangers with no investment in the outcome."
    ),
    "witness_stand": (
        "An empty wooden witness stand in a California courtroom. "
        "Natural afternoon light falls from tall windows onto the "
        "stand's surface. A microphone on a flexible arm extends "
        "toward the empty chair. Behind it, the jury box is visible "
        "as rows of wooden seats in shadow. The courtroom is quiet, "
        "between sessions. The stand where testimony was finally heard."
    ),
    "courtroom_light": (
        "A California courtroom bathed in natural afternoon light from "
        "tall windows on the left wall. Two counsel tables face the "
        "judge's bench. The jury box is on the right, its chairs in "
        "warm shadow. The light quality is distinct — warmer, more "
        "natural than fluorescent. Wood surfaces glow. The courtroom "
        "where twelve people heard what no family court would examine."
    ),
}

# =========================================================================
# B45 — What the Jury Found
# Verdict form on judge's bench, afternoon light. 11-1 finding of malice.
# Scene canon: NO dramatic announcement, NO jury visible, NO celebration.
# The form itself is the subject. Warmest court scene in the narrative.
# =========================================================================
B45_PROMPTS = {
    "verdict_form": (
        "A single sheet of paper lying on a dark wooden judge's bench "
        "surface. Afternoon light from a tall window falls directly "
        "onto the paper, making it glow warm against the dark wood. "
        "A pen lies beside the form. The bench surface is polished "
        "tobacco brown. The courtroom behind is in soft shadow. "
        "The verdict as an object. The paper that made the record permanent."
    ),
    "bench_light": (
        "A judge's bench in an empty California courtroom. Afternoon "
        "golden light streams through tall windows onto the bench "
        "surface where a folded document sits. The gavel rests beside "
        "it. The courtroom is empty — the verdict has been read and "
        "everyone has gone. The light on the bench is warm, almost "
        "evening gold. The institution at its clearest moment."
    ),
    "form_closeup": (
        "Close-up of a document on a polished dark wooden surface. "
        "Warm afternoon light illuminates the paper from the left. "
        "A pen rests on the paper. The document has checked boxes "
        "visible but the words are not readable. The wood grain of "
        "the bench surface is visible beneath the paper's edge. "
        "The warmest light in any courtroom in this story."
    ),
}

# =========================================================================
# B46 — Affirmed
# Appellate court affirms verdict. Marble corridor, cool and formal.
# The permanence of institutional stone. A hand holding the decision.
# Scene canon: NO courtroom interior, NO celebration, NO dramatic reaction.
# =========================================================================
B46_PROMPTS = {
    "marble_corridor": (
        "A long marble corridor in an appellate courthouse, stretching "
        "into deep perspective. Cool institutional light from overhead "
        "fixtures reflects off polished marble floors. The corridor is "
        "empty. Formal architectural details — stone columns, brass "
        "fixtures. The distance is the subject. The corridor of "
        "institutional finality. Permanence rendered in stone."
    ),
    "hand_document": (
        "A hand seen from behind carries a folded document while walking "
        "down a long marble corridor. The corridor stretches ahead into "
        "distance. Cool overhead light. The hand is anonymous — just a "
        "figure walking away with a decision. Marble walls recede on "
        "both sides. The loneliness of vindication in an empty "
        "institutional corridor. Permanence that changes nothing."
    ),
    "corridor_light": (
        "Looking down a marble appellate courthouse hallway. Cool "
        "overhead light reflects on polished stone floors. At the far "
        "end, a single window lets in afternoon light — a warm rectangle "
        "at the vanishing point against the cool institutional corridor. "
        "The hallway is empty. Formal, distant, the architecture of "
        "appellate finality. The verdict embedded in stone."
    ),
}

# =========================================================================
# B47 — The Record Is Open
# Five archive artifacts on a dark surface under warm desk lamp.
# The archive achieving its final form. Documentation as resistance.
# Scene canon: NO library aesthetic, NO computer screen, NO people.
# =========================================================================
B47_PROMPTS = {
    "five_artifacts": (
        "Five objects arranged on a dark surface under a warm desk lamp. "
        "A red hardbound book with tabs. A stack of printed pages. "
        "A small audio recorder. A thick court filing with colored tabs. "
        "A phone lying face-up with a faint glow. Each object casts its "
        "own shadow. The lamp illuminates them from the left. The dark "
        "surface connects them. Five witnesses that cannot be silenced."
    ),
    "archive_desk": (
        "A dark wooden desk at night with a warm desk lamp illuminating "
        "a careful arrangement. Red-spined evidence books stand upright. "
        "Printed blog pages are stacked beside them. Court filings with "
        "colored tabs fan out across the surface. A small recording device "
        "sits among the papers. Night outside the window. The archive "
        "builder's workspace. Documentation as survival."
    ),
    "red_books": (
        "Three red hardbound books standing upright on a dark desk, "
        "their spines catching warm lamplight. Photographs and printed "
        "documents are visible tucked between their pages as tabs. "
        "A desk lamp illuminates them from one side. The desk surface "
        "is otherwise dark. Behind the books, a window shows night. "
        "The permanent record. Five years bound and shelved and alive."
    ),
}

# =========================================================================
# B48 — The Trap
# Iron gate ajar in deep shadow. Phone face-down with edge glow.
# The mechanism of conditioned contact. Night, deep shadow.
# Scene canon: NO people, NO house exterior, NO daylight.
# Title-safe LEFT third (unique).
# =========================================================================
B48_PROMPTS = {
    "gate_phone": (
        "A narrow iron gate standing slightly ajar in deep shadow. "
        "On the ground before the gate, a phone lies face-down, its "
        "edges glowing faint warm gold from the screen beneath. "
        "The gate bars cast geometric shadows on the floor. A single "
        "overhead light creates harsh shadows through the bars. "
        "Complete darkness beyond the gate. The trap made architectural. "
        "The phone glows with what cannot be reached."
    ),
    "bars_shadow": (
        "Iron gate bars filling the frame, casting long geometric shadows "
        "across a stone floor. Through the bars, darkness. On this side "
        "of the bars, a phone lies face-down on the stone, its screen "
        "edge glowing faint evening gold. A folded document sits wedged "
        "between two bars. Cold iron. Cold stone. The only warmth is "
        "the phone's edge glow — a child's photograph, conditional."
    ),
    "threshold": (
        "A threshold between light and dark. On the left, a narrow space "
        "lit by a single overhead fixture. On the right, iron gate bars "
        "and complete darkness beyond. A phone lies on the threshold "
        "itself, half in light, half in shadow, its screen glow visible "
        "at the edge. The geometric pattern of gate shadows crosses "
        "the lit floor. The architecture of impossible choice."
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
    "B43": B43_PROMPTS,
    "B44": B44_PROMPTS,
    "B45": B45_PROMPTS,
    "B46": B46_PROMPTS,
    "B47": B47_PROMPTS,
    "B48": B48_PROMPTS,
}

if __name__ == "__main__":
    print("=" * 60)
    print("Banner Generation — B43–B48")
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
