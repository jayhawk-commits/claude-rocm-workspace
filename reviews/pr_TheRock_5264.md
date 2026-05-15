# PR Review: ROCm/TheRock#5264

* **PR:** https://github.com/ROCm/TheRock/pull/5264
* **Title:** `CK patch to fix Math Libs builds`
* **Base:** `compiler/amd-staging`
* **Head:** `af78342a70e52413c05245d4117b0a4c45fa9b38`
* **Reviewed:** 2026-05-15
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**DO NOT APPROVE AS-IS / LIKELY SUPERSEDED BY #5268** - This PR adds the CK warning-suppression patch and the compiler submodule bumps from `compiler/amd-staging`, but it does not include the LLVM assembler fix that the PR description itself points to in ROCm/TheRock#5268.

That distinction matters because the current public CI for this PR has a failing `comm-libs` build, while #5268 is the PR that adds the assembler-side patch for that failure mode. I would not approve #5264 independently unless the author makes the intended merge order explicit and the CI failure is resolved or accepted as out of scope.

## Findings

### BLOCKING: this PR is only a partial fix for the current compiler branch breakage

The PR description says the `comm-libs` assembler failure is handled by ROCm/TheRock#5268, and the current public checks for #5264 show a failing `comm-libs` build:

* https://github.com/ROCm/TheRock/actions/runs/25928477484/job/76221709551?pr=5264

Since #5268 includes this CK patch plus the LLVM assembler patch, #5264 should probably either wait behind #5268, be closed as superseded, or have a very explicit merge-order note from the author.

### IMPORTANT: the new carried patch needs upstream tracking in the patch text

The CK patch explains the symptom and references an upstream fix, but it does not include the explicit upstream tracking/removal status required for new TheRock-carried patches:

* https://github.com/ROCm/TheRock/blob/af78342a70e52413c05245d4117b0a4c45fa9b38/patches/amd-mainline/rocm-libraries/0001-CK-Suppress-Wlifetime-safety-lifetimebound-violation.patch#L4-L9
* https://github.com/ROCm/TheRock/blob/main/patches/README.md#commit-message-requirements

This is worth asking for before merge, because external repository CI has to apply these patches and the patch needs a clear path to deletion.

## Suggested Review Comment

```text
I would hold this one for now. This PR carries the CK warning-suppression patch, but its own description points to ROCm/TheRock#5268 for the LLVM assembler fix needed by the comm-libs failure, and the current public CI has a failing comm-libs build. Can we either make the intended merge order explicit, or treat this as superseded by #5268?

Also, since this adds a TheRock-carried patch, could the patch text include the upstream tracking/removal status required by patches/README.md?
```

## Verification

* Refreshed `origin/compiler/amd-staging` and `refs/remotes/pr/5264`.
* Checked PR metadata: open, not draft, already approved by another reviewer.
* Checked top-level and inline comments; no existing review comments at review time.
* Reviewed the diff against the actual base branch, not `main`.
* Ran `git -c safe.directory=* diff --check origin/compiler/amd-staging...refs/remotes/pr/5264`; it reports whitespace inside the generated patch file footer/context, which is expected for patch files and the repository applies patches with whitespace warnings disabled.
* Checked public PR checks; `comm-libs` was failing and some broad build jobs were still pending.
