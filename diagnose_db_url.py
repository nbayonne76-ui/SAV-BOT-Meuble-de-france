#!/usr/bin/env python
"""Diagnostic script to check DATABASE_URL format"""
import os
import sys
sys.path.insert(0, 'backend')

from dotenv import load_dotenv
load_dotenv()

database_url = os.getenv("DATABASE_URL", "")

print("=" * 60)
print("DATABASE_URL DIAGNOSTIC")
print("=" * 60)
print(f"Length: {len(database_url)}")
print(f"Raw repr: {repr(database_url)}")
print(f"Starts with: {database_url[:20] if database_url else 'EMPTY'}")
print(f"Ends with: {database_url[-20:] if database_url else 'EMPTY'}")
print()
print("Character analysis:")
for i, char in enumerate(database_url[-30:] if len(database_url) > 30 else database_url):
    if char in ['\n', '\r', '\t', ' ']:
        print(f"  Position {i}: {repr(char)} (WHITESPACE!)")
print()

# Check for problematic characters
has_newline = '\n' in database_url
has_carriage = '\r' in database_url
has_trailing_space = database_url.endswith(' ')

if has_newline or has_carriage or has_trailing_space:
    print("⚠️  PROBLEMS DETECTED:")
    if has_newline:
        print("  - Contains newline (\\n)")
    if has_carriage:
        print("  - Contains carriage return (\\r)")
    if has_trailing_space:
        print("  - Has trailing space")
    print()
    print("Cleaned URL:")
    cleaned = database_url.strip()
    print(f"  {cleaned}")
    print(f"  Length: {len(cleaned)}")
else:
    print("✅ No whitespace issues detected")
