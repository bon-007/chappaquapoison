#!/usr/bin/env python3
"""
ChappaquaPoison v3 — Build Orchestrator

Manages the complete build pipeline with dependency resolution,
timing reports, and error handling.

Usage:
    python3 build.py --target all [--verbose] [--dry-run]
    python3 build.py --target html --verbose
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
SVG_ENGINE_DIR = PROJECT_ROOT / "svg_engine"
BUILD_DIR = PROJECT_ROOT / "_build"
OUTPUT_DIR = PROJECT_ROOT / "_site"
LOG_FILE = BUILD_DIR / "build.log"

# Ensure build directory exists
BUILD_DIR.mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class BuildTarget:
    """Represents a build target with dependencies and execution info."""

    def __init__(
        self,
        name: str,
        script: str,
        args: List[str] = None,
        dependencies: List[str] = None,
    ):
        self.name = name
        self.script = script
        self.args = args or []
        self.dependencies = dependencies or []
        self.status = "pending"  # pending, running, success, failed, skipped
        self.start_time = None
        self.end_time = None
        self.duration = 0
        self.error = None

    @property
    def elapsed(self) -> float:
        """Return elapsed time in seconds."""
        return self.duration

    def format_duration(self) -> str:
        """Format duration as human-readable string."""
        if self.duration < 1:
            return f"{self.duration * 1000:.0f}ms"
        return f"{self.duration:.2f}s"

    def __repr__(self) -> str:
        return f"<BuildTarget {self.name}: {self.status}>"


class BuildOrchestrator:
    """Orchestrates the build process with dependency resolution."""

    # Define all available targets and their dependencies
    TARGET_GRAPH = {
        "data": {
            "script": "parse_posts.py",
            "args": [],
            "dependencies": [],
        },
        "css": {
            "script": "build_css.py",
            "args": [],
            "dependencies": [],
        },
        "svg": {
            "script": "render_assets.py",
            "args": ["--all", f"--output={PROJECT_ROOT}/Images"],
            "dependencies": ["data"],
        },
        "html": {
            "script": "build_html.py",
            "args": [],
            "dependencies": ["data", "css"],
        },
        "search": {
            "script": "build_search_index.py",
            "args": [],
            "dependencies": ["data"],
        },
        "validate": {
            "script": "validate.py",
            "args": [],
            "dependencies": ["data"],
        },
        "timeline": {
            "script": "build_timeline.py",
            "args": [],
            "dependencies": ["data"],
        },
        "tags": {
            "script": "build_tag_matrix.py",
            "args": [],
            "dependencies": ["data"],
        },
        "evidence-map": {
            "script": "build_evidence_map.py",
            "args": [],
            "dependencies": [],
        },
        "all": {
            "script": None,  # Virtual target
            "args": [],
            "dependencies": ["data", "css", "svg", "html", "search", "validate"],
        },
    }

    def __init__(self, verbose: bool = False, dry_run: bool = False):
        self.verbose = verbose
        self.dry_run = dry_run
        self.targets: Dict[str, BuildTarget] = {}
        self.results: Dict[str, Tuple[bool, str]] = {}
        self.failed_targets: List[str] = []
        self.execution_order: List[str] = []

        if self.verbose:
            logger.setLevel(logging.DEBUG)

    def resolve_dependencies(self, target: str) -> List[str]:
        """
        Resolve all dependencies for a target in correct order.

        Returns a list of targets to execute in dependency order.
        Raises ValueError if circular dependencies are detected.
        """
        if target not in self.TARGET_GRAPH:
            raise ValueError(f"Unknown target: {target}")

        visited: Set[str] = set()
        visiting: Set[str] = set()
        order: List[str] = []

        def dfs(t: str):
            if t in visited:
                return
            if t in visiting:
                raise ValueError(f"Circular dependency detected involving {t}")

            visiting.add(t)

            if t in self.TARGET_GRAPH:
                for dep in self.TARGET_GRAPH[t]["dependencies"]:
                    dfs(dep)

            visiting.remove(t)
            visited.add(t)
            order.append(t)

        dfs(target)
        return order

    def create_target(self, name: str) -> BuildTarget:
        """Create a BuildTarget from the graph definition."""
        if name not in self.TARGET_GRAPH:
            raise ValueError(f"Unknown target: {name}")

        definition = self.TARGET_GRAPH[name]
        script = definition["script"]
        args = definition["args"]
        deps = definition["dependencies"]

        # For virtual targets (like 'all'), use None as script
        script_path = (
            str(SCRIPTS_DIR / script) if script and not script.startswith("/") else script
        )

        return BuildTarget(
            name=name,
            script=script_path,
            args=args,
            dependencies=deps,
        )

    def check_script_exists(self, target: BuildTarget) -> bool:
        """Check if the script for a target exists."""
        if target.script is None:
            return True  # Virtual targets are always valid
        return Path(target.script).exists()

    def run_target(self, target: BuildTarget) -> bool:
        """
        Execute a single target.

        Returns True if successful, False otherwise.
        """
        if target.name == "all":
            logger.info("Target 'all' is virtual; dependencies will be executed.")
            return True

        if not self.check_script_exists(target):
            error_msg = f"Script not found: {target.script}"
            logger.error(error_msg)
            target.status = "failed"
            target.error = error_msg
            return False

        target.status = "running"
        target.start_time = time.time()

        cmd = [sys.executable, target.script] + target.args

        logger.info(f"Starting: {target.name}")
        if self.verbose:
            logger.debug(f"Command: {' '.join(cmd)}")

        if self.dry_run:
            logger.info(f"[DRY RUN] Would execute: {' '.join(cmd)}")
            target.status = "success"
            target.duration = 0.0
            return True

        try:
            result = subprocess.run(
                cmd,
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            target.end_time = time.time()
            target.duration = target.end_time - target.start_time

            if result.returncode == 0:
                target.status = "success"
                logger.info(
                    f"Completed: {target.name} ({target.format_duration()})"
                )
                if self.verbose and result.stdout:
                    logger.debug(f"Output:\n{result.stdout}")
                return True
            else:
                target.status = "failed"
                target.error = result.stderr or result.stdout
                logger.error(
                    f"Failed: {target.name} (exit code {result.returncode})"
                )
                if result.stderr:
                    logger.error(f"Error output:\n{result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            target.status = "failed"
            target.error = "Execution timeout (5 minutes)"
            logger.error(f"Timeout: {target.name}")
            return False
        except Exception as e:
            target.status = "failed"
            target.error = str(e)
            logger.error(f"Exception in {target.name}: {e}")
            return False

    def build(self, target: str) -> int:
        """
        Execute a build target and all its dependencies.

        Returns 0 if successful, 1 if any target failed.
        """
        logger.info("=" * 70)
        logger.info(f"ChappaquaPoison v2 Build System")
        logger.info(f"Target: {target}")
        logger.info(f"Verbose: {self.verbose}, Dry Run: {self.dry_run}")
        logger.info(f"Start time: {datetime.now().isoformat()}")
        logger.info("=" * 70)

        try:
            # Resolve dependencies
            self.execution_order = self.resolve_dependencies(target)
            logger.info(f"Execution order: {' → '.join(self.execution_order)}")

            # Create targets
            for target_name in self.execution_order:
                self.targets[target_name] = self.create_target(target_name)

            # Execute targets
            build_start = time.time()
            for target_name in self.execution_order:
                build_target = self.targets[target_name]
                success = self.run_target(build_target)

                if not success:
                    self.failed_targets.append(target_name)
                    # Continue to next target instead of stopping

            build_end = time.time()
            total_duration = build_end - build_start

            # Report results
            self._report_results(total_duration)

            return 0 if not self.failed_targets else 1

        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            return 1
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return 1

    def _report_results(self, total_duration: float):
        """Print a summary report of build results."""
        logger.info("=" * 70)
        logger.info("Build Summary")
        logger.info("=" * 70)

        for target_name in self.execution_order:
            target = self.targets[target_name]
            status_icon = {
                "success": "✓",
                "failed": "✗",
                "skipped": "⊘",
                "pending": "?",
            }.get(target.status, "?")

            duration_str = (
                f" ({target.format_duration()})"
                if target.status in ("success", "failed")
                else ""
            )
            logger.info(f"  {status_icon} {target.name:15} {target.status:10}{duration_str}")

        logger.info("=" * 70)
        logger.info(f"Total time: {total_duration:.2f}s")
        logger.info(f"Build log: {LOG_FILE}")

        if self.failed_targets:
            logger.error(f"Failed targets: {', '.join(self.failed_targets)}")
        else:
            logger.info("All targets completed successfully!")

        logger.info(f"End time: {datetime.now().isoformat()}")
        logger.info("=" * 70)


def main():
    """Parse arguments and run the build."""
    parser = argparse.ArgumentParser(
        description="ChappaquaPoison v2 Build Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 build.py --target all
  python3 build.py --target html --verbose
  python3 build.py --target data --dry-run
        """,
    )

    parser.add_argument(
        "--target",
        required=True,
        choices=[
            "data",
            "css",
            "svg",
            "html",
            "search",
            "validate",
            "timeline",
            "tags",
            "evidence-map",
            "all",
        ],
        help="Target to build",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be executed without running commands",
    )

    args = parser.parse_args()

    # Create orchestrator and run build
    orchestrator = BuildOrchestrator(
        verbose=args.verbose,
        dry_run=args.dry_run,
    )

    exit_code = orchestrator.build(args.target)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
