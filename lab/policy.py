"""Default-deny policy with three classes: allow, require_approval, forbid.

Rules match on (action, path prefix of the *canonical* target). First match wins;
no match -> forbid. A permit can never override `forbid`.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

ALLOW, REQUIRE, FORBID = "allow", "require_approval", "forbid"


@dataclass(frozen=True)
class Rule:
    action: str          # e.g. "delete", "write", "read", "exec", or "*"
    prefix: str          # canonical path prefix
    decision: str


class Policy:
    def __init__(self, rules: list[Rule]):
        for r in rules:
            if r.decision not in (ALLOW, REQUIRE, FORBID):
                raise ValueError(f"bad decision {r.decision}")
        self.rules = rules

    def decide(self, action: str, target_path: str) -> str:
        real = os.path.realpath(target_path)
        for r in self.rules:
            pref = os.path.realpath(r.prefix)
            inside = real == pref or real.startswith(pref.rstrip(os.sep) + os.sep)
            if (r.action in ("*", action)) and inside:
                return r.decision
        return FORBID
