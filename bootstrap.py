#!/usr/bin/env python3
"""Bootstrap script to set up development environment for new repos."""

from __future__ import annotations

import argparse
import logging
import os
import platform
import shutil
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
log = logging.getLogger(__name__)

CONFIG_DIR = (
    Path(os.environ["USERPROFILE"]) / ".config"
    if platform.system() == "Windows"
    else Path.home() / ".config"
)

HOOKS_DIR = CONFIG_DIR / "hooks"
TEMPLATE_DIR = CONFIG_DIR / "repo-template"
GIT_HOOKS_DIR = Path(".git") / "hooks"


def get_hooks_source() -> tuple[str, str]:
    """Return hook source files."""
    return (
        str(HOOKS_DIR / "pre-push"),
        str(HOOKS_DIR / "pre-commit"),
    )


def hooks_installed() -> bool:
    """Check if hooks are already installed."""
    pre_push = GIT_HOOKS_DIR / "pre-push"
    pre_commit = GIT_HOOKS_DIR / "pre-commit"
    return pre_push.exists() or pre_commit.exists()


def copy_hooks(overwrite: bool = False) -> None:
    """Copy hooks to .git/hooks directory."""
    pre_push_src, pre_commit_src = get_hooks_source()

    if not HOOKS_DIR.exists():
        log.warning("Hooks directory not found: %s", HOOKS_DIR)
        return

    GIT_HOOKS_DIR.mkdir(parents=True, exist_ok=True)

    for src, name in [(pre_push_src, "pre-push"), (pre_commit_src, "pre-commit")]:
        dest = GIT_HOOKS_DIR / name
        if dest.exists() and not overwrite:
            log.info("Hook already exists, skipping: %s", name)
            continue

        try:
            if platform.system() == "Windows":
                shutil.copy(src, dest)
            else:
                if dest.exists():
                    dest.unlink()
                os.symlink(src, dest)
            log.info("Installed hook: %s", name)
        except OSError as e:
            log.error("Failed to install %s: %s", name, e)


def copy_template(overwrite: bool = False) -> None:
    """Copy template files to current directory."""
    if not TEMPLATE_DIR.exists():
        log.warning("Template directory not found: %s", TEMPLATE_DIR)
        return

    files_copied = 0

    for item in TEMPLATE_DIR.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(TEMPLATE_DIR)
            dest = Path(".") / rel_path

            if dest.exists() and not overwrite:
                log.info("File already exists, skipping: %s", rel_path)
                continue

            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)
            log.info("Copied: %s", rel_path)
            files_copied += 1

    if files_copied == 0:
        log.info("No new files to copy")
    else:
        log.info("Copied %d template files", files_copied)


def check_environment() -> bool:
    """Check for required environment variables."""
    if "GITHUB_TOKEN" not in os.environ:
        log.warning("GITHUB_TOKEN not set. Branch protection features unavailable.")
        log.info("Set with: export GITHUB_TOKEN=your_token")
        return False
    return True


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Bootstrap development environment for new repos"
    )
    parser.add_argument(
        "--hooks",
        action="store_true",
        help="Install hooks only",
    )
    parser.add_argument(
        "--template",
        action="store_true",
        help="Copy template files only",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset to defaults (overwrites existing files)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not Path(".git").exists():
        log.error("Not a git repository. Run from repo root.")
        sys.exit(1)

    check_environment()

    if args.reset:
        log.info("Resetting to defaults...")
        copy_hooks(overwrite=True)
        copy_template(overwrite=True)
    elif args.hooks:
        copy_hooks(overwrite=False)
    elif args.template:
        copy_template(overwrite=False)
    else:
        if not hooks_installed():
            log.info("Installing hooks...")
            copy_hooks(overwrite=False)
        else:
            log.info("Hooks already installed")

        template_files = [
            TEMPLATE_DIR / "AGENTS.md",
            TEMPLATE_DIR / ".github" / "workflows" / "ci.yml",
        ]
        missing = [f for f in template_files if not f.exists() or not (Path(".") / f.relative_to(TEMPLATE_DIR)).exists()]

        if missing:
            log.info("Copying template files...")
            copy_template(overwrite=False)
        else:
            log.info("Template files already present")

    log.info("Done!")


if __name__ == "__main__":
    main()
