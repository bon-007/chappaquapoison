#!/usr/bin/env python3
"""
Build comprehensive CSS from design tokens.

Reads design tokens from tokens.json and generates a comprehensive CSS file
that includes CSS custom properties, typography, spacing, layout utilities,
phase colors, ECS badges, and evidence block styles.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List


class TokensToCSSBuilder:
    """Converts design tokens to CSS output."""

    def __init__(self, tokens_path: str, output_path: str):
        """
        Initialize the builder.

        Args:
            tokens_path: Path to tokens.json file
            output_path: Path where CSS should be written
        """
        self.tokens_path = Path(tokens_path)
        self.output_path = Path(output_path)
        self.tokens: Dict[str, Any] = {}

    def load_tokens(self) -> bool:
        """Load tokens from JSON file."""
        try:
            with open(self.tokens_path, 'r') as f:
                self.tokens = json.load(f)
            print(f"✓ Loaded tokens from {self.tokens_path}")
            return True
        except FileNotFoundError:
            print(f"✗ Error: Tokens file not found at {self.tokens_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"✗ Error parsing JSON: {e}")
            return False

    def build_css(self) -> str:
        """Build complete CSS from tokens."""
        css_parts = [
            self._generate_header(),
            self._generate_css_variables(),
            self._generate_base_typography(),
            self._generate_phase_utilities(),
            self._generate_ecs_badges(),
            self._generate_evidence_styles(),
            self._generate_layout_utilities(),
            self._generate_print_styles(),
            self._generate_footer(),
        ]
        return "\n".join(css_parts)

    def _generate_header(self) -> str:
        """Generate CSS file header."""
        name = self.tokens.get("name", "Design Tokens")
        version = self.tokens.get("version", "1.0")
        updated = self.tokens.get("updated", "")

        return f"""/**
 * {name}
 * v{version}
 * Updated: {updated}
 *
 * This file is auto-generated from tokens.json
 * DO NOT edit directly — regenerate via build_css.py
 */

