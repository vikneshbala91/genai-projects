"""
Format query results into plain English explanations
"""
import os
import logging
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)


class ResultFormatter:
    """Convert query results into plain English explanations"""

    def __init__(self):
        self._load_env()

        # Initialize LLM
        self.llm = AzureChatOpenAI(
            azure_deployment=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"],
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            temperature=0.3,  # Slightly higher for natural language
        )

        # Create prompt template
        self.prompt = self._create_prompt()

        # Create chain
        self.chain = self.prompt | self.llm | StrOutputParser()

    def _load_env(self):
        """Load environment variables"""
        for key in list(os.environ.keys()):
            if key.startswith('AZURE_OPENAI'):
                del os.environ[key]

        project_root = Path(__file__).parent.parent.parent
        env_path = project_root / ".env"
        load_dotenv(dotenv_path=env_path)

    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the result explanation prompt"""
        template = """You are a helpful data analyst assistant.
Your task is to explain query results in plain, easy-to-understand English.

# User's Question:
{question}

# SQL Query Executed:
{sql_query}

# Query Results:
{results}

# Instructions:
1. Provide a clear, concise explanation of what the results show
2. Highlight key findings or patterns
3. Use plain language, avoid technical jargon
4. If results are empty, explain why that might be
5. Keep the response concise (2-4 sentences)

# Your Explanation:"""

        return ChatPromptTemplate.from_template(template)

    def explain_results(
        self,
        question: str,
        sql_query: str,
        results: List[Dict],
        max_rows_to_show: int = 10
    ) -> str:
        """
        Generate plain English explanation of query results

        Args:
            question: Original natural language question
            sql_query: SQL query that was executed
            results: Query results as list of dicts
            max_rows_to_show: Maximum number of rows to include in explanation

        Returns:
            Plain English explanation
        """
        try:
            # Limit results for context
            results_summary = results[:max_rows_to_show]

            # Format results for prompt
            if not results:
                results_str = "No rows returned"
            elif len(results) == 1:
                results_str = f"1 row:\n{results[0]}"
            else:
                results_str = f"{len(results)} rows (showing first {len(results_summary)}):\n"
                for i, row in enumerate(results_summary, 1):
                    results_str += f"{i}. {row}\n"

            explanation = self.chain.invoke({
                "question": question,
                "sql_query": sql_query,
                "results": results_str
            })

            return explanation.strip()

        except Exception as e:
            logger.error(f"Error formatting results: {e}")
            return "I found the data, but had trouble explaining it. Please check the table below."
