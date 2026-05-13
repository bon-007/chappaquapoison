#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "mflux>=0.16.0",
#   "Pillow",
# ]
# ///
"""
generate_banners_local.py — Generate ALL v3 site banners using MFLUX (local Apple Silicon)

Generates hero banner, OG sharing image, and all 49 post banners in one run.
Uses MFLUX (MLX-native FLUX) on Apple Silicon. No API keys, no billing.

Usage:
  uv run scripts/generate_banners_local.py --model schnell --force   # Generate everything (~25 min)
  uv run scripts/generate_banners_local.py --posts B01,B07           # Test specific banners
  uv run scripts/generate_banners_local.py --only hero --force       # Just the hero banner
  uv run scripts/generate_banners_local.py --only og --force         # Just the OG image
  uv run scripts/generate_banners_local.py --dry-run                 # Preview all prompts

Images generated (51+ total):
  1. hero-banner.png        — Homepage hero (800×450)
  2. og-banner.png          — Social sharing image (1200×630)
  3. banners/v3/banner_B##_banner.png — 49 post banners (800×450, B01-B49 excl B13)
"""

import json
import os
import sys
import time
import re
import argparse
import hashlib
from pathlib import Path

# ─── Configuration ─────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
BANNERS_DIR = PROJECT_ROOT / 'Images' / 'banners' / 'v3'
SITE_BANNERS_DIR = PROJECT_ROOT / '_site' / 'images' / 'banners' / 'v3'
IMAGES_DIR = PROJECT_ROOT / '_site' / 'images'
SCENES_FILE = PROJECT_ROOT / 'banner_scenes.json'
POSTS_JSON = PROJECT_ROOT / 'posts.json'

# Banner output size (matched to existing banners)
OUTPUT_WIDTH = 800
OUTPUT_HEIGHT = 450

# Generation size (16:9, larger for quality then downscale)
GEN_WIDTH = 1280
GEN_HEIGHT = 720

# Model configurations
MODEL_CONFIGS = {
    'schnell': {
        'name': 'FLUX.1 Schnell',
        'steps': 4,
        'description': 'Fast generation, 12B params, Apache 2.0 license',
    },
    'dev': {
        'name': 'FLUX.1 Dev',
        'steps': 20,
        'description': 'Higher quality, 12B params, slower',
    },
    'zimage': {
        'name': 'Z-Image Turbo',
        'steps': 9,
        'description': '6B params, fast, good quality',
    },
}
DEFAULT_MODEL = 'schnell'
DEFAULT_QUANTIZE = 8

# ─── Phase Colors & Metadata ──────────────────────────────────────

PHASE_INFO = {
    'I':   {'name': 'Before Tara',    'color': '#A69070'},
    'II':  {'name': 'The Setup',      'color': '#D4A35F'},
    'III': {'name': 'The Crime',      'color': '#B46C4C'},
    'IV':  {'name': 'The Flight',     'color': '#7A8C9A'},
    'V':   {'name': 'The System',     'color': '#4A5568'},
}

# ─── Quality Ranking (worst → best) ──────────────────────────────
# All banners start at score 0 (needs generation).

QUALITY_RANKING = [
    # All 51 v3 posts need generation (B00-B51, no B13)
    'B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09', 'B10',
    'B11', 'B12', 'B14', 'B15', 'B16', 'B17', 'B18', 'B19', 'B20',
    'B21', 'B22', 'B23', 'B24', 'B25', 'B26', 'B27', 'B28', 'B29', 'B30',
    'B31', 'B32', 'B33', 'B34', 'B35', 'B36', 'B37', 'B38', 'B39', 'B40',
    'B41', 'B42', 'B43', 'B44', 'B45', 'B46', 'B47', 'B47a', 'B47b', 'B48', 'B49',
]

QUALITY_SCORES = {pid: 0 for pid in QUALITY_RANKING}

# ─── Accent Color System ─────────────────────────────────────────

ACCENT_COLORS = {
    'evie_blue':    {'prompt': 'vivid sky blue',       'hex': '#4A90D9',
                     'meaning': 'innocence, Evie, what is being fought for'},
    'amber_gold':   {'prompt': 'warm amber gold',      'hex': '#D4A35F',
                     'meaning': 'Steve, warmth, home, fatherhood, hope'},
    'teal_green':   {'prompt': 'bright teal green',    'hex': '#2D9B8A',
                     'meaning': 'truth, evidence, discovery, the water'},
    'danger_red':   {'prompt': 'saturated crimson red', 'hex': '#B46C4C',
                     'meaning': 'Tara, the Walshes, danger, manipulation'},
    'court_violet': {'prompt': 'rich violet purple',    'hex': '#7B68AE',
                     'meaning': 'courts, judges, institutional power, justice'},
}

