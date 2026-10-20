"""The contract every storage backend must follow.

The rest of the application only talks to this interface, so Azure Blob can be
swapped for another backend (or an in-memory fake in tests) without other changes.
"""

from typing import Protocol


class ObjectNotFound(Exception):
    """The requested object does not exist in storage."""


class StorageBackend(Protocol):
    def ping(self) -> bool:
        """True if the storage can be reached right now."""

    def put(self, key: str, data: bytes) -> None: ...

    def get(self, key: str) -> bytes:
        """Return the object's bytes or raise ObjectNotFound."""

    def delete(self, key: str) -> None:
        """Delete the object. Deleting a missing object is not an error."""
