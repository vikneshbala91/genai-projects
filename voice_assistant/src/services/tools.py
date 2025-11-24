from dataclasses import dataclass
from typing import List, Optional

from src import intents
from src.services import calendar, search, sheets


@dataclass
class ToolCall:
    tool: str
    content: str
    amount: Optional[float] = None
    when: Optional[str] = None


def registry():
    """Map tool names to callables that perform the action."""
    return {
        "note": lambda settings, call: sheets.append_note(settings, call.content),
        "transaction": lambda settings, call: sheets.append_transaction(
            settings, call.content, call.amount
        ),
        "read_transactions": lambda settings, call: sheets.read_sheet(
            settings, settings.transactions_sheet_id, "VoiceAssistant Transactions", limit=5
        ),
        "read_notes": lambda settings, call: sheets.read_sheet(
            settings, settings.notes_sheet_id, "VoiceAssistant Notes", limit=5
        ),
        "search": lambda settings, call: search.search_web(call.content),
        "reminder": lambda settings, call: calendar.create_reminder(
            settings, call.content, call.when
        ),
        "exit": lambda settings, call: "exit",
    }


def intent_to_tool_calls(intent_list: List[intents.Intent]) -> List[ToolCall]:
    calls: List[ToolCall] = []
    for intent in intent_list:
        calls.append(
            ToolCall(
                tool=intent.type.value,
                content=intent.content,
                amount=intent.amount,
                when=intent.when,
            )
        )
    return calls
