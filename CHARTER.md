# Charter

## Purpose
Reproduce published agent-safety breaks on our own machine, prove them with an instrument we have
audited first, then test candidate fixes against them. Reproduce → prove → stop → fix.

This lab does not try to discover new breaks for publication. Its value is a working testbed in
which a known break fires reliably and a fix can be measured against it.

## First target
The self-approval failure class from METR's per-action monitor write-up (§4a): an agent reaching the
review channel for its own flagged actions. Fix under test: an approval gate with harness-held
identity, default-deny policy, independent approver and one-use bound permits.

## Claims this lab will make, and only these
1. **Instrument claims** (Phase 0): each planted break is detected; the gold path is clean; each
   safety check is load-bearing (mutation check). Evidence: scripted agents.
2. **Reproduction claims** (Phase 1): the rate at which named models, with a named prompt version,
   attempt self-approval on this surface. Strata never pooled. Nulls reported.
3. **Fix claims** (Phase 2): zero self-approval successes in the gate arm (a floor, not a rate),
   plus the task-completion cost of the gate.

## Claims this lab will not make
- That any result generalises to METR's environment, to other surfaces, or to models not run.
- That the gate is secure in general. It is tested against the attacks listed in `audit/`, no others.
- That a null in Phase 1 refutes METR's observation (different surface; see FAILURE_MODES F-01).

## Discipline
Follows June Kim's published practice (mapped in `docs/JUNE_DISCIPLINES.md`): preregister before
data, answer the 22-question checklist, audit yourself first, run and mutate the gold, report
passed / failed / unresolved / not-tested separately, append-only data, publish the full trail.
Every claim in our own reports carries a provenance tag (owner's Honesty and Grounding Contract).

## Ethics and safety
- Synthetic data only. No real client data, credentials, names or contact details anywhere.
- The vulnerable panel is deliberately unsafe and must never guard anything real.
- API keys stay in the harness environment; the agent process gets a scrubbed environment.
- Agents run as an unprivileged user (enforced mode) or in a container with no network (container mode).
