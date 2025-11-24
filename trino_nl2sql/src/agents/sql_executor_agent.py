"""
Agent wrapper for executing Trino SQL with basic safety checks.
"""
import logging
import re
from typing import Tuple, List, Dict
from trino_executor import TrinoExecutor


class SQLExecutorAgent:
    """Run Trino SQL after basic read-only validation."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.executor = TrinoExecutor()

    @staticmethod
    def _strip_trailing_semicolon(sql: str) -> str:
        """Remove trailing semicolons/spaces to avoid Trino parse errors."""
        return sql.rstrip().rstrip(";").rstrip()

    def _ensure_read_only(self, sql: str):
        """Block obvious DDL/DML/merge patterns."""
        dangerous = re.search(r"\b(DROP|TRUNCATE|DELETE|UPDATE|MERGE|ALTER|CREATE|INSERT|REPLACE)\b", sql, flags=re.IGNORECASE)
        if dangerous:
            raise ValueError("Unsafe SQL detected (non-read-only).")

    def execute(self, sql: str) -> Tuple[List[Dict], List[str]]:
        sql = self._strip_trailing_semicolon(sql.strip())
        self._ensure_read_only(sql)
        return self.executor.execute_query(sql)

    def format_results_as_html(self, results: List[Dict], columns: List[str]) -> str:
        return self.executor.format_results_as_html(results, columns)

    def close(self):
        self.executor.close()
