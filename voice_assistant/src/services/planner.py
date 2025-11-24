from typing import List, Optional

from src.config import Settings
from src.services.llm_client import make_client
from src.services.tools import ToolCall


def plan_with_llm(text: str, settings: Settings, allowed_tools: List[str]) -> Optional[List[ToolCall]]:
    client = make_client(settings)
    if not client:
        return None

    system_prompt = (
        "You are a tool planner for a personal assistant. "
        "Given a user request, output a JSON array of tool calls. "
        f"Allowed tools: {', '.join(allowed_tools)}. "
        "Each item must include: tool (string), content (string), amount (number or null), when (string or null). "
        "Only include tools from the allowed list. "
        "Split multi-intent requests into multiple tool calls in logical order. "
        "Use null for fields you cannot infer. Keep content concise and actionable."
    )

    try:
        response = client.chat.completions.create(
            model=_model_name(settings),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            max_tokens=160,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content
        if not raw:
            return None
        data = _parse_json(raw)
        if not data:
            return None
        items = data if isinstance(data, list) else [data]
        calls: List[ToolCall] = []
        for item in items:
            tool = item.get("tool")
            if tool not in allowed_tools:
                continue
            calls.append(
                ToolCall(
                    tool=tool,
                    content=item.get("content") or text,
                    amount=item.get("amount"),
                    when=item.get("when"),
                )
            )
        return calls or None
    except Exception:
        return None


def _parse_json(raw: str):
    import json

    try:
        return json.loads(raw)
    except Exception:
        return None


def _model_name(settings: Settings) -> str:
    if settings.azure_openai_endpoint and settings.azure_openai_key:
        return settings.azure_openai_model
    return settings.openai_model
