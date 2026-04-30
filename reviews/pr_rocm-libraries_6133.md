# PR Review: ROCm/rocm-libraries#6133

* **PR:** https://github.com/ROCm/rocm-libraries/pull/6133
* **Title:** `[ci] Adding label support for PRs`
* **Base:** `develop`
* **Head:** `63785c0f80c7a525751655e570ee8bbf3d138758`
* **Reviewed:** 2026-04-30
* **State at review:** OPEN

---

## Overall Assessment

**CHANGES REQUESTED** - The new label parser and tests disagree on supported test type names, so documented/tested label values such as `test_type:smoke` do not work.

## Findings

### BLOCKING: `test_type:smoke` is tested and described but rejected by the parser

`parse_test_labels()` only accepts `quick`, `standard`, `comprehensive`, and `full` at [`therock_configure_ci.py#L85-L86`](https://github.com/ROCm/rocm-libraries/blob/63785c0f80c7a525751655e570ee8bbf3d138758/.github/scripts/therock_configure_ci.py#L85-L86). However, the added test case uses `test_type:smoke` and expects the result to be `smoke` at [`therock_configure_ci_test.py#L299-L313`](https://github.com/ROCm/rocm-libraries/blob/63785c0f80c7a525751655e570ee8bbf3d138758/.github/scripts/tests/therock_configure_ci_test.py#L299-L313). In the current code, that label falls into the warning path at [`therock_configure_ci.py#L113-L114`](https://github.com/ROCm/rocm-libraries/blob/63785c0f80c7a525751655e570ee8bbf3d138758/.github/scripts/therock_configure_ci.py#L113-L114), leaving the default test type instead of honoring the label.

There is a second mismatch in the workflow-file path behavior: code now sets `test_type = "quick"` for CI workflow changes at [`therock_configure_ci.py#L264-L274`](https://github.com/ROCm/rocm-libraries/blob/63785c0f80c7a525751655e570ee8bbf3d138758/.github/scripts/therock_configure_ci.py#L264-L274), while the existing unit test still expects `smoke` at [`therock_configure_ci_test.py#L249-L259`](https://github.com/ROCm/rocm-libraries/blob/63785c0f80c7a525751655e570ee8bbf3d138758/.github/scripts/tests/therock_configure_ci_test.py#L249-L259).

**Required action:** Decide whether rocm-libraries should use `smoke` or `quick` as the reduced test type, then update the parser, tests, and PR/docs examples consistently. If `smoke` remains a supported label, add it to `valid_test_types` with the correct priority.

## Verification

* Inspected the PR diff and label/test-type flow.
* Attempted to run `.github/scripts/tests/therock_configure_ci_test.py`, but this local environment lacks the `requests` dependency imported by the test harness.
* Checked PR metadata; the linked TheRock CI run includes failures in the rollup, so it is not clean evidence for this PR as-is.
