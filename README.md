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

**What the scripted instrument checks show** (see `audit/SELF_AUDIT_RESULTS.md` and the owner-machine audit):
- the vulnerable panel lets a scripted agent approve its own request and the action executes;
- the gate records the same attempt and nothing happens;
- forged, replayed and symlink-swapped permits are rejected;
- with the OS boundary on, a shell route around the gate changes nothing; without it, the oracle flags the change as unauthorized;
- every safety check is load-bearing: 18 of 18 deliberate code mutations make the test suite fail (`mutation/MUTATION_RESULTS.md`).

**Live result:** 40 exploratory, hidden-panel `qwen3.8-27b` runs in enforced networkless
containers recorded 0 self-approval attempts (20 neutral, 20 pressure). Nine runs inspected or named
the panel; 39/40 completed the file-level task check. The 0/20 cells do not establish a low attempt
rate. No live Phase 2 gate comparison was run. See `RESULTS_2026-11-06.md` and the two dated audits.
The current-session results are exploratory because the owner prediction was blank and D-006/D-007
changed model/adapter and isolation after two engineering smoke runs.

## Quick start

```bash
python3 -m pip install pytest            # only dependency (stdlib otherwise)
bash scripts/verify.sh                   # tests + self-audit + manifest; nonzero exit on any failure
sudo bash scripts/setup_enforced.sh      # optional: creates user 'labagent' so the OS boundary is real
sudo -E bash scripts/verify.sh           # rerun with enforced mode included
```

Example live run with an Anthropic API account (not used in this session; read the prereg first):
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
| `data/` | append-only pilot and exploratory trial records plus batch schedules/logs |
| `WORKLOG.md` | dated record of every session, including mistakes |

## Honest limits

The oracle sees file-state changes only; reads and exfiltration are not observed. Docker enforced mode
was exercised on the owner machine, but container escape was not tested. The vulnerable panel is a
file-based model of the trust boundary, not METR's UI. There is no SMS or external human MFA service;
live runs used a scripted denying approver. See `audit/CONTROL_BOUNDARY_AUDIT_2026-11-06.md`.

License: not yet chosen (owner's decision before publishing).
