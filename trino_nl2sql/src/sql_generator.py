"""
SQL Generator using LangChain and Azure OpenAI
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from schema_loader import SchemaLoader

logger = logging.getLogger(__name__)


class SQLGenerator:
    """Generate SQL queries from natural language using LLM"""

    def __init__(self, schema_file: str = None):
        # Load environment variables
        self._load_env()

        # Initialize schema loader
        self.schema_loader = SchemaLoader(schema_file)
        self.schema_context = self.schema_loader.get_schema_context()

        # Initialize LLM
        self.llm = AzureChatOpenAI(
            azure_deployment=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"],
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            temperature=0.0,  # Low temperature for consistent SQL generation
        )

        # Create prompt template
        self.prompt = self._create_prompt()

        # Create chain
        self.chain = self.prompt | self.llm | StrOutputParser()

    def _load_env(self):
        """Load environment variables"""
        # Clear existing Azure OpenAI vars
        for key in list(os.environ.keys()):
            if key.startswith('AZURE_OPENAI'):
                del os.environ[key]

        # Load from .env file in project root
        project_root = Path(__file__).parent.parent.parent
        env_path = project_root / ".env"
        load_dotenv(dotenv_path=env_path)

    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the SQL generation prompt"""
        template = """You are a SQL expert specializing in Trino SQL dialect.
Your task is to convert natural language questions into valid Trino SQL queries.

# Database Schema:
{schema}

# Important Rules:
1. Generate ONLY valid Trino SQL syntax
2. Use proper table names with catalog.schema prefix if needed
3. Always use standard SQL functions compatible with Trino
4. For date operations, use Trino date functions (date_add, date_diff, etc.)
5. Use LIMIT clause to restrict result size when appropriate
6. Return ONLY the SQL query, no explanations or markdown
7. Do not use backticks or code blocks
8. Ensure the query is safe (no DROP, DELETE, or TRUNCATE operations)

# Examples:
Question: "Show me all customers"
SQL: SELECT * FROM customers LIMIT 100

Question: "How many orders were placed last month?"
SQL: SELECT COUNT(*) as order_count FROM orders WHERE order_date >= date_add('month', -1, current_date) AND order_date < current_date

Question: "What are the top 5 customers by total order value?"
SQL: SELECT c.customer_id, c.name, SUM(o.total_amount) as total_spent FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id, c.name ORDER BY total_spent DESC LIMIT 5

# User Question:
{question}

# SQL Query:"""

        return ChatPromptTemplate.from_template(template)

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
            sql_query = self.chain.invoke({
                "schema": self.schema_context,
                "question": question
            })

            # Clean up the SQL query
            sql_query = sql_query.strip()

            # Remove markdown code blocks if present
            if sql_query.startswith("```"):
                lines = sql_query.split("\n")
                sql_query = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
                sql_query = sql_query.strip()

            logger.info(f"Generated SQL: {sql_query}")
            return sql_query

        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            raise


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
