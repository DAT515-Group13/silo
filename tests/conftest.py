import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import ObjectNotFound, get_storage


class InMemoryStorage:
    """Fake storage for tests: no network, no Azure account needed."""

    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.healthy = True
        self.fail_writes = False

    def ping(self) -> bool:
        return self.healthy

    def put(self, key: str, data: bytes) -> None:
        if self.fail_writes:
            raise RuntimeError("simulated storage failure")
        self.objects[key] = data

    def get(self, key: str) -> bytes:
        try:
            return self.objects[key]
        except KeyError as exc:
            raise ObjectNotFound(key) from exc

    def delete(self, key: str) -> None:
        self.objects.pop(key, None)


@pytest.fixture
def storage() -> InMemoryStorage:
    return InMemoryStorage()


@pytest.fixture
def client(storage: InMemoryStorage):
    app.dependency_overrides[get_storage] = lambda: storage
    yield TestClient(app)
    app.dependency_overrides.clear()