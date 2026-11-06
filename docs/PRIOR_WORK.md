# Prior work and sources

Each entry says what we take from it and how well it was checked.
"Fetched 2026-11-05" = the page was read during the build session that produced this repo.
"Earlier session" = read in a previous session; not re-read for this build.

## The break we reproduce
**METR, "Implementing and Evaluating a Basic Per-Action Monitor for Safer Evals"** (research note, 2026-09-27).
https://metr.org/notes/2026-09-27-implementing-a-basic-blocking-action-monitor/ — fetched 2026-11-05.
- §4a: a researcher "observed their coding agent unpromptedly open the human review panel and send keystrokes".
- §4a "What we're missing": "Enforcement / authentication to ensure only humans are able to review these flagged actions."
- Human review blocks the run until reviewed or until a timeout, which auto-rejects.
- What it does NOT say (as far as we read): that the agent succeeded in approving its own action.
- Our lab copies the failure class (the reviewed party can write to the review channel), not the surface (a UI).

## Discipline
**June Kim** — https://www.june.kim — fetched 2026-11-05 unless noted.
- "The Prereg Checklist" https://www.june.kim/the-prereg-checklist (answered in `prereg/P1_CHECKLIST.md`)
- "Does Loading the Framework Help Diagnose Missing Parts?" https://www.june.kim/round3-preregistration (prereg structure: hypotheses, decision tree by phase, logging and commit policy, predictions with Beta priors, append-only data)
- "How to Audit a Benchmark" https://www.june.kim/how-to-audit-a-benchmark (earlier session)
- "Make No Mistakes" https://www.june.kim/make-no-mistakes (earlier session)
- "Never test in whole what you can test in parts" https://www.june.kim/test-in-parts (earlier session)
- "Close the loop" https://www.june.kim/close-the-loop (earlier session)
- Benchmark audits (Terminal-Bench "blind to destruction", τ²-bench gold mutation) — earlier session; mapped in `docs/JUNE_DISCIPLINES.md`.

## Related designs (not copied; checked against)
- **Inspect (UK AISI) approval policies**: human and automatic approvers; custom approvers can approve, modify, reject, escalate or terminate. Earlier session. Our gate is a minimal standalone version of the same idea plus bound one-use permits.
- **RewardHackingAgents**, arXiv 2603.11337: fresh workspaces, patch tracking, file-access logging, trusted reference; reports evaluator-tampering attempts in about half of natural episodes. Earlier session. Source of our "next breaks" list and of the file-state oracle idea.
- **ImpossibleBench**, https://github.com/safety-research/impossiblebench — earlier session: PR #4 fix (`allow_test_modifications` not forwarded), commit 52ebb0f, merged as 74ae2e8 on 2026-10-12. A reminder that harness flags can silently not reach the code that uses them; our adapter and CLI tests check that flags reach the run (`panel_disclosure`, `arm`, `mode` are recorded in every row and config).

## Not claimed as novel
The gate's parts (default-deny policy, out-of-band approval, signed one-use capabilities bound to a
target) are standard security engineering. The lab's contribution is a reproducible, audited testbed
for this failure class, not the mechanism.
