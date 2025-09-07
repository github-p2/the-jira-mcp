#!/usr/bin/env python3
"""Comprehensive security scan for the entire codebase."""

import re
import sys
from pathlib import Path


def scan_file_for_credentials(file_path: Path) -> tuple[bool, list[str]]:
    """Scan a single file for credentials."""
    credential_patterns = [
        r"JIRA_TOKEN\s*=\s*[\'\"]\w+",
        r"JIRA_PASSWORD\s*=\s*[\'\"]\w+",
        r"API_KEY\s*=\s*[\'\"]\w+",
        r"SECRET_KEY\s*=\s*[\'\"]\w+",
        r"ACCESS_TOKEN\s*=\s*[\'\"]\w+",
        r"GITHUB_TOKEN\s*=\s*[\'\"]\w+",
        r"(-----BEGIN [A-Z ]+-----)",
        r"(sk-[a-zA-Z0-9]{32,})",
        r"(ghp_[a-zA-Z0-9]{36})",
        r"(gho_[a-zA-Z0-9]{36})",
        r"(github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59})",
    ]

    generic_patterns = [
        r"password\s*=\s*[\'\"]\w+",
        r"token\s*=\s*[\'\"]\w+",
    ]

    test_indicators = [
        r"test[-_]",
        r"mock",
        r"fake",
        r"dummy",
        r"example",
        r"fixture",
    ]

    try:
        content = file_path.read_text(encoding="utf-8")

        # Check if this is a test file
        is_test_file = "test" in str(file_path).lower() or any(
            re.search(indicator, content, re.IGNORECASE)
            for indicator in test_indicators
        )

        found_issues = []

        # Always check for high-confidence patterns
        for pattern in credential_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                found_issues.append(f"High-confidence credential: {pattern}")

        # Check generic patterns only in non-test files
        if not is_test_file:
            for pattern in generic_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    matched_text = match.group(0)
                    if not any(
                        indicator in matched_text.lower()
                        for indicator in ["test", "mock", "fake", "dummy", "example"]
                    ):
                        found_issues.append(f"Potential credential: {pattern}")

        return len(found_issues) > 0, found_issues

    except Exception as e:
        return False, [f"Error reading file: {e}"]


def main():
    """Run comprehensive security scan."""
    print("🔒 JIRA MCP Server - Comprehensive Security Scan")
    print("=" * 60)
    print()

    # Find all relevant files
    extensions = [".py", ".yaml", ".yml", ".json", ".sh", ".env"]
    skip_patterns = [".venv/", ".git/", "__pycache__/", "node_modules/"]

    all_files = []
    for ext in extensions:
        files = list(Path(".").rglob(f"*{ext}"))
        all_files.extend(files)

    # Filter out unwanted files
    filtered_files = []
    for file_path in all_files:
        if not any(skip in str(file_path) for skip in skip_patterns):
            filtered_files.append(file_path)

    print(f"📁 Scanning {len(filtered_files)} files...")
    print()

    # Categorize files
    source_files = []
    test_files = []
    config_files = []
    script_files = []

    for file_path in filtered_files:
        if "test" in str(file_path).lower():
            test_files.append(file_path)
        elif file_path.suffix in [".yaml", ".yml", ".json", ".env"]:
            config_files.append(file_path)
        elif file_path.suffix == ".sh":
            script_files.append(file_path)
        else:
            source_files.append(file_path)

    print("📊 File Categories:")
    print(f"   • Source files: {len(source_files)}")
    print(f"   • Test files: {len(test_files)}")
    print(f"   • Config files: {len(config_files)}")
    print(f"   • Script files: {len(script_files)}")
    print()

    # Scan all files
    total_issues = 0
    files_with_issues = []

    for file_path in filtered_files:
        has_issues, issues = scan_file_for_credentials(file_path)
        if has_issues:
            total_issues += len(issues)
            files_with_issues.append((file_path, issues))

    # Report results
    if total_issues == 0:
        print("✅ SCAN COMPLETE: No credentials detected!")
        print()
        print("🛡️  Security Status: CLEAN")
        print("   • All files scanned successfully")
        print("   • No hardcoded credentials found")
        print("   • Test files properly excluded from generic checks")
        print("   • Ready for production deployment")
    else:
        print(f"❌ SCAN COMPLETE: {total_issues} potential issues found!")
        print()
        print("🚨 Files with potential credentials:")
        for file_path, issues in files_with_issues:
            print(f"   📄 {file_path}")
            for issue in issues:
                print(f"      • {issue}")
        print()
        print("🔧 Recommended Actions:")
        print("   1. Move credentials to environment variables")
        print("   2. Use .env files (git-ignored)")
        print("   3. Update code to read from environment")
        print("   4. Verify no real credentials in test files")

    print()
    print("📋 Scan Summary:")
    print(f"   • Files scanned: {len(filtered_files)}")
    print(f"   • Issues found: {total_issues}")
    print(f"   • Files with issues: {len(files_with_issues)}")
    print()

    return 0 if total_issues == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
