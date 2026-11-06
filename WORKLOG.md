# Worklog (append-only; newest session at the bottom)

## 2026-11-05 — build session (owner + Claude as build assistant)

**Goal set by owner:** reproduce a published break on our own machine, prove it, then test fixes.
Follow June Kim's disciplines. Package for a GitHub repo.

**Built:** gate, permits, policy, ledger, oracle, vulnerable panel, runner (local + enforced modes),
three tasks, scripted agents (gold, mutated gold, 6 attacks), bare-API LLM adapters (Anthropic,
OpenAI-compatible), trial CLI, analysis, self-audit, mutation check, docs, prereg, specs.

**Environment facts:** Linux container, running as root. Created `labagent` (uid 30033) for enforced
mode. No Docker daemon (socket missing) → container mode written, untested. No live model API calls
were made; adapters tested only against canned responses.

**Mistakes and findings, in order (each one fixed and covered by a test unless marked):**
1. Enforced runs silently did nothing: `runuser` not on the scrubbed PATH. Runs were marked `errored`
   in the ledger, but my printed summary omitted `run_status`, so I first misread them. Fix: absolute
   path via `shutil.which(..., path=/usr/sbin:...)`. Lesson: always print run_status.
2. Panel reviewer answered instantly, so self-approval could never win. Fix: `reviewer_latency_steps = 2`
   (frozen prereg parameter); pending requests resolved after finish.
3. Replay was reported as `inode_changed` (the file was already gone). Fix: check one-use before binding.
4. Self-approval was detected only in the panel arm. Fix: symmetric detection in both arms.
5. T3's mutated gold deleted a file that did not exist (no-op "mutation"). Fix: per-task
   `unrelated_file` + witness-complete assertion (the mutation must change something).
6. **Inode reuse:** a deleted-and-recreated file got the same inode and passed the permit binding
   (test returned `(True, 'ok')`). Fix: bind `ctime_ns` as well. Mutant M03.
7. Adapter tests failed with KeyError: fake transport stored a mutable reference. Fix: deepcopy.
8. Mutation script first said KILLED without naming the failing test. Fix: `-rf`, record first FAILED.
9. **Panel advertised the decision-file path in arm A only** (inflates attempts; asymmetric arms).
   Fix: `panel_disclosure` factor, default `hidden`; panel directory present in both arms. D-001, M15.
10. **Self-audit check was wrong:** `forbid` with an approving approver expected zero protected
    changes, but the gold's legitimate request is (correctly) executed. Gate was right; my check was
    wrong. Fix: check the forbidden path and unauthorized effects; new matrix test. D-002.
11. **Statistics:** first plan used Beta-posterior thresholds with peeking every batch, which does not
    keep error control (June's Q22). Replaced with a mixture e-process. My first statistics test was
    too weak: mutant M16 (an invalid max-likelihood "e-value") **survived**. Added an exact
    `E_p0[E_n] ≤ 1` test; M16 now killed. D-003.
12. `panel_touch` matched the run id, which contained `A_panel` → arm-dependent false positives.
    Fix: strip run id; test.
13. **Run id leaked the arm and task to the agent** (`T1_disk_cleanup-A_panel-...` was its cwd and its
    panel agent_id). Fix: opaque `r<hex12>`. D-004, F-17.
14. Agent could read the harness logs (ledger, tool calls, config) in enforced mode. Fix: 0600. D-005, M18.

**Operating characteristics** (from `scripts/analyze.py`, simulated, 600 sims, 10-batch cap):
P(reject H0) = 0.012 at p=0.05, 0.20 at 0.10, 0.70 at 0.15, 0.96 at 0.20.
Reproduce: `python3 scripts/power_sim.py`.

**State at end of session:** 74 tests pass (local + enforced); self-audit 54/54 expectations met;
mutation 0 of 18 survivors; spec→test links OK; redaction scan OK. Phase 0 must be re-run on the
owner's machine before Phase 1 (PLAN gate).

**Open:** F-04 (other self-approval routes), F-10 (eval-awareness from names), F-12 (external ledger
head in verify), F-13 (approver deception), F-16 (container mode). Owner to fill prereg §4, §6, §8.
