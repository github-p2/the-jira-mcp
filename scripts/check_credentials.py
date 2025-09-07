#!/usr/bin/env python3
"""Pre-commit hook to detect hardcoded credentials."""

import re
import sys
from pathlib import Path


def main():
    """Check for hardcoded credentials in files."""
    # Patterns for detecting real credentials
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

    # Generic patterns that need additional context checking
    generic_patterns = [
        r"password\s*=\s*[\'\"]\w+",
        r"token\s*=\s*[\'\"]\w+",
    ]

    # Test patterns to identify legitimate test files
    test_indicators = [
        r"test[-_]",
        r"mock",
        r"fake",
        r"dummy",
        r"example",
        r"fixture",
    ]

    found_credentials = False

    for file_path in sys.argv[1:]:
        path = Path(file_path)

        # Skip certain files and directories
        if path.suffix in [".py", ".yaml", ".yml", ".json", ".env", ".sh"] and not any(
            skip in str(path)
            for skip in [".venv/", "docs/testing/", ".secrets.baseline"]
        ):
            try:
                content = path.read_text(encoding="utf-8")

                # Check if this is a test file
                is_test_file = "test" in str(path).lower() or any(
                    re.search(indicator, content, re.IGNORECASE)
                    for indicator in test_indicators
                )

                # Always check for high-confidence credential patterns
                for pattern in credential_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        print(
                            f"❌ Potential credential found in {file_path}: {pattern}"
                        )
                        found_credentials = True

                # Check generic patterns only in non-test files
                if not is_test_file:
                    for pattern in generic_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            matched_text = match.group(0)
                            # Skip if it looks like a test value
                            if not any(
                                indicator in matched_text.lower()
                                for indicator in [
                                    "test",
                                    "mock",
                                    "fake",
                                    "dummy",
                                    "example",
                                ]
                            ):
                                print(
                                    f"❌ Potential credential found in {file_path}: {pattern}"
                                )
                                found_credentials = True

            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")

    if found_credentials:
        print("\n🚨 SECURITY ALERT: Potential credentials detected!")
        print(
            "Please remove hardcoded credentials and use environment variables instead."
        )
        sys.exit(1)
    else:
        print("✅ No hardcoded credentials detected")
        sys.exit(0)


if __name__ == "__main__":
    main()
