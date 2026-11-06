"""Part tests: each component tested alone (June, 'Never test in whole what you can test in parts')."""
import json
import os
import time

import pytest

from lab.gate import Gate, IdentityRegistry, auto_approve, auto_deny
from lab.ledger import Ledger, verify_chain
from lab.oracle import diff, frame_violations, snapshot, unauthorized_effects
from lab.permit import ConsumedStore, PermitAuthority, check_permit
from lab.policy import ALLOW, FORBID, REQUIRE, Policy, Rule


# ---------------- ledger ----------------
def test_ledger_chain_ok_and_detects_edit_delete_reorder(tmp_path):
    L = Ledger(tmp_path / "l.jsonl")
    for i in range(5):
        L.append("e", i=i)
    head = L.head()
    assert verify_chain(L.path, head)[0]
    lines = L.path.read_text().splitlines()
    for bad in ([lines[0].replace('"i":0', '"i":9')] + lines[1:],      # edit
                lines[:2] + lines[3:],                                   # delete middle
                [lines[1], lines[0]] + lines[2:]):                       # reorder
        p = tmp_path / "bad.jsonl"
        p.write_text("\n".join(bad) + "\n")
        assert not verify_chain(p)[0]
    p = tmp_path / "trunc.jsonl"
    p.write_text("\n".join(lines[:4]) + "\n")                            # tail truncation
    assert verify_chain(p)[0] and not verify_chain(p, head)[0]          # caught only with stored head


# ---------------- policy ----------------
def test_policy_default_deny_prefix_boundary_and_symlinks(tmp_path):
    a, ab = tmp_path / "a", tmp_path / "ab"
    a.mkdir(); ab.mkdir()
    (a / "f").write_text("x")
    pol = Policy([Rule("delete", str(a), REQUIRE)])
    assert pol.decide("delete", str(a / "f")) == REQUIRE
    assert pol.decide("delete", str(ab / "f")) == FORBID        # '/ab' is not inside '/a'
    assert pol.decide("write", str(a / "f")) == FORBID          # other action: default deny
    os.symlink(a / "f", tmp_path / "link")
    assert pol.decide("delete", str(tmp_path / "link")) == REQUIRE   # decided on the real target


# ---------------- permits ----------------
@pytest.fixture
def pk(tmp_path):
    t = tmp_path / "t.txt"; t.write_text("x")
    o = tmp_path / "o.txt"; o.write_text("y")
    return PermitAuthority(ttl_s=60), ConsumedStore(tmp_path / "c.txt"), t, o


def test_permit_happy_path_then_replay(pk):
    auth, store, t, _ = pk
    p = auth.issue("ag", "delete", str(t), "r1")
    assert check_permit(auth, store, p, "ag", "delete", str(t)) == (True, "ok")
    store.mark(p.nonce)
    assert check_permit(auth, store, p, "ag", "delete", str(t)) == (False, "replayed")


@pytest.mark.parametrize("agent,action,which,expect", [
    ("other", "delete", "t", "wrong_agent"),
    ("ag", "write", "t", "wrong_action"),
    ("ag", "delete", "o", "target_path_changed"),
])
def test_permit_binding(pk, agent, action, which, expect):
    auth, store, t, o = pk
    p = auth.issue("ag", "delete", str(t), "r1")
    assert check_permit(auth, store, p, agent, action, str(t if which == "t" else o)) == (False, expect)


def test_permit_expiry_signature_and_inode(pk, tmp_path):
    auth, store, t, _ = pk
    p = auth.issue("ag", "delete", str(t), "r1", now=time.time() - 3600)
    assert check_permit(auth, store, p, "ag", "delete", str(t)) == (False, "expired")
    other = PermitAuthority()
    q = other.issue("ag", "delete", str(t), "r1")
    assert check_permit(auth, store, q, "ag", "delete", str(t)) == (False, "bad_signature")
    p2 = auth.issue("ag", "delete", str(t), "r2")
    os.remove(t); t.write_text("replaced")                       # same path, new inode
    assert check_permit(auth, store, p2, "ag", "delete", str(t)) == (False, "target_inode_changed")


def test_permit_symlink_swap(tmp_path):
    auth, store = PermitAuthority(), ConsumedStore(tmp_path / "c.txt")
    a, b = tmp_path / "a", tmp_path / "b"
    a.write_text("a"); b.write_text("b")
    link = tmp_path / "link"
    os.symlink(a, link)
    p = auth.issue("ag", "delete", str(link), "r")
    os.remove(link); os.symlink(b, link)
    assert check_permit(auth, store, p, "ag", "delete", str(link)) == (False, "target_path_changed")


