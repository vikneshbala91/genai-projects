from typing import List, Optional

from src import intents
from src.config import Settings
from src.services.llm_client import make_client


def classify_with_llm(text: str, settings: Settings) -> Optional[List[intents.Intent]]:
    client = make_client(settings)
    if not client:
        return None

    system_prompt = (
        "You are an intent classifier for a voice assistant. "
        "You may receive one or multiple tasks in a single utterance. "
        "Split them into a list of intents; valid intent types: note, transaction, search, reminder, exit. "
        "Return JSON array of objects with: intent (string), amount (number or null), when (string or null), content (string). "
        "Content should echo the user request fragment without extra text. "
        "Amount should be parsed if the user mentions money. "
        "When should capture a simple time phrase if present. "
        "Only include intents you are confident about."
    )

    try:
        response = client.chat.completions.create(
            model=_model_name(settings),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            max_tokens=120,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content
        if not raw:
            return None
        data = _parse_json(raw)
        if not data:
            return None
        items = data if isinstance(data, list) else [data]
        intents_list: List[intents.Intent] = []
        for item in items:
            try:
                intent_type = intents.IntentType(item.get("intent", "unknown"))
            except Exception:
                intent_type = intents.IntentType.UNKNOWN
            intents_list.append(
                intents.Intent(
                    type=intent_type,
                    content=item.get("content", text),
                    amount=item.get("amount"),
                    when=item.get("when"),
                )
            )
        return intents_list or None
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
