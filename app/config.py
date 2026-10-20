"""Settings come from environment variables only. Nothing secret has a default."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    environment: str
    version: str
    azure_connection_string: str | None
    azure_container: str


def get_settings() -> Settings:
    return Settings(
        environment=os.getenv("ENVIRONMENT", "local"),
        version=os.getenv("APP_VERSION", "dev"),
        azure_connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING") or None,
        azure_container=os.getenv("AZURE_CONTAINER", "files"),
    )
