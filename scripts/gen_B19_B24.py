#!/usr/bin/env python3
"""
Banner Generation — B19–B24
Read chapters, consulted scene canon and character guides.
Environmental/still-life compositions preferred.
"""
import os
import sys
import json
import urllib.request
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
# B19 — The Leaning Tower
# Chapter: Millennium Tower penthouse, sinking building, floor-to-ceiling
# windows overlooking SF bay, ball rolls on floor, security, George the advisor
# =========================================================================
B19_PROMPTS = {
    "penthouse_windows": (
        "A penthouse apartment at the top of a glass skyscraper. Floor-to-ceiling "
        "windows look out over San Francisco at dusk, bay and fog beyond. A single "
        "tennis ball rests on a hardwood floor, having rolled to the far corner. "
        "Empty modern furniture, marble kitchen island behind. The room tilts almost "
        "imperceptibly. Fog presses against the glass. A man's silhouette stands "
        "at the window, small against the city."
    ),
    "tower_exterior": (
        "A tall glass residential tower in San Francisco SoMa at dusk, "
        "seen from the street. The building leans slightly against its "
        "straight-edged neighbors. Warm amber lobby light glows through "
        "ground-floor glass. Fog rolls in from the bay. A lone figure enters "
        "the lobby past a security desk. Steel, glass, concrete, evening fog. "
        "The lean is subtle but unmistakable."
    ),
    "lobby_security": (
        "A modern glass lobby of a luxury apartment tower at night. Security desk "
        "with a guard, marble floors reflecting overhead light, elevator bank beyond "
        "requiring key cards. A man seen from behind walks toward the elevators "
        "carrying a briefcase. Through the glass walls, San Francisco fog and city "
        "lights. The architecture of controlled access. Sterile, secure, solitary."
    ),
}

# =========================================================================
# B20 — The Niacin Flush
# Chapter: Hotel wine-and-art event, dining table, two women walking past,
# skin flushing red, Tara recording on phone. Hotel second floor, gallery.
# =========================================================================
B20_PROMPTS = {
    "wine_tablecloth": (
        "A still life on a white tablecloth at a hotel dining event. "
        "A glass of red wine, a phone face-down beside it, a napkin folded. "
        "Gallery paintings hang on temporary walls in the blurred background. "
        "Warm brass chandelier light overhead. The wine catches the light "
        "like something dangerous. Formal, controlled, the moment before "
        "something goes wrong."
    ),
    "flushed_hands": (
        "Close-up of two hands gripping the edge of a white tablecloth. "
        "The skin on the hands and forearms is flushed deep red, the flush "
        "spreading visibly. A wine glass stands nearby, half-full. "
        "Hotel dining room blurred behind. Brass fixtures, warm overhead light. "
        "The body reacting to something invisible in the room."
    ),
    "gallery_walk": (
        "A hotel dining room on the second floor, seen from a distance. "
        "White tablecloths, wine glasses, brass chandelier. Through an archway "
        "a gallery space with paintings on temporary walls is visible. "
        "Two silhouetted women walk past in the middle distance. "
        "Evening atmosphere, polished and formal. Something deliberate "
        "hidden inside something social."
    ),
}

# =========================================================================
# B21 — She Asked Me to Put Drugs in Your Wine
# Chapter: Millennium Tower kitchen, early morning, Abby approaches Steve,
# quiet penthouse stillness, the confession that changes everything.
# Scene canon: morning light, counter between them, domestic quiet.
# =========================================================================
B21_PROMPTS = {
    "kitchen_confession": (
        "A penthouse kitchen in early morning light. White marble counter "
        "with two coffee mugs on it. A window behind shows pale coastal sky. "
        "The room is silent and still. One mug is full, the other barely touched. "
        "Morning light falls across the counter in a clean band. "
        "The domestic quiet of a space about to be changed by a sentence."
    ),
    "two_figures_doorway": (
        "Two adults seen from behind through a kitchen doorway in a "
        "modern penthouse. Morning light between them. A woman stands "
        "with her arms at her sides, rigid. A man faces her across "
        "a white marble counter. Through the window behind them, "
        "a park is visible in pale morning light. The silence has weight."
    ),
    "wine_glass_morning": (
        "A single wine glass on a white marble kitchen counter in morning "
        "light. The glass is empty and clean, washed and placed upright. "
        "Morning sun streams through a tall window onto the marble. "
        "Behind the glass, a bottle of wine stands unopened. "
        "The domestic scene carries the weight of what the glass once held. "
        "Quiet, forensic, the morning after knowledge arrives."
    ),
}

# =========================================================================
# B22 — "You Almost Made Me Abandon Our Daughter"
# Chapter: Millennium Tower, dim room, phone glow, Tara's accusatory message,
# everyone carrying the same knowledge, the pretense continuing.
# Scene canon: phone screen glow in dark room, cool blue-white light.
# =========================================================================
B22_PROMPTS = {
    "phone_glow_dark": (
        "A dark penthouse living room at night. A phone screen face-up on "
        "a marble coffee table casts blue-white light onto the ceiling. "
        "Through floor-to-ceiling windows behind, San Francisco city lights "
        "and fog. The phone is the brightest thing in the room. "
        "An armchair beside the table, empty. The message as a cold light "
        "in a dark apartment."
    ),
    "fog_window_phone": (
        "A floor-to-ceiling window in a high-rise apartment at night. "
        "Fog presses against the outside of the glass. City lights glow "
        "faintly below. In the window's reflection, a phone screen glows — "
        "a small bright rectangle reflected in the dark glass. "
        "The room behind is barely visible. Isolation at altitude."
    ),
    "counter_notification": (
        "A kitchen counter in a dim penthouse apartment. A phone lies "
        "face-up, its screen illuminated with a notification. The blue-white "
        "glow lights the marble surface around it. A wine glass stands "
        "beside it, untouched. Through a window, city lights in fog. "
        "The stillness of a room where everyone knows everything "
        "and nothing has changed."
    ),
}

