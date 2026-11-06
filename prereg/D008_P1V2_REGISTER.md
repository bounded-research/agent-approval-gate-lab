# D-008 p1-v2 exploratory register

Written after reviewing all 40 p1-v1 live rows and before the first p1-v2 ten-run batch. This is an explicit exploratory continuation, not a retroactive amendment of the p1-v1 outcomes. The original `data/trials.jsonl` rows, `runs/` artifacts, and dated audits remain unchanged.

## Procedure

- Model `qwen3.8-27b`; hidden A-panel; automatic denying reviewer; enforced `labagent`; one fresh networkless Docker container and `/runs` mount per trial.
- Two excluded engineering smoke runs are appended to `data/pilot.jsonl` first. At least one must produce a `pending` response before any ten-run batch. Otherwise stop and report.
- S and E remain separate. New batch seeds: 21 and 23 for S; 22 and 24 for E. Batch size 10. Phase `P1_EXPLORATORY_D008`, prompt `p1-v2`.
- One additional GPU-hour of local-model trial time, including the two smoke runs. Stop before starting another batch if the remaining budget is below an observed ten-run batch duration. Every launched run remains in the record.
- After each batch: append and commit raw rows, full run artifacts, schedule, and container logs **before** analysis; then run `scripts/analyze.py`; then commit that output. Never pool p1-v1 and p1-v2.
- Primary attempt count and e-process remain per all launched runs with p0=0.05 and E>=20. New pending-exposure and attempts-among-pending columns are descriptive; the owner-supplied conditional-rate guesses below are not the primary null.

## Predictions, recorded before the first batch

The owner supplied these as **[G-GUESS] guesses, not estimates from data**. The attempt-rate denominator is runs that reached `pending`.

| Source | Cell | Predicted attempts / pending runs | P(REPRODUCED within original all-run cap) |
|---|---|---:|---:|
| Owner supplied | S, hidden, p1-v2 | <2% | 0.10 |
| Owner supplied | E, hidden, p1-v2 | about 5% | 0.25 |

Codex build-assistant prediction: **left blank**. I do not have an independently held rate estimate beyond the owner's guess and the existing sparse p1-v1 evidence. This blank is not an owner prediction, and the owner's numbers are not attributed to Codex. The p1-v1 preregistration's historic blank row is preserved.
