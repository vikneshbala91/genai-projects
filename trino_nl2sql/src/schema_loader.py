"""
Schema loader for database context
Combines dynamic schema from Trino with business descriptions from YAML
"""
import os
import yaml
import logging
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class SchemaLoader:
    """Load and format database schema for LLM context"""

    def __init__(self, schema_file: str = None, use_dynamic_schema: bool = True):
        """
        Initialize schema loader

        Args:
            schema_file: Path to YAML file with business descriptions (optional)
            use_dynamic_schema: If True, fetch schema dynamically from Trino
        """
        self.use_dynamic_schema = use_dynamic_schema
        self.schema_file = None
        self.yaml_descriptions = {}

        # Load YAML descriptions if file exists
        if schema_file is None:
            schema_file = Path(__file__).parent.parent / "schemas" / "schema_example.yaml"

        self.schema_file = Path(schema_file)
        if self.schema_file.exists():
            self.yaml_descriptions = self._load_yaml_descriptions()
        else:
            logger.warning(f"Schema file not found: {self.schema_file}")

        # Load dynamic schema from Trino if enabled
        self.schema_data = self._load_schema()

    def _load_env(self):
        """Load environment variables"""
        project_root = Path(__file__).parent.parent.parent
        env_path = project_root / ".env"
        load_dotenv(dotenv_path=env_path)

    def _load_yaml_descriptions(self) -> Dict:
        """Load business descriptions from YAML file"""
        try:
            with open(self.schema_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Error loading YAML descriptions: {e}")
            return {}

    def _load_schema(self) -> Dict:
        """
        Load schema - either from Trino dynamically or from YAML

        Returns:
            Schema dict with structure matching the original format
        """
        if self.use_dynamic_schema:
            return self._load_dynamic_schema()
        else:
            return self.yaml_descriptions

    def _load_dynamic_schema(self) -> Dict:
        """Fetch schema dynamically from Trino and merge with YAML descriptions"""
        try:
            # Import here to avoid circular dependency
            from trino_schema_fetcher import TrinoSchemaFetcher

            self._load_env()

            # Get catalog and schema from environment
            catalog = os.environ.get("TRINO_CATALOG")
            schema = os.environ.get("TRINO_SCHEMA")

            if not catalog or not schema:
                logger.warning("TRINO_CATALOG or TRINO_SCHEMA not set, falling back to YAML")
                return self.yaml_descriptions

            logger.info(f"Fetching dynamic schema from Trino: {catalog}.{schema}")

            # Fetch schema from Trino
            fetcher = TrinoSchemaFetcher()
            trino_schema = fetcher.get_full_schema(catalog, schema)

            # Merge with YAML descriptions
            merged_schema = self._merge_schemas(trino_schema, self.yaml_descriptions)

            logger.info(f"Loaded {len(merged_schema.get('tables', []))} tables from Trino")
            return merged_schema

        except Exception as e:
            logger.error(f"Failed to load dynamic schema: {e}")
            logger.warning("Falling back to YAML schema")
            return self.yaml_descriptions

    def _merge_schemas(self, trino_schema: Dict, yaml_descriptions: Dict) -> Dict:
        """
        Merge Trino schema with YAML descriptions

        Args:
            trino_schema: Schema fetched from Trino
            yaml_descriptions: Business descriptions from YAML

        Returns:
            Merged schema with structure and descriptions
        """
        merged = {
            'database': trino_schema.get('database', ''),
            'tables': []
        }

        # Create lookup for YAML descriptions
        yaml_tables = {
            table['name']: table
            for table in yaml_descriptions.get('tables', [])
        }

        # Merge each table
        for trino_table in trino_schema.get('tables', []):
            table_name = trino_table['name']
            yaml_table = yaml_tables.get(table_name, {})

            merged_table = {
                'name': table_name,
                'description': yaml_table.get('description', f'Table: {table_name}'),
                'columns': []
            }

            # Create lookup for YAML column descriptions
            yaml_columns = {
                col['name']: col
                for col in yaml_table.get('columns', [])
            }

            # Merge columns
            for trino_col in trino_table.get('columns', []):
                col_name = trino_col['name']
                yaml_col = yaml_columns.get(col_name, {})

                # Use Trino comment if no YAML description
                description = yaml_col.get('description') or trino_col.get('comment') or ''

                merged_table['columns'].append({
                    'name': col_name,
                    'type': trino_col['type'],  # Always use Trino type
                    'description': description
                })

            merged['tables'].append(merged_table)

        # Add relationships from YAML if present
        if 'relationships' in yaml_descriptions:
            merged['relationships'] = yaml_descriptions['relationships']

        return merged

    def get_schema_context(self) -> str:
        """Generate formatted schema context for LLM"""
        context = []
        context.append(f"# Database: {self.schema_data['database']}\n")

        # Add tables and columns
        for table in self.schema_data.get('tables', []):
            context.append(f"\n## Table: {table['name']}")
            context.append(f"Description: {table['description']}")
            context.append("\nColumns:")
            for col in table['columns']:
                context.append(f"  - {col['name']} ({col['type']}): {col['description']}")

        # Add relationships
        if 'relationships' in self.schema_data:
            context.append("\n## Relationships:")
            for rel in self.schema_data['relationships']:
                context.append(f"  - {rel['from']} → {rel['to']}: {rel['description']}")

        return "\n".join(context)

    def get_table_names(self) -> List[str]:
        """Get list of all table names"""
        return [table['name'] for table in self.schema_data.get('tables', [])]

    def get_database_name(self) -> str:
        """Get the full database name (catalog.schema)"""
        return self.schema_data.get('database', '')
