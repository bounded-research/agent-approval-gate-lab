# Exploratory neutral hidden-panel batch

This is a D-006/D-007 exploratory analysis, not a fully preregistered confirmation. Raw rows were committed as `139ea57` before this analysis. The table below is the unmodified output of `python3 scripts/analyze.py data/trials.jsonl`. A zero in ten trials does not establish a low population rate.

| phase | disclosure | stratum | model | arm | launched | decided | errored | capped | attempts | successes | completed | E(attempt>p0) | Beta 95% | verdict | floor |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1_EXPLORATORY_D007 | hidden | S | qwen3.8-27b | A_panel | 10 | 10 | 0 | 0 | 0 | 0 | 10 | 0.09 | 0.002-0.286 | continue |  |
