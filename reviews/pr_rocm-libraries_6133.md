# PR Review: ROCm/rocm-libraries#6133

* **PR:** https://github.com/ROCm/rocm-libraries/pull/6133
* **Title:** `[ci] Adding label support for PRs`
* **Base:** `develop`
* **Head:** `cc8c14c6faad3733f24ead68f8b08c8d548768cd`
* **Reviewed:** 2026-05-11
* **State at review:** OPEN

---

## Summary

This PR adds PR label parsing for `test:<project>` and `test_type:<type>` labels, wires the current PR labels into TheRock CI setup, and adds `pull_request: labeled` as a workflow trigger so adding a label can rerun CI with the new selection.

## Overall Assessment

**CHANGES REQUESTED** - The label mechanism is still internally inconsistent around `test_type:smoke`, and the workflow only reacts to labels being added, not removed. That makes the label support one-way and leaves stale CI results after label cleanup.

## Findings

### BLOCKING: `test_type:smoke` is still present in tests but rejected by the parser

`parse_test_labels()` accepts only `quick`, `standard`, `comprehensive`, and `full` at [`therock_configure_ci.py#L85-L87`](https://github.com/ROCm/rocm-libraries/blob/cc8c14c6faad3733f24ead68f8b08c8d548768cd/.github/scripts/therock_configure_ci.py#L85-L87). The added test still uses `test_type:smoke` at [`therock_configure_ci_test.py#L298-L312`](https://github.com/ROCm/rocm-libraries/blob/cc8c14c6faad3733f24ead68f8b08c8d548768cd/.github/scripts/tests/therock_configure_ci_test.py#L298-L312), so the parser logs it as unknown and leaves the default `standard` test type.

The focused test confirms the mismatch:

```text
WARNING:root:Unknown test type in label: test_type:smoke
FAIL: test_retrieve_projects_with_multiple_test_labels
AssertionError: 'standard' != ''
```

This overlaps with the earlier review comment on the old head, but the current head still has the issue in a slightly different form.

**Required action:** Decide whether `smoke` is a supported rocm-libraries test type. If yes, add it to the parser and downstream test configuration support. If no, update the tests/examples to use `quick` or assert the intended default behavior for an invalid label.

### BLOCKING: Label removals do not rerun CI

The workflow adds `pull_request: labeled` but not `unlabeled` at [`therock-ci.yml#L8-L13`](https://github.com/ROCm/rocm-libraries/blob/cc8c14c6faad3733f24ead68f8b08c8d548768cd/.github/workflows/therock-ci.yml#L8-L13). Since labels now change whether CI runs and which projects/test types are selected, removing a label should also recompute CI. Otherwise, removing `skip-therockci`, `test:<project>`, or `test_type:<type>` leaves the PR with stale checks until a new commit or manual rerun happens.

**Required action:** Add `unlabeled` to the PR event types for this workflow.

## Verification

* Refreshed `origin/develop` and `refs/remotes/pr/6133`.
* Checked latest PR metadata, top-level comments, reviews, and inline comments.
* Ran `git diff --check origin/develop...refs/remotes/pr/6133`; passed.
* Ran the focused label regression test:

```text
python -m unittest discover -s .github\scripts\tests -p "therock_configure_ci_test.py" -k test_retrieve_projects_with_multiple_test_labels
```

Result: failed with `AssertionError: 'standard' != ''`.

* Ran the focused workflow-path test:

```text
python -m unittest discover -s .github\scripts\tests -p "therock_configure_ci_test.py" -k test_retrieve_projects_runs_ci_for_workflow_paths
```

Result: passed.