CHARACTER_ACCENT = {
    'steve':        'amber_gold',
    'evie':         'evie_blue',
    'evie_older':   'evie_blue',
    'tara':         'danger_red',
    'walsh_sr':     'danger_red',
    'maura':        'danger_red',
    'brendan':      'danger_red',
    'brienne':      'amber_gold',
    'nanny':        'evie_blue',
    'doctor':       'teal_green',
    'lawyer':       'court_violet',
    'horowitz':     'court_violet',
}

SCENE_TYPE_ACCENT = {
    'workshop':   'amber_gold',
    'cityscape':  'evie_blue',
    'estate':     'danger_red',
    'hallway':    'court_violet',
    'document':   'teal_green',
    'courtroom':  'court_violet',
    'window':     'amber_gold',
    'hospital':   'teal_green',
    'phone':      'danger_red',
    'kitchen':    'amber_gold',
    'office':     'teal_green',
    'silhouette': 'evie_blue',
    'landscape':  'teal_green',
    'staircase':  'court_violet',
    'archive':    'teal_green',
    'boat':       'amber_gold',
}


def get_scene_accent(scene):
    """Determine the dominant accent color for a scene."""
    characters = scene.get('characters', [])
    primary = None
    secondary = None
    seen = set()
    for char in characters:
        accent = CHARACTER_ACCENT.get(char)
        if accent and accent not in seen:
            if primary is None:
                primary = accent
            elif secondary is None:
                secondary = accent
            seen.add(accent)
    if primary is None:
        scene_type = scene.get('scene_type', 'document')
        primary = SCENE_TYPE_ACCENT.get(scene_type, 'amber_gold')
    return primary, secondary


# ─── Style Description ────────────────────────────────────────────
# CRITICAL: FLUX Schnell T5 encoder has 256 token limit (~1024 chars).
# Prompts beyond this are SILENTLY TRUNCATED.
# Scene description must come FIRST. Style is a short tail anchor.
# Target: total prompt under 200 tokens (~800 chars).

STYLE_TAG = (
    "Dark graphic novel illustration with heavy crosshatching and dense ink linework. "
    "Near-black background, amber-gold glow accents, teal-green secondary color. "
    "Hatched shading on rough dark paper, thick outlines, muted palette. "
    "No text, letters, or words anywhere."
)

# ─── Composition Variety System ─────────────────────────────────

COMPOSITIONS = {
    'center':       'Subject centered in the frame, dark atmosphere surrounding.',
    'left':         'Subject on the left side of frame, open dark space to the right.',
    'right':        'Subject on the right side of frame, dark atmospheric space to the left.',
    'wide':         'Wide establishing shot, subject small in a large atmospheric environment.',
    'close':        'Close-up view filling the frame, intimate and detailed.',
    'low_angle':    'Low angle looking upward, subject looming large, dramatic perspective.',
    'overhead':     'Overhead birds-eye view looking down at the scene below.',
    'symmetrical':  'Symmetrical balanced composition, mirrored elements, centered vanishing point.',
    'diagonal':     'Dynamic diagonal composition, strong perspective lines cutting across the frame.',
    'split':        'Split composition — two distinct halves of the image showing contrast or duality.',
}

# ─── Character Descriptions ──────────────────────────────────────

CHARACTER_DESCRIPTIONS = {
    # SHORT character tags — each under 30 words to preserve token budget for scene
    'steve': 'A tall lean man, ash-blond buzzed hair, rectangular glasses, gray t-shirt, dark jeans. Seen from behind in warm amber silhouette.',
    'tara': 'A blonde woman in a fitted black dress, seen from behind in cool blue silhouette. Composed, still.',
    'evie': 'A tiny blonde toddler in blue overalls with a navy hair bow. The brightest warm element in the frame.',
    'evie_older': 'A small blonde girl age 7 in blue overalls with a navy hair bow, seen from behind. Bright against darkness.',
    'walsh_sr': 'A large man in a charcoal suit, silver hair, seen as a dark imposing silhouette from below.',
    'brienne': 'A slim young woman with dark brown hair in a white blouse, seen from behind, hesitating.',
    'nanny': 'A young dark-haired woman in a navy cardigan, seen from behind in a doorway.',
    'horowitz': 'A judge in dark robes, face in shadow, seen from below behind an elevated bench.',
}

