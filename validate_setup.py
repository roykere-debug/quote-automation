#!/usr/bin/env python3
"""
Validation script - checks if your setup is correct
Runs without the full automation to avoid Python 3.14 compatibility issues
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

print("=" * 60)
print("Quote Automation - Setup Validation")
print("=" * 60)

# Load .env
load_dotenv()

# Check required environment variables
required_vars = [
    "AIRTABLE_API_KEY",
    "AIRTABLE_BASE_ID",
    "AIRTABLE_LEADS_TABLE_ID",
    "AIRTABLE_SERVICES_TABLE_ID",
    "GEMINI_API_KEY",
    "GEMINI_MODEL",
    "GOOGLE_DOC_TEMPLATE_ID",
    "GMAIL_SENDER",
    "ROY_NOTIFICATION_EMAIL",
]

print("\n1. Checking environment variables...")
missing = []
for var in required_vars:
    value = os.getenv(var)
    if value:
        # Mask sensitive values
        if "KEY" in var or "TOKEN" in var:
            display_value = value[:10] + "..."
        else:
            display_value = value
        print(f"   ✓ {var}: {display_value}")
    else:
        print(f"   ✗ {var}: MISSING")
        missing.append(var)

if missing:
    print(f"\n❌ Missing {len(missing)} environment variables:")
    for var in missing:
        print(f"   - {var}")
    sys.exit(1)

# Check Google credentials file
print("\n2. Checking Google credentials...")
creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
if os.path.exists(creds_file):
    print(f"   ✓ Google credentials file found: {creds_file}")
else:
    print(f"   ✗ Google credentials file not found: {creds_file}")
    print("   → Download from Google Cloud Console and place in this directory")
    sys.exit(1)

# Check logs directory
print("\n3. Checking logs directory...")
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)
print(f"   ✓ Logs directory ready: {logs_dir}")

# Summary
print("\n" + "=" * 60)
print("✅ Setup validation complete!")
print("=" * 60)
print("\nTo run the full automation:")
print("  ./venv/bin/python3 main.py")
print("\nNote: Due to Python 3.14 compatibility issues, you may need to:")
print("  1. Use Python 3.13 (better compatibility)")
print("  2. Or run on a server with Python 3.11-3.13")
print("  3. The venv is set up and ready - just needs Python version fix")
print("\n" + "=" * 60)
