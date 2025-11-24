"""
Trino Query Executor
"""
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv
import trino
from trino.auth import BasicAuthentication
import pandas as pd
from tabulate import tabulate
import warnings

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)


class TrinoExecutor:
    """Execute SQL queries on Trino and format results"""

    def __init__(self):
        self._load_env()
        self.connection = None

    def _load_env(self):
        """Load environment variables"""
        project_root = Path(__file__).parent.parent
        env_path = project_root / ".env"
        load_dotenv(dotenv_path=env_path)

    def connect(self):
        """Establish connection to Trino with BasicAuthentication from .env"""
        try:
            # Get credentials from environment variables
            trino_user = os.environ.get("TRINO_USER")
            trino_password = os.environ.get("TRINO_PASSWORD")

            if not trino_user or not trino_password:
                raise ValueError("TRINO_USER and TRINO_PASSWORD must be set in .env file")

            # Create BasicAuthentication
            trino_auth = BasicAuthentication(trino_user, trino_password)

            # Connect to Trino
            # Note: Some Trino installations behind reverse proxies may require
            # specifying the source parameter or removing catalog/schema from connection
            connection_kwargs = {
                "host": os.environ.get("TRINO_HOST", "common-warehouse-cia.mediacorp.sg"),
                "port": int(os.environ.get("TRINO_PORT", 443)),
                "user": trino_user,
                "http_scheme": os.environ.get("TRINO_HTTP_SCHEME", "https"),
                "auth": trino_auth,
                "verify": False
            }

            # Add catalog and schema if specified
            catalog = os.environ.get("TRINO_CATALOG")
            schema = os.environ.get("TRINO_SCHEMA")
            if catalog:
                connection_kwargs["catalog"] = catalog
            if schema:
                connection_kwargs["schema"] = schema

            self.connection = trino.dbapi.connect(**connection_kwargs)
            logger.info("Connected to Trino successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Trino: {e}")
            raise

    def execute_query(self, sql: str) -> Tuple[List[Dict], List[str]]:
        """
        Execute SQL query and return results

        Args:
            sql: SQL query to execute

        Returns:
            Tuple of (rows as list of dicts, column names)
        """
        if self.connection is None:
            self.connect()

        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)

            # Get column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            # Fetch all rows
            rows = cursor.fetchall()

            # Convert to list of dicts
            result_dicts = []
            for row in rows:
                result_dicts.append(dict(zip(columns, row)))

            logger.info(f"Query executed successfully. Returned {len(result_dicts)} rows.")
            return result_dicts, columns

        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise

    def format_results_as_table(self, results: List[Dict], columns: List[str]) -> str:
        """
        Format query results as a text table

        Args:
            results: List of result dictionaries
            columns: List of column names

        Returns:
            Formatted table string
        """
        if not results:
            return "No results found."

        # Convert to DataFrame for easy formatting
        df = pd.DataFrame(results)

        # Use tabulate for nice formatting
        table = tabulate(df, headers='keys', tablefmt='grid', showindex=False)
        return table

    def format_results_as_html(self, results: List[Dict], columns: List[str]) -> str:
        """
        Format query results as HTML table

        Args:
            results: List of result dictionaries
            columns: List of column names

        Returns:
            HTML table string
        """
        if not results:
            return "<p>No results found.</p>"

        df = pd.DataFrame(results)
        html = df.to_html(index=False, classes='table table-striped table-bordered')
        return html

    def close(self):
        """Close the Trino connection"""
        if self.connection:
            self.connection.close()
            logger.info("Trino connection closed")


if __name__ == "__main__":
    # Test the executor
    logging.basicConfig(level=logging.INFO)

    executor = TrinoExecutor()

    # Test query
    test_sql = "SELECT 1 as id, 'test' as name UNION ALL SELECT 2, 'test2'"

    try:
        results, columns = executor.execute_query(test_sql)
        print("\nResults:")
        print(executor.format_results_as_table(results, columns))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        executor.close()
