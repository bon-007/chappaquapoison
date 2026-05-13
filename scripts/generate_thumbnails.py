#!/usr/bin/env python3
"""Generate thumbnails for evidence items from source PDFs, images, and videos.

⚠ DEPRECATED: This script's data has been absorbed into evidence_index_canonical.json.
To update evidence data, edit directly in canonical and re-run: python3 scripts/build_canonical_evidence_index.py
"""

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EVIDENCE_META = PROJECT_ROOT / "evidence_metadata.json"
THUMB_DIR = PROJECT_ROOT / "Images" / "thumbnails" / "evidence"
THUMB_WIDTH = 120
THUMB_HEIGHT = 80

def ensure_dir():
    THUMB_DIR.mkdir(parents=True, exist_ok=True)

def safe_thumb_name(file_path):
    """Create a safe thumbnail filename from evidence path."""
    # e.g., Evidence/pdf/declarations/ExA_01.pdf -> ExA_01.jpg
    base = Path(file_path).stem
    # sanitize
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in base)
    return f"{safe}.jpg"

def generate_pdf_thumbnail(pdf_path, thumb_path):
    """Extract first page of PDF as thumbnail using pdftoppm."""
    try:
        # pdftoppm outputs to prefix-1.ppm, then convert
        tmp_prefix = str(thumb_path).replace('.jpg', '')
        result = subprocess.run(
            ['pdftoppm', '-jpeg', '-f', '1', '-l', '1',
             '-scale-to-x', str(THUMB_WIDTH * 2), '-scale-to-y', '-1',
             str(pdf_path), tmp_prefix],
            capture_output=True, timeout=10
        )
        # pdftoppm creates tmp_prefix-1.jpg
        candidate = f"{tmp_prefix}-1.jpg"
        if os.path.exists(candidate):
            # Resize to exact thumbnail size
            subprocess.run(
                ['convert', candidate,
                 '-resize', f'{THUMB_WIDTH}x{THUMB_HEIGHT}^',
                 '-gravity', 'North',
                 '-extent', f'{THUMB_WIDTH}x{THUMB_HEIGHT}',
                 '-quality', '75',
                 str(thumb_path)],
                capture_output=True, timeout=10
            )
            os.remove(candidate)
            return os.path.exists(str(thumb_path))
        # Try alternate naming (some versions use -01)
        for suffix in ['-01.jpg', '-1.jpg', '-001.jpg']:
            alt = f"{tmp_prefix}{suffix}"
            if os.path.exists(alt):
                subprocess.run(
                    ['convert', alt,
                     '-resize', f'{THUMB_WIDTH}x{THUMB_HEIGHT}^',
                     '-gravity', 'North',
                     '-extent', f'{THUMB_WIDTH}x{THUMB_HEIGHT}',
                     '-quality', '75',
                     str(thumb_path)],
                    capture_output=True, timeout=10
                )
                os.remove(alt)
                return os.path.exists(str(thumb_path))
        return False
    except Exception as e:
        return False

def generate_image_thumbnail(img_path, thumb_path):
    """Resize image to thumbnail."""
    try:
        subprocess.run(
            ['convert', str(img_path),
             '-resize', f'{THUMB_WIDTH}x{THUMB_HEIGHT}^',
             '-gravity', 'Center',
             '-extent', f'{THUMB_WIDTH}x{THUMB_HEIGHT}',
             '-quality', '75',
             str(thumb_path)],
            capture_output=True, timeout=10
        )
        return os.path.exists(str(thumb_path))
    except:
        return False

def generate_video_thumbnail(video_path, thumb_path):
    """Extract frame from video at 2 seconds."""
    try:
        subprocess.run(
            ['ffmpeg', '-y', '-i', str(video_path),
             '-ss', '2', '-vframes', '1',
             '-vf', f'scale={THUMB_WIDTH}:{THUMB_HEIGHT}:force_original_aspect_ratio=increase,crop={THUMB_WIDTH}:{THUMB_HEIGHT}',
             str(thumb_path)],
            capture_output=True, timeout=15
        )
        return os.path.exists(str(thumb_path))
    except:
        return False

def generate_html_thumbnail(html_path, thumb_path):
    """Generate placeholder for HTML evidence."""
    # Use ImageMagick to create a simple text card
    try:
        label = Path(html_path).stem[:20]
        subprocess.run(
            ['convert', '-size', f'{THUMB_WIDTH}x{THUMB_HEIGHT}',
             'xc:#1E2633',
             '-fill', '#D4A35F', '-font', 'DejaVu-Sans',
             '-pointsize', '11',
             '-gravity', 'Center', '-annotate', '0', f'HTML\n{label}',
             '-quality', '75',
             str(thumb_path)],
            capture_output=True, timeout=10
        )
        return os.path.exists(str(thumb_path))
    except:
        return False

def main():
    ensure_dir()

    with open(EVIDENCE_META) as f:
        evidence = json.load(f)

    stats = {'pdf': 0, 'jpg': 0, 'mp4': 0, 'm4a': 0, 'html': 0, 'docx': 0,
             'success': 0, 'failed': 0, 'skipped': 0}

    total = len(evidence)

    for i, (file_path, meta) in enumerate(evidence.items()):
        thumb_name = safe_thumb_name(file_path)
        thumb_path = THUMB_DIR / thumb_name

        # Store thumbnail mapping in meta
        meta['thumbnail'] = f"Images/thumbnails/evidence/{thumb_name}"

        # Skip if already exists
        if thumb_path.exists():
            stats['skipped'] += 1
            continue

        source_path = PROJECT_ROOT / file_path
        ext = file_path.rsplit('.', 1)[-1].lower() if '.' in file_path else ''

        if (i + 1) % 50 == 0:
            print(f"  Processing {i+1}/{total}...", flush=True)

        ok = False
        if ext == 'pdf' and source_path.exists():
            ok = generate_pdf_thumbnail(source_path, thumb_path)
            stats['pdf'] += 1
        elif ext in ('jpg', 'jpeg', 'png') and source_path.exists():
            ok = generate_image_thumbnail(source_path, thumb_path)
            stats['jpg'] += 1
        elif ext == 'mp4' and source_path.exists():
            ok = generate_video_thumbnail(source_path, thumb_path)
            stats['mp4'] += 1
        elif ext in ('m4a',) and source_path.exists():
            # Audio — create a placeholder
            ok = generate_html_thumbnail(file_path, thumb_path)
            stats['m4a'] += 1
        elif ext == 'html' and source_path.exists():
            ok = generate_html_thumbnail(file_path, thumb_path)
            stats['html'] += 1
        elif ext == 'docx' and source_path.exists():
            ok = generate_html_thumbnail(file_path, thumb_path)
            stats['docx'] += 1
        else:
            # File doesn't exist or unknown type
            ok = generate_html_thumbnail(file_path, thumb_path)

        if ok:
            stats['success'] += 1
        else:
            stats['failed'] += 1

    # Save updated metadata with thumbnail paths
    with open(EVIDENCE_META, 'w') as f:
        json.dump(evidence, f, indent=2)

    print(f"\n=== Thumbnail Generation Complete ===")
    print(f"  Total: {total}")
    print(f"  Success: {stats['success']}")
    print(f"  Skipped (existing): {stats['skipped']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  By type: PDF={stats['pdf']}, JPG={stats['jpg']}, MP4={stats['mp4']}, HTML={stats['html']}, Audio={stats['m4a']}, DOCX={stats['docx']}")

if __name__ == '__main__':
    main()
