"""
SQL Generator using LangChain and Azure OpenAI
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from schema_loader import SchemaLoader
from agents import PlanningAgent, SQLBuilderAgent, SQLValidatorAgent

logger = logging.getLogger(__name__)


class SQLGenerator:
    """Generate SQL queries from natural language using LLM"""

    def __init__(self, schema_file: str = None, use_dynamic_schema: bool = True):
        """
        Initialize SQL Generator

        Args:
            schema_file: Path to YAML file with business descriptions (optional)
            use_dynamic_schema: If True, fetch schema dynamically from Trino (default: True)
        """
        # Load environment variables
        self._load_env()

        # Initialize schema loader with dynamic schema support
        self.schema_loader = SchemaLoader(schema_file, use_dynamic_schema=use_dynamic_schema)
        self.schema_context = self.schema_loader.get_schema_context()
        self.database_name = self.schema_loader.get_database_name()
        self.catalog, self.schema_name = self._parse_catalog_schema(self.database_name)

        # Initialize LLM
        self.llm = AzureChatOpenAI(
            azure_deployment=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"],
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            temperature=0.0,  # Low temperature for consistent SQL generation
        )

        # Agents
        self.planner = PlanningAgent(self.llm)
        self.sql_builder = SQLBuilderAgent(self.llm)
        self.validator = SQLValidatorAgent(self.sql_builder)

    def _load_env(self):
        """Load environment variables"""
        # Clear existing Azure OpenAI vars to avoid mixing environments
        for key in list(os.environ.keys()):
            if key.startswith('AZURE_OPENAI'):
                del os.environ[key]

        # Load from .env file in project root (trino_nl2sql)
        project_root = Path(__file__).parent.parent
        env_path = project_root / ".env"
        load_dotenv(dotenv_path=env_path)

    def generate_sql(self, question: str) -> str:
        """
        Generate SQL query from natural language question

        Args:
            question: Natural language question

        Returns:
            Generated SQL query string
        """
        logger.info(f"Generating SQL for question: {question}")

        try:
            plan = self.planner.plan(
                question=question,
                schema_context=self.schema_context,
                catalog=self.catalog or "",
                schema_name=self.schema_name or "",
                database=self.database_name or "",
            )
            plan_context = self.planner.format_for_prompt(plan)

            # Multi-query path: build and validate each step separately
            if plan.get("plan_type") == "multi_query":
                sql_tasks = []
                for step in plan.get("steps", []):
                    step_id = step.get("id", "q1")
                    objective = step.get("objective", question)
                    step_plan_context = (
                        f"plan_type: multi_query\n"
                        f"step: {step_id}\n"
                        f"objective: {objective}\n"
                        f"final_instruction: {plan.get('final_instruction', '')}"
                    )
                    step_question = f"{question}\nSub-task {step_id}: {objective}"

                    sql = self.sql_builder.build(
                        question=step_question,
                        schema_context=self.schema_context,
                        catalog=self.catalog or "",
                        schema_name=self.schema_name or "",
                        database=self.database_name or "",
                        plan_context=step_plan_context,
                    )
                    sql = self.validator.validate(
                        sql,
                        question=step_question,
                        schema_context=self.schema_context,
                        plan_context=step_plan_context,
                        catalog=self.catalog or "",
                        schema_name=self.schema_name or "",
                        database=self.database_name or "",
                    )
                    sql_tasks.append(
                        {"id": step_id, "objective": objective, "sql": sql}
                    )

                logger.info(f"Generated {len(sql_tasks)} SQL statements for multi_query plan.")
                return sql_tasks

            # First attempt
            sql_query = self.sql_builder.build(
                question=question,
                schema_context=self.schema_context,
                catalog=self.catalog or "",
                schema_name=self.schema_name or "",
                database=self.database_name or "",
                plan_context=plan_context,
            )

            # Post-process and validate compatibility with Trino
            sql_query = self.validator.validate(
                sql_query,
                question=question,
                schema_context=self.schema_context,
                plan_context=plan_context,
                catalog=self.catalog or "",
                schema_name=self.schema_name or "",
                database=self.database_name or "",
            )

            logger.info(f"Generated SQL: {sql_query}")
            return sql_query

        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            raise


    def _parse_catalog_schema(self, database: str):
        """Extract catalog and schema names from fully qualified database string."""
        if not database or "." not in database:
            return None, None
        parts = database.split(".", 1)
        catalog = parts[0]
        schema = parts[1] if len(parts) > 1 else None
        return catalog, schema

if __name__ == "__main__":
    # Test the SQL generator
    logging.basicConfig(level=logging.INFO)

    generator = SQLGenerator()

    test_questions = [
        "Show me all customers",
        "How many orders were placed last month?",
        "What are the top 5 products by price?",
    ]

    for question in test_questions:
        print(f"\nQuestion: {question}")
        sql = generator.generate_sql(question)
        print(f"SQL: {sql}\n")
