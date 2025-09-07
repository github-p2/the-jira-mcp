# Maintenance Guide

## Keeping CI and Pre-commit in Sync

### Quick Commands

```bash
# Check if dependencies are synchronized
uv run python scripts/sync_dependencies.py

# Full sync validation (includes version checks)
./scripts/check_ci_precommit_sync.sh

# Run the pre-commit dependency sync hook
uv run pre-commit run dependency-sync --all-files
```

### When Adding Dependencies

1. Add to `pyproject.toml` first
2. Run sync check: `uv run python scripts/sync_dependencies.py`
3. Update `.pre-commit-config.yaml` if prompted
4. Verify: `uv run pre-commit run mypy --all-files`

### Automated Validation

- ✅ Pre-commit hook validates on config changes
- ✅ CI validates before running mypy
- ✅ Local scripts available for manual checking

See [docs/CI_PRECOMMIT_SYNC.md](docs/CI_PRECOMMIT_SYNC.md) for detailed documentation.
