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

cat > src/banner.py <<'PY'
VERSION = 1
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

[execution]
pass_env = ["PYTHONPATH"]

[[claim]]
id = "role-check-regression"
description = "A viewer must not be treated as an administrator."
observer = "outcome-receipt-v1"
command = ["python", "-m", "deltawitness.unittest_probe", "--start-directory", "tests", "--verbosity", "0"]
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

cat > src/banner.py <<'PY'
VERSION = 2
PY

cat >> tests/test_access.py <<'PY'

    def test_viewer_is_denied(self):
        self.assertFalse(is_admin({"role": "viewer"}))
PY

git add .
git commit -m "fix: require admin role, update banner, and add a regression witness" >/dev/null

PYTHONPATH="$PROJECT_ROOT/src" python -m deltawitness.cli verify \
  --repo "$DEMO_ROOT" \
  --base "$BASE" \
  --head HEAD \
  --spec deltawitness.toml

MATRIX_REPORT="$(git rev-parse --git-path deltawitness/report.json)"
PYTHONPATH="$PROJECT_ROOT/src" python -m deltawitness.cli verify-report "$MATRIX_REPORT"

if git status --porcelain=v1 | grep -q .; then
  echo "DeltaWitness demo error: matrix verification dirtied the working tree" >&2
  git status --short >&2
  exit 1
fi

PYTHONPATH="$PROJECT_ROOT/src" python -m deltawitness.cli influence \
  --repo "$DEMO_ROOT" \
  --base "$BASE" \
  --head HEAD \
  --spec deltawitness.toml

INFLUENCE_REPORT="$(git rev-parse --git-path deltawitness/influence.json)"
PYTHONPATH="$PROJECT_ROOT/src" python -m deltawitness.cli verify-report "$INFLUENCE_REPORT"

if git status --porcelain=v1 | grep -q .; then
  echo "DeltaWitness demo error: influence analysis dirtied the working tree" >&2
  git status --short >&2
  exit 1
fi

printf '%s\n' "DeltaWitness end-to-end demonstration passed."
