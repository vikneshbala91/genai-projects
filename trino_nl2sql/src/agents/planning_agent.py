"""
Agent responsible for deciding whether to use a single query or a multi-CTE plan.
"""
import json
from typing import Dict, Any
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class PlanningAgent:
    """Decide whether a question needs a single query or a small multi-CTE plan."""

    def __init__(self, llm):
        self.prompt = self._create_prompt()
        self.chain = self.prompt | llm | StrOutputParser()

    def _create_prompt(self) -> ChatPromptTemplate:
        template = """You are a careful planner for generating Trino SQL. Decide if the user's question needs one SQL query, a single query with multiple CTEs, or multiple separate queries. Keep the plan minimal and safe.

Output STRICT JSON with keys:
- plan_type: "single", "multi_cte", or "multi_query"
- steps: array of objects: [{ "id": "q1", "objective": "<short description>", "tables": ["optional_table1","optional_table2"] }]
- final_instruction: short note on how to produce the final result (if single, restate the goal; if multi, explain how CTEs should combine).

Constraints:
- Read-only analytics only (no INSERT/UPDATE/DELETE/DDL).
 - For multi_cte or multi_query keep 2-3 steps max.
- Only include tables that match the catalog/schema provided.

Catalog: {catalog}
Schema: {schema_name}
Fully-qualified: {database}

Schema summary:
{schema_context}

User question: {question}

Respond with JSON only."""
        return ChatPromptTemplate.from_template(template)

    def plan(
        self,
        *,
        question: str,
        schema_context: str,
        catalog: str,
        schema_name: str,
        database: str,
    ) -> Dict[str, Any]:
        """Return normalized plan dict."""
        try:
            raw = self.chain.invoke(
                {
                    "schema_context": schema_context,
                    "question": question,
                    "catalog": catalog,
                    "schema_name": schema_name,
                    "database": database,
                }
            ).strip()
            plan = json.loads(raw)
        except Exception:
            # Fallback to single-step plan on any parsing/LLM failure
            plan = {
                "plan_type": "single",
                "steps": [{"id": "q1", "objective": question}],
                "final_instruction": "Answer the question in one query",
            }

        plan_type = plan.get("plan_type", "single")
        steps = plan.get("steps") or [{"id": "q1", "objective": question}]
        final_instruction = plan.get("final_instruction") or "Produce the final answer from the steps."
        return {"plan_type": plan_type, "steps": steps, "final_instruction": final_instruction}

    @staticmethod
    def format_for_prompt(plan: Dict[str, Any]) -> str:
        """Pretty-print plan for use inside the SQL prompt."""
        lines = [f"plan_type: {plan.get('plan_type', 'single')}"]
        for step in plan.get("steps", []):
            step_id = step.get("id", "q1")
            objective = step.get("objective", "")
            tables = ", ".join(step.get("tables", []))
            table_info = f" tables: {tables}" if tables else ""
            lines.append(f"{step_id}: {objective}{table_info}")
        lines.append(f"final_instruction: {plan.get('final_instruction', '')}")
        return "\n".join(lines)
