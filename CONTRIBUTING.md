# Contributing to JIRA MCP Server

🎉 Thank you for your interest in contributing to the JIRA MCP Server! This guide will help you get started with contributing to our enterprise-grade open-source project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Community](#community)

## 📜 Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- uv (recommended) or Poetry
- A GitHub account

### First Time Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/jira-mcp-server.git
   cd jira-mcp-server
   ```

3. **Add the upstream repository**:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/jira-mcp-server.git
   ```

4. **Set up the development environment**:
   ```bash
   make dev-setup
   ```

## 🔧 Development Setup

### Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Using Poetry

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Install pre-commit hooks
pre-commit install
```

### Verify Installation

```bash
# Run tests to ensure everything is working
make test

# Run linting
make lint

# Check code formatting
make format-check
```

## 🔄 Development Workflow

### 1. Create a Branch

Always create a new branch for your work:

```bash
# Update your fork
git checkout main
git pull upstream main

# Create and switch to a new branch
git checkout -b feature/your-feature-name
```

### Branch Naming Conventions

- `feature/description` - for new features
- `fix/description` - for bug fixes
- `docs/description` - for documentation updates
- `refactor/description` - for code refactoring
- `test/description` - for adding or updating tests

### 2. Make Your Changes

- Write clear, concise commit messages
- Follow our [code style guidelines](#code-style)
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

Before submitting, ensure your changes pass all checks:

```bash
# Run the full test suite
make test

# Run linting and formatting checks
make lint
make format-check

# Check test coverage
make test-cov

# Run security checks
make security-check
```

### 4. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "feat: add support for custom JIRA fields

- Add CustomField class for handling custom field types
- Implement validation for custom field values
- Add tests for custom field operations
- Update documentation with custom field examples

Closes #123"
```

#### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

### 5. Push and Create Pull Request

```bash
# Push your branch to your fork
git push origin feature/your-feature-name
```

Then create a Pull Request through GitHub's web interface.

## 🎨 Code Style

### Formatting and Linting

We use the following tools to maintain code quality:

- **Black** for code formatting (line length: 88)
- **Ruff** for linting and import sorting
- **mypy** for type checking
- **bandit** for security scanning

### Style Guidelines

1. **Follow PEP 8** with Black's formatting
2. **Use type hints** for all function parameters and return values
3. **Write docstrings** for all public functions and classes using Google style
4. **Keep functions small** and focused on a single responsibility
5. **Use meaningful variable names** that describe their purpose

### Example Code Style

```python
from typing import Dict, List, Optional
import asyncio


class JiraIssue:
    """Represents a JIRA issue with core functionality.

    Args:
        key: The issue key (e.g., 'PROJ-123')
        summary: Brief description of the issue
        description: Detailed description of the issue
        issue_type: Type of issue (Bug, Task, Story, etc.)
    """

    def __init__(
        self,
        key: str,
        summary: str,
        description: Optional[str] = None,
        issue_type: str = "Task",
    ) -> None:
        self.key = key
        self.summary = summary
        self.description = description
        self.issue_type = issue_type

    async def update_summary(self, new_summary: str) -> bool:
        """Update the issue summary.

        Args:
            new_summary: The new summary text

        Returns:
            True if update was successful, False otherwise

        Raises:
            JiraAPIError: If the API request fails
        """
        # Implementation here
        pass
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_server.py -v

# Run tests with coverage
make test-cov

# Run tests for specific functionality
pytest tests/ -k "test_issue" -v
```

### Writing Tests

1. **Write tests for all new functionality**
2. **Use descriptive test names** that explain what is being tested
3. **Follow the AAA pattern** (Arrange, Act, Assert)
4. **Use fixtures** for common test setup
5. **Mock external dependencies** (JIRA API calls)

### Test Structure

```python
import pytest
from unittest.mock import AsyncMock, patch

from jira_mcp_server import JiraIssue


class TestJiraIssue:
    """Test suite for JiraIssue class."""

    @pytest.fixture
    def sample_issue(self) -> JiraIssue:
        """Create a sample issue for testing."""
        return JiraIssue(
            key="TEST-123",
            summary="Test issue",
            description="Test description",
            issue_type="Bug"
        )

    @pytest.mark.asyncio
    async def test_update_summary_success(self, sample_issue: JiraIssue) -> None:
        """Test successful summary update."""
        # Arrange
        new_summary = "Updated test issue"

        # Act
        with patch('jira_mcp_server.api.update_issue') as mock_update:
            mock_update.return_value = True
            result = await sample_issue.update_summary(new_summary)

        # Assert
        assert result is True
        assert sample_issue.summary == new_summary
        mock_update.assert_called_once()
```

## 📝 Pull Request Process

### Before Submitting

1. **Ensure all tests pass**: `make test`
2. **Verify code quality**: `make lint`
3. **Check formatting**: `make format-check`
4. **Update documentation** if needed
5. **Add changelog entry** if applicable

### Pull Request Template

When creating a PR, include:

- **Clear description** of what the PR does
- **Related issue numbers** (use "Closes #123")
- **Testing instructions** for reviewers
- **Screenshots** for UI changes
- **Breaking changes** if any

### Review Process

1. **Automated checks** will run (CI/CD pipeline)
2. **Code review** by maintainers
3. **Testing** on different environments
4. **Documentation review** if applicable
5. **Final approval** and merge

### PR Requirements

- [ ] All CI checks pass
- [ ] At least one approving review from a maintainer
- [ ] No merge conflicts
- [ ] Branch is up to date with main
- [ ] Documentation updated (if needed)

## 🐛 Issue Guidelines

### Before Creating an Issue

1. **Search existing issues** to avoid duplicates
2. **Check the documentation** for answers
3. **Try the latest version** to see if the issue still exists

### Issue Types

- **Bug Report**: Something isn't working as expected
- **Feature Request**: Suggest a new feature or enhancement
- **Question**: Ask for help or clarification
- **Documentation**: Improve or fix documentation

### Bug Report Template

```markdown
**Description**
A clear description of what the bug is.

**Steps to Reproduce**
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., macOS 12.0]
- Python version: [e.g., 3.9.7]
- Package version: [e.g., 1.0.0]
- JIRA version: [e.g., Cloud/Server 8.5]

**Additional Context**
Any other context about the problem.
```

## 👥 Community

### Getting Help

- **GitHub Discussions**: For questions and community discussions
- **GitHub Issues**: For bug reports and feature requests
- **Documentation**: Check our comprehensive docs

### Communication Guidelines

- **Be respectful** and inclusive
- **Use clear, descriptive titles** for issues and PRs
- **Provide context** and examples when asking questions
- **Be patient** with responses from volunteers

## 🏆 Recognition

We appreciate all contributors! Contributors will be:

- **Listed in our README** and release notes
- **Mentioned in our changelog** for significant contributions
- **Invited to our contributor Discord** (coming soon)

## 📚 Additional Resources

- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)
- [Python Style Guide (PEP 8)](https://www.python.org/dev/peps/pep-0008/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

---

Thank you for contributing to JIRA MCP Server! 🚀
