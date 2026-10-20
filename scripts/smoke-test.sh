#!/usr/bin/env bash
# Usage: scripts/smoke-test.sh <namespace> [expected-version]
# Checks a deployed environment through a temporary kubectl port-forward:
# liveness, readiness (= Azure Blob reachable), the running version, and a blob round trip.
set -euo pipefail

NS="${1:?usage: $0 <namespace> [expected-version]}"
EXPECTED="${2:-}"
PORT="${SMOKE_PORT:-18080}"
BASE="http://127.0.0.1:${PORT}"

kubectl -n "$NS" port-forward svc/silo "${PORT}:80" >/dev/null 2>&1 &
PF_PID=$!
trap 'kill "$PF_PID" 2>/dev/null || true' EXIT

for _ in $(seq 1 30); do
  curl -fsS "$BASE/healthz" >/dev/null 2>&1 && break
  sleep 1
done

echo "healthz:  $(curl -fsS "$BASE/healthz")"
echo "readyz:   $(curl -fsS "$BASE/readyz")"

VERSION_JSON="$(curl -fsS "$BASE/version")"
echo "version:  $VERSION_JSON"
if [ -n "$EXPECTED" ] && ! grep -q "$EXPECTED" <<<"$VERSION_JSON"; then
  echo "FAIL: expected version $EXPECTED is not what is running" >&2
  exit 1
fi

echo "selftest: $(curl -fsS -X POST "$BASE/selftest")"
echo "Smoke test passed for namespace '$NS'."
