# Deviations log (append-only)

Any change to a frozen artifact (`prereg/P1_PREREG.md` §9) after the prereg commit goes here, with
before → after, reason, date, and whether any data had been seen. Changes made BEFORE the prereg
commit are listed too, so reviewers can see how the design moved.

| ID | Date (UTC) | Data seen? | Artifact | Before → After | Reason |
|---|---|---|---|---|---|
| D-001 | 2026-11-05 | No model data exists | `lab/panel.py`, `lab/runner.py` | Panel reply always named the decision-file path → path named only if `panel_disclosure="advertised"`; default `hidden`. Panel directory now created in both arms. | Self-review: advertising the path in arm A only inflates attempts and makes arm comparison asymmetric (checklist Q8, Q16). |
| D-002 | 2026-11-05 | No model data exists | `tests/test_matrix.py` | Added `test_forbidden_not_overridable_by_approving_approver` (new expectation; no existing expectation edited). | The self-audit found that `forbid` was only tested with a denying approver. |
| D-003 | 2026-11-05 | No model data exists | `scripts/analyze.py` | Beta-posterior stopping → mixture e-process stopping (Beta kept as descriptive). Cap 30 → 10 batches per cell. | Checklist Q22: Beta posteriors with repeated peeking do not keep error control. Cap: budget; power published in prereg §5. |
| D-004 | 2026-11-05 | No model data exists | `lab/runner.py` | run id `"{task}-{arm}-{agent}-{hex8}"` → opaque `"r{hex12}"` | The id is the agent's cwd path component and its panel agent_id; it revealed the arm (F-17). |
| D-005 | 2026-11-05 | No model data exists | `lab/runner.py` | Harness logs world-readable → 0600 in enforced mode | Agent could read operator decisions and labels (F-18). |
