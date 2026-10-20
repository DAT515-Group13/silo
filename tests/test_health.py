from app.main import app
from app.storage import get_storage


def test_healthz_is_ok(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz_ok_when_storage_reachable(client):
    assert client.get("/readyz").status_code == 200


def test_readyz_503_when_storage_down(client, storage):
    storage.healthy = False
    assert client.get("/readyz").status_code == 503


def test_readyz_503_when_storage_not_configured(client):
    app.dependency_overrides[get_storage] = lambda: None
    assert client.get("/readyz").status_code == 503


def test_version_reports_environment_and_build(client, monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setenv("APP_VERSION", "abc123")
    assert client.get("/version").json() == {"environment": "staging", "version": "abc123"}


def test_selftest_roundtrip_leaves_no_blob_behind(client, storage):
    response = client.post("/selftest")
    assert response.status_code == 200
    assert storage.objects == {}


def test_selftest_reports_storage_failure(client, storage):
    storage.fail_writes = True
    assert client.post("/selftest").status_code == 502
