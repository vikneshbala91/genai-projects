"""
Agent responsible for generating Trino SQL from the question and an optional plan.
"""
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class SQLBuilderAgent:
    """Generate Trino SQL given schema context and an optional plan."""

    def __init__(self, llm):
        self.prompt = self._create_prompt()
        self.chain = self.prompt | llm | StrOutputParser()

    def _create_prompt(self) -> ChatPromptTemplate:
        template = """You are a SQL expert specializing in the Trino SQL dialect.
Your task is to convert natural language questions into valid Trino SQL queries ONLY using Trino-supported syntax.

# Database:
Catalog: {catalog}
Schema: {schema_name}
Fully-qualified: {database}

# Database Schema:
{schema_context}

# Plan:
{plan_context}

# Important Rules:
1. Generate ONLY valid Trino SQL syntax — avoid constructs from MySQL, SQL Server, Oracle, or PostgreSQL that Trino does not support.
2. Do NOT use `TOP`, `LIMIT` with `WITH TIES`, `AUTO_INCREMENT`, `IFNULL`, `STR_TO_DATE`, `DATE_SUB`, `GETDATE()`, `NOW()`, `INTERVAL` expressions, or backticks (`). Replace them with Trino equivalents (e.g., `date_add`, `date_diff`, `current_date`, `current_timestamp`).
3. Use proper table identifiers; prefer unquoted lower-case names or double-quoted identifiers only when necessary.
4. For date operations, use Trino date/time functions such as `date_add`, `date_diff`, `current_date`, `current_timestamp`.
5. Use the `LIMIT` clause to restrict result size when appropriate (Trino supports `LIMIT`).
6. Return ONLY the SQL query, no explanations, no markdown, no surrounding code fences.
7. Ensure the query is read-only and safe: do not generate `DROP`, `DELETE`, `TRUNCATE`, `UPDATE`, `MERGE`, or DDL statements.
8. Prefer `CAST(... AS type)` for conversions (avoid the `::type` syntax) and `COUNT(*)` for counts.
9. If the user asks to list tables, use `information_schema.tables` filtered by the catalog/schema above. Example: SELECT table_name FROM <catalog>.information_schema.tables WHERE table_schema = '<schema_name>' ORDER BY table_name;
10. If the user asks to list columns for a table, use `information_schema.columns` filtered by `table_schema` and `table_name`.
11. If the plan_type is multi_cte, use CTEs named after the step ids (e.g., WITH q1 AS (...), q2 AS (...)) and produce a final SELECT that combines them per the plan. Keep the number of CTEs small and avoid duplicate work.

# User Question:
{question}

# SQL Query:"""
        return ChatPromptTemplate.from_template(template)

    def build(
        self,
        *,
        question: str,
        schema_context: str,
        plan_context: str,
        catalog: str,
        schema_name: str,
        database: str,
    ) -> str:
        return self.chain.invoke(
            {
                "schema_context": schema_context,
                "question": question,
                "catalog": catalog,
                "schema_name": schema_name,
                "database": database,
                "plan_context": plan_context,
            }
        )
