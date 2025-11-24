from dataclasses import dataclass
from typing import Optional

import speech_recognition as sr

from src import intents
from src.config import load_settings
from src.services import calendar, planner, search, sheets, speech, tools


@dataclass
class Context:
    settings: object
    recognizer: sr.Recognizer


def handle_intent(intent: intents.Intent, ctx: Context) -> bool:
    """Returns False when the loop should exit."""
    if intent.type == intents.IntentType.EXIT:
        print("Exiting. Bye!")
        return False

    if intent.type == intents.IntentType.NOTE:
        if ctx.settings.notes_sheet_id:
            sheets.append_note(ctx.settings, intent.content)
            print("Saved note to sheet.")
        else:
            print("Notes sheet ID missing; set NOTES_SHEET_ID.")
        return True

    if intent.type == intents.IntentType.TRANSACTION:
        if ctx.settings.transactions_sheet_id:
            sheets.append_transaction(ctx.settings, intent.content, intent.amount)
            print("Saved transaction to sheet.")
        else:
            print("Transactions sheet ID missing; set TRANSACTIONS_SHEET_ID.")
        return True

    if intent.type == intents.IntentType.SEARCH:
        results = search.search_web(intent.content)
        print("Search results:")
        for idx, result in enumerate(results, start=1):
            print(f"{idx}. {result}")
        return True

    if intent.type == intents.IntentType.REMINDER:
        if ctx.settings.credentials_path:
            calendar.create_reminder(ctx.settings, intent.content, intent.when)
            print("Reminder added to calendar.")
        else:
            print("Calendar not configured; set GOOGLE_APPLICATION_CREDENTIALS.")
        return True

    print("🤔 Didn't understand. Say note/transaction/search/remind/exit.")
    return True


def main() -> None:
    settings = load_settings()
    recognizer = sr.Recognizer()
    ctx = Context(settings=settings, recognizer=recognizer)
    tool_registry = tools.registry()

    print("Voice assistant ready. Say 'exit' to quit.")
    while True:
        utterance: Optional[str] = speech.listen_for_text(ctx.recognizer)
        if not utterance:
            print("No input detected.")
            continue

        print(f"You said: {utterance}")
        # Prefer an LLM plan that can select multiple tools; otherwise fall back to intent classification.
        tool_plan = planner.plan_with_llm(utterance, ctx.settings, allowed_tools=list(tool_registry.keys()))
        if tool_plan:
            for call in tool_plan:
                tool_fn = tool_registry.get(call.tool)
                if not tool_fn:
                    print(f"Unknown tool requested: {call.tool}")
                    continue
                result = tool_fn(ctx.settings, call)
                if call.tool == "search" and result:
                    print("Search results:")
                    for idx, item in enumerate(result, start=1):
                        print(f"{idx}. {item}")
                if call.tool in {"read_transactions", "read_notes"} and result:
                    sheet_id, rows = result
                    print(f"{call.tool} (sheet id: {sheet_id}):")
                    for row in rows:
                        print(row)
                if call.tool == "exit" or result == "exit":
                    print("Exiting. Bye!")
                    return
            continue

        intent_list = intents.classify_intents(utterance, ctx.settings)
        for intent in intent_list:
            if not handle_intent(intent, ctx):
                return


if __name__ == "__main__":
    main()
