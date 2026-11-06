#!/usr/bin/env bash
# Fail-closed verification. Exit 0 only if EVERY step passes. Any failure -> nonzero exit.
#   bash scripts/verify.sh          tests, spec links, self-audit, manifest, redaction scan
#   bash scripts/verify.sh --full   also the mutation check (slower, ~5 min)
# Run as root (sudo -E) after scripts/setup_enforced.sh to include enforced-mode tests.
set -euo pipefail
cd "$(dirname "$0")/.."
FULL=0; [[ "${1:-}" == "--full" ]] && FULL=1
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
fail() { echo "VERIFY FAILED: $*" >&2; exit 1; }

echo "== 1. manifest (files match MANIFEST.sha256)"
[[ -f MANIFEST.sha256 ]] || fail "MANIFEST.sha256 missing"
sha256sum --quiet -c MANIFEST.sha256 || fail "manifest mismatch"

echo "== 2. redaction scan (no personal names, emails or phone numbers)"
python3 scripts/redaction_scan.py || fail "redaction scan"

echo "== 3. test suite"
python3 -m pytest -p no:cacheprovider || fail "pytest"

echo "== 4. spec -> test links"
python3 scripts/check_specs.py || fail "spec links"

echo "== 5. self-audit (output to temp dir; committed audit/ is the reference)"
AUDIT_OUT="$TMP/audit" python3 scripts/self_audit.py || fail "self-audit"

if [[ $FULL == 1 ]]; then
  echo "== 6. mutation check"
  MUTATION_OUT="$TMP/MUTATION_RESULTS.md" python3 mutation/run_mutants.py || fail "mutation survivors"
fi

python3 -c "from lab.runner import enforced_available as e; print('enforced mode available:', e())"
echo "VERIFY OK"
