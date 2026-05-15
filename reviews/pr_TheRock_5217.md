# PR Review: ROCm/TheRock#5217

* **PR:** https://github.com/ROCm/TheRock/pull/5217
* **Title:** `[hipfile] Add initial hipFile support`
* **Base:** `main`
* **Head:** `9c733f7224707f1b308943ccebcae4b15f432ebe`
* **Reviewed:** 2026-05-15
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**CHANGES REQUESTED** - The overall integration shape looks reasonable: the PR adds a new `storage-libs` build stage, wires hipFile as a Linux-only target-neutral artifact, adds native package definitions, and documents the new feature flag.

However, I see a configure-time blocker in the new hipFile subproject wiring. The integration clears `ROCM_PATH` to avoid host ROCm leakage, which is good, but hipFile's upstream CMake falls back to reading `${ROCM_PATH}/.info/version` unless `ROCM_VERSION` is provided. Since this PR does not pass `ROCM_VERSION`, the new `storage-libs` stage can fail before it reaches normal dependency discovery.

## Findings

### BLOCKING: hipFile configure can read `/.info/version` after TheRock clears `ROCM_PATH`

The new hipFile subproject passes empty `ROCM_PATH` and `ROCM_DIR` values at:

* https://github.com/ROCm/TheRock/blob/9c733f7224707f1b308943ccebcae4b15f432ebe/storage-libs/CMakeLists.txt#L17-L18

That matches TheRock's hermetic-build pattern, but hipFile's own CMake requires a version source. At the rocm-systems commit used by this PR, hipFile only seeds `ROCM_VERSION` from the environment, otherwise it reads `${ROCM_PATH}/.info/version`:

* https://github.com/ROCm/rocm-systems/blob/39213316d216a88bb3ea38d262224c6a2d3abb08/projects/hipfile/CMakeLists.txt#L115-L134

The TheRock subproject wrapper also unsets the `ROCM_PATH` environment variable before configure. With `-DROCM_PATH=` and no `-DROCM_VERSION=...`, `${ROCM_PATH}` remains empty in the cache and the fallback becomes `/.info/version`, which is not a valid TheRock source of truth. Please pass TheRock's computed ROCm version explicitly, e.g. `-DROCM_VERSION=${ROCM_MAJOR_VERSION}.${ROCM_MINOR_VERSION}.${ROCM_PATCH_VERSION}`, alongside the existing cleared path variables.

## Suggested Review Comment

```text
I think the hipFile configure args need one more TheRock-provided value. This PR correctly clears `ROCM_PATH`/`ROCM_DIR` to avoid picking up a host ROCm install, but hipFile's CMake falls back to reading `${ROCM_PATH}/.info/version` unless `ROCM_VERSION` is already defined. Since the subproject wrapper also unsets the `ROCM_PATH` environment variable, the current args can leave hipFile trying to read `/.info/version` during configure. Could we pass `-DROCM_VERSION=${ROCM_MAJOR_VERSION}.${ROCM_MINOR_VERSION}.${ROCM_PATCH_VERSION}` in `storage-libs/CMakeLists.txt`?
```

## Verification

* Refreshed `origin/main` and `refs/remotes/pr/5217`.
* Checked PR metadata: open, not draft, review required.
* Checked existing inline comments; the earlier `ROCM_PATH` discussion is related, but this `ROCM_VERSION` fallback issue is still present in the latest source.
* Reviewed the current diff across the new `storage-libs` stage, artifact descriptor, topology, native package definitions, and docs.
* Fetched the rocm-systems submodule commit referenced by TheRock and inspected `projects/hipfile/CMakeLists.txt`.
* Ran `git -c safe.directory=* diff --check origin/main...refs/remotes/pr/5217`; passed.
* Checked public PR checks; unit/pre-commit/setup jobs were green, but multi-arch CI had not yet reached the new `storage-libs` stage at review time.
