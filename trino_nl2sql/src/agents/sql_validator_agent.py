"""
Agent responsible for validating and, when possible, repairing generated SQL to be Trino-safe.
Runs lightweight local checks first and only reuses the builder when non-Trino constructs are detected.
"""
import logging
import re
from typing import List


class SQLValidatorAgent:
    """Validate Trino SQL; optionally retry via the SQL builder when issues are detected."""

    def __init__(self, sql_builder):
        self.sql_builder = sql_builder
        self.logger = logging.getLogger(__name__)

    def validate(
        self,
        sql_query: str,
        *,
        question: str,
        schema_context: str,
        plan_context: str,
        catalog: str,
        schema_name: str,
        database: str,
    ) -> str:
        """Normalize, detect issues, and retry once if non-Trino constructs are present."""
        sql_query = sql_query.strip()
        sql_query = self._strip_code_fences(sql_query)
        sql_query = self._normalize_common_functions(sql_query)

        issues = self._detect_non_trino(sql_query)
        if issues:
            self.logger.warning(f"Detected non-Trino constructs: {issues}. Attempting one automatic retry.")
            note = (
                "The previous SQL used non-Trino constructs: " + ", ".join(issues) + ". "
                "Rewrite the query using only Trino-supported syntax (use date_add/date_diff/current_date/current_timestamp), "
                "remove backticks, avoid :: casts, and do not include explanation. Return only the SQL query."
            )
            retry_question = note + "\nUser Question: " + question

            retry_sql = self.sql_builder.build(
                question=retry_question,
                schema_context=schema_context,
                catalog=catalog,
                schema_name=schema_name,
                database=database,
                plan_context=plan_context,
            )
            retry_sql = self._strip_code_fences(retry_sql.strip())
            retry_sql = self._normalize_common_functions(retry_sql)

            issues_after = self._detect_non_trino(retry_sql)
            if issues_after:
                self.logger.error(f"Retry still contains non-Trino constructs: {issues_after}")
                raise ValueError(f"Generated SQL contains non-Trino constructs: {issues_after}")

            return retry_sql

        return sql_query

    @staticmethod
    def _strip_code_fences(sql: str) -> str:
        if not sql.startswith("```"):
            return sql
        lines = sql.split("\n")
        return "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:]).strip()

    @staticmethod
    def _normalize_common_functions(sql: str) -> str:
        # Replace common non-Trino function calls with Trino equivalents
        replacements = [
            (r"\bNOW\s*\(\s*\)", "current_timestamp"),
            (r"\bGETDATE\s*\(\s*\)", "current_timestamp"),
            (r"\bSYSDATE\s*\(\s*\)", "current_timestamp"),
            (r"\bIFNULL\s*\(", "coalesce("),
            (r"\bISNULL\s*\(", "coalesce("),
            (r"\bNVL\s*\(", "coalesce("),
        ]
        for pat, repl in replacements:
            sql = re.sub(pat, repl, sql, flags=re.IGNORECASE)

        # Remove Postgres-style casts like col::int
        sql = re.sub(r"(\w+)\s*::\s*(\w+)", r"CAST(\1 AS \2)", sql)

        # Remove backticks if any (Trino prefers double quotes or unquoted identifiers)
        sql = sql.replace("`", "")
        return sql

    @staticmethod
    def _detect_non_trino(sql: str) -> List[str]:
        issues = []
        checks = {
            "backticks": r"`",
            "top_clause": r"\bTOP\b",
            "date_sub": r"\bDATE_SUB\b",
            "str_to_date": r"\bSTR_TO_DATE\b",
            "getdate_now": r"\b(NOW\(|GETDATE\(|SYSDATE\()",
            "interval_keyword": r"\bINTERVAL\b",
            "auto_increment": r"\bAUTO_INCREMENT\b",
            "ifnull": r"\bIFNULL\b",
            "isnull": r"\bISNULL\b",
            "nvl": r"\bNVL\s*\(",
            "from_unixtime": r"\bFROM_UNIXTIME\b",
            "unix_timestamp": r"\bUNIX_TIMESTAMP\b",
            "with_ties": r"\bWITH\s+TIES\b",
            "postgres_cast": r"::\s*\w+",
            "ddl": r"\b(DROP|TRUNCATE|DELETE|UPDATE|MERGE|ALTER|CREATE)\b",
        }

        for name, pattern in checks.items():
            if re.search(pattern, sql, flags=re.IGNORECASE):
                issues.append(name)

        return issues
