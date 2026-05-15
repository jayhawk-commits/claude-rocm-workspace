# PR Review: ROCm/TheRock#4812

* **PR:** https://github.com/ROCm/TheRock/pull/4812
* **Title:** `Add test filter standardisation to rocrtst`
* **Base:** `main`
* **Head:** `9bb166a200024092462872df9f7519e1c007fc3e`
* **Reviewed:** 2026-05-14
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**NO BLOCKING FINDINGS / OK TO APPROVE AFTER CI TRIAGE** - This is a one-line change that moves the `rocrtst` CI entry from its bespoke runner to the shared `test_runner.py` path at [`fetch_test_configurations.py#L551-L555`](https://github.com/ROCm/TheRock/blob/9bb166a200024092462872df9f7519e1c007fc3e/build_tools/github_actions/fetch_test_configurations.py#L551-L555).

The latest public CI run has unrelated failures, but the changed `rocrtst` job passed. I do not see existing review comments to avoid duplicating.

## Findings

None blocking.

## Suggested Review Comment

```text
No blocking comments from me. This is a narrow switch of `rocrtst` onto the shared test runner, and the `rocrtst` job passed in the latest CI run I checked. The remaining failures look outside this one-line diff, so I would just want those triaged before merge.
```

## Verification

* Refreshed `origin/main` and `refs/remotes/pr/4812`.
* Checked latest PR metadata: open, not draft, mergeable, review required.
* Checked top-level and inline comments; no existing review comments at review time.
* Reviewed changed file: `build_tools/github_actions/fetch_test_configurations.py`.
* Ran `git -c safe.directory=* diff --check origin/main...refs/remotes/pr/4812`; passed.
* Checked latest public PR checks. The `rocrtst` job passed; remaining failures were outside the changed test entry.
