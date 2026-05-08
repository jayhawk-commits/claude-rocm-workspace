# PR Review: ROCm/TheRock#5040

* **PR:** https://github.com/ROCm/TheRock/pull/5040
* **Title:** `Fallback libhipcxx tests to AMDGPU_TARGETS`
* **Base:** `main`
* **Head:** `48d872c77a45705deb3d264c73e849877888613b`
* **Reviewed:** 2026-05-05
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**NO NEW BLOCKING FINDINGS** - The implementation is small and the added fail-fast behavior avoids passing an empty architecture into the libhipcxx test invocations. I did not find a new correctness issue that is not already covered by the existing review discussion.

## Existing Comment Check

Checked the latest PR state on 2026-05-05 at head `48d872c7`. There are two existing inline comments from Scott Todd:

* [`libhipcxx_utils.py`](https://github.com/ROCm/TheRock/pull/5040/files#diff-a7f0606a81ede53820e01581d628cc1ac06632e2675e0c24fe1bcb8cf80c2d6bR50): the design question of why libhipcxx needs to fall back from `offload-arch` instead of trusting `offload-arch` coverage.
* [`libhipcxx_utils_test.py`](https://github.com/ROCm/TheRock/pull/5040/files#diff-e6d0d4cc7c472e21a0d61ee900dc550b6321763920371b7bd613881203e4d191R15): whether unit tests for scripts under `test_executable_scripts` belong in this repo as those scripts move toward project-owned code.

Those comments cover the review concerns I would otherwise raise, so I would avoid adding a duplicate comment.

## Notes

The change makes `get_gpu_architecture_portable()` prefer the existing `offload-arch` path, then fall back to `AMDGPU_TARGETS` only when `offload-arch` returns no usable output or cannot be executed. The returned fallback normalizes comma- or semicolon-delimited targets into a semicolon list, which is passed to CMake through the existing direct `subprocess.run([...])` argument list.

The two libhipcxx test scripts now raise `RuntimeError` if architecture discovery still returns nothing. That is a useful guard: previously a missing architecture could continue into configure/test commands in a less obvious state.

## Verification

* Refreshed `origin/main`, `refs/remotes/pr/5040`, PR metadata, and inline review comments on 2026-05-05.
* Reviewed local worktree at `48d872c7`.
* Ran `git -c safe.directory=* diff --check origin/main...HEAD` - passed.
* Ran `python -m unittest build_tools\github_actions\tests\libhipcxx_utils_test.py` - passed, 3 tests.
* Ran `python -m py_compile` on the touched libhipcxx utility and test scripts - passed.
* Latest PR review decision is `APPROVED`; existing CI had completed pre-commit/unit-test jobs, with some larger Multi-Arch CI jobs still failing or queued at review time.
