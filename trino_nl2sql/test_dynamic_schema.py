#!/usr/bin/env python3
"""
Test script for dynamic schema fetching from Trino
"""
import sys
import logging
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from schema_loader import SchemaLoader


def test_dynamic_schema():
    """Test dynamic schema loading from Trino"""

    print("\n" + "="*80)
    print("Testing Dynamic Schema Fetching from Trino")
    print("="*80 + "\n")

    try:
        # Initialize schema loader with dynamic schema enabled
        logger.info("Initializing SchemaLoader with dynamic schema...")
        loader = SchemaLoader(use_dynamic_schema=True)

        # Get the schema context
        schema_context = loader.get_schema_context()

        # Display results
        print("\n" + "-"*80)
        print("SCHEMA CONTEXT (for LLM)")
        print("-"*80)
        print(schema_context)
        print("-"*80 + "\n")

        # Get table names
        table_names = loader.get_table_names()
        print(f"Found {len(table_names)} tables:")
        for i, table in enumerate(table_names, 1):
            print(f"  {i}. {table}")

        # Get database name
        db_name = loader.get_database_name()
        print(f"\nDatabase: {db_name}")

        print("\n" + "="*80)
        print("SUCCESS: Dynamic schema loaded successfully!")
        print("="*80 + "\n")

        return True

    except Exception as e:
        print("\n" + "="*80)
        print("ERROR: Failed to load dynamic schema")
        print("="*80)
        logger.error(f"Error: {e}", exc_info=True)
        print("\nPlease check:")
        print("1. Your .env file exists and has correct TRINO_CATALOG and TRINO_SCHEMA values")
        print("2. You can connect to Trino (test with test_connection.py)")
        print("3. The catalog and schema exist in your Trino instance")
        print("\n")
        return False


def test_static_schema():
    """Test static schema loading from YAML (fallback mode)"""

    print("\n" + "="*80)
    print("Testing Static Schema Loading (YAML only)")
    print("="*80 + "\n")

    try:
        # Initialize schema loader with dynamic schema disabled
        logger.info("Initializing SchemaLoader with static schema...")
        loader = SchemaLoader(use_dynamic_schema=False)

        # Get the schema context
        schema_context = loader.get_schema_context()

        # Display results
        print("\n" + "-"*80)
        print("SCHEMA CONTEXT (from YAML)")
        print("-"*80)
        print(schema_context)
        print("-"*80 + "\n")

        print("="*80)
        print("SUCCESS: Static schema loaded successfully!")
        print("="*80 + "\n")

        return True

    except Exception as e:
        logger.error(f"Error loading static schema: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "TRINO SCHEMA LOADER TEST" + " "*34 + "║")
    print("╚" + "="*78 + "╝")

    # Test dynamic schema
    dynamic_success = test_dynamic_schema()

    # Test static schema
    static_success = test_static_schema()

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Dynamic Schema Test: {'✓ PASSED' if dynamic_success else '✗ FAILED'}")
    print(f"Static Schema Test:  {'✓ PASSED' if static_success else '✗ FAILED'}")
    print("="*80 + "\n")

    sys.exit(0 if (dynamic_success or static_success) else 1)
