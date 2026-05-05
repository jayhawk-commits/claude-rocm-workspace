# PR Review: ROCm/rocm-libraries#6986

* **PR:** https://github.com/ROCm/rocm-libraries/pull/6986
* **Title:** `[stinkytofu] Fix Windows build: vcpkg toolchain chaining, getenv safety, remove GTest fetch`
* **Base:** `develop`
* **Head:** `f41e8eb39b3e4c1f80d86fced6463eaf03b9536f`
* **Reviewed:** 2026-05-04
* **State at review:** OPEN

---

## Overall Assessment

**COMMENT / NO BLOCKING FINDINGS** - The PR is a focused Windows/CI repair on top of the StinkyTofu workflow: it makes GTest an explicit dependency, chains the vcpkg toolchain into the generated Windows toolchain file, and replaces the Windows `getenv` call with `_dupenv_s`. I did not find a correctness issue that should block the PR.

## Findings

No blocking findings.

## Design Notes

The source is unchanged from the prior review pass; the latest refresh only changed the surrounding PR state.

The removal of the `FetchContent` fallback in favor of `find_package(GTest REQUIRED)` is a reasonable CI-hardening direction: the build no longer reaches out to GitHub during CMake configure, and the Windows workflow now installs GTest explicitly with vcpkg ([`stinkytofu-ci.yml#L92-L93`](https://github.com/ROCm/rocm-libraries/blob/f41e8eb39b3e4c1f80d86fced6463eaf03b9536f/.github/workflows/stinkytofu-ci.yml#L92-L93), [`tests/CMakeLists.txt#L4-L5`](https://github.com/ROCm/rocm-libraries/blob/f41e8eb39b3e4c1f80d86fced6463eaf03b9536f/shared/stinkytofu/tests/CMakeLists.txt#L4-L5)). The tradeoff is that standalone developers now need an external GTest package; that is acceptable for this PR, but worth documenting if StinkyTofu standalone builds are expected to be easy outside CI.

The vcpkg integration preserves the existing `lib.exe` archive-command override by including vcpkg's toolchain from the generated Windows toolchain file before setting `CMAKE_AR` and the static archive commands ([`tasks.py#L198-L253`](https://github.com/ROCm/rocm-libraries/blob/f41e8eb39b3e4c1f80d86fced6463eaf03b9536f/shared/stinkytofu/tasks.py#L198-L253)). That matches the shape of the existing Windows workaround and should let CMake find vcpkg-provided GTest without losing the ROCm/MSVC archiver fix.

The `_dupenv_s` change is scoped to Windows and frees the duplicated environment value after copying it into the search-path vector ([`IntrinsicRegistry.cpp#L113-L123`](https://github.com/ROCm/rocm-libraries/blob/f41e8eb39b3e4c1f80d86fced6463eaf03b9536f/shared/stinkytofu/src/ir/logical/IntrinsicRegistry.cpp#L113-L123)). That addresses the Windows CRT safety warning without changing the non-Windows path.

## Latest Comment Check

Checked latest PR state on 2026-05-04 at head `f41e8eb3`. The PR has one Codecov bot top-level comment and no inline review comments. The current head has a human approval from `hcman2`; the earlier `cycheng` approval is on older commit `bb1fdea2`. There were no human comment threads to avoid duplicating.

## Verification

* Refreshed PR metadata, review comments, inline comments, and check status on 2026-05-04.
* Fetched latest `origin/develop` and `refs/pull/6986/head`; reviewed local worktree at `f41e8eb3`.
* Latest GitHub checks for the current head show StinkyTofu CI on Linux and Windows passing, along with pre-commit and required summary checks.
* Ran `git -c safe.directory=* diff --check origin/develop...HEAD` - passed.
* Ran `python -m py_compile shared\stinkytofu\tasks.py` - passed.
