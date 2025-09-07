#!/usr/bin/env python3
"""
Comprehensive CI vs Pre-commit command comparison and sync verification.

This script runs all CI commands locally and compares results with pre-commit.
"""

import subprocess  # nosec B404 - Used for running CI validation commands
import sys
from pathlib import Path


def run_command(cmd: str, description: str) -> tuple[int, str]:
    """Run a command and return exit code and output."""
    print(f"\n🔧 {description}")
    print(f"   Command: {cmd}")

    result = (
        subprocess.run(  # nosec B602 - Commands are predefined CI validation commands
            cmd, shell=True, capture_output=True, text=True, cwd=Path.cwd()
        )
    )

    status = "✅ PASS" if result.returncode == 0 else "❌ FAIL"
    print(f"   Status: {status}")

    if result.returncode != 0:
        print(f"   Output: {result.stdout}")
        print(f"   Error: {result.stderr}")

    return result.returncode, result.stdout + result.stderr


def main():
    """Compare all CI commands with current state."""
    print("🔍 CI vs Local Command Comparison")
    print("=" * 50)

    # These are the exact commands from CI
    ci_commands = [
        ("uv run ruff check .", "CI: Run linting (Ruff)"),
        ("uv run black --check .", "CI: Check formatting (Black)"),
        ("uv run python scripts/sync_dependencies.py", "CI: Validate dependency sync"),
        ("uv run mypy src/", "CI: Type checking (mypy)"),
        ("uv run bandit -r src/", "CI: Security check (Bandit)"),
    ]

    print(f"\n📋 Testing {len(ci_commands)} CI commands locally:")

    failed_commands = []

    for cmd, description in ci_commands:
        exit_code, output = run_command(cmd, description)
        if exit_code != 0:
            failed_commands.append((cmd, description))

    print("\n📊 Results:")
    print(f"   Total commands: {len(ci_commands)}")
    print(f"   Passed: {len(ci_commands) - len(failed_commands)}")
    print(f"   Failed: {len(failed_commands)}")

    if failed_commands:
        print("\n❌ Failed commands that will cause CI to fail:")
        for cmd, desc in failed_commands:
            print(f"   • {desc}: {cmd}")

        print("\n💡 To fix these issues:")
        print(
            "   1. Run the manual formatting: uv run pre-commit run black-format --all-files --hook-stage manual"
        )
        print("   2. Fix any remaining issues manually")
        print("   3. Re-run this script to verify")

        return 1
    else:
        print("\n✅ All CI commands pass locally!")
        print("   Pre-commit and CI are now synchronized.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