# ─── Scene Type → Visual Description Mapping ─────────────────────

SCENE_DESCRIPTIONS = {
    'workshop':  'A dimly-lit workshop at night, painted in dark watercolor washes. Workbench cluttered with circuit boards and soldering tools under a single amber desk lamp.',
    'cityscape': 'A dark city skyline at twilight across water, painted in ink wash and watercolor. Building silhouettes against a deep indigo sky. Scattered warm amber windows glowing.',
    'estate':    'A white colonial house on a manicured hill at dusk, painted in muted watercolors. Long tree-lined driveway, iron fence. Warm golden light in the windows against a darkening sky.',
    'hallway':   'A long dark hallway with doors on both sides, painted in deep shadow washes. One door ajar with warm golden light spilling across the floor.',
    'document':  'A desk surface at night, painted in tight watercolor focus. Papers with abstract wavy lines stacked under a warm desk lamp. A fountain pen, sealed envelopes.',
    'courtroom': 'A dark courtroom painted in somber earth tones. Elevated judge bench in shadow, rich wooden paneling catching a single shaft of overhead light.',
    'window':    'A dark interior room with a luminous window. Warm golden light streaming through glass panes, curtains half-drawn, dust motes visible in the beam.',
    'hospital':  'A hospital corridor at night, painted in cool blue-white washes. Glossy floor reflecting overhead fluorescents. Clinical emptiness stretching to a vanishing point.',
    'phone':     'A phone screen glowing in darkness, casting a rectangle of colored light onto a surface. The screen shows abstract colored shapes — NO readable text.',
    'kitchen':   'A dark kitchen with a single pendant lamp casting warm golden light onto a counter. Wine bottles and glasses catch the light.',
    'office':    'A workspace at night, painted in contrasting warm and cool light. A computer screen casts blue glow. An amber desk lamp fights the blue.',
    'silhouette':'A figure in silhouette standing in a bright doorway. Warm golden light flooding in from outside.',
    'landscape': 'A landscape at golden hour, painted in expressive watercolor. Dark rolling hills, dramatic layered sky.',
    'archive':   'A records room deep in shadow. Rows of metal filing cabinets receding into darkness. A single overhead light creating a cone of brightness.',
    'boat':      'A boat deck at golden hour on dark water, painted in warm atmospheric washes. Railing in foreground, sunset catching the waves.',
}


def build_prompt(scene, phase_info):
    """Build a prompt for FLUX Schnell image generation.

    CRITICAL CONSTRAINT: T5 encoder limit is 256 tokens (~1024 chars).
    Anything beyond this is SILENTLY TRUNCATED.

    Strategy: Scene FIRST (what to draw), style LAST (how to draw it).
    Target: under 200 tokens total.
    """
    scene_type = scene.get('scene_type', 'document')
    characters = scene.get('characters', [])

    scene_override = scene.get('visual_description', None)
    scene_desc = scene_override if scene_override else SCENE_DESCRIPTIONS.get(scene_type, SCENE_DESCRIPTIONS['document'])

    # === BUILD PROMPT: Scene first, characters second, style last ===
    parts = []

    # 1. SCENE DESCRIPTION — the most important part, goes first
    parts.append(scene_desc.rstrip('.') + '.')

    # 2. CHARACTER — short tag only if characters present
    if characters:
        for char_key in characters:
            desc = CHARACTER_DESCRIPTIONS.get(char_key)
            if desc:
                parts.append(desc)

    # 3. STYLE TAG — short anchor at the end
    parts.append(STYLE_TAG)

    prompt = ' '.join(parts)

    # Warn if over budget
    est_tokens = len(prompt) / 4  # rough estimate
    if est_tokens > 230:
        print(f"  ⚠ WARNING: {scene['post_id']} prompt ~{int(est_tokens)} tokens (limit 256), may be truncated")

    return prompt


def post_id_to_seed(post_id):
    """Generate a deterministic seed from post ID for reproducibility."""
    h = hashlib.md5(post_id.encode()).hexdigest()
    return int(h[:8], 16) % (2**31)


