# PR Review: ROCm/TheRock#4908

* **PR:** https://github.com/ROCm/TheRock/pull/4908
* **Title:** `[CI] Auto-generate manifest-diff report from multi-arch CI on PR/push/schedule`
* **Base:** `main`
* **Head:** `ede586caf7c55d3e0bac3ae3c7b3a4b1fa274f87`
* **Reviewed:** 2026-05-14
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**WAIT / DO NOT ADD NEW REVIEW YET** - This PR already has active changes requested, has merge conflicts, and has existing design-review threads covering the main concerns. I would not add another top-level review until the author rebases and responds with a design update.

## Existing Blocking Context

The latest metadata reports the PR as `CONFLICTING` and `CHANGES_REQUESTED`.

The main active design concern is already covered by Scott's inline comments: the PR still adds `manifest_diff` inside `setup_multi_arch.yml` with `needs: setup` and calls the reusable `manifest-diff.yml` workflow from there ([`setup_multi_arch.yml#L171-L180`](https://github.com/ROCm/TheRock/blob/ede586caf7c55d3e0bac3ae3c7b3a4b1fa274f87/.github/workflows/setup_multi_arch.yml#L171-L180)). Since callers wait for the reusable setup workflow to finish before downstream build/test jobs can consume its outputs, this keeps manifest-diff generation on the CI setup path. The existing thread already asks whether that is fast enough and suggests moving it lower in the graph or producing a lightweight setup output instead.

There is also an existing thread asking for compatibility testing for PRs from forks and future external-repo callers. The PR currently excludes external repo callers in `setup_multi_arch.yml`, and the author said those cases need follow-up design work.

## Suggested Next Step

Do not post a duplicate finding now. Ask the author to:

1. Rebase/resolve conflicts.
2. Address the existing critical-path design thread.
3. Confirm fork-PR credential behavior with logs.
4. State whether external repo and release-driver support are intentionally out of scope for this PR.

After that, re-review the updated design and workflow placement.

## Verification

* Refreshed `origin/main` and `refs/remotes/pr/4908`.
* Checked latest PR metadata: open, not draft, conflicting, changes requested.
* Checked top-level reviews and inline comments; existing threads cover workflow placement, elevated permissions, fork compatibility, and external caller scope.
* Reviewed changed files at a high level:
  * `.github/workflows/manifest-diff.yml`
  * `.github/workflows/setup_multi_arch.yml`
  * `build_tools/generate_manifest_diff_report.py`
  * `build_tools/github_actions/github_actions_api.py`
  * related tests and docs
* Ran `git -c safe.directory=* diff --check origin/main...refs/remotes/pr/4908`; passed.
* Ran focused tests from a PR snapshot:

```text
python -m unittest build_tools\tests\generate_manifest_diff_report_test.py build_tools\github_actions\tests\github_actions_api_test.py
```

Result: 55 tests passed.

* Ran `python -m compileall -q build_tools\generate_manifest_diff_report.py build_tools\github_actions\github_actions_api.py`; passed.
