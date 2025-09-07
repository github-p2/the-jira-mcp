#!/usr/bin/env python3
"""
Analyze CI workflow vs pre-commit synchronization issues.

This script identifies all discrepancies between CI steps and pre-commit hooks.
"""

from pathlib import Path

import yaml


def extract_ci_steps() -> list[tuple[str, str]]:
    """Extract all CI steps that run code quality checks."""
    ci_file = Path(".github/workflows/ci.yml")
    if not ci_file.exists():
        return []

    with open(ci_file) as f:
        ci_config = yaml.safe_load(f)

    steps = []
    quality_job = ci_config.get("jobs", {}).get("quality", {})

    for step in quality_job.get("steps", []):
        if "run" in step and any(
            tool in step["run"] for tool in ["ruff", "black", "mypy", "bandit"]
        ):
            name = step.get("name", "Unnamed step")
            command = step["run"].strip()
            steps.append((name, command))

    return steps


def extract_precommit_hooks() -> list[tuple[str, str, bool]]:
    """Extract all pre-commit hooks that run code quality checks."""
    precommit_file = Path(".pre-commit-config.yaml")
    if not precommit_file.exists():
        return []

    with open(precommit_file) as f:
        precommit_config = yaml.safe_load(f)

    hooks = []
    for repo in precommit_config.get("repos", []):
        for hook in repo.get("hooks", []):
            hook_id = hook.get("id", "")
            is_manual = "manual" in hook.get("stages", [])

            if any(tool in hook_id for tool in ["black", "ruff", "mypy", "bandit"]):
                entry = hook.get("entry", hook_id)
                hooks.append((hook_id, entry, is_manual))

    return hooks


def analyze_sync_issues() -> dict[str, list[str]]:
    """Analyze synchronization issues between CI and pre-commit."""
    ci_steps = extract_ci_steps()
    precommit_hooks = extract_precommit_hooks()

    issues = {
        "missing_in_precommit": [],
        "missing_in_ci": [],
        "command_mismatches": [],
        "manual_only_hooks": [],
    }

    print("🔍 CI/Pre-commit Synchronization Analysis")
    print("=" * 50)

    print(f"\n📋 CI Steps ({len(ci_steps)}):")
    for name, command in ci_steps:
        print(f"  • {name}: {command}")

    print(f"\n🪝 Pre-commit Hooks ({len(precommit_hooks)}):")
    for hook_id, entry, is_manual in precommit_hooks:
        manual_text = " (MANUAL ONLY)" if is_manual else ""
        print(f"  • {hook_id}: {entry}{manual_text}")
        if is_manual:
            issues["manual_only_hooks"].append(hook_id)

    # Check for command mismatches
    ci_commands = {step[0]: step[1] for step in ci_steps}

    # Black check mismatch
    if "Check formatting (Black)" in ci_commands:
        ci_black = ci_commands["Check formatting (Black)"]
        if "--check" in ci_black:
            issues["command_mismatches"].append(
                "Black: CI uses '--check' (no auto-fix) but pre-commit uses auto-formatting"
            )

    return issues


def main():
    """Main analysis function."""
    issues = analyze_sync_issues()

    print("\n🚨 Synchronization Issues Found:")
    print("-" * 40)

    if issues["command_mismatches"]:
        print("\n❌ Command Mismatches:")
        for issue in issues["command_mismatches"]:
            print(f"  • {issue}")

    if issues["manual_only_hooks"]:
        print("\n⚠️  Manual-only hooks (not run by default):")
        for hook in issues["manual_only_hooks"]:
            print(f"  • {hook}")

    if not any(issues.values()):
        print("✅ No issues found!")

    print("\n💡 Recommendations:")
    print("  1. Make pre-commit black-check hook run by default")
    print("  2. Ensure all CI steps have equivalent pre-commit hooks")
    print("  3. Use consistent command flags between CI and pre-commit")


if __name__ == "__main__":
    main()