def find_output_filename(post_id):
    """Determine the output filename for a post."""
    raw = post_id.replace('B', '')
    m = re.match(r'^(\d+)(.*)', raw)
    if m:
        num = int(m.group(1))
        suffix = m.group(2)
    else:
        num = 0
        suffix = raw
    padded = f"B{num:02d}{suffix}"
    return f"banner_{padded}_banner.png"


def load_model(model_key, quantize):
    """Load the MFLUX model."""
    print(f"\n  Loading model: {MODEL_CONFIGS[model_key]['name']} (quantize={quantize})...")
    print(f"  (First run will download ~6-12GB of model weights — subsequent runs use cache)")
    print()

    start = time.time()

    if model_key == 'zimage':
        from mflux.models.z_image import ZImage
        from mflux.models.common.config import ModelConfig
        model = ZImage(
            model_config=ModelConfig.z_image_turbo(),
            quantize=quantize,
        )
    elif model_key in ('schnell', 'dev'):
        try:
            from mflux.models.flux1.variants.flux1 import Flux1
            from mflux.models.common.config import ModelConfig
            config = ModelConfig.schnell() if model_key == 'schnell' else ModelConfig.dev()
            model = Flux1(model_config=config, quantize=quantize)
        except ImportError:
            from mflux.models.flux.variants.txt2img.flux import Flux1
            model = Flux1.from_name(model_name=model_key, quantize=quantize)
    else:
        raise ValueError(f"Unknown model: {model_key}")

    elapsed = time.time() - start
    print(f"  ✓ Model loaded in {elapsed:.1f}s")
    return model


def build_hero_prompt():
    """Build the prompt for the homepage hero banner (Evie by the river).
    Scene first, style last. Under 200 tokens."""
    return (
        "A small blonde girl in blue overalls sits alone at the edge of dark water at dusk, "
        "her back to the viewer, facing a vast city skyline across the river. "
        "She has a dark navy hair bow. She is tiny against the enormous dark cityscape. "
        "Amber window lights glow in the distant towers. Dark water reflects faint light. "
        "Wide shot, the child small and alone in the lower third of the frame. "
        f"{STYLE_TAG}"
    )


def build_og_prompt():
    """Build the prompt for the OpenGraph social sharing image.
    Scene first, style last. Under 200 tokens."""
    return (
        "Wide panoramic view of a dark city skyline at dusk across still water. "
        "Building silhouettes with scattered amber window lights against deep indigo sky. "
        "A tiny blonde girl in blue overalls sits at the water's edge in the lower left, small against the vast cityscape. "
        "Dark water reflects faint city lights. "
        f"{STYLE_TAG}"
    )


