# PR Review: ROCm/rocm-systems#6154

* **PR:** https://github.com/ROCm/rocm-systems/pull/6154
* **Title:** `Update TheRock reference to (ea63b75)`
* **Base:** `develop`
* **Head:** `c5482b9accbf396bbe40164347ebb8f0d2e2704c`
* **Reviewed:** 2026-05-15
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**NO BLOCKING FINDINGS / OK AFTER CI COMPLETES** - This is a mechanical TheRock reference bump in seven rocm-systems reusable workflows. The new ref is a full commit SHA on current TheRock `main`, and the changed workflows all point at the same new pinned commit.

The TheRock range from `fac13173...` to `ea63b756...` includes current build-infra changes plus the rocm-systems submodule bump that this PR is meant to consume. I do not see a review blocker in the rocm-systems diff itself.

## Findings

None blocking.

## Suggested Review Comment

```text
No blocking comments from me. This is a mechanical TheRock ref bump to a pinned commit on TheRock main, and the changed workflows are consistent. I would just wait for the current package/CI run to finish cleanly before merge.
```

## Verification

* Refreshed `origin/develop` and `refs/remotes/pr/6154`.
* Fetched TheRock `origin/main` and verified `ea63b756da34b8243f79a2332ef336ea76fdd188` is on that branch.
* Reviewed changed workflow refs; all seven updated from the old pinned TheRock commit to the same new pinned TheRock commit.
* Ran `git -c safe.directory=* diff --check origin/develop...refs/remotes/pr/6154`; passed.
* Checked public PR checks; package jobs were still in progress at review time.
