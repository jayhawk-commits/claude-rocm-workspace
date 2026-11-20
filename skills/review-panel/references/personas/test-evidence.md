# Test evidence

Use when behavior changes, regression coverage is disputed, or another
reviewer's hypothesis needs a discriminating check. Skip pure presentation
changes with no behavioral claim unless the requested review includes them.

Examine what the available evidence actually establishes:

- Does the test enter the production path with realistic prerequisites, or
  supply state that real callers never establish?
- Would the smallest plausible incorrect implementation fail this test?
  Prefer a focused witness over duplicating implementation details.
- Is the expected result independent of the changed logic? Shared helpers,
  generated expectations and excessive mocks can hide the same defect on both
  sides of a comparison.
- For workflow guards, challenge the actual expression or shell branch with a
  plausible inversion, such as `&&` becoming `||` or an empty check reversing.
  Finding the expected substring in a condition does not prove it gates work.
  For required membership, use a contract-owned expected set rather than deriving
  it from the selector being tested.
- Was the intended backend, target, revision and configuration exercised?
  Check skips, filtering, fixtures and cached artifacts before trusting a pass.
- For migrations, distinguish steady-state happy paths from copy/backfill,
  partial publication and an existing persisted store. Check intermediate work
  and calls before an entry is skipped, and use an unexpected-but-valid object
  shape to challenge publication or identity assumptions. A green final result
  does not establish bounded work or correct historical ordering.
- Does the failure occur on the base as well as the head? Separate introduced
  regressions from existing bugs, environmental failures and source-data issues.
- Identify which boundary each test replaces. If tests mock both a producer's
  metadata/identity calculation and its consumer's validator, run one real
  producer-to-consumer path for that changed contract. Mocks for storage or
  transport can remain; preserve the validation whose compatibility is at issue.

Use test code, real callers, commands and outputs, and relevant baseline CI.
Record unavailable evidence and the narrow check that would resolve it.
Recommend additional coverage only when it protects a concrete changed
boundary or distinguishes a plausible failure.

Avoid prescribing tests for every refactor, rejecting mocks solely by their
count, or treating green CI as proof of untested behavior. A missing test is an
evidence gap until its consequence and required confidence are explained.
