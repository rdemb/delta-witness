#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEMO_ROOT="$(mktemp -d -t deltawitness-demo-XXXXXX)"
trap 'rm -rf "$DEMO_ROOT"' EXIT

cd "$DEMO_ROOT"
git init -b main >/dev/null
git config user.email demo@example.invalid
git config user.name "DeltaWitness Demo"
mkdir -p src tests

cat > src/access.py <<'PY'
def is_admin(user):
    return bool(user.get("role"))
PY

cat > tests/test_access.py <<'PY'
import sys
import unittest

sys.path.insert(0, "src")
from access import is_admin


class AccessTests(unittest.TestCase):
    def test_admin_is_allowed(self):
        self.assertTrue(is_admin({"role": "admin"}))
PY

cat > deltawitness.toml <<'TOML'
[paths]
code = ["src/**"]
tests = ["tests/**"]

[[claim]]
id = "role-check-regression"
description = "A viewer must not be treated as an administrator."
command = ["python", "-m", "unittest", "discover", "-s", "tests"]
timeout_seconds = 30

[claim.expect]
base_base = "pass"
base_candidate = "fail"
candidate_base = "pass"
candidate_candidate = "pass"
TOML

git add .
git commit -m "base: vulnerable role check" >/dev/null
BASE="$(git rev-parse HEAD)"

cat > src/access.py <<'PY'
def is_admin(user):
    return user.get("role") == "admin"
PY

cat >> tests/test_access.py <<'PY'

    def test_viewer_is_denied(self):
        self.assertFalse(is_admin({"role": "viewer"}))
PY

git add .
git commit -m "fix: require the admin role and add a regression witness" >/dev/null

PYTHONPATH="$PROJECT_ROOT/src" python -m deltawitness.cli verify \
  --repo "$DEMO_ROOT" \
  --base "$BASE" \
  --head HEAD \
  --spec deltawitness.toml \
  --output .deltawitness/report.json

PYTHONPATH="$PROJECT_ROOT/src" python -m deltawitness.cli verify-report \
  "$DEMO_ROOT/.deltawitness/report.json"