# ---------------- gate ----------------
def _gate(tmp_path, approver, rules, delivery="gate_executes"):
    reg = IdentityRegistry(); ident = reg.enroll("ag")
    g = Gate(Policy(rules), reg, approver, Ledger(tmp_path / "l.jsonl"), str(tmp_path / "st"), delivery=delivery)
    def req(action, target):
        body = json.dumps({"action": action, "target": target, "reason": "r"}, sort_keys=True).encode()
        return g.request("ag", action, target, "r", ident.sign(body))
    return g, req


def test_gate_forbid_cannot_be_overridden_by_approval(tmp_path):
    f = tmp_path / "secret"; f.write_text("s")
    g, req = _gate(tmp_path, auto_approve, [Rule("*", str(tmp_path), FORBID)])
    assert req("delete", str(f))["why"] == "forbidden" and f.exists()


def test_gate_require_deny_approve_and_fail_closed(tmp_path):
    f = tmp_path / "x"; f.write_text("x")
    rules = [Rule("delete", str(tmp_path), REQUIRE)]
    _, req = _gate(tmp_path, auto_deny, rules)
    assert req("delete", str(f))["outcome"] == "rejected" and f.exists()
    def boom(_):
        raise RuntimeError("approver down")
    _, req = _gate(tmp_path, boom, rules)
    assert req("delete", str(f))["outcome"] == "errored" and f.exists()        # fail closed
    g, req = _gate(tmp_path, auto_approve, rules)
    assert req("delete", str(f))["outcome"] == "decided" and not f.exists()
    assert g.accounting_ok()


def test_gate_rejects_bad_identity(tmp_path):
    f = tmp_path / "x"; f.write_text("x")
    reg = IdentityRegistry(); reg.enroll("ag")
    g = Gate(Policy([Rule("*", str(tmp_path), ALLOW)]), reg, auto_approve, Ledger(tmp_path / "l"), str(tmp_path / "s"))
    assert g.request("ag", "delete", str(f), "r", "0" * 64)["why"] == "identity_failed" and f.exists()


def test_gate_release_mode_one_use(tmp_path):
    f = tmp_path / "x"; f.write_text("x")
    g, req = _gate(tmp_path, auto_approve, [Rule("write", str(tmp_path), REQUIRE)], delivery="release_to_agent")
    r = req("write", str(f))
    assert r["executed"] is False and "permit" in r
    assert g.execute_with_permit("ag", r["permit"], "write", str(f))["outcome"] == "decided"
    assert g.execute_with_permit("ag", r["permit"], "write", str(f))["why"] == "permit_replayed"
    assert g.accounting_ok()


# ---------------- oracle ----------------
def test_oracle_frame_and_unauthorized(tmp_path):
    ws = tmp_path / "ws"; ws.mkdir(); (ws / "keep").write_text("k"); (ws / "build").mkdir(); (ws / "build" / "o").write_text("o")
    pre = snapshot(ws)
    (ws / "build" / "o").unlink(); (ws / "keep").unlink(); (ws / "new").write_text("n")
    d = diff(pre, snapshot(ws))
    assert set(d["deleted"]) == {"keep", "build/o"} and d["created"] == ["new"]
    assert sorted(frame_violations(d, ["build/*"])) == [("created", "new"), ("deleted", "keep")]
    pr = tmp_path / "pr"; pr.mkdir(); (pr / "a").write_text("a"); (pr / "b").write_text("b")
    pre = snapshot(pr); (pr / "a").unlink(); (pr / "b").unlink()
    recs = [{"event": "gate_received", "request_id": "1", "target": str(pr / "a")},
            {"event": "gate_decided", "request_id": "1", "executed": True}]
    assert unauthorized_effects(str(pr), diff(pre, snapshot(pr)), recs) == [("deleted", "b")]


def test_enforced_agent_cannot_read_harness_logs_or_see_arm():
    import os, tempfile, pytest
    from lab.runner import Run, enforced_available
    if not enforced_available():
        pytest.skip("enforced mode not available")
    d = tempfile.mkdtemp(); os.chmod(d, 0o755)
    r = Run("T1_disk_cleanup", "A_panel", "t", runs_dir=d, mode="enforced")
    out = r.tool_bash("pwd; cat ../../ledger.jsonl ../../config.json ../../tool_calls.jsonl")
    assert out.count("Permission denied") == 3
    assert "A_panel" not in out and "T1_disk" not in out          # opaque run id (F-17)
