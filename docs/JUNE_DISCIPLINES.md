# June Kim's disciplines, and where each one lives here

Read from https://www.june.kim (checklist and round-3 prereg fetched 2026-11-05; the others in an
earlier session). This table is our reading, not June's endorsement; he has not reviewed this repo.

| Discipline (source) | What it asks | Where it is in this repo | Status |
|---|---|---|---|
| Prereg checklist, 22 questions (The Prereg Checklist) | Answer each, or "skipped — reason", before data | `prereg/P1_CHECKLIST.md` (all 22 answered) | done |
| Hypothesis, falsifier, decision tree by phase (Round 3 prereg) | H1/H0, phases with gates, stopping thresholds, caps | `prereg/P1_PREREG.md`, `docs/PLAN.md` | done; stopping uses an e-process instead of Beta thresholds (D-003, reason given) |
| Timestamped predictions (Q21) | Numeric predictions committed before data | `P1_PREREG.md` §8 | done for build assistant; owner row empty until filled |
| Commit before inspection; append-only data (Round 3) | Raw committed before analysis; never overwrite | `scripts/run_trials.py` appends only; README and PLAN order: commit raw → analyse → commit; test asserts prior rows untouched | done; commit order is a procedure, not enforced by code |
| Publish the full trail (Q20) | Data, nulls, exclusions, pilots, prompt iterations, forks | `data/`, `runs/`, `DEVIATIONS.md`, `WORKLOG.md`, `mutation/` incl. the survivor | done (structure); trail grows with use |
| Audit yourself first (How to Audit a Benchmark) | Run your own instrument against known answers before judging others | `scripts/self_audit.py` → `audit/SELF_AUDIT_RESULTS.md` | done |
| Run the gold; mutate the gold (Audit; τ²-bench) | Gold must pass; an injected violation must be caught | `gold` and `mutated_gold_frame` agents; matrix tests; witness-complete assertion | done |
| Symmetric validity gate (Audit) | Same check both ways: clean passes, broken fails | gold-clean + every seeded attack; mutation check (18 mutants) | done |
| Floors vs rates (Audit) | Safety claims as floors where one counterexample matters | Phase 2 primary = floor rule in `analyze.py`; mutant M17 | done |
| passed / failed / unresolved / not-tested, separately (Audit) | Never merge "not tested" into "passed" | `audit/SELF_AUDIT_RESULTS.md` sections | done |
| Name the cure (Audit) | Each failure comes with the fix | `docs/FAILURE_MODES.md` status column; DEVIATIONS reasons | done |
| State-delta gate (Terminal-Bench audit) | Snapshot before, diff after, allowlist = reference footprint; completion and safety reported separately | `lab/oracle.py` snapshot/diff/frame; `allow_globs` per task; outcome has `task_completed` and safety fields separately | done (file state only) |
| Artifact-first, independent supervisor (Make No Mistakes) | Judge by artifacts, by a checker independent of the actor | oracle diffs protected tree itself, trusts only executed ledger events | done |
| Three outcomes + interface accounting (Make No Mistakes) | decided / errored / rejected; received = sum | `gate.py` Counters, `accounting_ok` in every outcome | done |
| Test in parts (Never test in whole…) | Unit-test each mechanism before the whole | `tests/test_parts.py`, `tests/test_analysis_and_cli.py`, then `test_matrix.py` | done |
| Close the loop / define done (Close the loop) | Implementation-agnostic spec that defines done | `spec/features/*.feature` | written; not executed by a BDD runner (each scenario names its test) |
| Worklog every session | Dated, includes mistakes | `WORKLOG.md` | done |
