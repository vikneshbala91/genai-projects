from datetime import datetime
from typing import Optional, Tuple

import gspread
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from gspread import Worksheet
from gspread.exceptions import APIError

from src.config import Settings


def _credentials(settings: Settings):
    # Drive scope is included so we can create sheets when needed.
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    if settings.service_account_info:
        return service_account.Credentials.from_service_account_info(
            settings.service_account_info, scopes=scopes
        )
    if settings.credentials_path:
        return service_account.Credentials.from_service_account_file(
            str(settings.credentials_path), scopes=scopes
        )
    if settings.oauth_client_info:
        creds = None
        if settings.oauth_token_path and settings.oauth_token_path.exists():
            creds = Credentials.from_authorized_user_file(
                str(settings.oauth_token_path), scopes
            )
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(
                    settings.oauth_client_info, scopes
                )
                creds = flow.run_local_server(port=0)
            if settings.oauth_token_path:
                settings.oauth_token_path.parent.mkdir(parents=True, exist_ok=True)
                with open(settings.oauth_token_path, "w") as token:
                    token.write(creds.to_json())
        return creds
    raise FileNotFoundError(
        "Set GOOGLE_SERVICE_ACCOUNT_JSON/GOOGLE_APPLICATION_CREDENTIALS (service account) "
        "or GOOGLE_OAUTH_CLIENT_JSON (OAuth client)."
    )


def _ensure_sheet(
    settings: Settings, sheet_id: str, fallback_title: str
) -> Tuple[Worksheet, str]:
    client = gspread.authorize(_credentials(settings))
    if sheet_id:
        try:
            return client.open_by_key(sheet_id).sheet1, sheet_id
        except APIError:
            # If the sheet is missing or inaccessible, try creating a new one.
            pass

    spreadsheet = client.create(fallback_title)
    worksheet = spreadsheet.sheet1
    return worksheet, spreadsheet.id


def append_note(settings: Settings, text: str) -> None:
    sheet, new_id = _ensure_sheet(settings, settings.notes_sheet_id, "VoiceAssistant Notes")
    if not settings.notes_sheet_id:
        settings.notes_sheet_id = new_id
    sheet.append_row([datetime.utcnow().isoformat(), text], value_input_option="USER_ENTERED")


def append_transaction(settings: Settings, text: str, amount: Optional[float]) -> None:
    sheet, new_id = _ensure_sheet(settings, settings.transactions_sheet_id, "VoiceAssistant Transactions")
    if not settings.transactions_sheet_id:
        settings.transactions_sheet_id = new_id
    sheet.append_row(
        [datetime.utcnow().isoformat(), amount if amount is not None else "", text],
        value_input_option="USER_ENTERED",
    )


def read_sheet(settings: Settings, sheet_id: str, fallback_title: str, limit: int = 5):
    sheet, new_id = _ensure_sheet(settings, sheet_id, fallback_title)
    rows = sheet.get_all_values()[:limit]
    return new_id, rows
