# PR Review: ROCm/rocm-systems#6144

* **PR:** https://github.com/ROCm/rocm-systems/pull/6144
* **Title:** `[GHA] Exempt draft PRs from being marked as stale`
* **Base:** `develop`
* **Head:** `12fbce1ce5a13f9c258cffe8d085888aa9ee2395`
* **Reviewed:** 2026-05-15
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**NO BLOCKING FINDINGS / OK TO APPROVE AFTER CI TRIAGE** - This is a narrow workflow policy change that adds `exempt-draft-pr: true` to the `actions/stale@v10` configuration at [`.github/workflows/close-stale-prs.yml#L65-L66`](https://github.com/ROCm/rocm-systems/blob/12fbce1ce5a13f9c258cffe8d085888aa9ee2395/.github/workflows/close-stale-prs.yml#L65-L66). I verified that `actions/stale@v10` defines this input, and the existing workflow already scopes the action to PRs with issue stale/close disabled.

The required CI summary was failing at review time, but the PR only changes the scheduled/manual stale workflow configuration. I do not see a code-review blocker in the diff itself.

## Findings

None blocking.

## Suggested Review Comment

```text
No blocking comments from me. This is a narrow `actions/stale@v10` configuration change, and `exempt-draft-pr` is a supported input for that action. I would just want the current CI failure triaged before merge.
```

## Verification

* Refreshed `origin/develop` and `refs/remotes/pr/6144`.
* Checked PR metadata: open, not draft, review required.
* Checked top-level and inline comments; no existing review comments at review time.
* Reviewed changed workflow: `.github/workflows/close-stale-prs.yml`.
* Verified the upstream `actions/stale@v10` action metadata includes `exempt-draft-pr`.
* Ran `git -c safe.directory=* diff --check origin/develop...refs/remotes/pr/6144`; passed.
