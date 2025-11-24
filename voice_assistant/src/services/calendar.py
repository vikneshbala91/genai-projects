from datetime import datetime, timedelta
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

from src.config import Settings


def _credentials(settings: Settings):
    scopes = ["https://www.googleapis.com/auth/calendar"]
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


def create_reminder(settings: Settings, summary: str, when: Optional[str]) -> None:
    # If we cannot parse a time, schedule 30 minutes from now to keep the UX predictable.
    start_time = _parse_when(settings, when)
    end_time = start_time + timedelta(minutes=30)

    service = build("calendar", "v3", credentials=_credentials(settings))
    event_body = {
        "summary": summary,
        "start": {"dateTime": start_time.isoformat(), "timeZone": settings.timezone},
        "end": {"dateTime": end_time.isoformat(), "timeZone": settings.timezone},
    }
    service.events().insert(calendarId=settings.calendar_id, body=event_body).execute()


def _parse_when(settings: Settings, when: Optional[str]) -> datetime:
    now = datetime.now().astimezone()
    if not when:
        return now + timedelta(minutes=30)

    lowered = when.lower()
    if "tomorrow" in lowered:
        candidate = now + timedelta(days=1)
        return candidate.replace(hour=9, minute=0, second=0, microsecond=0)
    if "today" in lowered:
        return now.replace(hour=9, minute=0, second=0, microsecond=0)

    # Simple HH:MM parsing with optional am/pm.
    for meridiem in ["am", "pm"]:
        if meridiem in lowered:
            lowered = lowered.replace(meridiem, "").strip()
            try:
                hour, minute = [int(part) for part in lowered.split(":")]
                if meridiem == "pm" and hour < 12:
                    hour += 12
                return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            except Exception:
                return now + timedelta(minutes=30)

    try:
        hour, minute = [int(part) for part in lowered.split(":")]
        return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    except Exception:
        return now + timedelta(minutes=30)
