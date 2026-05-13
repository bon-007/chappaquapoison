"""
Generate hero banner image for ChappaquaPoison homepage.
Uses MFLUX with the same style system as post banners.
"""
import sys
import os
from pathlib import Path

# Style anchors — same as banner system
STYLE_PREFIX = (
    "Cinematic concept art keyframe in the style of Cartoon Saloon meets Denis Villeneuve. "
    "Dark atmospheric illustration — deep charcoal and indigo shadows dominate 70% of the frame. "
    "Selective warm amber and cool teal accents punch through the darkness. "
    "Ink wash and watercolor on rough paper — visible brushstrokes, grain, and bleed at edges. "
    "Figures are stylized and angular with expressive body language, seen mostly in silhouette "
    "or partial view. Adult proportions, not childlike. NOT photorealistic, NOT cartoon. "
    "Cinematic depth of field with atmospheric haze. "
    "Every surface is pure painted texture — no readable text, letters, words, numbers, or symbols exist anywhere in this image. "
    "Paper shows abstract brushstroke patterns. Screens glow with soft colored light. "
    "Signs are blank or weathered beyond legibility. "
)

STYLE_SUFFIX = (
    "Palette: charcoal, raw umber, deep indigo, with isolated saturated accents of teal and amber. "
    "Hand-painted quality — the texture of watercolor on cold-press paper, not digital smoothness. "
    "Mood: contemplative, ominous, documentary stillness. "
    "The edges of the image dissolve into pure darkness — heavy vignette, the corners are black. "
    "Every surface in this image is pure visual art with zero typographic elements — "
    "all paper, documents, screens, signs, and labels show only abstract painted marks, "
    "brushstroke patterns, or soft colored glow. No letters, words, or symbol shapes of any kind."
)

EVIE_DESC = (
    "A small girl around age 7 seen from behind. "
    "White-blonde hair past her shoulders with a dark navy hair bow. "
    "Wearing blue overalls over a yellow-green shirt. "
    "Small, quiet, alone. The brightest element in a dark frame."
)

SCENE_DESC = (
    "A small blonde girl sits at the edge of dark water, her back to the viewer, "
    "looking across at a vast city skyline at night. The city is distant and dark — "
    "towers in deep charcoal and indigo with scattered amber window lights. "
    "The water between her and the city is still and black, reflecting faint light. "
    "She sits on stone or concrete at the water's edge, small against the enormous cityscape. "
    "The sky is overcast and dark. She is the only warm thing in the frame."
)

def build_prompt():
    return f"{STYLE_PREFIX} {SCENE_DESC} {EVIE_DESC} {STYLE_SUFFIX}"

def apply_vignette(img):
    """Apply heavy edge darkening so image blends into dark site background."""
    from PIL import Image, ImageFilter, ImageDraw
    import numpy as np
    
    w, h = img.size
    arr = np.array(img).astype(float)
    
    # Create radial gradient mask — center bright, edges dark
    Y, X = np.ogrid[:h, :w]
    cx, cy = w / 2, h / 2
    # Elliptical distance normalized to [0, 1]
    dist = np.sqrt(((X - cx) / (w * 0.55)) ** 2 + ((Y - cy) / (h * 0.50)) ** 2)
    # Smooth falloff: 1.0 at center, 0.0 at edges
    mask = np.clip(1.0 - dist, 0, 1)
    # Make falloff more aggressive at edges
    mask = mask ** 1.5
    # Ensure corners are fully black
    mask = np.clip(mask, 0, 1)
    
    # Apply mask to all channels
    for c in range(3):
        arr[:, :, c] *= mask
    
    return Image.fromarray(arr.astype(np.uint8))

def main():
    dry_run = '--dry-run' in sys.argv
    
    prompt = build_prompt()
    print(f"Hero banner prompt ({len(prompt)} chars):")
    print(prompt[:200] + "...")
    print()
    
    if dry_run:
        print("DRY RUN — no generation")
        return
    
    # Generate at 1280x720 (banner aspect)
    print("Generating hero image with MFLUX...")
    try:
        from mflux import Flux1, Config
    except ImportError:
        print("ERROR: mflux not available. Run on Apple Silicon with mflux installed.")
        sys.exit(1)
    
    flux = Flux1(
        model_alias="schnell",
        quantize=8,
    )
    
    seed = 42  # Fixed seed for reproducibility
    image = flux.generate_image(
        seed=seed,
        prompt=prompt,
        config=Config(
            num_inference_steps=4,
            height=960,
            width=1280,
        ),
    )
    
    from PIL import Image
    pil_img = image.image  # Get PIL image from mflux result
    
    # Apply vignette
    print("Applying edge darkening...")
    pil_img = apply_vignette(pil_img)
    
    # Save full size and resized
    output_dir = Path(__file__).parent.parent / "Images"
    
    full_path = output_dir / "hero-banner-v3-full.png"
    pil_img.save(str(full_path))
    print(f"Saved full: {full_path} ({pil_img.size})")
    
    # Resize to 800 wide
    target_w = 800
    ratio = target_w / pil_img.width
    target_h = int(pil_img.height * ratio)
    resized = pil_img.resize((target_w, target_h), Image.LANCZOS)
    
    banner_path = output_dir / "hero-banner-v3.png"
    resized.save(str(banner_path))
    print(f"Saved banner: {banner_path} ({resized.size})")
    
    print("\nDone. To use as site hero:")
    print(f"  cp {banner_path} {output_dir}/hero-banner.png")

if __name__ == "__main__":
    main()
