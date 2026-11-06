# Cross-run isolation probe

Run before the larger model batch on 2026-11-06, after two excluded T1 engineering smoke runs. No Phase 1 batch had begun.

## Original shared-run layout

Inside the enforced Docker image, create two `Run` objects with the same 0755 parent `runs_dir`. Execute a scripted gold agent in the first, then ask the second run's `labagent` shell to test readability of the first run's workspace README. Observed output: `cross_run_readable True`.

This proves a later run under the same `labagent` UID can inspect an earlier workspace if both share a mounted run parent. The original `scripts/run_trials.py --n 10` route does not isolate those workspaces from one another. It does not prove that either live smoke agent actually inspected an earlier run.

## Changed execution path

D-007 added `scripts/run_isolated_batch.py`, which starts each trial in a separate networkless container with its own `/runs` mount. A marker created in one host run directory was absent in a container mounting a different host directory: `other_mount_marker_visible=1` is the shell exit status of `test -e /runs/marker` (1 means absent). The task selector refuses a multi-run container: `run_trials.py: error: --task requires --n 1`, exit 2.

This tests mount separation and the CLI guard. It does not establish that Docker isolation defeats kernel or container escape, and it is not a live model outcome. The default shared-run CLI still exists and must not be used for independence claims.
