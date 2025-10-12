#!/usr/bin/env python3
"""
Quick test script to verify setup
"""
import os
import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

print("🧪 Testing Trino NL2SQL Setup...\n")

# Test 1: Check environment variables
print("1️⃣ Checking environment variables...")
from dotenv import load_dotenv
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

required_vars = [
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_CHAT_DEPLOYMENT"
]

missing_vars = []
for var in required_vars:
    if not os.environ.get(var):
        missing_vars.append(var)
        print(f"   ❌ {var}: Not set")
    else:
        print(f"   ✅ {var}: Set")

if missing_vars:
    print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
    print("   Update your .env file in the project root")
else:
    print("   ✅ All required environment variables are set")

# Test 2: Check schema file
print("\n2️⃣ Checking schema file...")
schema_file = Path(__file__).parent / "schemas" / "schema_example.yaml"
if schema_file.exists():
    print(f"   ✅ Schema file found: {schema_file}")
    try:
        from src.schema_loader import SchemaLoader
        loader = SchemaLoader(str(schema_file))
        tables = loader.get_table_names()
        print(f"   ✅ Found {len(tables)} tables: {', '.join(tables)}")
    except Exception as e:
        print(f"   ❌ Error loading schema: {e}")
else:
    print(f"   ❌ Schema file not found: {schema_file}")

# Test 3: Test SQL Generator (if env vars are set)
if not missing_vars:
    print("\n3️⃣ Testing SQL Generator...")
    try:
        from src.sql_generator import SQLGenerator
        generator = SQLGenerator()
        test_question = "Show me all customers"
        sql = generator.generate_sql(test_question)
        print(f"   ✅ SQL Generator working!")
        print(f"   Question: {test_question}")
        print(f"   Generated SQL: {sql[:100]}...")
    except Exception as e:
        print(f"   ❌ Error testing SQL Generator: {e}")
else:
    print("\n3️⃣ Skipping SQL Generator test (missing env vars)")

# Test 4: Check Trino connection (optional)
print("\n4️⃣ Checking Trino configuration...")
trino_vars = ["TRINO_HOST", "TRINO_PORT", "TRINO_USER"]
trino_configured = all(os.environ.get(var) for var in trino_vars)

if trino_configured:
    print(f"   ✅ Trino host: {os.environ.get('TRINO_HOST')}")
    print(f"   ✅ Trino port: {os.environ.get('TRINO_PORT')}")
    print(f"   ℹ️  Note: Connection test requires running Trino cluster")
else:
    print("   ℹ️  Trino not configured (optional for SQL generation)")

# Summary
print("\n" + "="*50)
print("📋 Setup Summary")
print("="*50)

if not missing_vars:
    print("✅ Azure OpenAI: Configured")
else:
    print("❌ Azure OpenAI: Missing configuration")

if schema_file.exists():
    print("✅ Database Schema: Found")
else:
    print("❌ Database Schema: Not found")

if trino_configured:
    print("✅ Trino: Configured")
else:
    print("⚠️  Trino: Not configured (optional)")

print("\n🚀 Next Steps:")
if missing_vars or not schema_file.exists():
    print("   1. Update .env file with Azure OpenAI credentials")
    print("   2. Configure your schema in schemas/schema_example.yaml")
    print("   3. Run: python trino_nl2sql/src/app.py")
else:
    print("   ✅ Setup looks good!")
    print("   Run: python trino_nl2sql/src/app.py")
    print("   Then open: http://localhost:8080")
