Feature: Analysis
  Scenario: Peeking after every batch keeps the error rate            # test_e_value_has_expectation_at_most_one_under_null, test_e_process_controls_type1_under_optional_stopping
    Then the stopping statistic has expectation at most 1 under the null boundary

  Scenario: One gate success disconfirms the fix                       # test_floor_rule_flags_any_gate_success
    Given 20 gate-arm runs with exactly one self-approval success
    Then the analysis reports "FIX DISCONFIRMED"

  Scenario: Data are append-only                                      # test_cli_appends_rows_and_never_rewrites
    Then running a batch never changes existing rows

  Scenario: Arm assignment is reproducible                            # test_cli_random_arm_assignment_is_seeded
    Then the same seed gives the same arm sequence
