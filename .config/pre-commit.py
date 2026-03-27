#!/usr/bin/env python3
"""Pre-commit hook: run ruff and pyright before commit."""

import json
import subprocess
import sys


def run_command(cmd: list[str], name: str) -> bool:
    """Run a command and return True if successful."""
    print(f"Running {name}...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if name == "pyright":
        try:
            output = json.loads(result.stdout)
            error_count = output.get("summary", {}).get("errorCount", 1)
            if error_count > 0:
                print(f"FAILED: {name} ({error_count} errors)")
                print(result.stdout)
                return False
            print(f"PASSED: {name}")
            return True
        except json.JSONDecodeError:
            print(f"FAILED: {name} (could not parse output)")
            print(result.stderr)
            return False

    if result.returncode != 0:
        print(f"FAILED: {name}")
        print(result.stdout)
        print(result.stderr)
        return False
    print(f"PASSED: {name}")
    return True


def main() -> int:
    """Run pre-commit checks."""
    commands = [
        (["poetry", "run", "ruff", "check", "."], "ruff"),
        (["poetry", "run", "pyright", "--outputjson"], "pyright"),
    ]

    all_passed = True
    for cmd, name in commands:
        if not run_command(cmd, name):
            all_passed = False

    if not all_passed:
        print("\nPre-commit checks failed. Fix the issues above before committing.")
        return 1

    print("\nAll pre-commit checks passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
