"""
Schema loader for database context
"""
import yaml
from pathlib import Path
from typing import Dict, List


class SchemaLoader:
    """Load and format database schema for LLM context"""

    def __init__(self, schema_file: str = None):
        if schema_file is None:
            # Default to example schema
            schema_file = Path(__file__).parent.parent / "schemas" / "schema_example.yaml"
        self.schema_file = Path(schema_file)
        self.schema_data = self._load_schema()

    def _load_schema(self) -> Dict:
        """Load schema from YAML file"""
        with open(self.schema_file, 'r') as f:
            return yaml.safe_load(f)

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