"""

    def _generate_css_variables(self) -> str:
        """Generate CSS custom properties from tokens."""
        lines = [":root {", "  /* ========================================"]
        lines.append("     PALETTE: CORE COLORS")
        lines.append("     ======================================== */")

        palette = self.tokens.get("palette", {})

        # Core colors
        core = palette.get("core", {})
        for key, value in core.items():
            var_name = self._camel_to_kebab(key)
            hex_color = value.get("hex", "")
            lines.append(f"  --color-{var_name}: {hex_color};")

        # Semantic colors
        lines.append("")
        lines.append("  /* Semantic */")
        semantic = palette.get("semantic", {})
        for key, value in semantic.items():
            var_name = self._camel_to_kebab(key)
            hex_color = value.get("hex", "")
            lines.append(f"  --color-{var_name}: {hex_color};")

        # ECS colors
        lines.append("")
        lines.append("  /* ECS Ratings */")
        ecs = palette.get("ecs", {})
        for key, value in ecs.items():
            hex_color = value.get("hex", "")
            lines.append(f"  --ecs-{key}: {hex_color};")

        # Phase colors
        lines.append("")
        lines.append("  /* Phase Colors */")
        phase = palette.get("phase", {})
        for key, value in phase.items():
            hex_color = value.get("hex", "")
            name = value.get("name", "")
            lines.append(f"  --phase-{key.lower()}: {hex_color}; /* {name} */")

        # Badge colors
        lines.append("")
        lines.append("  /* Badge Colors */")
        badges = palette.get("badges", {})
        for key, value in badges.items():
            hex_color = value.get("hex", "")
            label = value.get("label", "")
            lines.append(f"  --badge-{key.lower()}: {hex_color}; /* {label} */")

        # Typography families
        lines.append("")
        lines.append("  /* ========================================")
        lines.append("     TYPOGRAPHY: FONT FAMILIES")
        lines.append("     ======================================== */")
        typography = self.tokens.get("typography", {})

        families_seen = set()
        for key, value in typography.items():
            family = value.get("family", "")
            if family and family not in families_seen:
                families_seen.add(family)

        # Extract unique font families
        font_map = {
            "body": "Source Serif 4, Georgia, serif",
            "heading": "Playfair Display, Georgia, serif",
            "ui": "Inter, -apple-system, sans-serif",
            "mono": "JetBrains Mono, Courier New, monospace",
        }

        for name, family in font_map.items():
            lines.append(f"  --font-{name}: {family};")

        # Spacing scale
        lines.append("")
        lines.append("  /* ========================================")
        lines.append("     SPACING: SCALE")
        lines.append("     ======================================== */")
        spacing = self.tokens.get("spacing", {})
        unit = spacing.get("unit", "px")
        scale = spacing.get("scale", {})

        lines.append(f"  --space-unit: {spacing.get('base', 8)}{unit};")
        for key, value in scale.items():
            lines.append(f"  --space-{key}: {value}{unit};")

        # Layout
        lines.append("")
        lines.append("  /* ========================================")
        lines.append("     LAYOUT: DIMENSIONS")
        lines.append("     ======================================== */")
        layout = self.tokens.get("layout", {})
        content = layout.get("content", {})

        max_width = content.get("maxWidth", 1200)
        padding = content.get("padding", 40)

        lines.append(f"  --layout-max-width: {max_width}px;")
        lines.append(f"  --layout-padding: {padding}px;")

        lines.append("}")
        return "\n".join(lines)

    def _generate_base_typography(self) -> str:
        """Generate base typography classes."""
        lines = [
            "",
            "/* ========================================",
            "   TYPOGRAPHY: BASE CLASSES",
            "   ======================================== */",
            "",
        ]

        typography = self.tokens.get("typography", {})

        # Display
        if "display" in typography:
            t = typography["display"]
            size_min = t.get("size", {}).get("min", 32)
            size_max = t.get("size", {}).get("max", 40)
            weight = t.get("weight", 700)
            lines.append("h1, .display {")
            lines.append(f"  font-family: var(--font-heading);")
            lines.append(f"  font-weight: {weight};")
            lines.append(f"  font-size: clamp({size_min}px, 5vw, {size_max}px);")
            lines.append(f"  margin: 0;")
            lines.append(f"  color: var(--color-body-text-dark);")
            lines.append("}")
            lines.append("")

        # Section Header
        if "sectionHeader" in typography:
            t = typography["sectionHeader"]
            size_min = t.get("size", {}).get("min", 24)
            size_max = t.get("size", {}).get("max", 28)
            weight = t.get("weight", 600)
            lines.append("h2, .section-header {")
            lines.append(f"  font-family: var(--font-heading);")
            lines.append(f"  font-weight: {weight};")
            lines.append(f"  font-size: clamp({size_min}px, 4vw, {size_max}px);")
            lines.append(f"  margin: var(--space-lg) 0 var(--space-md) 0;")
            lines.append(f"  color: var(--color-body-text-dark);")
            lines.append("}")
            lines.append("")

        # Body text
        if "body" in typography:
            t = typography["body"]
            size_min = t.get("size", {}).get("min", 17)
            size_max = t.get("size", {}).get("max", 18)
            weight = t.get("weight", 400)
            line_height = t.get("lineHeight", 1.7)
            lines.append("body, p, .body-text {")
            lines.append(f"  font-family: var(--font-body);")
            lines.append(f"  font-weight: {weight};")
            lines.append(f"  font-size: clamp({size_min}px, 2.5vw, {size_max}px);")
            lines.append(f"  line-height: {line_height};")
            lines.append(f"  color: var(--color-body-text-dark);")
            lines.append("}")
            lines.append("")

        # Caption
        if "caption" in typography:
            t = typography["caption"]
            size = t.get("size", {}).get("value", 13)
            weight = t.get("weight", 400)
            lines.append(".caption, caption, figcaption {")
            lines.append(f"  font-family: var(--font-ui);")
            lines.append(f"  font-weight: {weight};")
            lines.append(f"  font-size: {size}px;")
            lines.append(f"  color: var(--color-muted-caption);")
            lines.append("}")
            lines.append("")

        # Docket / monospace
        if "docket" in typography:
            t = typography["docket"]
            size = t.get("size", {}).get("value", 14)
            weight = t.get("weight", 400)
            lines.append("code, .docket, .case-number {")
            lines.append(f"  font-family: var(--font-mono);")
            lines.append(f"  font-weight: {weight};")
            lines.append(f"  font-size: {size}px;")
            lines.append(f"  background-color: var(--color-code-docket);")
            lines.append(f"  color: var(--color-body-text-dark);")
            lines.append(f"  padding: var(--space-xs) var(--space-sm);")
            lines.append(f"  border-radius: 2px;")
            lines.append("}")
            lines.append("")

        # Blockquote
        if "blockquote" in typography:
            t = typography["blockquote"]
            size = t.get("size", {}).get("value", 17)
            weight = t.get("weight", 400)
            style = t.get("style", "italic")
            lines.append("blockquote, .blockquote {")
            lines.append(f"  font-family: var(--font-body);")
            lines.append(f"  font-weight: {weight};")
            lines.append(f"  font-style: {style};")
            lines.append(f"  font-size: {size}px;")
            lines.append(f"  margin: var(--space-md) 0;")
            lines.append(f"  padding-left: var(--space-md);")
            lines.append(f"  border-left: 3px solid var(--color-steel);")
            lines.append(f"  color: var(--color-body-text-dark);")
            lines.append("}")
            lines.append("")

        # Phase tags
        if "phaseTag" in typography:
            t = typography["phaseTag"]
            size = t.get("size", {}).get("value", 12)
            weight = t.get("weight", 600)
            transform = t.get("transform", "uppercase")
            lines.append(".phase-tag, .phase-label {")
            lines.append(f"  font-family: var(--font-ui);")
            lines.append(f"  font-weight: {weight};")
            lines.append(f"  font-size: {size}px;")
            lines.append(f"  text-transform: {transform};")
            lines.append(f"  letter-spacing: 0.05em;")
            lines.append("}")
            lines.append("")

        # Evidence heading
        if "evidenceHeading" in typography:
            t = typography["evidenceHeading"]
            size = t.get("size", {}).get("value", 15)
            weight = t.get("weight", 600)
            lines.append(".evidence-heading, h3.evidence {")
            lines.append(f"  font-family: var(--font-ui);")
            lines.append(f"  font-weight: {weight};")
            lines.append(f"  font-size: {size}px;")
            lines.append(f"  color: var(--color-body-text-dark);")
            lines.append(f"  margin: var(--space-md) 0 var(--space-sm) 0;")
            lines.append("}")
            lines.append("")

        # Reconstruction notice
        if "reconstructionNotice" in typography:
            t = typography["reconstructionNotice"]
            size = t.get("size", {}).get("value", 11)
            weight = t.get("weight", 400)
            lines.append(".reconstruction-notice, .editor-note {")
            lines.append(f"  font-family: var(--font-ui);")
            lines.append(f"  font-weight: {weight};")
            lines.append(f"  font-size: {size}px;")
            lines.append(f"  color: var(--color-muted-caption);")
            lines.append(f"  font-style: italic;")
            lines.append("}")
            lines.append("")

        return "\n".join(lines)

    def _generate_phase_utilities(self) -> str:
        """Generate phase color utility classes."""
        lines = [
            "",
            "/* ========================================",
            "   PHASE COLORS: UTILITIES",
            "   ======================================== */",
            "",
        ]

        phase = self.tokens.get("palette", {}).get("phase", {})

        for key, value in phase.items():
            hex_color = value.get("hex", "")
            name = value.get("name", "")
            phase_lower = key.lower()

            lines.append(f"/* Phase {key}: {name} */")
            lines.append(f".phase-{phase_lower} {{")
            lines.append(f"  background-color: var(--phase-{phase_lower});")
            lines.append(f"  color: white;")
            lines.append(f"}}")
            lines.append("")

            lines.append(f".phase-{phase_lower}-text {{")
            lines.append(f"  color: var(--phase-{phase_lower});")
            lines.append(f"}}")
            lines.append("")

            lines.append(f".phase-{phase_lower}-bg {{")
            lines.append(f"  background-color: var(--phase-{phase_lower});")
            lines.append(f"}}")
            lines.append("")

            lines.append(f".phase-{phase_lower}-border {{")
            lines.append(f"  border-color: var(--phase-{phase_lower});")
            lines.append(f"}}")
            lines.append("")

        return "\n".join(lines)

    def _generate_ecs_badges(self) -> str:
        """Generate ECS rating badge styles."""
        lines = [
            "",
            "/* ========================================",
            "   ECS RATINGS: BADGE STYLES",
            "   ======================================== */",
            "",
        ]

        ecs = self.tokens.get("palette", {}).get("ecs", {})

        for key, value in ecs.items():
            hex_color = value.get("hex", "")
            label = value.get("label", "")
            rating = value.get("range", "")

            lines.append(f"/* ECS {key.capitalize()}: {label} ({rating}) */")
            lines.append(f".ecs-{key} {{")
            lines.append(f"  background-color: var(--ecs-{key});")
            lines.append(f"  color: white;")
            lines.append(f"  padding: var(--space-xs) var(--space-sm);")
            lines.append(f"  border-radius: 3px;")
            lines.append(f"  font-size: 11px;")
            lines.append(f"  font-weight: 600;")
            lines.append(f"  text-transform: uppercase;")
            lines.append(f"  letter-spacing: 0.05em;")
            lines.append(f"  display: inline-block;")
            lines.append(f"}}")
            lines.append("")

            lines.append(f".ecs-{key}-text {{")
            lines.append(f"  color: var(--ecs-{key});")
            lines.append(f"  font-weight: 600;")
            lines.append(f"}}")
            lines.append("")

            lines.append(f".ecs-{key}-border {{")
            lines.append(f"  border: 1px solid var(--ecs-{key});")
            lines.append(f"}}")
            lines.append("")

        return "\n".join(lines)

    def _generate_evidence_styles(self) -> str:
        """Generate evidence block and related styles."""
        lines = [
            "",
            "/* ========================================",
            "   EVIDENCE: BLOCK STYLES",
            "   ======================================== */",
            "",
        ]

        lines.append("/* Evidence Block: Paper-like appearance */")
        lines.append(".evidence-block, .document-excerpt {")
        lines.append("  background-color: var(--color-aged-document);")
        lines.append("  color: var(--color-body-text-light);")
        lines.append("  padding: var(--space-lg);")
        lines.append("  border: 1px solid var(--color-steel);")
        lines.append("  border-radius: 2px;")
        lines.append("  margin: var(--space-md) 0;")
        lines.append("  font-family: var(--font-body);")
        lines.append("}")
        lines.append("")

        lines.append("/* Reconstruction notice: Editorial insertion */")
        lines.append(".reconstruction-notice {")
        lines.append("  background-color: rgba(169, 169, 169, 0.1);")
        lines.append("  border-left: 3px solid var(--color-muted-caption);")
        lines.append("  padding: var(--space-sm) var(--space-md);")
        lines.append("  margin: var(--space-md) 0;")
        lines.append("  font-style: italic;")
        lines.append("  color: var(--color-muted-caption);")
        lines.append("}")
        lines.append("")

        lines.append("/* Source badge: Provenance indicator */")
        lines.append(".source-badge {")
        lines.append("  display: inline-block;")
        lines.append("  background-color: var(--color-steel);")
        lines.append("  color: white;")
        lines.append("  padding: var(--space-xs) var(--space-sm);")
        lines.append("  border-radius: 2px;")
        lines.append("  font-size: 10px;")
        lines.append("  font-weight: 600;")
        lines.append("  text-transform: uppercase;")
        lines.append("  letter-spacing: 0.05em;")
        lines.append("  margin-right: var(--space-xs);")
        lines.append("}")
        lines.append("")

        lines.append("/* Redaction: Obscured content */")
        lines.append(".redaction, .redacted {")
        lines.append("  background-color: var(--color-deep-charcoal);")
        lines.append("  color: var(--color-deep-charcoal);")
        lines.append("  border-radius: 2px;")
        lines.append("  padding: 0 2px;")
        lines.append("}")
        lines.append("")

        lines.append(".redaction:hover {")
        lines.append("  cursor: not-allowed;")
        lines.append("}")
        lines.append("")

        lines.append("/* Highlighted evidence */")
        lines.append(".highlight-evidence {")
        lines.append("  background-color: var(--color-muted-amber);")
        lines.append("  color: var(--color-body-text-light);")
        lines.append("  padding: 2px 4px;")
        lines.append("  border-radius: 1px;")
        lines.append("}")
        lines.append("")

        return "\n".join(lines)

    def _generate_layout_utilities(self) -> str:
        """Generate layout utility classes."""
        lines = [
            "",
            "/* ========================================",
            "   LAYOUT: UTILITIES",
            "   ======================================== */",
            "",
        ]

        lines.append("/* Container: Constrained width content */")
        lines.append(".container, .content-container {")
        lines.append("  max-width: var(--layout-max-width);")
        lines.append("  margin: 0 auto;")
        lines.append("  padding: 0 var(--layout-padding);")
        lines.append("}")
        lines.append("")

        lines.append("/* Content: Reading measure */")
        lines.append(".content, main {")
        lines.append("  max-width: var(--layout-max-width);")
        lines.append("  margin: 0 auto;")
        lines.append("}")
        lines.append("")

        lines.append("/* Spacing utilities */")
        spacing = self.tokens.get("spacing", {})
        scale = spacing.get("scale", {})

        for key, value in scale.items():
            lines.append(f".m-{key} {{ margin: var(--space-{key}); }}")
            lines.append(f".mt-{key} {{ margin-top: var(--space-{key}); }}")
            lines.append(f".mb-{key} {{ margin-bottom: var(--space-{key}); }}")
            lines.append(f".ml-{key} {{ margin-left: var(--space-{key}); }}")
            lines.append(f".mr-{key} {{ margin-right: var(--space-{key}); }}")
            lines.append(f".p-{key} {{ padding: var(--space-{key}); }}")
            lines.append(f".pt-{key} {{ padding-top: var(--space-{key}); }}")
            lines.append(f".pb-{key} {{ padding-bottom: var(--space-{key}); }}")
            lines.append(f".pl-{key} {{ padding-left: var(--space-{key}); }}")
            lines.append(f".pr-{key} {{ padding-right: var(--space-{key}); }}")
            lines.append("")

        lines.append("/* Flexbox utilities */")
        lines.append(".flex { display: flex; }")
        lines.append(".flex-col { flex-direction: column; }")
        lines.append(".flex-row { flex-direction: row; }")
        lines.append(".flex-center { justify-content: center; align-items: center; }")
        lines.append(".flex-between { justify-content: space-between; }")
        lines.append(".flex-around { justify-content: space-around; }")
        lines.append("")

        lines.append("/* Grid utilities */")
        lines.append(".grid { display: grid; }")
        lines.append(".grid-2 { grid-template-columns: repeat(2, 1fr); }")
        lines.append(".grid-3 { grid-template-columns: repeat(3, 1fr); }")
        lines.append(".grid-gap-sm { gap: var(--space-sm); }")
        lines.append(".grid-gap-md { gap: var(--space-md); }")
        lines.append(".grid-gap-lg { gap: var(--space-lg); }")
        lines.append("")

        lines.append("/* Text utilities */")
        lines.append(".text-center { text-align: center; }")
        lines.append(".text-left { text-align: left; }")
        lines.append(".text-right { text-align: right; }")
        lines.append(".text-justify { text-align: justify; }")
        lines.append("")

        lines.append("/* Link utilities */")
        lines.append("a, .link {")
        lines.append("  color: var(--color-link-default);")
        lines.append("  text-decoration: none;")
        lines.append("  border-bottom: 1px solid transparent;")
        lines.append("  transition: all 0.2s ease;")
        lines.append("}")
        lines.append("")

        lines.append("a:hover, .link:hover {")
        lines.append("  color: var(--color-link-hover);")
        lines.append("  border-bottom-color: var(--color-link-hover);")
        lines.append("}")
        lines.append("")

        lines.append("a:visited, .link:visited {")
        lines.append("  color: var(--color-link-visited);")
        lines.append("}")
        lines.append("")

        return "\n".join(lines)

    def _generate_print_styles(self) -> str:
        """Generate print media styles."""
        lines = [
            "",
            "/* ========================================",
            "   PRINT: STYLES",
            "   ======================================== */",
            "",
            "@media print {",
            "  /* Light background for printing */",
            "  body {",
            "    background-color: white;",
            "    color: black;",
            "  }",
            "",
            "  /* Override dark mode colors */",
            "  .evidence-block, .document-excerpt {",
            "    background-color: #FAFAF8;",
            "    color: #1A1A1A;",
            "    border: 1px solid #CCC;",
            "  }",
            "",
            "  /* Hide navigation and controls */",
            "  nav, .navigation, [role='navigation'] {",
            "    display: none;",
            "  }",
            "",
            "  /* Optimize heading colors */",
            "  h1, h2, h3, h4, h5, h6 {",
            "    color: black;",
            "    page-break-after: avoid;",
            "  }",
            "",
            "  /* Keep together */",
            "  blockquote {",
            "    page-break-inside: avoid;",
            "  }",
            "",
            "  /* Print badges with borders */",
            "  .source-badge, .ecs-verified, .ecs-caution, .ecs-limited, .ecs-minimal {",
            "    border: 1px solid #333;",
            "    background-color: transparent;",
            "    color: black;",
            "  }",
            "}",
        ]

        return "\n".join(lines)

    def _generate_footer(self) -> str:
        """Generate CSS file footer."""
        return """
