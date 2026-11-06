# Mutation results

Each row breaks one safety mechanism. KILLED = the test suite caught it.

| Mutant | Result | First failing test |
|---|---|---|
| M01 one-use check removed | KILLED (suite failed) | `FAILED tests/test_matrix.py::test_permit_attacks[local] - AssertionError: ass...` |
| M02 target path binding removed | KILLED (suite failed) | `FAILED tests/test_matrix.py::test_permit_attacks[local] - AssertionError: ass...` |
| M03 inode/ctime binding removed | KILLED (suite failed) | `FAILED tests/test_parts.py::test_permit_expiry_signature_and_inode - Assertio...` |
| M04 permit signature not checked | KILLED (suite failed) | `FAILED tests/test_matrix.py::test_permit_attacks[local] - AssertionError: ass...` |
| M05 permit expiry not checked | KILLED (suite failed) | `FAILED tests/test_parts.py::test_permit_expiry_signature_and_inode - Assertio...` |
| M06 policy default-allow | KILLED (suite failed) | `FAILED tests/test_parts.py::test_policy_default_deny_prefix_boundary_and_symlinks` |
| M07 forbid overridable | KILLED (suite failed) | `FAILED tests/test_matrix.py::test_forbidden_request_rejected[T1_disk_cleanup-local]` |
| M08 approver deny ignored | KILLED (suite failed) | `FAILED tests/test_matrix.py::test_gold_is_clean[B_gate-T1_disk_cleanup-local]` |
| M09 identity not verified | KILLED (suite failed) | `FAILED tests/test_parts.py::test_gate_rejects_bad_identity - AssertionError: ...` |
| M10 frame check disabled | KILLED (suite failed) | `FAILED tests/test_matrix.py::test_mutated_gold_is_caught_and_witness_is_complete[T1_disk_cleanup-local]` |
| M11 unauthorized-effect check disabled | KILLED (suite failed) | `FAILED tests/test_matrix.py::test_alt_route[A_panel-T1_disk_cleanup-local] - ...` |
| M12 self-approval detection disabled | KILLED (suite failed) | `FAILED tests/test_matrix.py::test_self_approval_break_and_fix[T1_disk_cleanup-local]` |
| M13 ledger prev-hash not checked | KILLED (suite failed) | `FAILED tests/test_parts.py::test_ledger_chain_ok_and_detects_edit_delete_reorder` |
| M14 agent runs as root in enforced mode | KILLED (suite failed) | `FAILED tests/test_matrix.py::test_alt_route[A_panel-T1_disk_cleanup-enforced]` |
| M15 panel always discloses decision path | KILLED (suite failed) | `FAILED tests/test_analysis_and_cli.py::test_panel_disclosure_factor_and_symmetric_panel_dir` |
| M16 e-value peeks at the best alternative (invalid) | KILLED (suite failed) | `FAILED tests/test_analysis_and_cli.py::test_e_value_has_expectation_at_most_one_under_null` |
| M18 harness logs readable by agent | KILLED (suite failed) | `FAILED tests/test_parts.py::test_enforced_agent_cannot_read_harness_logs_or_see_arm` |
| M17 floor rule ignores gate successes | KILLED (suite failed) | `FAILED tests/test_analysis_and_cli.py::test_floor_rule_flags_any_gate_success` |

Survivors: 0 of 18
