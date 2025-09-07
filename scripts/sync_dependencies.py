#!/usr/bin/env python3
"""
Script to ensure CI and pre-commit dependencies stay in sync.

This script validates that the mypy additional_dependencies in pre-commit
match the runtime dependencies that will be available in CI.
"""

import sys
from pathlib import Path

import tomllib
import yaml


def get_project_dependencies() -> set[str]:
    """Extract dependencies from pyproject.toml that should be available in CI."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found")

    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)

    dependencies = set()

    # Add main dependencies
    for dep in pyproject["project"]["dependencies"]:
        dep_name = dep.split(">=")[0].split("==")[0].split("[")[0].strip()
        dependencies.add(dep_name)

    # Add dev dependencies (since CI installs with [dev])
    if "dev" in pyproject["project"]["optional-dependencies"]:
        for dep in pyproject["project"]["optional-dependencies"]["dev"]:
            dep_name = dep.split(">=")[0].split("==")[0].split("[")[0].strip()
            dependencies.add(dep_name)

    return dependencies


def get_precommit_mypy_dependencies() -> set[str]:
    """Extract mypy additional_dependencies from pre-commit config."""
    precommit_path = Path(".pre-commit-config.yaml")
    if not precommit_path.exists():
        raise FileNotFoundError(".pre-commit-config.yaml not found")

    with open(precommit_path) as f:
        precommit_config = yaml.safe_load(f)

    mypy_deps = set()

    for repo in precommit_config["repos"]:
        if "mirrors-mypy" in repo["repo"]:
            for hook in repo["hooks"]:
                if hook["id"] == "mypy":
                    for dep in hook.get("additional_dependencies", []):
                        # Remove version constraints and extras
                        dep_name = (
                            dep.split(">=")[0].split("==")[0].split("[")[0].strip()
                        )
                        mypy_deps.add(dep_name)

    return mypy_deps


def get_runtime_dependencies_for_mypy() -> set[str]:
    """
    Get the subset of project dependencies that should be available to mypy.

    This filters out dependencies that are only needed at runtime but not
    for type checking.
    """
    project_deps = get_project_dependencies()

    # Dependencies that should be available for type checking
    # (excluding test-only, build-only, or pure runtime dependencies)
    mypy_relevant_deps = {
        "httpx",
        "pydantic",
        "pydantic-settings",
        "click",
        "structlog",
        "tenacity",
        "python-jose",
        "python-multipart",
        "jira",
        "mcp",
        "pyyaml",  # Note: PyYAML is imported as 'yaml' but package is 'pyyaml'
    }

    return mypy_relevant_deps.intersection(project_deps)


def get_required_type_stubs() -> set[str]:
    """Get the type stub packages that should be in additional_dependencies."""
    return {"types-requests", "types-PyYAML"}


def validate_dependency_sync() -> bool:
    """Validate that pre-commit mypy dependencies are in sync with project dependencies."""
    try:
        project_deps = get_runtime_dependencies_for_mypy()
        type_stubs = get_required_type_stubs()
        expected_mypy_deps = project_deps | type_stubs

        actual_mypy_deps = get_precommit_mypy_dependencies()

        print("🔍 Dependency Sync Validation")
        print("=" * 50)
        print(f"Expected mypy dependencies: {sorted(expected_mypy_deps)}")
        print(f"Actual mypy dependencies:   {sorted(actual_mypy_deps)}")

        missing = expected_mypy_deps - actual_mypy_deps
        extra = actual_mypy_deps - expected_mypy_deps

        if missing:
            print(f"\n❌ Missing dependencies in pre-commit: {sorted(missing)}")

        if extra:
            print(f"\n⚠️  Extra dependencies in pre-commit: {sorted(extra)}")

        if not missing and not extra:
            print("\n✅ Dependencies are in sync!")
            return True

        if missing:
            print(
                "\n🔧 To fix, add these to .pre-commit-config.yaml mypy additional_dependencies:"
            )
            print(f"   {', '.join(sorted(missing))}")

        return False

    except Exception as e:
        print(f"❌ Error validating dependencies: {e}")
        return False


def main():
    """Main entry point."""
    if not validate_dependency_sync():
        sys.exit(1)

    print("\n🎉 All dependency checks passed!")


if __name__ == "__main__":
    main()
