# Security Guidelines

This document outlines security practices for the JIRA MCP Server project.

## Credential Management

### ⚠️ NEVER commit credentials to git

**Prohibited items:**
- API tokens, passwords, or secret keys
- `.env` files with real credentials
- Private keys (`.key`, `.pem`, `.crt` files)
- Configuration files with embedded secrets

### ✅ Best Practices

1. **Use Environment Variables**
   ```bash
   # Good: Set via environment
   export JIRA_URL="https://your-company.atlassian.net"
   export JIRA_TOKEN="your-token-here"

   # Bad: Hardcoded in files
   JIRA_TOKEN = "actual-token-value"  # ❌ Never do this
   ```

2. **Use `.env` files locally (git-ignored)**
   ```bash
   # Create local .env file (not committed)
   echo "JIRA_URL=https://your-server.com" > .env
   echo "JIRA_TOKEN=your-token" >> .env
   ```

3. **Use example/template files**
   ```bash
   # Good: Template files
   .env.example     # ✅ Committed (no real values)
   .env             # ❌ Git-ignored (real values)
   ```

## Pre-commit Security Hooks

The project includes multiple layers of credential detection:

### 1. detect-secrets
- Scans for common secret patterns
- Maintains baseline of known false positives
- Runs on every commit

### 2. GitGuardian
- Cloud-based secret detection
- Detects 400+ types of secrets
- GitHub integration available

### 3. Custom Credential Check
- Project-specific patterns
- JIRA, GitHub, API key detection
- Customizable regex patterns

### 4. Bandit Security Linter
- Python security issues
- Hardcoded password detection
- Vulnerability scanning

## Environment Variables

### Required Variables
```bash
JIRA_URL=https://your-company.atlassian.net
JIRA_TOKEN=your-api-token
JIRA_USERNAME=your-username  # Optional
```

### Optional Variables
```bash
MCP_KNOWLEDGE_STORE_PATH=knowledge_store.yaml
MCP_LOG_LEVEL=INFO
MCP_MAX_RESULTS=100
```

## Token Security

### JIRA API Tokens
- Generate from: Profile → Security → API Tokens
- Use Bearer authentication for corporate JIRA
- Rotate tokens regularly
- Scope to minimal required permissions

### Storage
- Store in environment variables or secure credential managers
- Never store in source code
- Use different tokens for dev/staging/production

## Deployment Security

### Development
```bash
# Use .env file (git-ignored)
cp .env.example .env
# Edit .env with your credentials
```

### Production
```bash
# Use environment variables or secret management
export JIRA_URL="..."
export JIRA_TOKEN="..."
```

### CI/CD
- Use encrypted environment variables
- GitHub Secrets, GitLab CI Variables, etc.
- Never log credential values

## Incident Response

If credentials are accidentally committed:

1. **Immediate**: Rotate/invalidate the exposed credentials
2. **Remove**: Use `git filter-branch` or BFG to remove from history
3. **Verify**: Check if credentials were accessed
4. **Update**: Implement additional safeguards

## Security Scanning

### Automated Credential Detection

The project includes multiple tools for detecting hardcoded credentials:

```bash
# Run comprehensive scan (all files)
make security-scan

# Run quick scan (sample of files)
make security-scan-quick

# Run standard security checks
make security-check

# Direct script usage
uv run python scripts/check_credentials.py file1.py file2.py
uv run python scripts/full_security_scan.py
```

### Pre-commit Integration

Security checks run automatically on every commit:

```bash
# Install hooks (one-time setup)
make dev-setup

# Manual run on all files
make pre-commit
```

### Scan Results Interpretation

**✅ Clean Scan:**
- No credentials detected
- All files properly configured
- Ready for production

**❌ Issues Found:**
- Specific files and patterns identified
- Actionable remediation steps provided
- Commit blocked until resolved

### Test File Handling

The scanner intelligently handles test files:
- **Test files**: Allows mock/fake credentials
- **Production files**: Strict credential detection
- **Indicators**: Detects "test", "mock", "fake", "dummy" patterns

## Tools and Resources

- [detect-secrets](https://github.com/Yelp/detect-secrets)
- [GitGuardian](https://gitguardian.com/)
- [GitHub Security Advisories](https://github.com/advisories)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Bandit Security Linter](https://bandit.readthedocs.io/)