def generate_single_image(model, prompt, steps, seed, output_width, output_height,
                           gen_width=None, gen_height=None):
    """Generate a single image using MFLUX."""
    import tempfile
    import glob as globmod
    from PIL import Image

    gw = gen_width or GEN_WIDTH
    gh = gen_height or GEN_HEIGHT

    try:
        start = time.time()

        gen_kwargs = dict(
            prompt=prompt,
            seed=seed,
            num_inference_steps=steps,
            width=gw,
            height=gh,
        )

        generated = model.generate_image(**gen_kwargs)
        elapsed = time.time() - start

        tmp_dir = tempfile.mkdtemp(prefix='mflux_')
        save_path = os.path.join(tmp_dir, 'output.png')
        generated.save(path=save_path)

        saved_files = globmod.glob(os.path.join(tmp_dir, '*.png'))
        if not saved_files:
            saved_files = globmod.glob(os.path.join(tmp_dir, '*'))
        if not saved_files:
            generated.save(path=tmp_dir)
            saved_files = globmod.glob(os.path.join(tmp_dir, '*'))
        if not saved_files:
            raise RuntimeError(f"MFLUX save() produced no output files in {tmp_dir}")

        actual_file = saved_files[0]
        pil_img = Image.open(actual_file)
        pil_img.load()

        pil_img = pil_img.resize((output_width, output_height), Image.LANCZOS)

        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)

        print(f"    ✓ Generated in {elapsed:.1f}s (seed={seed})")
        return pil_img

    except Exception as e:
        print(f"    ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Generate all v3 site images locally with MFLUX (Apple Silicon)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --model schnell --force       # Generate ALL images (hero + OG + 49 banners)
  %(prog)s --posts B01,B12,B49           # Test specific banners only
  %(prog)s --only hero                   # Only regenerate hero banner
  %(prog)s --only og                     # Only regenerate OG sharing image
  %(prog)s --only banners                # Only regenerate post banners
  %(prog)s --dry-run                     # Preview all prompts
  %(prog)s -q 4 --force                  # Use 4-bit quantization (less RAM)
        """
    )
    parser.add_argument('--posts', type=str,
                        help='Generate only specific banners (comma-separated, e.g., B01,B12,B49)')
    parser.add_argument('--only', choices=['hero', 'og', 'banners'],
                        help='Generate only one image type (default: all)')
    parser.add_argument('--model', choices=list(MODEL_CONFIGS.keys()), default=DEFAULT_MODEL,
                        help=f'Model to use (default: {DEFAULT_MODEL})')
    parser.add_argument('--dry-run', action='store_true', help='Show prompts without generating')
    parser.add_argument('--force', action='store_true', help='Regenerate even if file exists')
    parser.add_argument('--steps', type=int, default=None,
                        help='Override number of inference steps')
    parser.add_argument('--seed', type=int, default=None,
                        help='Fixed seed for all images (default: deterministic per post)')
    parser.add_argument('-q', '--quantize', type=int, default=DEFAULT_QUANTIZE,
                        choices=[4, 8], help=f'Quantization bits (default: {DEFAULT_QUANTIZE})')

    args = parser.parse_args()

    if args.posts and not args.only:
        args.only = 'banners'

    model_config = MODEL_CONFIGS[args.model]
    steps = args.steps or model_config['steps']

    # ─── Build the job queue ──────────────────────────────────
    jobs = []

    generate_hero = args.only in (None, 'hero')
    generate_og = args.only in (None, 'og')
    generate_banners = args.only in (None, 'banners')

    # --- Hero banner ---
    hero_output = IMAGES_DIR / 'hero-banner.png'
    if generate_hero:
        if args.force or not hero_output.exists():
            jobs.append({
                'label': 'HERO: Homepage banner',
                'prompt': build_hero_prompt(),
                'output_path': hero_output,
                'seed': args.seed or 42,
                'output_w': OUTPUT_WIDTH, 'output_h': OUTPUT_HEIGHT,
            })

    # --- OG sharing image ---
    og_output = IMAGES_DIR / 'og-banner.png'
    if generate_og:
        if args.force or not og_output.exists():
            jobs.append({
                'label': 'OG: Social sharing image (1200×630)',
                'prompt': build_og_prompt(),
                'output_path': og_output,
                'seed': args.seed or 77,
                'output_w': 1200, 'output_h': 630,
                'gen_w': 1280, 'gen_h': 720,
            })

    # --- Post banners (49) ---
    if generate_banners:
        if not SCENES_FILE.exists():
            print(f"\n✗ Scene data not found at {SCENES_FILE}")
            sys.exit(1)

        scenes = json.load(open(SCENES_FILE))
        scene_by_id = {s['post_id']: s for s in scenes}

        if args.posts:
            target_ids = [p.strip() for p in args.posts.split(',')]
        else:
            target_ids = QUALITY_RANKING

        BANNERS_DIR.mkdir(parents=True, exist_ok=True)
        SITE_BANNERS_DIR.mkdir(parents=True, exist_ok=True)

        for pid in target_ids:
            scene = scene_by_id.get(pid)
            if not scene:
                print(f"  ⚠ No scene data for {pid}, skipping")
                continue

            filename = find_output_filename(pid)
            output_path = BANNERS_DIR / filename

            if output_path.exists() and not args.force:
                continue

            score = QUALITY_SCORES.get(pid, '?')
            jobs.append({
                'label': f'{pid} [Q={score}]: {scene["title"]}',
                'prompt': build_prompt(scene, PHASE_INFO),
                'output_path': output_path,
                'seed': args.seed or post_id_to_seed(pid),
                'output_w': OUTPUT_WIDTH, 'output_h': OUTPUT_HEIGHT,
                # Also save to _site for immediate viewing
                'site_path': SITE_BANNERS_DIR / filename,
            })

    # ─── Print header ─────────────────────────────────────────
    print("=" * 60)
    print("  ChappaquaPoison v3 Image Generator (MFLUX / Apple Silicon)")
    print("=" * 60)
    print(f"\n  Model: {model_config['name']}")
    print(f"  Inference steps: {steps}")
    print(f"  Quantization: {args.quantize}-bit")
    print(f"  Output size: {OUTPUT_WIDTH}×{OUTPUT_HEIGHT} (banners/hero)")

    hero_count = sum(1 for j in jobs if j['label'].startswith('HERO'))
    og_count = sum(1 for j in jobs if j['label'].startswith('OG'))
    banner_count = len(jobs) - hero_count - og_count
    print(f"\n  Jobs queued: {len(jobs)} total")
    if hero_count: print(f"    Hero banner: {hero_count}")
    if og_count:   print(f"    OG image:    {og_count}")
    if banner_count: print(f"    Post banners: {banner_count}")

    if not jobs:
        print("\n  ✓ All images already exist. Use --force to regenerate.")
        return

    # ─── Time estimate ────────────────────────────────────────
    est_per_image = {'schnell': 30, 'dev': 120, 'zimage': 140}
    est = est_per_image.get(args.model, 140)
    total_min = (len(jobs) * est) / 60
    total_hrs = total_min / 60
    print(f"\n  Estimated time: ~{est}s/image × {len(jobs)} = ", end='')
    if total_hrs >= 1:
        print(f"~{total_hrs:.1f} hours")
    else:
        print(f"~{total_min:.0f} minutes")

    # ─── Dry run ──────────────────────────────────────────────
    if args.dry_run:
        print(f"\n{'─' * 60}")
        print("  DRY RUN — Showing prompts (no generation)")
        print(f"{'─' * 60}\n")
        for job in jobs[:8]:
            print(f"  [{job['label']}]")
            print(f"  Seed: {job['seed']} | Output: {job['output_path'].name}")
            print(f"  Prompt ({len(job['prompt'])} chars):")
            for line in job['prompt'].strip().split('. '):
                print(f"    {line}.")
            print()
        if len(jobs) > 8:
            print(f"  ... and {len(jobs) - 8} more\n")
        return

    # ─── Load model ───────────────────────────────────────────
    try:
        model = load_model(args.model, args.quantize)
    except ImportError as e:
        print(f"\n✗ MFLUX not installed.")
        print(f"  Error: {e}")
        print(f"\n  Install with: uv tool install --upgrade mflux")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Failed to load model: {e}")
        sys.exit(1)

    # ─── Generate all images ──────────────────────────────────
    print(f"\n{'─' * 60}")
    print(f"  Generating {len(jobs)} images...")
    print(f"{'─' * 60}\n")

    generated = 0
    errors = 0
    total_time = 0

    for i, job in enumerate(jobs):
        print(f"  [{i+1}/{len(jobs)}] {job['label']}")

        start = time.time()

        result = generate_single_image(
            model,
            prompt=job['prompt'],
            steps=steps,
            seed=job['seed'],
            output_width=job['output_w'],
            output_height=job['output_h'],
            gen_width=job.get('gen_w'),
            gen_height=job.get('gen_h'),
        )

        elapsed = time.time() - start
        total_time += elapsed

        if result:
            job['output_path'].parent.mkdir(parents=True, exist_ok=True)
            result.save(str(job['output_path']), 'PNG')
            print(f"    → Saved: {job['output_path'].name}")

            # Also save to _site for immediate viewing
            site_path = job.get('site_path')
            if site_path:
                site_path.parent.mkdir(parents=True, exist_ok=True)
                result.save(str(site_path), 'PNG')
                print(f"    → Also saved to _site/")

            generated += 1
        else:
            errors += 1
            print(f"    ✗ Failed")

        # Progress
        remaining = len(jobs) - (i + 1)
        if remaining > 0:
            avg = total_time / (i + 1)
            eta_min = (remaining * avg) / 60
            print(f"    ETA: ~{eta_min:.0f} min ({remaining} remaining)")
        print()

    # ─── Summary ──────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"  Generation complete!")
    print(f"  ✓ Generated: {generated}")
    if errors:
        print(f"  ✗ Errors: {errors}")
    print(f"  Total time: {total_time/60:.1f} minutes")
    print(f"\n  Banners saved to: {BANNERS_DIR}")
    print(f"  Also copied to:   {SITE_BANNERS_DIR}")
    print(f"\n  Next: python3 scripts/build_html.py")
    print(f"        Then open _site/index.html to review")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