/* ========================================
   END OF GENERATED CSS
   ======================================== */
"""

    def _camel_to_kebab(self, name: str) -> str:
        """Convert camelCase to kebab-case."""
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append("-")
                result.append(char.lower())
            else:
                result.append(char.lower())
        return "".join(result)

    def write_css(self, css_content: str) -> bool:
        """Write CSS to output file."""
        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.output_path, 'w') as f:
                f.write(css_content)
            print(f"✓ Wrote CSS to {self.output_path}")
            return True
        except IOError as e:
            print(f"✗ Error writing CSS: {e}")
            return False

    def get_file_size(self) -> int:
        """Get the size of the generated CSS file."""
        try:
            return self.output_path.stat().st_size
        except FileNotFoundError:
            return 0

    def run(self) -> bool:
        """Execute the full build process."""
        if not self.load_tokens():
            return False

        print(f"\nGenerating CSS from design tokens...")
        css_content = self.build_css()

        if not self.write_css(css_content):
            return False

        size = self.get_file_size()
        lines = css_content.count("\n")

        print(f"✓ CSS generation complete")
        print(f"  Generated {lines:,} lines")
        print(f"  File size: {size:,} bytes ({size/1024:.1f} KB)")
        print(f"\nCSS includes:")
        print(f"  • CSS Custom Properties (colors, typography, spacing)")
        print(f"  • Base Typography Classes")
        print(f"  • Phase Color Utilities (I–IX)")
        print(f"  • ECS Rating Badge Styles")
        print(f"  • Evidence Block Styles")
        print(f"  • Layout Utilities (spacing, flexbox, grid)")
        print(f"  • Print Media Styles")

        return True


def main():
    """Main entry point."""
    # Resolve paths
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent

    tokens_path = project_root / "svg_engine" / "tokens.json"
    output_path = project_root / "_site" / "css" / "tokens.css"

    # Create builder and run
    builder = TokensToCSSBuilder(str(tokens_path), str(output_path))

    if not builder.run():
        sys.exit(1)

    print(f"\n✓ Build successful!")
    sys.exit(0)


if __name__ == "__main__":
    main()
