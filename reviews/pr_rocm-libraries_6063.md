# PR Review: ROCm/rocm-libraries#6063

* **PR:** https://github.com/ROCm/rocm-libraries/pull/6063
* **Title:** `[ci] skipping builds if artifacts are available and run tests directly`
* **Base:** `develop`
* **Head:** `0bcf8cd86b01cbe946e2a611254f0ff1ea0ce6af`
* **Reviewed:** 2026-05-11
* **State at review:** OPEN

---

## Summary

This PR adds workflow-dispatch inputs that let Linux and/or Windows TheRock CI skip the build job and run tests against artifacts from a previous run. The previous review finding about an empty `artifact_run_id` was addressed by adding setup-time validation before the reusable workflow skips the build.

## Overall Assessment

**CHANGES REQUESTED** - The original prebuilt-artifact guard is now present, but the PR also changes workflow-dispatch project selection so a manual run with the existing default GPU-family fields produces no jobs. The new validation path also uses `sys.exit()` from helper code instead of raising an exception.

## Findings

### BLOCKING: Workflow dispatch now ignores the existing default target families

`run()` now returns `linux_projects=[]` or `windows_projects=[]` whenever the corresponding `AMDGPU_FAMILIES_INPUT` env var is empty during `workflow_dispatch` ([`therock_configure_ci.py#L224-L234`](https://github.com/ROCm/rocm-libraries/blob/0bcf8cd86b01cbe946e2a611254f0ff1ea0ce6af/.github/scripts/therock_configure_ci.py#L224-L234)). However, the workflow inputs still default both family fields to an empty string ([`therock-ci.yml#L18-L29`](https://github.com/ROCm/rocm-libraries/blob/0bcf8cd86b01cbe946e2a611254f0ff1ea0ce6af/.github/workflows/therock-ci.yml#L18-L29)), and the target discovery steps still interpret empty as the default targets (`gfx94X, gfx950` for Linux and `gfx1151` for Windows) at [`therock-ci.yml#L117-L132`](https://github.com/ROCm/rocm-libraries/blob/0bcf8cd86b01cbe946e2a611254f0ff1ea0ce6af/.github/workflows/therock-ci.yml#L117-L132).

That means a manual dispatch that provides `projects=projects/rocprim` but leaves the existing family inputs at their defaults no longer uses the workflow's default targets; it skips the platform before target discovery can apply those defaults.

**Required action:** Either remove the early empty-family skip and let target discovery keep applying defaults, or make this an explicit behavior change by changing the workflow input defaults/docs so users know that an empty family field means "skip this platform".

### BLOCKING: Validation exits instead of raising an exception

`validate_prebuilt_artifacts_config()` calls `sys.exit(1)` from inside the helper at [`therock_configure_ci.py#L203-L215`](https://github.com/ROCm/rocm-libraries/blob/0bcf8cd86b01cbe946e2a611254f0ff1ea0ce6af/.github/scripts/therock_configure_ci.py#L203-L215). Per the workspace Python review guidelines, helper code should fail fast by raising an exception rather than exiting the interpreter directly; this keeps the logic testable and avoids bypassing callers.

**Required action:** Replace the `logging.error(...); sys.exit(1)` path with `raise RuntimeError(...)` carrying the same message.

## Verification

* Refreshed `origin/develop` and `refs/remotes/pr/6063`.
* Checked latest PR metadata, top-level comments, reviews, and inline comments.
* Ran `git diff --check origin/develop...refs/remotes/pr/6063`; passed.
* Simulated the workflow-dispatch setup path with `GITHUB_EVENT_NAME=workflow_dispatch`, `PROJECTS=projects/rocprim`, `PLATFORM=linux`, and no GPU-family input. The script wrote:

```text
linux_projects=[]
test_type=standard
INFO:root:Skipping linux - no amdgpu_families specified in workflow_dispatch
```

* Current public checks are not clean, but the failures observed in the check summary are broader CI failures rather than evidence that the original empty-`artifact_run_id` issue remains.
