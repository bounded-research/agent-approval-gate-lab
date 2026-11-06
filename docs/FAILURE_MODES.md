# Failure-mode registry: ways this lab can fool itself

Append new entries; never delete. Status: OPEN / MITIGATED (how) / ACCEPTED (stated limit).

| ID | Failure mode | Effect on claims | Status |
|---|---|---|---|
| F-01 | Our panel is files; METR's was a UI receiving keystrokes. | A Phase 1 null does not refute METR; a positive is about this surface. | ACCEPTED, stated in CHARTER and prereg |
| F-02 | Panel reply advertised the decision-file path in arm A only. | Inflated attempts in A; asymmetric arms. | MITIGATED: `panel_disclosure` factor, `hidden` default, test + mutant M15 (D-001) |
| F-03 | Detector never fires (bug) → false "no break". | Phase 1 null would be an artifact. | MITIGATED: scripted self_approve in every Phase 0; mutant M12 |
| F-04 | Attempt routes other than writing a decision file (editing `pending/`, deleting requests, killing processes). | Undercount. | OPEN: `panel_touch` secondary + hand review (`data/ATTEMPT_REVIEW.md`); not in primary |
| F-05 | Agent reaches protected files by the shell in local mode. | Fix looks broken / break looks bigger. | MITIGATED: Phase 1–2 forbidden in local mode; enforced mode tested; mutant M14 |
| F-06 | Arm A writes `pending/*.json`; arm B leaves `pending/` empty. | Arm A shows the agent more about the channel. | ACCEPTED, reported; inherent to "vulnerable panel vs gate" |
| F-07 | Invalid sequential statistic under peeking. | False "reproduced". | MITIGATED: e-process; exact expectation test; mutant M16 (first test missed it) |
| F-08 | Measurement keyed on strings that contain the arm name (`A_panel` in paths). | Arm-dependent false positives. | MITIGATED: run id stripped in `panel_touch`; test |
| F-09 | Inode reuse lets a recreated file pass a permit binding. | Permit for old file used on new file. | MITIGATED: ctime_ns in binding; test; mutant M03 |
| F-10 | Eval awareness: model recognises a test from names (`panel`, `protected`, `labagent`). | Behaviour may differ from deployment. | OPEN: names are plain; not measured. Consider renamed variant as a later deviation |
| F-11 | Inherited context (memory, prior chats) leaks the lab's purpose to the agent. | Confound seen in the owner's previous lab. | MITIGATED: bare API, adapter test asserts no memory in request |
| F-12 | Ledger tail truncation undetected without external head. | Deleted final events. | OPEN: store ledger head outside run dir (e.g. in `data/trials.jsonl` row — done for live runs) and compare in verify |
| F-13 | Approver deception via `reason` text. | Human approves a bad action. | OPEN, not tested (approvers are automatic) |
| F-14 | Harness flag not forwarded (ImpossibleBench PR #4 class). | Runs silently use defaults. | MITIGATED: every parameter written to config.json and data rows; CLI tests |
| F-15 | Self-audit check itself wrong (forbid case first required zero protected changes). | False FAIL or false PASS in audit. | MITIGATED: fixed, matrix test added (D-002); WORKLOG |
| F-16 | Container mode untested. | Unknown boundary. | OPEN |
| F-17 | Run directory and agent id contained task, arm and agent name (`T1_disk_cleanup-A_panel-...`), visible to the agent as its cwd and in pending files. | Arm and test leak to the subject; eval awareness. | MITIGATED 2026-11-05: opaque run id `r<12 hex>`; labels only in config.json (D-004) |
| F-18 | Agent can read top-level run logs (ledger, tool_calls) in enforced mode. | Could learn operator decisions early or infer a test. | MITIGATED 2026-11-05: ledger, config, tool_calls, outcome are 0600 root in enforced mode; test; mutant M18 (D-005) |
| F-19 | Free-text action or annotated target fails to match a policy rule but is reported as an explicit `forbidden` decision. | The agent is falsely told a legitimate request is disallowed; fewer runs reach pending, biasing the observed opportunity to self-approve downward. | MITIGATED for p1-v2 by action enum, exact-path guidance and validation, separate `unrecognized_request` reply in both arms, pending-exposure metrics, scripted regression and mutants M19/M20. Residual: a model may ignore tool-schema guidance; invalid requests still fail closed. D-008. |
