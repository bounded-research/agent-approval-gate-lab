"""Action-bound, one-use permits.

A permit authorizes exactly one (agent_id, action, target, request_id) before `exp`.
The target is bound by canonical real path AND (device, inode) at request time, so a
symlink swap or rename between approval and execution is detected at consume time.
Permits are HMAC-signed with a key held only by the approver side; the agent never sees it.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import asdict, dataclass
from pathlib import Path


def target_identity(path: str) -> dict:
    """Canonical identity of a filesystem target. Missing targets have ino=None."""
    real = os.path.realpath(path)
    try:
        st = os.lstat(real)
        # ctime_ns is included because inode numbers are reused: delete + recreate at the same path can
        # yield the same (dev, ino). A recreated or modified target gets a new ctime. (Found by
        # tests/test_parts.py::test_permit_expiry_signature_and_inode on 2026-11-05; see WORKLOG.)
        return {"real": real, "dev": st.st_dev, "ino": st.st_ino, "ctime_ns": st.st_ctime_ns}
    except FileNotFoundError:
        return {"real": real, "dev": None, "ino": None, "ctime_ns": None}


@dataclass(frozen=True)
class Permit:
    agent_id: str
    action: str
    target: dict          # output of target_identity at request time
    request_id: str
    exp: float
    nonce: str
    sig: str = ""

    def body(self) -> bytes:
        d = asdict(self)
        d.pop("sig")
        return json.dumps(d, sort_keys=True, separators=(",", ":")).encode()


class PermitAuthority:
    """Lives with the approver, outside the agent's box. Holds the signing key."""

    def __init__(self, key: bytes | None = None, ttl_s: float = 120.0):
        self._key = key or secrets.token_bytes(32)
        self.ttl_s = ttl_s

    def issue(self, agent_id: str, action: str, target_path: str, request_id: str, now: float | None = None) -> Permit:
        now = time.time() if now is None else now
        p = Permit(agent_id, action, target_identity(target_path), request_id, now + self.ttl_s, secrets.token_hex(16))
        sig = hmac.new(self._key, p.body(), hashlib.sha256).hexdigest()
        return Permit(**{**asdict(p), "sig": sig})

    def verify_sig(self, p: Permit) -> bool:
        good = hmac.new(self._key, p.body(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(good, p.sig)


class ConsumedStore:
    """One-use enforcement. Append-only file of consumed nonces (kept outside the agent's box)."""

    def __init__(self, path: str | os.PathLike):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def seen(self, nonce: str) -> bool:
        return nonce in self.path.read_text().split()

    def mark(self, nonce: str) -> None:
        with self.path.open("a") as f:
            f.write(nonce + "\n")


def check_permit(auth: PermitAuthority, store: ConsumedStore, p: Permit, agent_id: str, action: str,
                 target_path: str, now: float | None = None) -> tuple[bool, str]:
    """Return (ok, reason). Order: signature, one-use, binding, freshness (so reasons are specific)."""
    now = time.time() if now is None else now
    if not auth.verify_sig(p):
        return False, "bad_signature"
    if store.seen(p.nonce):
        return False, "replayed"
    if p.agent_id != agent_id:
        return False, "wrong_agent"
    if p.action != action:
        return False, "wrong_action"
    cur = target_identity(target_path)
    if cur["real"] != p.target["real"]:
        return False, "target_path_changed"
    if (cur["dev"], cur["ino"], cur["ctime_ns"]) != (p.target.get("dev"), p.target.get("ino"), p.target.get("ctime_ns")):
        return False, "target_inode_changed"
    if now > p.exp:
        return False, "expired"
    return True, "ok"
