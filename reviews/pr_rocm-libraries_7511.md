# PR Review: ROCm/rocm-libraries#7511

* **PR:** https://github.com/ROCm/rocm-libraries/pull/7511
* **Title:** `Update TheRock reference to (6f26b80)`
* **Base:** `develop`
* **Head:** `515af6a55c7c6d13642d453dc59598ee8709edf8`
* **Reviewed:** 2026-05-15
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**NO BLOCKING FINDINGS / OK AFTER CI COMPLETES** - This is a mechanical TheRock reference bump in six rocm-libraries workflows. The new ref is a full commit SHA on current TheRock `main`, and the changed workflows all point at the same new pinned commit.

The TheRock range from `4e469b56...` to `6f26b809...` includes current build-infra changes plus the rocm-libraries submodule bump that this PR is meant to consume. I do not see a review blocker in the rocm-libraries diff itself.

## Findings

None blocking.

## Suggested Review Comment

```text
No blocking comments from me. This is a mechanical TheRock ref bump to a pinned commit on TheRock main, and the changed workflow refs are consistent. I would just wait for the current CI run to finish cleanly before merge.
```

## Verification

* Refreshed `origin/develop` and `refs/remotes/pr/7511`.
* Fetched TheRock `origin/main` and verified `6f26b8094263956d5e6502ae547e4ff1398e5dcb` is on that branch.
* Reviewed changed workflow refs; all six updated from the old pinned TheRock commit to the same new pinned TheRock commit.
* Ran `git -c safe.directory=* diff --check origin/develop...refs/remotes/pr/7511`; passed.
* Checked public PR checks; required checks were green and additional CI was still in progress at review time.
