# Voice Assistant Prototype

Minimal voice-driven personal assistant that routes spoken commands to Google Sheets, Google Calendar, or a lightweight web search. The prototype focuses on:
- Capturing speech (or typed fallback) to text
- Intent routing for notes, transactions, search, and reminders
- Writing rows to Google Sheets for notes/transactions
- Creating Calendar events/reminders
- Printing quick web search results

## Quick start

1) Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2) Google setup (service account recommended)
- Create a Google Cloud project and enable Sheets and Calendar APIs.
- Create a service account and download its JSON key.
- Share the target sheets with the service account email.
- For Calendar, grant access to the service account on the target calendar.

3) Configure environment
```bash
cp .env.example .env
# edit .env with your sheet IDs, calendar ID, timezone, and credentials path
# optional: set OPENAI_API_KEY and OPENAI_MODEL (default gpt-4o-mini) for LLM intent classification
# or configure Azure OpenAI instead:
# AZURE_OPENAI_API_KEY=...
# AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
# AZURE_OPENAI_MODEL=gpt-4o-mini   # use your Azure chat deployment name
# AZURE_OPENAI_API_VERSION=2024-06-01
# (back-compat: AZURE_OPENAI_CHAT_DEPLOYMENT is also read if present)
# For Google auth:
# - Service account: point to a file (GOOGLE_APPLICATION_CREDENTIALS) or paste JSON inline (GOOGLE_SERVICE_ACCOUNT_JSON).
# - OAuth client (user consent): paste client JSON as GOOGLE_OAUTH_CLIENT_JSON; the app will run a local consent flow and cache tokens in GOOGLE_OAUTH_TOKEN_FILE (default token.json).
```

4) Run the assistant
```bash
python -m src.main
```
Speak after the prompt. If the microphone is unavailable, the app falls back to typed input.

## What the prototype can do
- **Notes:** “Note that I need to buy groceries” → appends a row to the notes sheet.
- **Transactions:** “Transaction fifty dollars for lunch” → appends a row with amount parsed when possible. If the sheet ID is missing or not found, a new sheet is created and its ID is printed for reuse.
- **Search:** “Search best Thai food near me” → prints DuckDuckGo results in the console.
- **Reminder/Calendar:** “Set a reminder tomorrow 9am to call mom” → creates a calendar entry.
- **Exit:** Say “exit” or “quit” to stop.
- With `OPENAI_API_KEY` set, intent classification uses an LLM; otherwise falls back to rule-based heuristics.
- The LLM path can split multiple tasks in one utterance (e.g., “note to water plants and set reminder tomorrow 9am to call mom and search best Thai near me” will generate multiple intents executed sequentially).
- A lightweight planner now selects tools (note/transaction/search/reminder/exit) for multi-step requests. More advanced tool/agent behaviors can be added by expanding the planner prompt or tool registry in `src/services/planner.py` and `src/services/tools.py`.

## Limitations and next steps
- Speech recognition uses `SpeechRecognition` with Google Web Speech API by default; swap in an offline engine (e.g., Whisper/Vosk) if needed.
- Amount/time parsing is intentionally light; integrate a proper NLU/NLP model for accuracy.
- Web search is console-only; hook to a browser, vector search, or LLM-based answerer as needed.
- Add tests plus richer logging/telemetry when the prototype stabilizes.
