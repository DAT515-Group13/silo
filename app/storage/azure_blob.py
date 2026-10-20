"""Azure Blob Storage implementation of StorageBackend."""

from azure.core.exceptions import AzureError, ResourceNotFoundError
from azure.storage.blob import BlobServiceClient

from app.storage.base import ObjectNotFound


class AzureBlobStorage:
    def __init__(self, connection_string: str, container: str) -> None:
        # Short timeouts and few retries so a broken network fails fast
        # (readiness probes must not hang).
        service = BlobServiceClient.from_connection_string(
            connection_string, retry_total=2, connection_timeout=5, read_timeout=15
        )
        self._container = service.get_container_client(container)

    def ping(self) -> bool:
        try:
            self._container.get_container_properties()
            return True
        except AzureError:
            return False

    def put(self, key: str, data: bytes) -> None:
        self._container.upload_blob(name=key, data=data, overwrite=True)

    def get(self, key: str) -> bytes:
        try:
            return self._container.download_blob(key).readall()
        except ResourceNotFoundError as exc:
            raise ObjectNotFound(key) from exc

    def delete(self, key: str) -> None:
        try:
            self._container.delete_blob(key)
        except ResourceNotFoundError:
            pass