# =========================================================================
# B23 — The Uber (The Airport)
# Chapter: June 4 2018, Tara walks out with Evie, Uber at a bus zone on
# Mission Street, Bryan Crutcher jumps in. Morning SF light. Departure.
# =========================================================================
B23_PROMPTS = {
    "bus_zone_sedan": (
        "A black sedan stopped in a San Francisco bus zone on a bright morning. "
        "The rear door is open. Buses loading and unloading around it. "
        "A tall glass tower rises behind. Morning coastal light, ordinary "
        "city street, pedestrians walking past. The open car door is the only "
        "thing wrong in the frame. Urban, banal, the departure hiding "
        "in plain sight."
    ),
    "mission_street_exit": (
        "The entrance of a modern glass apartment tower on a San Francisco "
        "street. A woman walks away from the lobby carrying an infant, "
        "seen from behind, heading toward a waiting car at the curb. "
        "Morning light, the pale coastal sky of an SF June day. "
        "A security camera's perspective. The ordinary architecture "
        "of an irreversible act."
    ),
    "carseat_backseat": (
        "The back seat of a sedan seen through an open rear door. "
        "An infant car seat is strapped in, a small blanket draped over it. "
        "The city street is reflected in the car window. "
        "Morning light falls across the seat. A bus stop sign is visible "
        "past the door frame. The geometry of a departure."
    ),
}

# =========================================================================
# B24 — Crabtree's Kittle House
# Chapter: First supervised visit, parking lot in Chappaqua, stone-and-timber
# inn, autumn dusk, gravel, bare trees. Steve arrives early. Three months
# since he held Evie.
# Scene canon: autumn dusk, stone inn, parking lot, sodium lamps.
# =========================================================================
B24_PROMPTS = {
    "inn_parking_dusk": (
        "A small parking lot beside a stone-and-timber inn in Chappaqua "
        "at autumn dusk. Bare trees, scattered leaves on gravel. Two cars parked. "
        "Warm sodium lights beginning to glow. The inn is old, two centuries, "
        "set back from the road. Amber light in its windows. "
        "A figure stands alone beside one of the cars, waiting. "
        "Quiet, expectant, the architecture of a supervised visit."
    ),
    "gravel_path": (
        "A gravel path leading to a stone inn surrounded by bare autumn trees. "
        "Golden late-afternoon light filters through branches onto the path. "
        "Fallen leaves in amber and tobacco brown. A man walks toward the inn, "
        "seen from behind, his silhouette small against the old stone building. "
        "Six acres of quiet. Chappaqua dusk. A father arriving early."
    ),
    "inn_window_autumn": (
        "The stone facade of an old New England inn at autumn dusk. "
        "Warm amber light glows from tall windows. A wooden sign hangs "
        "from an iron bracket — no readable text, just a weathered shape. "
        "Bare branches frame the entrance. Gravel drive in foreground. "
        "The fading light of a Westchester October. A place designed "
        "for nothing more contentious than a late reservation."
    ),
}


def generate_image(prompt_text, output_path):
    """Generate a single image via Replicate Flux 2 Pro."""
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


ALL_BANNERS = {
    "B19": B19_PROMPTS,
    "B20": B20_PROMPTS,
    "B21": B21_PROMPTS,
    "B22": B22_PROMPTS,
    "B23": B23_PROMPTS,
    "B24": B24_PROMPTS,
}


if __name__ == "__main__":
    print("=" * 60)
    print("Banner Generation — B19–B24")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Cover ref: {'YES' if COVER_IMG.exists() else 'MISSING'}")
    print(f"Hero ref: {'YES' if HERO_IMG.exists() else 'MISSING'}")
    print("=" * 60)

    results = {}
    for banner_id, prompts in ALL_BANNERS.items():
        print(f"\n{'='*60}")
        print(f"  {banner_id}")
        print(f"{'='*60}")
        results[banner_id] = {}
        for variant_name, prompt_text in prompts.items():
            word_count = len((prompt_text + SUFFIX_D2).split())
            print(f"\n  [{variant_name}] ({word_count} words)")
            out_path = OUTPUT_DIR / f"{banner_id}_{variant_name}.png"
            result = generate_image(prompt_text, out_path)
            if "error" in result:
                print(f"    ERROR: {result['error']}")
            else:
                print(f"    OK: {result['size_kb']:.0f} KB")
            results[banner_id][variant_name] = result

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total = 0
    ok = 0
    for bid, variants in results.items():
        for vname, res in variants.items():
            total += 1
            if "error" not in res:
                ok += 1
                print(f"  {bid}_{vname}: {res['size_kb']:.0f} KB")
            else:
                print(f"  {bid}_{vname}: FAILED — {res['error']}")
    print(f"\nGenerated {ok}/{total} images")
