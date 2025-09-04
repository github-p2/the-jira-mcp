.PHONY: help install dev-setup test test-cov lint format format-check security-check clean docs
.DEFAULT_GOAL := help

# Detect if we're using Poetry or uv
HAS_POETRY := $(shell command -v poetry 2> /dev/null)
HAS_UV := $(shell command -v uv 2> /dev/null)

ifdef HAS_UV
    PYTHON_RUNNER = uv run
    INSTALL_CMD = uv pip install -e ".[dev]"
    SYNC_CMD = uv pip sync requirements-dev.txt
else ifdef HAS_POETRY
    PYTHON_RUNNER = poetry run
    INSTALL_CMD = poetry install --extras dev
    SYNC_CMD = poetry install --sync
else
    PYTHON_RUNNER = python -m
    INSTALL_CMD = pip install -e ".[dev]"
    SYNC_CMD = pip install -r requirements-dev.txt
endif

help: ## Show this help message
	@echo "🚀 JIRA MCP Server Development Commands"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "\033[36m\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development Setup
install: ## Install dependencies
	@echo "📦 Installing dependencies..."
	$(INSTALL_CMD)

dev-setup: install ## Set up development environment
	@echo "🔧 Setting up development environment..."
ifdef HAS_UV
	@echo "Using uv for dependency management"
	uv venv --python 3.8
	@echo "Activate with: source .venv/bin/activate"
else ifdef HAS_POETRY
	@echo "Using Poetry for dependency management"
	poetry install --extras dev
else
	@echo "Using pip for dependency management"
	python -m venv .venv
	@echo "Activate with: source .venv/bin/activate (Linux/Mac) or .venv\\Scripts\\activate (Windows)"
	.venv/bin/pip install -e ".[dev]"
endif
	@echo "Installing pre-commit hooks..."
	$(PYTHON_RUNNER) pre-commit install
	@echo "✅ Development environment ready!"

##@ Code Quality
lint: ## Run linting checks
	@echo "🔍 Running linting checks..."
	$(PYTHON_RUNNER) ruff check .
	$(PYTHON_RUNNER) black --check .
	$(PYTHON_RUNNER) mypy src/

format: ## Format code with Black and Ruff
	@echo "🎨 Formatting code..."
	$(PYTHON_RUNNER) black .
	$(PYTHON_RUNNER) ruff check --fix .

format-check: ## Check code formatting
	@echo "🔍 Checking code formatting..."
	$(PYTHON_RUNNER) black --check .
	$(PYTHON_RUNNER) ruff check .

security-check: ## Run security checks
	@echo "🔒 Running security checks..."
	$(PYTHON_RUNNER) bandit -r src/ -f json -o bandit-report.json || $(PYTHON_RUNNER) bandit -r src/

##@ Testing
test: ## Run tests
	@echo "🧪 Running tests..."
	$(PYTHON_RUNNER) pytest

test-cov: ## Run tests with coverage
	@echo "🧪 Running tests with coverage..."
	$(PYTHON_RUNNER) pytest --cov=src/jira_mcp_server --cov-report=term-missing --cov-report=html

test-fast: ## Run tests without coverage
	@echo "⚡ Running fast tests..."
	$(PYTHON_RUNNER) pytest -x --no-cov

test-watch: ## Run tests in watch mode
	@echo "👀 Running tests in watch mode..."
	$(PYTHON_RUNNER) pytest-watch

##@ Documentation
docs: ## Build documentation
	@echo "📚 Building documentation..."
	@echo "Documentation generation not implemented yet"

docs-serve: ## Serve documentation locally
	@echo "🌐 Serving documentation locally..."
	@echo "Documentation serving not implemented yet"

##@ Project Management
clean: ## Clean up build artifacts
	@echo "🧹 Cleaning up..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf bandit-report.json
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

pre-commit: ## Run pre-commit hooks on all files
	@echo "🔧 Running pre-commit hooks..."
	$(PYTHON_RUNNER) pre-commit run --all-files

release-check: ## Check if ready for release
	@echo "🚀 Checking release readiness..."
	$(MAKE) lint
	$(MAKE) test-cov
	$(MAKE) security-check
	@echo "✅ Ready for release!"

##@ CI/CD Helpers
ci-install: ## Install dependencies for CI
	@echo "🤖 Installing CI dependencies..."
ifdef HAS_UV
	uv pip install -e ".[dev]"
else ifdef HAS_POETRY
	poetry install --extras dev --no-interaction --no-ansi
else
	pip install -e ".[dev]"
endif

ci-test: ## Run CI tests
	@echo "🤖 Running CI tests..."
	$(PYTHON_RUNNER) pytest --cov=src/jira_mcp_server --cov-report=xml --cov-report=term

##@ Development Utilities
show-deps: ## Show dependency tree
ifdef HAS_POETRY
	poetry show --tree
else ifdef HAS_UV
	uv pip list
else
	pip list
endif

update-deps: ## Update dependencies
	@echo "📦 Updating dependencies..."
ifdef HAS_POETRY
	poetry update
else ifdef HAS_UV
	uv pip install --upgrade -e ".[dev]"
else
	pip install --upgrade -e ".[dev]"
endif

check-deps: ## Check for dependency vulnerabilities
	@echo "🔒 Checking dependencies for vulnerabilities..."
ifdef HAS_POETRY
	poetry audit || echo "Poetry audit not available, consider using pip-audit"
else
	pip-audit || echo "pip-audit not installed, run: pip install pip-audit"
endif

env-info: ## Show environment information
	@echo "🔍 Environment Information:"
	@echo "Python version: $$(python --version)"
	@echo "Poetry: $$(command -v poetry >/dev/null && echo 'installed' || echo 'not found')"
	@echo "uv: $$(command -v uv >/dev/null && echo 'installed' || echo 'not found')"
	@echo "Virtual env: $${VIRTUAL_ENV:-'not activated'}"
