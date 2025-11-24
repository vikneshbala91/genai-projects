from typing import Optional

from openai import AzureOpenAI, OpenAI

from src.config import Settings


def make_client(settings: Settings) -> Optional[OpenAI]:
    """
    Choose AzureOpenAI (if endpoint+key provided) else OpenAI (api key).
    """
    if settings.azure_openai_endpoint and settings.azure_openai_key:
        return AzureOpenAI(
            api_key=settings.azure_openai_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint.rstrip("/"),
        )
    if settings.openai_api_key:
        return OpenAI(api_key=settings.openai_api_key)
    return None
