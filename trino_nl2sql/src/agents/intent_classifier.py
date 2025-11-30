"""
Lightweight intent classifier to decide whether to run SQL or ask clarifying questions.
"""
import json
import re
from typing import Dict, Any
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class IntentClassifier:
    """Classifies user input intent before running SQL generation."""

    def __init__(self, llm):
        self.prompt = self._create_prompt()
        self.chain = self.prompt | llm | StrOutputParser()

    def _create_prompt(self) -> ChatPromptTemplate:
        template = """You are an intent classifier in front of a data Q&A system.
Decide if the user message should trigger SQL generation, needs clarification, or is chit-chat.

Return STRICT JSON with keys:
- intent: one of ["data_query", "clarification_needed", "chitchat", "other"]
- follow_up: short clarifying question if intent is "clarification_needed", else "".

Rules:
- If the user greets or makes small talk, mark as "chitchat".
- If the request is ambiguous or lacks key filters/metrics, mark "clarification_needed" and propose a specific follow-up question.
- Otherwise use "data_query".
- If the message is a short greeting with no data nouns/metrics/tables (e.g., "hi", "hello", "hey there", "good morning", "what's up"), classify as "chitchat" — never run SQL for these.
- If the user just says "help", "what can you do", or similar, classify as "clarification_needed" and ask what they want to analyze.
- If the message is unrelated to the database (e.g., weather, news, personal opinions, jokes), classify as "other" and suggest asking a data question. Do not run SQL.
- Keep answers concise; do not add explanations outside JSON.

Examples:
- "hi" -> {"intent": "chitchat", "follow_up": ""}
- "hello there" -> {"intent": "chitchat", "follow_up": ""}
- "help" -> {"intent": "clarification_needed", "follow_up": "What dataset or metric should I explore for you?"}
- "show top 10 customers by revenue" -> {"intent": "data_query", "follow_up": ""}
- "can you tell me about sales?" -> {"intent": "clarification_needed", "follow_up": "Which region or time period for sales?"}
- "what's up" -> {"intent": "chitchat", "follow_up": ""}
- "what's the weather" -> {"intent": "other", "follow_up": "I can help with your database; what would you like to analyze?"}

User message: {question}
Respond with JSON only."""
        return ChatPromptTemplate.from_template(template)

    def _looks_like_non_data(self, question: str) -> bool:
        """Heuristic guardrail: short, non-analytic requests should not trigger SQL."""
        q = question.lower().strip()
        # Very short or greeting-like
        if len(q) <= 20 and not re.search(r"\d", q):
            return True
        # No common data verbs/nouns present
        data_tokens = ["show", "list", "count", "top", "total", "revenue", "sales", "orders", "customers", "table", "column", "metric", "trend", "average", "sum", "min", "max"]
        if not any(token in q for token in data_tokens):
            return True
        return False

    def classify(self, question: str) -> Dict[str, Any]:
        """Return a normalized intent dict."""
        try:
            raw = self.chain.invoke({"question": question}).strip()
            data = json.loads(raw)
        except Exception:
            data = {"intent": "data_query", "follow_up": ""}

        intent = data.get("intent", "data_query")
        follow_up = data.get("follow_up", "")

        # Heuristic backstop: if LLM thinks it's a data_query but it looks like small talk or off-topic, downgrade.
        if intent == "data_query" and self._looks_like_non_data(question):
            intent = "other"
            if not follow_up:
                follow_up = "I can help with your database; what would you like to analyze?"

        return {"intent": intent, "follow_up": follow_up}
