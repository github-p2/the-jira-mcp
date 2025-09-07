#!/bin/bash
set -e

echo "🔍 Checking CI and Pre-commit Sync"
echo "=================================="

# Run the Python validation script
uv run python scripts/sync_dependencies.py

# Additional check: Compare mypy versions
echo
echo "📦 Checking tool versions..."

# Extract mypy version from pre-commit config
PRECOMMIT_MYPY_VERSION=$(grep -A 5 "mirrors-mypy" .pre-commit-config.yaml | grep "rev:" | sed 's/.*rev: *//' | tr -d ' ')
echo "Pre-commit mypy version: $PRECOMMIT_MYPY_VERSION"

# Check if pyproject.toml specifies mypy version
if grep -q "mypy" pyproject.toml; then
    PYPROJECT_MYPY_VERSION=$(grep "mypy" pyproject.toml | head -1 | sed 's/.*mypy[>=]*\([^"]*\).*/\1/' | tr -d '"')
    echo "Pyproject mypy version:  $PYPROJECT_MYPY_VERSION"

    if [ "$PRECOMMIT_MYPY_VERSION" != "$PYPROJECT_MYPY_VERSION" ]; then
        echo "⚠️  Mypy versions differ between pre-commit and pyproject.toml"
        echo "   Consider aligning them for consistency"
    fi
fi

echo
echo "✅ CI and Pre-commit sync check completed!"
