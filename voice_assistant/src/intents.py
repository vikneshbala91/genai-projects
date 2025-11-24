import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class IntentType(str, Enum):
    NOTE = "note"
    TRANSACTION = "transaction"
    SEARCH = "search"
    REMINDER = "reminder"
    EXIT = "exit"
    UNKNOWN = "unknown"


@dataclass
class Intent:
    type: IntentType
    content: str
    amount: Optional[float] = None
    when: Optional[str] = None


def classify_intents(text: str, settings) -> List[Intent]:
    from src.services.llm_intents import classify_with_llm

    llm_result = classify_with_llm(text, settings)
    if llm_result:
        return llm_result

    return [parse_intent_rule_based(text)]


def parse_intent_rule_based(text: str) -> Intent:
    lowered = text.lower().strip()

    if lowered in {"exit", "quit", "stop"}:
        return Intent(type=IntentType.EXIT, content=text)

    if "remind" in lowered or "calendar" in lowered:
        return Intent(type=IntentType.REMINDER, content=text, when=_extract_time(text))

    if "transaction" in lowered or "spent" in lowered or "pay" in lowered:
        return Intent(
            type=IntentType.TRANSACTION,
            content=text,
            amount=_extract_amount(text),
        )

    if lowered.startswith("search ") or "search for" in lowered or "look up" in lowered:
        return Intent(type=IntentType.SEARCH, content=_strip_prefix(lowered, text))

    if "note" in lowered or lowered.startswith("remember"):
        return Intent(type=IntentType.NOTE, content=text)

    return Intent(type=IntentType.UNKNOWN, content=text)


def _extract_amount(text: str) -> Optional[float]:
    match = re.search(r"(-?\\d+(?:\\.\\d+)?)", text.replace(",", ""))
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def _extract_time(text: str) -> Optional[str]:
    match = re.search(r"(today|tomorrow|\\d{1,2}:\\d{2}\\s*(?:am|pm)?)", text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def _strip_prefix(lowered: str, original: str) -> str:
    prefixes = ["search ", "search for ", "look up "]
    for prefix in prefixes:
        if lowered.startswith(prefix):
            return original[len(prefix) :].strip()
    return original.strip()
