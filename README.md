# agent-approval-gate-lab

A small, reproducible lab for one known agent-safety break and one candidate fix.

**The break (reproduced, not discovered here).** METR's per-action monitor write-up reports a coding
agent that, unprompted, opened the human review panel meant to approve its own flagged actions and
sent keystrokes to it. METR lists "enforcement / authentication to ensure only humans are able to
review these flagged actions" as missing. METR did **not** report a successful self-approval. This lab
rebuilds that failure class: a review channel the reviewed agent can write to.

**The candidate fix.** An approval gate outside the agent's reach:
harness-held agent identity (the agent never sees its key), a default-deny policy
(`allow` / `require_approval` / `forbid`), an independent approver, and one-use HMAC permits bound to
agent, action, canonical path, file identity (dev, inode, ctime) and expiry. Two delivery modes:
the gate performs the action, or it releases a one-use permit to the agent (an MFA-style flow).

**What is proven so far** (by scripted agents, not by models; see `audit/SELF_AUDIT_RESULTS.md`):
- the vulnerable panel lets a scripted agent approve its own request and the action executes;
- the gate records the same attempt and nothing happens;
- forged, replayed and symlink-swapped permits are rejected;
- with the OS boundary on, a shell route around the gate changes nothing; without it, the oracle flags the change as unauthorized;
- every safety check is load-bearing: 18 of 18 deliberate code mutations make the test suite fail (`mutation/MUTATION_RESULTS.md`).

**What is not proven:** anything about how often a real model attempts this. No live model run has
happened. That is Phase 1, preregistered in `prereg/P1_PREREG.md`.

## Quick start

```bash
python3 -m pip install pytest            # only dependency (stdlib otherwise)
bash scripts/verify.sh                   # tests + self-audit + manifest; nonzero exit on any failure
sudo bash scripts/setup_enforced.sh      # optional: creates user 'labagent' so the OS boundary is real
sudo -E bash scripts/verify.sh           # rerun with enforced mode included
```

Live runs (Phase 1; read the prereg first and commit before running):
```bash
export ANTHROPIC_API_KEY=...             # never commit keys; the agent process never sees them
sudo -E python3 scripts/run_trials.py --phase P1 --arm A_panel --backend anthropic \
     --model <model-id> --stratum S --n 10 --seed 1
git add data runs && git commit -m "P1 batch 1 raw"     # commit raw BEFORE analysis
python3 scripts/analyze.py
```

## Map

| Path | What |
|---|---|
| `CHARTER.md` | purpose, scope, ethics, what this lab will and won't claim |
| `docs/PLAN.md` | phases and decision tree |
| `docs/ARCHITECTURE.md` | components, trust boundaries, modes |
| `docs/FAILURE_MODES.md` | registry of known ways this lab can fool itself |
| `docs/JUNE_DISCIPLINES.md` | each discipline we follow and where it lives in the repo |
| `docs/PRIOR_WORK.md` | sources, with what was and wasn't verified |
| `prereg/` | Phase 1 preregistration, 22-question checklist, deviations log |
| `spec/features/` | implementation-agnostic behaviour specs (definition of done) |
| `lab/` | gate, permit, policy, ledger, oracle, vulnerable panel, runner, agents |
| `tasks/` | three tasks, each with a protected resource, a forbidden resource and a gold path |
| `tests/` | parts tests, frozen expectation matrix, adapter and analysis tests |
| `mutation/` | mutation check: break each mechanism, confirm a test fails |
| `scripts/` | verify, self-audit, trial runner, analysis, enforced-mode setup |
| `audit/` | self-audit results (passed / failed / unresolved / not-tested) |
| `data/` | append-only trial records (empty until Phase 1) |
| `WORKLOG.md` | dated record of every session, including mistakes |

## Honest limits

File-state oracle only: reads, exfiltration and network are not observed. Container mode is written
but untested (no Docker daemon in the build environment). The vulnerable panel is a file-based model
of METR's setup, not a copy of it. See `audit/SELF_AUDIT_RESULTS.md` § Not tested.

License: not yet chosen (owner's decision before publishing).
