"""Append-only, hash-chained event ledger.

Each line is a JSON object with `prev` = sha256 of the previous line (or "GENESIS").
The ledger is written by the harness/gate, never by the agent. `verify_chain` detects
edits, deletions, reordering and truncation-with-rewrite. It cannot detect truncation
of the tail by itself; the run record stores the final head hash and line count for that.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

GENESIS = "GENESIS"


def _h(line: str) -> str:
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


class Ledger:
    def __init__(self, path: str | os.PathLike):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def _last(self) -> tuple[str, int]:
        prev, n = GENESIS, 0
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if line:
                    prev, n = _h(line), n + 1
        return prev, n

    def append(self, event: str, **fields) -> dict:
        prev, n = self._last()
        rec = {"seq": n, "ts": time.time(), "event": event, "prev": prev, **fields}
        line = json.dumps(rec, sort_keys=True, separators=(",", ":"))
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
            f.flush()
            os.fsync(f.fileno())
        return rec

    def head(self) -> tuple[str, int]:
        """(hash of last line, number of lines) -- store this outside the ledger."""
        return self._last()

    def records(self) -> list[dict]:
        with self.path.open("r", encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]


def verify_chain(path: str | os.PathLike, expected_head: tuple[str, int] | None = None) -> tuple[bool, str]:
    prev, n = GENESIS, 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                return False, f"line {n}: not JSON"
            if rec.get("prev") != prev:
                return False, f"line {n}: prev mismatch"
            if rec.get("seq") != n:
                return False, f"line {n}: seq mismatch"
            prev, n = _h(line), n + 1
    if expected_head is not None and (prev, n) != tuple(expected_head):
        return False, f"head mismatch: got ({prev[:12]}, {n}), expected ({expected_head[0][:12]}, {expected_head[1]})"
    return True, f"ok ({n} records)"
