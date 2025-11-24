"""
Trino Schema Fetcher
Dynamically fetches database schema information from Trino
"""
import logging
from typing import List, Dict, Any, Optional
from trino_executor import TrinoExecutor

logger = logging.getLogger(__name__)


class TrinoSchemaFetcher:
    """Fetch schema information dynamically from Trino"""

    def __init__(self, executor: Optional[TrinoExecutor] = None):
        """
        Initialize schema fetcher

        Args:
            executor: Optional TrinoExecutor instance. If None, creates a new one.
        """
        self.executor = executor if executor else TrinoExecutor()
        if not self.executor.connection:
            self.executor.connect()

    @staticmethod
    def _quote(identifier: str) -> str:
        """Safely double-quote identifiers for Trino."""
        cleaned = identifier.replace('"', '""')
        return f'"{cleaned}"'

    def get_catalogs(self) -> List[str]:
        """Get list of available catalogs"""
        try:
            results, _ = self.executor.execute_query("SHOW CATALOGS")
            return [row['Catalog'] for row in results]
        except Exception as e:
            logger.error(f"Failed to fetch catalogs: {e}")
            return []

    def get_schemas(self, catalog: str) -> List[str]:
        """Get list of schemas in a catalog"""
        try:
            cat = self._quote(catalog)
            results, _ = self.executor.execute_query(f"SHOW SCHEMAS FROM {cat}")
            return [row['Schema'] for row in results]
        except Exception as e:
            logger.error(f"Failed to fetch schemas from {catalog}: {e}")
            return []

    def get_tables(self, catalog: str, schema: str) -> List[str]:
        """Get list of tables in a schema"""
        try:
            cat = self._quote(catalog)
            sch = self._quote(schema)
            results, _ = self.executor.execute_query(
                f"SHOW TABLES FROM {cat}.{sch}"
            )
            return [row['Table'] for row in results]
        except Exception as e:
            logger.error(f"Failed to fetch tables from {catalog}.{schema}: {e}")
            return []

    def get_table_columns(self, catalog: str, schema: str, table: str) -> List[Dict[str, str]]:
        """
        Get column information for a table

        Returns:
            List of dicts with keys: name, type, extra, comment
        """
        try:
            cat = self._quote(catalog)
            sch = self._quote(schema)
            tbl = self._quote(table)
            # Use DESCRIBE to get column information
            results, _ = self.executor.execute_query(
                f"DESCRIBE {cat}.{sch}.{tbl}"
            )

            columns = []
            for row in results:
                columns.append({
                    'name': row['Column'],
                    'type': row['Type'],
                    'extra': row.get('Extra', ''),
                    'comment': row.get('Comment', '')
                })

            return columns
        except Exception as e:
            logger.error(f"Failed to fetch columns for {catalog}.{schema}.{table}: {e}")
            return []

    def get_full_schema(self, catalog: str, schema: str) -> Dict[str, Any]:
        """
        Get complete schema information for a catalog.schema

        Returns:
            Dict with structure:
            {
                'database': 'catalog.schema',
                'tables': [
                    {
                        'name': 'table_name',
                        'columns': [
                            {'name': 'col_name', 'type': 'col_type', 'comment': '...'},
                            ...
                        ]
                    },
                    ...
                ]
            }
        """
        logger.info(f"Fetching full schema for {catalog}.{schema}")

        schema_info = {
            'database': f"{catalog}.{schema}",
            'tables': []
        }

        # Get all tables
        tables = self.get_tables(catalog, schema)
        logger.info(f"Found {len(tables)} tables in {catalog}.{schema}")

        # Get columns for each table
        for table in tables:
            logger.info(f"Fetching columns for {table}")
            columns = self.get_table_columns(catalog, schema, table)

            schema_info['tables'].append({
                'name': table,
                'columns': columns
            })

        return schema_info

    def get_sample_data(self, catalog: str, schema: str, table: str, limit: int = 5) -> List[Dict]:
        """Get sample data from a table to help understand the data"""
        try:
            cat = self._quote(catalog)
            sch = self._quote(schema)
            tbl = self._quote(table)
            results, _ = self.executor.execute_query(
                f"SELECT * FROM {cat}.{sch}.{tbl} LIMIT {limit}"
            )
            return results
        except Exception as e:
            logger.error(f"Failed to fetch sample data from {catalog}.{schema}.{table}: {e}")
            return []


if __name__ == "__main__":
    # Test the schema fetcher
    logging.basicConfig(level=logging.INFO)

    fetcher = TrinoSchemaFetcher()

    # Test: Get catalogs
    print("\n=== Available Catalogs ===")
    catalogs = fetcher.get_catalogs()
    for catalog in catalogs:
        print(f"  - {catalog}")

    # Test: Get schemas from first catalog
    if catalogs:
        test_catalog = catalogs[0]
        print(f"\n=== Schemas in {test_catalog} ===")
        schemas = fetcher.get_schemas(test_catalog)
        for schema in schemas[:10]:  # Show first 10
            print(f"  - {schema}")

        # Test: Get tables from first schema
        if schemas:
            test_schema = schemas[0]
            print(f"\n=== Tables in {test_catalog}.{test_schema} ===")
            tables = fetcher.get_tables(test_catalog, test_schema)
            for table in tables[:10]:  # Show first 10
                print(f"  - {table}")

            # Test: Get columns from first table
            if tables:
                test_table = tables[0]
                print(f"\n=== Columns in {test_catalog}.{test_schema}.{test_table} ===")
                columns = fetcher.get_table_columns(test_catalog, test_schema, test_table)
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
