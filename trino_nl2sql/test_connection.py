#!/usr/bin/env python3
"""
Test Trino connection
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from trino.auth import BasicAuthentication
import warnings

warnings.filterwarnings("ignore")

# Load environment variables
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

print("🔌 Testing Trino Connection...\n")

# Check if Trino variables are set
print("1️⃣ Checking Trino configuration...")
trino_vars = {
    "TRINO_HOST": os.environ.get("TRINO_HOST"),
    "TRINO_PORT": os.environ.get("TRINO_PORT"),
    "TRINO_USER": os.environ.get("TRINO_USER"),
    "TRINO_PASSWORD": os.environ.get("TRINO_PASSWORD"),
    "TRINO_CATALOG": os.environ.get("TRINO_CATALOG"),
    "TRINO_SCHEMA": os.environ.get("TRINO_SCHEMA"),
    "TRINO_HTTP_SCHEME": os.environ.get("TRINO_HTTP_SCHEME", "https"),
}

missing = []
for key, value in trino_vars.items():
    if value:
        if key == "TRINO_PASSWORD":
            print(f"   ✅ {key}: ********")
        else:
            print(f"   ✅ {key}: {value}")
    else:
        print(f"   ❌ {key}: Not set")
        missing.append(key)

if missing:
    print(f"\n⚠️  Missing configuration: {', '.join(missing)}")
    print("\n💡 To fix this:")
    print("   1. Go to Superset → Settings → Database Connections")
    print("   2. Find your Trino database and click Edit")
    print("   3. Copy the connection details")
    print("   4. Update .env file with the values")
    print("\n   See GET_TRINO_FROM_SUPERSET.md for detailed instructions")
    sys.exit(1)

# Try to connect
print("\n2️⃣ Testing connection to Trino...")
try:
    import trino

    # Create authentication
    trino_auth = BasicAuthentication(
        trino_vars['TRINO_USER'],
        trino_vars['TRINO_PASSWORD']
    )

    connection_params = {
        'host': trino_vars['TRINO_HOST'],
        'port': int(trino_vars['TRINO_PORT']),
        'user': trino_vars['TRINO_USER'],
        'catalog': trino_vars['TRINO_CATALOG'],
        'schema': trino_vars['TRINO_SCHEMA'],
        'http_scheme': trino_vars['TRINO_HTTP_SCHEME'],
        'auth': trino_auth,
        'verify': False
    }

    print(f"   Connecting to {trino_vars['TRINO_HOST']}:{trino_vars['TRINO_PORT']}...")

    conn = trino.dbapi.connect(**connection_params)
    cursor = conn.cursor()

    # Test query
    print("   ✅ Connection established!")
    print("\n3️⃣ Running test query...")

    # cursor.execute("SELECT current_catalog, current_schema")
    cursor.execute("SELECT * from mewatch_items limit 1")
    result = cursor.fetchone()

    print(f"   ✅ Query successful!")
    print(f"   📊 Current Catalog: {result[0]}")
    print(f"   📊 Current Schema: {result[1]}")

    # Try to list tables
    print("\n4️⃣ Listing tables in current schema...")
    try:
        cursor.execute(f"SHOW TABLES FROM {result[0]}.{result[1]}")
        tables = cursor.fetchall()

        if tables:
            print(f"   ✅ Found {len(tables)} tables:")
            for table in tables[:10]:  # Show first 10
                print(f"      • {table[0]}")
            if len(tables) > 10:
                print(f"      ... and {len(tables) - 10} more")
        else:
            print("   ℹ️  No tables found in this schema")
            print("   💡 You may need to specify a different schema")
    except Exception as e:
        print(f"   ⚠️  Could not list tables: {e}")

    cursor.close()
    conn.close()

    print("\n" + "="*60)
    print("✅ SUCCESS! Your Trino connection is working!")
    print("="*60)
    print("\n🚀 Next steps:")
    print("   1. Update schemas/schema_example.yaml with your tables")
    print("   2. Run: python src/app.py")
    print("   3. Open: http://localhost:8080")

except ImportError:
    print("   ❌ Error: trino package not installed")
    print("   💡 Run: pip install trino")
    sys.exit(1)

except Exception as e:
    print(f"   ❌ Connection failed: {e}")
    print("\n🔍 Troubleshooting:")
    print("   1. Check if host and port are correct")
    print("   2. Verify your username")
    print("   3. Ensure you have network access to Trino")
    print("   4. Try the connection in Superset SQL Lab first")
    print("\n   See GET_TRINO_FROM_SUPERSET.md for more help")
    sys.exit(1)
