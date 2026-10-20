import logging
from functools import lru_cache

from app.config import get_settings
from app.storage.base import ObjectNotFound, StorageBackend

__all__ = ["ObjectNotFound", "StorageBackend", "get_storage"]

log = logging.getLogger(__name__)


@lru_cache
def _azure(connection_string: str, container: str) -> StorageBackend:
    from app.storage.azure_blob import AzureBlobStorage

    return AzureBlobStorage(connection_string, container)


def get_storage() -> StorageBackend | None:
    """FastAPI dependency. Returns None when storage is not configured."""
    settings = get_settings()
    if settings.azure_connection_string is None:
        return None
    try:
        return _azure(settings.azure_connection_string, settings.azure_container)
    except ValueError:
        log.error("AZURE_STORAGE_CONNECTION_STRING is not a valid connection string")
        return None