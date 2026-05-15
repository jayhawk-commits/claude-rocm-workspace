# PR Review: ROCm/rocm-libraries#7132

* **PR:** https://github.com/ROCm/rocm-libraries/pull/7132
* **Title:** `[rocrand]Add test filter standardization to rocrand`
* **Base:** `develop`
* **Head:** `d686171301434436769200339f7d2aaa6fa866dc`
* **Reviewed:** 2026-05-15
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**CHANGES REQUESTED** - The rocRAND CTest categorization itself looks in line with the shared rocm-libraries pattern, but the PR also changes two reusable TheRock test workflows from a pinned TheRock commit to a mutable user branch. That should be fixed before merge.

## Findings

### BLOCKING: TheRock test workflows are pinned to a mutable user branch

The PR changes the TheRock checkout in both reusable package-test workflows from the reviewed pinned commit to `users/dravindr/tr_hipcub`:

* [`.github/workflows/therock-test-component.yml#L73`](https://github.com/ROCm/rocm-libraries/blob/d686171301434436769200339f7d2aaa6fa866dc/.github/workflows/therock-test-component.yml#L73)
* [`.github/workflows/therock-test-packages.yml#L46`](https://github.com/ROCm/rocm-libraries/blob/d686171301434436769200339f7d2aaa6fa866dc/.github/workflows/therock-test-packages.yml#L46)

That makes rocm-libraries test results depend on branch state outside this PR. If that branch moves or is deleted, these reusable workflows can start testing different TheRock behavior or fail before reaching the rocRAND changes. It also leaves these two workflows out of sync with the other TheRock workflows, which still use the pinned ref.

## Suggested Inline Comment

Target: `.github/workflows/therock-test-component.yml`, line 73. Mention the same issue also applies to `.github/workflows/therock-test-packages.yml`, line 46.

```text
This should not land pointing at a mutable user branch. These reusable TheRock test workflows become non-reproducible if the branch moves or disappears, and they can start validating behavior unrelated to this rocRAND PR. Could we pin this back to the intended TheRock commit, or update all TheRock workflow refs together to a reviewed upstream commit?
```

## Verification

* Refreshed `origin/develop` and `refs/remotes/pr/7132`.
* Checked PR metadata: open, not draft, mergeable, review required.
* Checked top-level and inline comments; no existing inline comments at review time.
* Reviewed changed files for workflow and rocRAND CTest categorization changes.
* Ran `git -c safe.directory=* diff --check origin/develop...refs/remotes/pr/7132`; passed.
