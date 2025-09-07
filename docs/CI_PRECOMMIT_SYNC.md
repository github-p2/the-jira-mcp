# CI and Pre-commit Synchronization

This document describes how to ensure that CI and local pre-commit checks remain in sync.

## The Problem

Previously, the CI environment had different dependencies available than the pre-commit environment, causing:
- CI to catch mypy errors that pre-commit missed locally
- Developers to push code thinking it was clean, only to have CI fail
- Inconsistent development experience

## The Solution

We've implemented Option B: **Align pre-commit with CI** by ensuring both environments have the same dependencies available.

### Key Components

1. **Synchronized Dependencies**: The `additional_dependencies` in `.pre-commit-config.yaml` now include all runtime dependencies that CI has available.

2. **Automated Validation**:
   - `scripts/sync_dependencies.py` - Python script that validates dependency sync
   - `scripts/check_ci_precommit_sync.sh` - Bash script for comprehensive checks
   - Pre-commit hook that runs the validation automatically

3. **CI Integration**: The CI workflow now validates dependency sync before running type checks.

### Current Mypy Dependencies

The following dependencies are synchronized between CI and pre-commit:

**Runtime Dependencies**:
- `click`, `httpx`, `jira`, `mcp`, `pydantic`, `pydantic-settings`
- `python-jose`, `python-multipart`, `pyyaml`, `structlog`, `tenacity`

**Type Stubs**:
- `types-requests`, `types-PyYAML`

## How to Maintain Sync

### When Adding New Dependencies

1. **Add to `pyproject.toml`** first:
   ```toml
   dependencies = [
       # ... existing deps ...
       "new-package>=1.0.0",
   ]
   ```

2. **Run the sync check**:
   ```bash
   uv run python scripts/sync_dependencies.py
   ```

3. **Update pre-commit if needed**: The script will tell you what to add to `.pre-commit-config.yaml`.

4. **Verify locally**:
   ```bash
   uv run pre-commit run mypy --all-files
   ```

### When Removing Dependencies

1. **Remove from `pyproject.toml`**
2. **Run sync check** to see if pre-commit needs updating
3. **Remove from pre-commit** if no longer needed

### Automated Checks

The sync is validated automatically:

1. **Pre-commit hook**: Runs `dependency-sync` hook on relevant file changes
2. **CI validation**: Runs before mypy in the CI pipeline
3. **Manual check**: Run `./scripts/check_ci_precommit_sync.sh`

## Troubleshooting

### "Missing dependencies in pre-commit"

Add the missing dependencies to `.pre-commit-config.yaml`:
```yaml
additional_dependencies: [types-requests, types-PyYAML, ..., missing-package]
```

### "Extra dependencies in pre-commit"

Remove unnecessary dependencies from the `additional_dependencies` list.

### Mypy version mismatches

Ensure the mypy version in `.pre-commit-config.yaml` matches the one in `pyproject.toml`:
```yaml
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.7.1  # Should match pyproject.toml version
```

## Future Improvements

- Auto-sync script that updates pre-commit config automatically
- Validation of other tool versions (black, ruff, etc.)
- Integration with dependency management tools
