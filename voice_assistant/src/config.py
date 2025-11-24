import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv


@dataclass
class Settings:
    credentials_path: Optional[Path]
    notes_sheet_id: str
    transactions_sheet_id: str
    calendar_id: str
    timezone: str
    openai_api_key: Optional[str]
    openai_model: str
    azure_openai_key: Optional[str]
    azure_openai_endpoint: Optional[str]
    azure_openai_model: str
    azure_openai_api_version: str
    service_account_info: Optional[Dict[str, Any]]
    oauth_client_info: Optional[Dict[str, Any]]
    oauth_token_path: Optional[Path]


def load_settings() -> Settings:
    load_dotenv()

    credentials_raw = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    credentials_path = Path(credentials_raw).expanduser() if credentials_raw else None
    service_account_info = _load_service_account_json()
    oauth_client_info = _load_oauth_client_json()
    oauth_token_path = (
        Path(os.environ.get("GOOGLE_OAUTH_TOKEN_FILE", "token.json")).expanduser()
        if oauth_client_info
        else None
    )

    return Settings(
        credentials_path=credentials_path if credentials_raw else None,
        notes_sheet_id=os.environ.get("NOTES_SHEET_ID", "").strip(),
        transactions_sheet_id=os.environ.get("TRANSACTIONS_SHEET_ID", "").strip(),
        calendar_id=os.environ.get("GOOGLE_CALENDAR_ID", "primary").strip(),
        timezone=os.environ.get("TIMEZONE", "UTC").strip(),
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
        openai_model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        azure_openai_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        azure_openai_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        azure_openai_model=os.environ.get("AZURE_OPENAI_MODEL")
        or os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT")
        or "gpt-4o-mini",
        azure_openai_api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-06-01"),
        service_account_info=service_account_info,
        oauth_client_info=oauth_client_info,
        oauth_token_path=oauth_token_path,
    )


def _load_service_account_json() -> Optional[Dict[str, Any]]:
    raw = (
        os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        or ""
    ).strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def _load_oauth_client_json() -> Optional[Dict[str, Any]]:
    raw = (
        os.environ.get("GOOGLE_OAUTH_CLIENT_JSON")
        or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON_OAUTH")
        or ""
    ).strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None
