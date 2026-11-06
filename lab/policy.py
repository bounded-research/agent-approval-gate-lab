"""Fail-closed policy with explicit allow/require/forbid and a separate no-match result.

Rules match on (action, path prefix of the *canonical* target). First match wins;
No match or malformed request -> unrecognized_request. Nothing executes on no-match.
A permit can never override an explicit `forbid`.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

ALLOW, REQUIRE, FORBID, UNRECOGNIZED = "allow", "require_approval", "forbid", "unrecognized_request"
VALID_ACTIONS = ("delete", "write")
TARGET_GUIDANCE = "Target must be the exact absolute path of one existing file or directory, nothing else."


def unrecognized_fields() -> dict:
    return {"why": UNRECOGNIZED, "valid_actions": list(VALID_ACTIONS), "target_guidance": TARGET_GUIDANCE}


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
        if action not in VALID_ACTIONS or not isinstance(target_path, str) or \
                not os.path.isabs(target_path) or target_path != os.path.abspath(target_path) or \
                not (os.path.isfile(target_path) or os.path.isdir(target_path)):
            return UNRECOGNIZED
        real = os.path.realpath(target_path)
        for r in self.rules:
            pref = os.path.realpath(r.prefix)
            inside = real == pref or real.startswith(pref.rstrip(os.sep) + os.sep)
            if (r.action in ("*", action)) and inside:
                return r.decision
        return UNRECOGNIZED
