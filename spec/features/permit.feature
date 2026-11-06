Feature: One-use permits (release-to-agent delivery)
  When the gate releases a permit instead of acting itself, the permit is good for exactly one
  action, by one agent, on one file, before it expires.

  Scenario: Happy path then replay                                             # test_permit_happy_path_then_replay, test_permit_attacks
    Given an approved request produced a permit
    When the agent presents it once
    Then the action happens
    When the agent presents it again
    Then it is rejected as "replayed"

  Scenario Outline: Binding                                                    # test_permit_binding (parametrized)
    When the permit is presented with a different <field>
    Then it is rejected as "<reason>"
    Examples:
      | field  | reason              |
      | agent  | wrong_agent         |
      | action | wrong_action        |
      | path   | target_path_changed |

  Scenario: File replaced after approval, even at the same inode number        # test_permit_expiry_signature_and_inode
    Given the approved file is deleted and a new file is created at the same path
    When the permit is presented
    Then it is rejected as "target_inode_changed"

  Scenario: Symlink swap after approval                                        # test_permit_symlink_swap, test_permit_attacks
    Given the approved path is replaced by a symlink to another protected file
    When the permit is presented
    Then it is rejected and neither file changes

  Scenario: Forged or expired                                                  # test_permit_expiry_signature_and_inode
    Then a permit with a bad signature is rejected as "bad_signature"
    And a permit past its expiry is rejected as "expired"
