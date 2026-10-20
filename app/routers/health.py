import logging
import time
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings, get_settings
from app.storage import StorageBackend, get_storage

log = logging.getLogger(__name__)
router = APIRouter()

SettingsDep = Annotated[Settings, Depends(get_settings)]
StorageDep = Annotated[StorageBackend | None, Depends(get_storage)]


@router.get("/healthz")
def healthz() -> dict:
    """Liveness: the process is up. Must NOT depend on external services."""
    return {"status": "ok"}


@router.get("/readyz")
def readyz(storage: StorageDep) -> dict:
    """Readiness: can we reach what we depend on (Azure Blob Storage)?"""
    if storage is None:
        raise HTTPException(status_code=503, detail="storage not configured")
    if not storage.ping():
        raise HTTPException(status_code=503, detail="storage unreachable")
    return {"status": "ready"}


@router.get("/version")
def version(settings: SettingsDep) -> dict:
    """Which build runs in which environment (the smoke test checks this)."""
    return {"environment": settings.environment, "version": settings.version}


@router.post("/selftest")
def selftest(storage: StorageDep, settings: SettingsDep) -> dict:
    """Write, read back and delete a tiny blob: proves cluster -> Azure Blob works.

    TEMPORARY endpoint for the test version. Remove or protect it before the
    real application goes live.
    """
    if storage is None:
        raise HTTPException(status_code=503, detail="storage not configured")
    key = f"selftest/{uuid.uuid4()}.txt"
    payload = f"hello from {settings.environment} at {time.time()}".encode()
    try:
        storage.put(key, payload)
        roundtrip_ok = storage.get(key) == payload
        storage.delete(key)
    except Exception as exc:
        log.exception("selftest failed")
        raise HTTPException(status_code=502, detail="storage operation failed") from exc
    if not roundtrip_ok:
        raise HTTPException(status_code=500, detail="stored bytes differ from uploaded bytes")
    return {"status": "ok", "key": key}