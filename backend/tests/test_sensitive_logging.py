# backend/tests/test_sensitive_logging.py
"""
Test suite for sensitive data filtering in logs
"""
import logging
from app.core.logging import SensitiveDataFilter


def test_sensitive_data_filter():
    """Test that sensitive data is properly redacted"""

    filter_instance = SensitiveDataFilter()

    # Test cases: (input, should_contain, should_not_contain)
    test_cases = [
        # API Keys
        (
            "API key: sk-1234567890abcdefghijklmnop",
            ["sk-***REDACTED***"],
            ["sk-1234567890abcdefghijklmnop"]
        ),
        (
            'api_key="abc123def456ghi789jkl012mno"',
            ["***REDACTED***"],
            ["abc123def456ghi789jkl012mno"]
        ),
        # Bearer Tokens
        (
            "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
            ["Bearer ***REDACTED***"],
            ["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"]
        ),
        # JWT Tokens
        (
            "Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U",
            ["***REDACTED_JWT***"],
            ["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"]
        ),
        # Passwords
        (
            'password="mySecretPass123"',
            ["password=***REDACTED***"],
            ["mySecretPass123"]
        ),
        (
            "password: SuperSecret!",
            ["password: ***REDACTED***"],
            ["SuperSecret!"]
        ),
        # Database URLs
        (
            "postgresql://user:secretpass@localhost:5432/db",
            ["postgresql://user:***REDACTED***@localhost"],
            ["secretpass"]
        ),
        # Emails
        (
            "User email: john.doe@example.com",
            ["***@example.com"],
            ["john.doe@"]
        ),
        # Multiple patterns in one string
        (
            "Login with password=secret123 and api_key=sk-1234567890abcdefghij",
            ["password=***REDACTED***", "sk-***REDACTED***"],
            ["secret123", "sk-1234567890abcdefghij"]
        ),
    ]

    print("Testing Sensitive Data Filter")
    print("=" * 60)

    passed = 0
    failed = 0

    for i, (input_text, should_contain, should_not_contain) in enumerate(test_cases, 1):
        redacted = filter_instance.redact_sensitive_data(input_text)

        # Check that required strings are present
        contains_all = all(s in redacted for s in should_contain)

        # Check that sensitive strings are NOT present
        contains_none = all(s not in redacted for s in should_not_contain)

        if contains_all and contains_none:
            print(f"✓ Test {i}: PASSED")
            print(f"  Input:    {input_text}")
            print(f"  Redacted: {redacted}")
            passed += 1
        else:
            print(f"✗ Test {i}: FAILED")
            print(f"  Input:    {input_text}")
            print(f"  Redacted: {redacted}")
            if not contains_all:
                print(f"  Missing: {[s for s in should_contain if s not in redacted]}")
            if not contains_none:
                print(f"  Still contains: {[s for s in should_not_contain if s in redacted]}")
            failed += 1
        print()

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = test_sensitive_data_filter()
    exit(0 if success else 1)
