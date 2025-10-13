#!/usr/bin/env python3
"""
Test both SQLAlchemy and trino.dbapi connection methods
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from trino.auth import BasicAuthentication
import warnings

warnings.filterwarnings("ignore")

# Load environment variables
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

TRINO_HOST = os.environ.get("TRINO_HOST")
TRINO_PORT = int(os.environ.get("TRINO_PORT", 443))
TRINO_USER = os.environ.get("TRINO_USER")
TRINO_PASSWORD = os.environ.get("TRINO_PASSWORD")
TRINO_CATALOG = os.environ.get("TRINO_CATALOG", "hive")
TRINO_SCHEMA = os.environ.get("TRINO_SCHEMA", "reco_prod")

print("=" * 70)
print("COMPARING SQLALCHEMY vs TRINO.DBAPI CONNECTION METHODS")
print("=" * 70)
print(f"\nHost: {TRINO_HOST}:{TRINO_PORT}")
print(f"Catalog.Schema: {TRINO_CATALOG}.{TRINO_SCHEMA}\n")

# Method 1: SQLAlchemy (YOUR WORKING CODE)
print("🧪 Method 1: SQLAlchemy with create_engine")
print("-" * 70)
try:
    from sqlalchemy import create_engine
    import pandas as pd

    trino_auth = BasicAuthentication(TRINO_USER, TRINO_PASSWORD)

    with create_engine(
        f"trino://{TRINO_HOST}:{TRINO_PORT}/{TRINO_CATALOG}/{TRINO_SCHEMA}",
        connect_args={
            "auth": trino_auth,
            "http_scheme": "https",
            "verify": False
        }
    ).connect() as connection:
        df = pd.read_sql("SELECT current_catalog, current_schema", connection)
        print(f"   ✅ SUCCESS!")
        print(f"   Catalog: {df.iloc[0, 0]}")
        print(f"   Schema: {df.iloc[0, 1]}")

        # Try mewatch_items
        df2 = pd.read_sql("SELECT * FROM mewatch_items LIMIT 1", connection)
        print(f"   ✅ mewatch_items query successful - got {len(df2)} row")

except Exception as e:
    print(f"   ❌ FAILED - {type(e).__name__}: {str(e)}")

# Method 2: trino.dbapi.connect
print("\n🧪 Method 2: trino.dbapi.connect")
print("-" * 70)
try:
    import trino

    trino_auth = BasicAuthentication(TRINO_USER, TRINO_PASSWORD)

    conn = trino.dbapi.connect(
        host=TRINO_HOST,
        port=TRINO_PORT,
        user=TRINO_USER,
        catalog=TRINO_CATALOG,
        schema=TRINO_SCHEMA,
        http_scheme="https",
        auth=trino_auth,
        verify=False
    )
    cursor = conn.cursor()
    cursor.execute("SELECT current_catalog, current_schema")
    result = cursor.fetchone()
    print(f"   ✅ SUCCESS!")
    print(f"   Catalog: {result[0]}")
    print(f"   Schema: {result[1]}")

    # Try mewatch_items
    cursor.execute("SELECT * FROM mewatch_items LIMIT 1")
    result2 = cursor.fetchone()
    print(f"   ✅ mewatch_items query successful")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"   ❌ FAILED - {type(e).__name__}: {str(e)}")
    import traceback
    print("\nFull error:")
    traceback.print_exc()

print("\n" + "=" * 70)
