# PR Review: ROCm/TheRock#5268

* **PR:** https://github.com/ROCm/TheRock/pull/5268
* **Title:** `Patch for Comm Libs`
* **Base:** `compiler/amd-staging`
* **Head:** `e4f1a2d635fe269a0f9365b0b8ca31f49d28d52b`
* **Reviewed:** 2026-05-15
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**IMPORTANT FOLLOW-UP BEFORE APPROVAL** - This looks like the more complete PR in the #5264/#5268 pair: it carries the CK warning-suppression patch and adds the LLVM assembler patch intended to address the `comm-libs` build failure. I do not see a direct code-shape blocker in the TheRock diff, but this PR adds two new carried patches, so it should meet the repository's patch-tracking rules before merge.

CI was still running at review time, including the build job that should validate the `comm-libs` fix. I would wait for that to finish cleanly.

## Findings

### IMPORTANT: new carried patches need explicit upstream tracking/removal status

The new LLVM and CK patch files explain the failures they address, but they do not include explicit upstream tracking or a removal condition in the patch text:

* https://github.com/ROCm/TheRock/blob/e4f1a2d635fe269a0f9365b0b8ca31f49d28d52b/patches/amd-mainline/llvm-project/0007-AMDGPU-VOPD-fix-assembler-to-allow-same-VGPR-src0-o.patch#L4-L18
* https://github.com/ROCm/TheRock/blob/e4f1a2d635fe269a0f9365b0b8ca31f49d28d52b/patches/amd-mainline/rocm-libraries/0001-CK-Suppress-Wlifetime-safety-lifetimebound-violation.patch#L4-L9
* https://github.com/ROCm/TheRock/blob/main/patches/README.md#commit-message-requirements

That is important because these patches become part of the external repository CI path. The patch text or PR description should identify the upstream issue/PR/commit that will absorb each patch and when TheRock can delete it.

### NOTE: this PR overlaps with #5264

ROCm/TheRock#5268 includes the same CK patch that ROCm/TheRock#5264 adds, plus the LLVM assembler patch. That makes #5268 look like the complete version of the fix. If #5268 merges first, #5264 should likely be closed or rebased away.

## Suggested Review Comment

```text
The direction makes sense to me: this appears to combine the CK warning patch with the LLVM assembler patch needed for the comm-libs failure. Before approval, could we add explicit upstream tracking/removal status for both new TheRock-carried patches per patches/README.md? After that I would wait for the current CI, especially the comm-libs build, to finish cleanly.
```

## Verification

* Refreshed `origin/compiler/amd-staging` and `refs/remotes/pr/5268`.
* Checked PR metadata: open, not draft, already approved by other reviewers.
* Checked top-level and inline comments; no existing review comments at review time.
* Reviewed the diff against the actual base branch, not `main`.
* Verified the referenced submodule commits are public GitHub commits.
* Ran `git -c safe.directory=* diff --check origin/compiler/amd-staging...refs/remotes/pr/5268`; it reports whitespace inside generated patch file footer/context, which is expected for patch files and the repository applies patches with whitespace warnings disabled.
* Checked public PR checks; many jobs were passing and the relevant broad build jobs were still pending.
