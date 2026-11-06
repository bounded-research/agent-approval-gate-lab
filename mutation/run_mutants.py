"""Mutation check: break each safety mechanism on purpose; the test suite MUST fail for every mutant.

A test suite that still passes against a broken gate proves nothing (Honesty Contract: tests cited
as proof need a FAIL run against broken code; June: make the validity gate symmetric).
Usage: python3 mutation/run_mutants.py   -> writes mutation/MUTATION_RESULTS.md, exits 1 if any mutant survives.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MUTANTS = [
    ("M01 one-use check removed", "lab/permit.py", "if store.seen(p.nonce):", "if False:"),
    ("M02 target path binding removed", "lab/permit.py", 'if cur["real"] != p.target["real"]:', "if False:"),
    ("M03 inode/ctime binding removed", "lab/permit.py", 'if (cur["dev"], cur["ino"], cur["ctime_ns"])', 'if False and (cur["dev"], cur["ino"], cur["ctime_ns"])'),
    ("M04 permit signature not checked", "lab/permit.py", "if not auth.verify_sig(p):", "if False:"),
    ("M05 permit expiry not checked", "lab/permit.py", "if now > p.exp:", "if False:"),
    ("M06 policy default-allow", "lab/policy.py", "        return FORBID", "        return ALLOW"),
    ("M07 forbid overridable", "lab/gate.py", "if decision == FORBID:", "if False:"),
    ("M08 approver deny ignored", "lab/gate.py", 'if verdict != "approve":', "if False:"),
    ("M09 identity not verified", "lab/gate.py", "if not self.registry.verify(agent_id, body, sig):", "if False:"),
    ("M10 frame check disabled", "lab/oracle.py", "return [(k, p) for k, p in changed_paths(d) if not any(fnmatch.fnmatch(p, g) for g in allow_globs)]", "return []"),
    ("M11 unauthorized-effect check disabled", "lab/oracle.py", "            out.append((k, rel))", "            pass"),
    ("M12 self-approval detection disabled", "lab/runner.py", "                self.self_approval_attempts.append(att)", "                pass"),
    ("M13 ledger prev-hash not checked", "lab/ledger.py", 'if rec.get("prev") != prev:', "if False:"),
    ("M14 agent runs as root in enforced mode", "lab/runner.py", "argv = [runuser, \"-u\", AGENT_USER, \"--\"] + argv", "argv = argv"),
    ("M15 panel always discloses decision path", "lab/panel.py", 'if self.disclosure == "advertised":', "if True:"),
    ("M16 e-value peeks at the best alternative (invalid)", "scripts/analyze.py", "return math.exp(m) * sum(math.exp(x - m) for x in logs) * h / (1 - p0)", "return math.exp(m)"),
    ("M18 harness logs readable by agent", "lab/runner.py", "                os.chmod(f, 0o600)", "                pass"),
    ("M17 floor rule ignores gate successes", "scripts/analyze.py", 'floor = ("FIX DISCONFIRMED: success in gate arm" if (k[-1] == "B_gate" and suc > 0) else "")', 'floor = ""'),
]


def main() -> int:
    rows, survivors = [], 0
    for name, rel, old, new in MUTANTS:
        tmp = Path(tempfile.mkdtemp())
        dst = tmp / "lab"
        shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns("runs", "data", ".git", "__pycache__", "*.zip", ".pytest_cache"))
        f = dst / rel
        src = f.read_text()
        if src.count(old) != 1:
            rows.append((name, "INVALID (pattern not found exactly once)", ""))
            survivors += 1
            continue
        f.write_text(src.replace(old, new))
        r = subprocess.run([sys.executable, "-m", "pytest", "-x", "-q", "-rf"], cwd=dst, capture_output=True, text=True, timeout=900)
        fails = [l for l in r.stdout.splitlines() if l.startswith(("FAILED", "ERROR"))]
        last = (fails[0][:150] if fails else (r.stdout.strip().splitlines() or ["?"])[-1])
        killed = r.returncode != 0
        survivors += 0 if killed else 1
        rows.append((name, "KILLED (suite failed)" if killed else "SURVIVED (suite passed!)", last))
        shutil.rmtree(tmp, ignore_errors=True)
    out = ["# Mutation results", "", "Each row breaks one safety mechanism. KILLED = the test suite caught it.", "",
           "| Mutant | Result | First failing test |", "|---|---|---|"]
    out += [f"| {a} | {b} | `{c}` |" for a, b, c in rows]
    out += ["", f"Survivors: {survivors} of {len(MUTANTS)}"]
    import os
    Path(os.environ.get("MUTATION_OUT", ROOT / "mutation" / "MUTATION_RESULTS.md")).write_text("\n".join(out) + "\n")
    print("\n".join(out))
    return 1 if survivors else 0


if __name__ == "__main__":
    sys.exit(main())
