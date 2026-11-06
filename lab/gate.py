"""The approval gate (treatment arm B) and the executor for protected actions.

Flow for one request:
  agent tool call -> harness signs with the agent's identity (agent never holds the key)
  -> Gate.request(): verify identity, policy decision
       allow            -> execute now
       forbid           -> reject (a permit can never override forbid)
       require_approval -> ask the Approver (outside the box); approve -> permit; deny/timeout -> reject
  -> delivery mode
       "gate_executes"     : the gate consumes the permit and executes immediately (recommended)
       "release_to_agent"  : the permit token is released to the agent, which must present it to
                             Gate.execute_with_permit() (Nick's MFA-style design); binding + one-use apply
Every decision is one of three outcomes (June, "Make No Mistakes"): decided / errored / rejected.
Interface accounting: received == decided + errored + rejected + pending, checked by `accounting_ok`.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import shutil
import uuid
from dataclasses import asdict, dataclass, field
from typing import Callable

from .ledger import Ledger
from .permit import ConsumedStore, Permit, PermitAuthority, check_permit
from .policy import ALLOW, FORBID, REQUIRE, Policy

DECIDED, ERRORED, REJECTED = "decided", "errored", "rejected"


# ---------------- identity (held by the harness, never by the agent) ----------------
class IdentityRegistry:
    def __init__(self):
        self._keys: dict[str, bytes] = {}

    def enroll(self, agent_id: str) -> "AgentIdentity":
        key = os.urandom(32)
        self._keys[agent_id] = key
        return AgentIdentity(agent_id, key)

    def verify(self, agent_id: str, payload: bytes, sig: str) -> bool:
        key = self._keys.get(agent_id)
        if key is None:
            return False
        return hmac.compare_digest(hmac.new(key, payload, hashlib.sha256).hexdigest(), sig)


@dataclass
class AgentIdentity:
    agent_id: str
    _key: bytes = field(repr=False)

    def sign(self, payload: bytes) -> str:
        return hmac.new(self._key, payload, hashlib.sha256).hexdigest()


# ---------------- approver (outside the box) ----------------
Approver = Callable[[dict], str]   # request dict -> "approve" | "deny" | "timeout"


def auto_deny(_req: dict) -> str:
    return "deny"


def auto_approve(_req: dict) -> str:
    return "approve"


def human_cli_approver(req: dict) -> str:  # pragma: no cover - interactive
    """Out-of-band human approval on the operator's own terminal (not reachable from the agent box).
    Swap this for an SMS/push/passkey channel; the rule is that the agent cannot read or answer it."""
    print(json.dumps(req, indent=2))
    ans = input("approve this exact action? [y/N] ").strip().lower()
    return "approve" if ans == "y" else "deny"


# ---------------- executor ----------------
def execute_protected(action: str, target: str, payload: str | None = None) -> None:
    if action == "delete":
        if os.path.isdir(target) and not os.path.islink(target):
            shutil.rmtree(target)
        else:
            os.remove(target)
    elif action == "write":
        with open(target, "w") as f:
            f.write(payload or "")
    else:
        raise ValueError(f"unsupported action {action}")


@dataclass
class Counters:
    received: int = 0
    decided: int = 0
    errored: int = 0
    rejected: int = 0
    pending: int = 0


class Gate:
    def __init__(self, policy: Policy, registry: IdentityRegistry, approver: Approver, ledger: Ledger,
                 state_dir: str, delivery: str = "gate_executes", permit_ttl_s: float = 120.0):
        assert delivery in ("gate_executes", "release_to_agent")
        self.policy, self.registry, self.approver, self.ledger = policy, registry, approver, ledger
        self.authority = PermitAuthority(ttl_s=permit_ttl_s)
        self.consumed = ConsumedStore(os.path.join(state_dir, "consumed_nonces.txt"))
        self.delivery = delivery
        self.c = Counters()

    # -- helpers
    def _out(self, outcome: str, rid: str, **kw) -> dict:
        setattr(self.c, outcome, getattr(self.c, outcome) + 1)
        self.ledger.append(f"gate_{outcome}", request_id=rid, **kw)
        return {"outcome": outcome, "request_id": rid, **kw}

    def accounting_ok(self) -> bool:
        c = self.c
        return c.received == c.decided + c.errored + c.rejected + c.pending

    # -- main entry
    def request(self, agent_id: str, action: str, target: str, reason: str, sig: str,
                payload: str | None = None) -> dict:
        rid = uuid.uuid4().hex[:12]
        self.c.received += 1
        body = json.dumps({"action": action, "target": target, "reason": reason}, sort_keys=True).encode()
        self.ledger.append("gate_received", request_id=rid, agent_id=agent_id, action=action, target=target, reason=reason)
        if not self.registry.verify(agent_id, body, sig):
            return self._out(REJECTED, rid, why="identity_failed")
        decision = self.policy.decide(action, target)
        self.ledger.append("gate_policy", request_id=rid, decision=decision)
        if decision == FORBID:
            return self._out(REJECTED, rid, why="forbidden")
        if decision == ALLOW:
            try:
                execute_protected(action, target, payload)
            except Exception as e:  # fail visibly, never silently
                return self._out(ERRORED, rid, why=f"exec_error:{type(e).__name__}")
            return self._out(DECIDED, rid, why="allowed", executed=True)
        # REQUIRE
        self.c.pending += 1
        req = {"request_id": rid, "agent_id": agent_id, "action": action,
               "target": os.path.realpath(target), "reason": reason}
        try:
            verdict = self.approver(req)
        except Exception as e:
            self.c.pending -= 1
            return self._out(ERRORED, rid, why=f"approver_error:{type(e).__name__}")
        self.c.pending -= 1
        self.ledger.append("gate_approver", request_id=rid, verdict=verdict)
        if verdict != "approve":                      # deny, timeout, anything else -> fail closed
            return self._out(REJECTED, rid, why=f"approver_{verdict}")
        permit = self.authority.issue(agent_id, action, target, rid)
        self.ledger.append("permit_issued", request_id=rid, nonce=permit.nonce, target=permit.target)
        if self.delivery == "release_to_agent":
            return self._out(DECIDED, rid, why="permit_released", executed=False, permit=asdict(permit))
        return self._consume_and_execute(permit, agent_id, action, target, payload, rid)

    def execute_with_permit(self, agent_id: str, permit: dict, action: str, target: str,
                            payload: str | None = None) -> dict:
        """Release mode: the agent presents a permit. Counted as a new interface event."""
        rid = permit.get("request_id", "?")
        self.c.received += 1
        try:
            p = Permit(**permit)
        except TypeError:
            return self._out(REJECTED, rid, why="malformed_permit")
        return self._consume_and_execute(p, agent_id, action, target, payload, rid)

    def _consume_and_execute(self, p: Permit, agent_id, action, target, payload, rid) -> dict:
        ok, why = check_permit(self.authority, self.consumed, p, agent_id, action, target)
        if not ok:
            return self._out(REJECTED, rid, why=f"permit_{why}")
        self.consumed.mark(p.nonce)
        try:
            execute_protected(action, target, payload)
        except Exception as e:
            return self._out(ERRORED, rid, why=f"exec_error:{type(e).__name__}")
        return self._out(DECIDED, rid, why="approved_and_executed", executed=True, nonce=p.nonce)
