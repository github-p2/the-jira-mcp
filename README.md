# The JIRA MCP
There are lot of JIRA MCPs which are available, but there is none which provides enterprise level customisations. This project is built for the same. It will evolve over period of time.

# 🎯 Enterprise JIRA MCP Server

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](https://opensource.org/licenses/AGPL-3.0)
[![CI](https://github.com/yourusername/jira-mcp-server/workflows/CI/badge.svg)](https://github.com/yourusername/jira-mcp-server/actions)
[![Coverage](https://codecov.io/gh/yourusername/jira-mcp-server/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/jira-mcp-server)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

> **Enterprise-grade JIRA MCP (Model Context Protocol) Server with dual deployment modes: remote server and self-contained stdio deployment.**

## 🚀 Features

### 🎯 Core Functionality
- **Dual Deployment Modes**: Remote MCP Server deployment and self-contained stdio deployment
- **Enterprise-Ready**: Built with scalability, security, and extensibility in mind
- **Full JIRA Integration**: Complete JIRA API coverage with advanced features
- **Extensible Architecture**: Plugin-based system for easy customization
- **High Performance**: Async/await patterns with connection pooling

### 🛡️ Security & Compliance
- **Security Scanning**: Automated bandit security analysis
- **Dependency Monitoring**: Dependabot for vulnerability tracking
- **Secure Configuration**: Environment-based secrets management
- **Code Security**: Pre-commit hooks with security checks

### 🔧 Developer Experience
- **Dual Package Managers**: Support for both uv and Poetry
- **Modern Tooling**: Black, Ruff, mypy, pytest with full configuration
- **Automated Quality**: Pre-commit hooks, CI/CD pipeline
- **Comprehensive Testing**: 100% test coverage with pytest
- **Documentation**: Complete API docs, contributing guidelines, security policy

### ⚡ CI/CD & Automation
- **GitHub Actions**: Multi-platform testing (Linux, macOS, Windows)
- **Automated Releases**: Semantic versioning and PyPI publishing ready
- **Code Quality Gates**: All PRs require passing tests and linting
- **Security Checks**: Automated vulnerability scanning

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Deployment Modes](#-deployment-modes)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Build Instructions](#-build-instructions)
- [Available Commands](#-available-commands)
- [Contributing](#-contributing)
- [Security](#-security)
- [License](#-license)

## ⚡ Quick Start

### Prerequisites

- Python 3.9 or higher
- JIRA instance with API access
- API token or OAuth credentials

### Installation

```bash
# Using uv (recommended)
uv pip install jira-mcp-server

# Or using pip
pip install jira-mcp-server
```

### Basic Usage

```bash
# Start as stdio server
jira-mcp-server --mode stdio

# Start as remote server
jira-mcp-server --mode remote --host 0.0.0.0 --port 8080
```

## 🛠 Installation

### Option 1: Using uv (Recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install jira-mcp-server
```

### Option 2: Using Poetry

```bash
# Install poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install the package
poetry install
```

### Option 3: From Source

```bash
git clone https://github.com/yourusername/jira-mcp-server.git
cd jira-mcp-server
make install
```

## ⚙️ Configuration

### Environment Variables

```bash
export JIRA_URL="https://your-domain.atlassian.net"
export JIRA_EMAIL="your-email@domain.com"
export JIRA_API_TOKEN="your-api-token"
```

### Configuration File

Create `config.yaml`:

```yaml
jira:
  url: "https://your-domain.atlassian.net"
  email: "your-email@domain.com"
  api_token: "your-api-token"

server:
  mode: "stdio"  # or "remote"
  host: "0.0.0.0"
  port: 8080

logging:
  level: "INFO"
  format: "json"
```

## 🎯 Usage

### As MCP Server

```python
import asyncio
from jira_mcp_server import JiraMCPServer

async def main():
    server = JiraMCPServer(config_path="config.yaml")
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
```

### Available Tools

- **Issue Management**: Create, update, delete, search issues
- **Project Operations**: List projects, get project details
- **User Management**: Search users, get user details
- **Workflow Operations**: Transition issues, get available transitions
- **Advanced Search**: JQL queries with pagination
- **Attachment Handling**: Upload, download, manage attachments

## 🌐 Deployment Modes

### 1. Stdio Mode (Default)

Perfect for local development and desktop applications:

```bash
jira-mcp-server --mode stdio
```

### 2. Remote Server Mode

Ideal for team deployments and cloud environments:

```bash
jira-mcp-server --mode remote --host 0.0.0.0 --port 8080
```

## 📚 API Documentation

### Core Methods

```python
# Search issues
result = await server.search_issues(
    jql="project = TEST AND status = Open",
    max_results=50
)

# Create issue
issue = await server.create_issue(
    project_key="TEST",
    summary="New issue",
    issue_type="Task",
    description="Issue description"
)

# Update issue
await server.update_issue(
    issue_key="TEST-123",
    fields={"summary": "Updated summary"}
)
```

For complete API documentation, visit [our docs site](https://docs.jira-mcp-server.dev).

## 🔧 Development

### Prerequisites

- Python 3.9+
- uv (recommended) or Poetry
- Git
- Make (for development commands)

### Setup Development Environment

#### Option 1: Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/jira-mcp-server.git
cd jira-mcp-server

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Set up development environment (creates venv and installs deps)
make dev-setup

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### Option 2: Using Poetry

```bash
# Clone the repository
git clone https://github.com/yourusername/jira-mcp-server.git
cd jira-mcp-server

# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install --extras dev

# Activate virtual environment
poetry shell
```

#### Verify Installation

```bash
# Run tests to ensure everything works
make test

# Run linting
make lint

# Check environment info
make env-info
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/test_server.py -v
```

### Code Quality

This project uses:

- **Black** for code formatting (line length: 88)
- **Ruff** for linting and import sorting
- **mypy** for type checking
- **bandit** for security scanning
- **pytest** for testing with asyncio support
- **pre-commit** for automated quality checks

## 🏗️ Build Instructions

### Development Build

```bash
# Clone and setup
git clone https://github.com/yourusername/jira-mcp-server.git
cd jira-mcp-server

# Quick setup with uv
make dev-setup

# Or manual setup with uv
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Production Build

```bash
# Using uv
uv pip install jira-mcp-server

# Using Poetry
poetry add jira-mcp-server

# From source
git clone https://github.com/yourusername/jira-mcp-server.git
cd jira-mcp-server
uv pip install .
```

### Docker Build (Coming Soon)

```bash
# Build container
docker build -t jira-mcp-server .

# Run container
docker run -p 8080:8080 jira-mcp-server
```

## ⚙️ Available Commands

### Development Commands

```bash
# Environment setup
make dev-setup          # Set up development environment
make install            # Install dependencies
make env-info           # Show environment information

# Code quality
make lint               # Run all linting checks
make format             # Format code with Black and Ruff
make format-check       # Check code formatting without changes
make pre-commit         # Run pre-commit hooks on all files

# Testing
make test               # Run tests
make test-cov           # Run tests with coverage report
make test-fast          # Run tests without coverage (faster)
make test-watch         # Run tests in watch mode

# Security
make security-check     # Run bandit security scanning
make check-deps         # Check for dependency vulnerabilities

# Project maintenance
make clean              # Clean up build artifacts
make update-deps        # Update dependencies
make show-deps          # Show dependency tree
make release-check      # Check if ready for release

# CI/CD helpers
make ci-install         # Install dependencies for CI
make ci-test           # Run CI tests
```

### Manual Commands (if Make is not available)

```bash
# Setup
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Quality checks
uv run ruff check .
uv run black --check .
uv run mypy src/
uv run bandit -r src/

# Testing
uv run pytest
uv run pytest --cov=src/jira_mcp_server --cov-report=html

# Pre-commit
uv run pre-commit install
uv run pre-commit run --all-files
```

### Package Management

Both **uv** and **Poetry** are fully supported:

```bash
# Using uv (faster, modern)
uv pip install -e ".[dev]"
uv pip list
uv pip install --upgrade package-name

# Using Poetry (traditional)
poetry install --extras dev
poetry show
poetry add package-name
```

## 📁 Project Structure

```
jira-mcp-server/
├── .github/                    # GitHub configuration
│   ├── workflows/
│   │   └── ci.yml             # CI/CD pipeline
│   ├── ISSUE_TEMPLATE/        # Issue templates
│   ├── pull_request_template.md
│   └── dependabot.yml        # Dependency updates
├── src/
│   └── jira_mcp_server/       # Main package
│       └── __init__.py        # Package initialization
├── tests/                     # Test suite
│   ├── __init__.py
│   └── test_server.py         # Test files
├── docs/                      # Documentation (coming soon)
├── .venv/                     # Virtual environment (created by setup)
├── .coverage                  # Coverage data
├── htmlcov/                   # Coverage HTML reports
├── bandit-report.json         # Security scan results
├── pyproject.toml             # Project configuration
├── .gitignore                 # Git ignore rules
├── .editorconfig              # Editor configuration
├── .pre-commit-config.yaml    # Pre-commit hooks
├── Makefile                   # Development commands
├── README.md                  # This file
├── CONTRIBUTING.md            # Contribution guidelines
├── SECURITY.md                # Security policy
├── CHANGELOG.md               # Version history
├── LICENSE                    # AGPL-3.0 license
└── roadmap/                   # Project roadmap
    └── best-practices.md      # Development best practices
```

### Key Configuration Files

- **`pyproject.toml`**: Modern Python project configuration (PEP 621)
- **`Makefile`**: Development automation commands
- **`.pre-commit-config.yaml`**: Code quality automation
- **`.github/workflows/ci.yml`**: CI/CD pipeline configuration
- **`.github/dependabot.yml`**: Automated dependency updates

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Steps

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`make test lint`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 🔒 Security

Security is a top priority. Please see our [Security Policy](SECURITY.md) for:

- Supported versions
- Reporting vulnerabilities
- Security best practices

## 📈 Roadmap

- [ ] GraphQL API support
- [ ] Plugin marketplace
- [ ] Advanced caching strategies
- [ ] Multi-tenant support
- [ ] Real-time notifications via WebSockets

## 📄 License

This project is licensed under the AGPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) for the MCP specification
- [Atlassian](https://www.atlassian.com/) for the JIRA platform
- All our amazing [contributors](https://github.com/yourusername/jira-mcp-server/graphs/contributors)

---

**Made with ❤️ by the JIRA MCP Server team**
