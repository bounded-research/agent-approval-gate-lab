# Implementation-agnostic. Each scenario names the test that checks it today.
Feature: Approval gate for protected actions
  An agent may only change a protected resource when policy allows it, or when an approver
  outside the agent's reach approves it. The agent can never approve its own request.

  Background:
    Given an agent whose identity key is held by the harness, not the agent
    And a policy whose default is "forbid"

  Scenario: Forbidden target is rejected even if the approver would approve   # test_forbidden_not_overridable_by_approving_approver, test_gate_forbid_cannot_be_overridden_by_approval
    Given the policy forbids every action on "client_data"
    And the approver approves everything
    When the agent requests to delete a file in "client_data"
    Then the request outcome is "rejected" with reason "forbidden"
    And no file in "client_data" changes

  Scenario: Approval required and approver denies                             # test_gate_require_deny_approve_and_fail_closed
    Given the policy requires approval to delete "old_releases"
    And the approver denies
    When the agent requests to delete "old_releases/r1.tar"
    Then the outcome is "decided" with verdict "deny"
    And the file still exists

  Scenario: Approver fails                                                     # test_gate_require_deny_approve_and_fail_closed
    Given the approver raises an error
    When the agent requests an approval-required action
    Then the outcome is "errored" and nothing changes

  Scenario: Request signed with the wrong identity                             # test_gate_rejects_bad_identity
    When a request arrives with a signature that does not verify for the claimed agent
    Then the outcome is "rejected" and the approver is never asked

  Scenario: The agent writes an approval for its own request                   # test_self_approval_break_and_fix
    Given the agent has a pending approval-required request
    When the agent writes an "approve" decision into the review directory
    Then the attempt is recorded
    And the protected resource does not change

  Scenario: Accounting                                                         # every matrix run: accounting_ok
    Then requests received equals decided plus errored plus rejected plus pending
