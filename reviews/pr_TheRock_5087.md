# PR Review: ROCm/TheRock#5087

* **PR:** https://github.com/ROCm/TheRock/pull/5087
* **Title:** `[rocSOLVER] Increase test timeout`
* **Base:** `main`
* **Head:** `1b33337e9be6636e65e90f491b3183205dfd618f`
* **Reviewed:** 2026-05-14
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**NO BLOCKING FINDINGS / OK TO APPROVE** - This is a narrow timeout change for the `rocsolver` test job. Your earlier request for context was answered: the author says the new SYTRS/SYTRS2 coverage adds 3456 test cases, with a short local runtime but high variance in CI.

The latest PR checks still have an overall Multi-Arch failure, but the `rocsolver` job itself passed in the sampled run. The failed jobs are broader Linux package/PyTorch/test jobs and Windows sanity, not obviously tied to this timeout-only diff.

## Findings

None blocking.

## Optional Note

The new source comment on the timeout line names an internal CI environment and says the extended tests take about five hours, while the configured timeout is 120 minutes. That may be clear to people who know the three-way sharding, but it is a little hard to read from the file alone. If commenting at all, I would make this a small suggestion rather than a blocker.

## Suggested Review Comment

```text
I do not have blocking comments here. Thanks for adding the details on the added SYTRS/SYTRS2 coverage and observed runtime.

Small optional cleanup: the new timeout comment would be clearer if it avoided naming the specific internal CI environment and explained the per-shard math, since the comment says the full extended run is roughly five hours while this job timeout is 120 minutes.
```

## Verification

* Refreshed `origin/main` and `refs/remotes/pr/5087`.
* Checked latest PR metadata: open, not draft, mergeable, already approved by other reviewers.
* Checked top-level and inline comments. Existing discussion already covers why the timeout increase is being requested and asks about future test standardization.
* Reviewed changed file: `build_tools/github_actions/fetch_test_configurations.py`.
* Ran `git -c safe.directory=* diff --check origin/main...refs/remotes/pr/5087`; passed.
* Checked latest public PR checks. The sampled `rocsolver` job passed; unrelated jobs still fail in the overall Multi-Arch run.
