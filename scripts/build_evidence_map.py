#!/usr/bin/env python3
"""
Evidence Map Builder for ChappaquaPoison v3

Reads EVIDENCE.md, posts.json, and Evidence/ directory to build a comprehensive
mapping between canonical evidence IDs (A-1, B-9, etc.) and actual files on disk.
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple


class EvidenceMapBuilder:
    """Build a comprehensive evidence map from multiple sources."""

    def __init__(self, base_path: str):
        """Initialize with base directory path."""
        self.base_path = Path(base_path)
        self.evidence_file = self.base_path / "EVIDENCE.md"
        self.posts_file = self.base_path / "posts.json"
        self.evidence_dir = self.base_path / "Evidence"

        # Store parsed data
        self.canonical_ids = {}  # Maps canonical ID (A-1) to metadata
        self.file_id_to_canonical = {}  # Maps file IDs (ExA_01) to canonical IDs
        self.files_on_disk = set()  # All files in Evidence directory
        self.evidence_references = {}  # Maps canonical ID to post references

    def parse_evidence_md(self):
        """Parse EVIDENCE.md to extract canonical IDs and metadata."""
        print("Parsing EVIDENCE.md...")

        with open(self.evidence_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract all table rows with evidence data
        # Pattern: | ID | Title | Badge | Date | ECS | Source | Format | File | Posts | ...
        pattern = r'\|\s*([A-H]-\d+)\s*\|\s*([^|]+)\s*\|\s*`([^`]+)`\s*\|\s*([^|]+)\s*\|\s*(\d+)\s*\|[^|]*\|\s*([^|]*)\s*\|\s*([^|]*)\s*\|\s*([^|]*)\s*\|'

        for match in re.finditer(pattern, content):
            canonical_id = match.group(1).strip()
            title = match.group(2).strip()
            badge = match.group(3).strip()
            date = match.group(4).strip()
            ecs = int(match.group(5).strip())
            file_format = match.group(6).strip()
            file_path = match.group(7).strip()
            posts = match.group(8).strip()

            # Extract category letter (A, B, C, etc.)
            category = canonical_id[0]

            self.canonical_ids[canonical_id] = {
                "title": title,
                "badge": badge,
                "date": date,
                "ecs": ecs,
                "format": file_format,
                "file_path": file_path,
                "posts": posts.split(", ") if posts else [],
                "category": category,
                "alternate_ids": [],
                "files_on_disk": []
            }

        # Extract file IDs from file paths (ExA_01, ExG_05, etc.)
        for canonical_id, metadata in self.canonical_ids.items():
            file_path = metadata.get("file_path", "")
            if file_path:
                # Extract file identifiers like ExA_01, ExG_05, ExI_02
                # Also handle F-001, F-002, etc. in media files
                file_ids = re.findall(r'(Ex[A-Z_]+_\d+[a-z]?|F-\d+)', file_path)
                for file_id in file_ids:
                    if file_id not in self.file_id_to_canonical:
                        self.file_id_to_canonical[file_id] = canonical_id
                        metadata["alternate_ids"].append(file_id)

        print(f"  Found {len(self.canonical_ids)} canonical IDs")

    def scan_evidence_directory(self):
        """Scan the Evidence directory to find all files."""
        print(f"Scanning {self.evidence_dir}...")

        if not self.evidence_dir.exists():
            print(f"  WARNING: Evidence directory not found at {self.evidence_dir}")
            return

        for root, dirs, files in os.walk(self.evidence_dir):
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.base_path)
                self.files_on_disk.add(str(relative_path))

        print(f"  Found {len(self.files_on_disk)} files on disk")

    def parse_posts_json(self):
        """Parse posts.json to extract evidence references."""
        print("Parsing posts.json...")

        if not self.posts_file.exists():
            print(f"  WARNING: posts.json not found")
            return

        with open(self.posts_file, 'r', encoding='utf-8') as f:
            posts_data = json.load(f)

        posts_list = posts_data.get("posts", [])

        for post in posts_list:
            post_id = post.get("id", "")
            evidence = post.get("evidence", {})
            collected_files = evidence.get("collected_files", [])

            # Extract references to evidence IDs from collected files
            for file_ref in collected_files:
                # Try to extract canonical ID references from file paths
                # Look for patterns like "A-1", "B-9", etc. in comments or directly referenced
                matches = re.findall(r'([A-H]-\d+)', file_ref)
                for canonical_id in matches:
                    if canonical_id not in self.evidence_references:
                        self.evidence_references[canonical_id] = []
                    if post_id not in self.evidence_references[canonical_id]:
                        self.evidence_references[canonical_id].append(post_id)

        print(f"  Processed {len(posts_list)} posts")

    def build_file_mappings(self):
        """Map files on disk to canonical IDs by matching patterns."""
        print("Building file mappings...")

        # For each file on disk, try to match it to a canonical ID
        for file_path in self.files_on_disk:
            # Extract file identifiers from the path
            # Match Ex* patterns and F-* patterns
            file_identifiers = re.findall(r'(Ex[A-Z_]+_\d+[a-z]?|F-\d+)', file_path)

            for file_id in file_identifiers:
                # Look up in our mapping
                if file_id in self.file_id_to_canonical:
                    canonical_id = self.file_id_to_canonical[file_id]
                    if file_path not in self.canonical_ids[canonical_id]["files_on_disk"]:
                        self.canonical_ids[canonical_id]["files_on_disk"].append(file_path)

            # Also do semantic matching for well-known declarations and documents
            file_lower = file_path.lower()

            # Tedla declaration
            if 'abrehet tedla' in file_lower or 'tedla_declaration' in file_lower:
                if 'C-1' in self.canonical_ids and file_path not in self.canonical_ids['C-1']["files_on_disk"]:
                    self.canonical_ids['C-1']["files_on_disk"].append(file_path)
                    if 'semantic_match' not in self.canonical_ids['C-1']:
                        self.canonical_ids['C-1']["semantic_match"] = True

            # Crutcher declaration
            if 'bryan f. crutcher' in file_lower or 'crutcher_declaration' in file_lower:
                if 'C-2' in self.canonical_ids and file_path not in self.canonical_ids['C-2']["files_on_disk"]:
                    self.canonical_ids['C-2']["files_on_disk"].append(file_path)
                    if 'semantic_match' not in self.canonical_ids['C-2']:
                        self.canonical_ids['C-2']["semantic_match"] = True

            # Williams declaration
            if 'pat williams' in file_lower or 'williams_declaration' in file_lower or 'williams declarations' in file_lower:
                if 'C-3' in self.canonical_ids and file_path not in self.canonical_ids['C-3']["files_on_disk"]:
                    self.canonical_ids['C-3']["files_on_disk"].append(file_path)
                    if 'semantic_match' not in self.canonical_ids['C-3']:
                        self.canonical_ids['C-3']["semantic_match"] = True

            # Gopal declaration
            if 'abilash a. gopal' in file_lower or ('gopal_declaration' in file_lower and 'pdf' in file_lower):
                # Could be A-4 or C-5
                if 'A-4' in self.canonical_ids and file_path not in self.canonical_ids['A-4']["files_on_disk"]:
                    self.canonical_ids['A-4']["files_on_disk"].append(file_path)
                    if 'semantic_match' not in self.canonical_ids['A-4']:
                        self.canonical_ids['A-4']["semantic_match"] = True
                if 'C-5' in self.canonical_ids and file_path not in self.canonical_ids['C-5']["files_on_disk"]:
                    self.canonical_ids['C-5']["files_on_disk"].append(file_path)
                    if 'semantic_match' not in self.canonical_ids['C-5']:
                        self.canonical_ids['C-5']["semantic_match"] = True

            # Walsh DV-120 Response
            if 'walsh_dv120' in file_lower or 'dv120' in file_lower:
                if 'C-6' in self.canonical_ids and file_path not in self.canonical_ids['C-6']["files_on_disk"]:
                    self.canonical_ids['C-6']["files_on_disk"].append(file_path)
                    if 'semantic_match' not in self.canonical_ids['C-6']:
                        self.canonical_ids['C-6']["semantic_match"] = True

            # DVRO petition
            if 'dvro_petition' in file_lower or 'dvro petition' in file_lower:
                if 'B-1' in self.canonical_ids and file_path not in self.canonical_ids['B-1']["files_on_disk"]:
                    self.canonical_ids['B-1']["files_on_disk"].append(file_path)
                    if 'semantic_match' not in self.canonical_ids['B-1']:
                        self.canonical_ids['B-1']["semantic_match"] = True

            # Motion to Vacate All Prior Orders (H-6)
            if 'motion_to_vacate_final' in file_lower or ('motion' in file_lower and 'vacate' in file_lower and 'final' in file_lower):
                if 'H-6' in self.canonical_ids and file_path not in self.canonical_ids['H-6']["files_on_disk"]:
                    self.canonical_ids['H-6']["files_on_disk"].append(file_path)
                    if 'semantic_match' not in self.canonical_ids['H-6']:
                        self.canonical_ids['H-6']["semantic_match"] = True

            # Motion to Vacate Exhibits Core (H-7)
            if 'exhibits_core' in file_lower or ('motion' in file_lower and 'vacate' in file_lower and 'exhibits' in file_lower and 'core' in file_lower):
                if 'H-7' in self.canonical_ids and file_path not in self.canonical_ids['H-7']["files_on_disk"]:
                    self.canonical_ids['H-7']["files_on_disk"].append(file_path)
                    if 'semantic_match' not in self.canonical_ids['H-7']:
                        self.canonical_ids['H-7']["semantic_match"] = True

        print("  File mappings complete")

    def identify_orphaned_and_missing(self) -> Tuple[List[str], List[str]]:
        """Identify orphaned files and missing files."""
        orphaned = []
        missing = []

        # Files on disk but not mapped to any canonical ID
        mapped_files = set()
        for metadata in self.canonical_ids.values():
            mapped_files.update(metadata["files_on_disk"])

        orphaned = list(self.files_on_disk - mapped_files)

        # Filter out obvious system files and metadata files
        filtered_orphaned = []
        for f in orphaned:
            # Skip system files, metadata files, and text reports
            if not any(skip in f for skip in ['.DS_Store', 'COMPLETION', 'MANIFEST', 'EXTRACTION',
                                               'TIER_2_3', 'INDEX.md', 'EVIDENCE_FILES_MANIFEST',
                                               'DETAILED_FILE']):
                filtered_orphaned.append(f)

        orphaned = filtered_orphaned

        # Canonical IDs that have no files on disk
        for canonical_id, metadata in self.canonical_ids.items():
            file_path = metadata.get("file_path", "")
            if file_path and not metadata["files_on_disk"]:
                # Only mark as missing if it has a file path specified (not —)
                if file_path.strip() and "—" not in file_path:
                    missing.append(canonical_id)

        return orphaned, missing

    def build_output(self) -> Dict:
        """Build the final output JSON structure."""
        orphaned, missing = self.identify_orphaned_and_missing()

        output = {
            "canonical_ids": {},
            "file_id_to_canonical": self.file_id_to_canonical,
            "orphaned_files": sorted(orphaned),
            "missing_files": sorted(missing)
        }

        # Build canonical_ids section
        for canonical_id in sorted(self.canonical_ids.keys()):
            metadata = self.canonical_ids[canonical_id]
            posts_list = list(set(metadata["posts"] + self.evidence_references.get(canonical_id, [])))
            # Filter out em-dashes and other placeholders
            posts_list = [p for p in posts_list if p and p != '—']

            output["canonical_ids"][canonical_id] = {
                "title": metadata["title"],
                "alternate_ids": sorted(metadata["alternate_ids"]),
                "files_on_disk": sorted(metadata["files_on_disk"]),
                "posts": sorted(posts_list),
                "status": "pending" if not metadata["files_on_disk"] else "collected",
                "ecs": metadata["ecs"],
                "category": metadata["category"]
            }

            # Add semantic match indicator if present
            if metadata.get("semantic_match"):
                output["canonical_ids"][canonical_id]["matched_by"] = "semantic"

        return output

    def generate_report(self, output: Dict) -> str:
        """Generate a human-readable console report."""
        canonical_ids = output["canonical_ids"]
        file_id_map = output["file_id_to_canonical"]
        orphaned = output["orphaned_files"]
        missing = output["missing_files"]

        # Count stats
        total_canonical = len(canonical_ids)
        total_files_on_disk = len(self.files_on_disk)
        mapped_files = sum(len(meta["files_on_disk"]) for meta in canonical_ids.values())
        collected_ids = sum(1 for meta in canonical_ids.values() if meta["files_on_disk"])
        pending_ids = total_canonical - collected_ids

        report = []
        report.append("\n" + "="*70)
        report.append("EVIDENCE MAP BUILDER REPORT")
        report.append("="*70)

        report.append("\nSUMMARY STATISTICS:")
        report.append(f"  Total canonical IDs (EVIDENCE.md): {total_canonical}")
        report.append(f"  Total files on disk: {total_files_on_disk}")
        report.append(f"  Mapped files: {mapped_files}")
        report.append(f"  Canonical IDs with files: {collected_ids}")
        report.append(f"  Canonical IDs pending: {pending_ids}")

        report.append("\nCATEGORY BREAKDOWN:")
        categories = {}
        for canonical_id, meta in canonical_ids.items():
            cat = meta["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "collected": 0}
            categories[cat]["total"] += 1
            if meta["files_on_disk"]:
                categories[cat]["collected"] += 1

        for cat in sorted(categories.keys()):
            stats = categories[cat]
            report.append(f"  {cat}: {stats['collected']}/{stats['total']} collected")

        report.append("\nFILE ID MAPPING:")
        report.append(f"  Unique file IDs mapped: {len(file_id_map)}")
        report.append(f"  Examples:")
        for file_id in sorted(file_id_map.keys())[:10]:
            canonical_id = file_id_map[file_id]
            report.append(f"    {file_id} -> {canonical_id}")

        report.append("\nORPHANED FILES (on disk, not in EVIDENCE.md):")
        if orphaned:
            report.append(f"  Total: {len(orphaned)}")
            for file in sorted(orphaned)[:20]:
                report.append(f"    {file}")
            if len(orphaned) > 20:
                report.append(f"    ... and {len(orphaned) - 20} more")
        else:
            report.append("  None")

        report.append("\nMISSING FILES (in EVIDENCE.md, not on disk):")
        if missing:
            report.append(f"  Total: {len(missing)}")
            for canonical_id in sorted(missing)[:20]:
                title = canonical_ids[canonical_id]["title"]
                report.append(f"    {canonical_id}: {title}")
            if len(missing) > 20:
                report.append(f"    ... and {len(missing) - 20} more")
        else:
            report.append("  None")

        report.append("\n" + "="*70)

        return "\n".join(report)

    def run(self) -> Dict:
        """Run the complete mapping process."""
        print(f"\nStarting Evidence Map Builder")
        print(f"Base path: {self.base_path}\n")

        self.parse_evidence_md()
        self.scan_evidence_directory()
        self.parse_posts_json()
        self.build_file_mappings()

        output = self.build_output()
        report = self.generate_report(output)

        return output, report


def main():
    """Main entry point."""
    base_path = str(Path(__file__).resolve().parent.parent)

    builder = EvidenceMapBuilder(base_path)
    output, report = builder.run()

    # Print report to console
    print(report)

    # Save JSON output
    output_file = Path(base_path) / "evidence_map.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nJSON output saved to: {output_file}")

    return 0


if __name__ == "__main__":
    exit(main())
