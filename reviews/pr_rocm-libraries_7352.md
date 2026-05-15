# PR Review: ROCm/rocm-libraries#7352

* **PR:** https://github.com/ROCm/rocm-libraries/pull/7352
* **Title:** `[hipDNN] ALMIOPEN-1869 Add wheel packaging for hipdnn-frontend Python bindings`
* **Base:** `develop`
* **Head:** `30c3da02037949697a81c9e2510cb9bb9d815903`
* **Reviewed:** 2026-05-15
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**OUT OF REVIEW SCOPE FOR ME** - This PR is about hipDNN frontend Python binding packaging, so I should not take action on it unless explicitly asked. Notes below are kept only as scratch context.

**CHANGES REQUESTED** - Existing review threads already cover the nanobind/TheRock dependency question and some CMake variable propagation details, so I would avoid repeating those. The new blocker I see is that normal `cmake --install` now invokes `pip wheel` for the Python bindings with build isolation still enabled.

## Findings

### BLOCKING: Default CMake install can trigger an isolated pip build

`HIPDNN_BUILD_PYTHON_BINDINGS` now defaults ON at [`projects/hipdnn/CMakeLists.txt#L158`](https://github.com/ROCm/rocm-libraries/blob/30c3da02037949697a81c9e2510cb9bb9d815903/projects/hipdnn/CMakeLists.txt#L158), and the top-level project adds the `python` subdirectory whenever that option is enabled at [`#L252-L254`](https://github.com/ROCm/rocm-libraries/blob/30c3da02037949697a81c9e2510cb9bb9d815903/projects/hipdnn/CMakeLists.txt#L252-L254).

In the non-scikit-build path, that subdirectory registers an `install(CODE)` block that runs `python -m pip wheel --no-deps` during `cmake --install` at [`projects/hipdnn/python/CMakeLists.txt#L73-L89`](https://github.com/ROCm/rocm-libraries/blob/30c3da02037949697a81c9e2510cb9bb9d815903/projects/hipdnn/python/CMakeLists.txt#L73-L89). Because `--no-build-isolation` is not passed, pip can still create an isolated PEP 517 build environment and resolve the `build-system.requires` entries from [`pyproject.toml#L4-L9`](https://github.com/ROCm/rocm-libraries/blob/30c3da02037949697a81c9e2510cb9bb9d815903/projects/hipdnn/python/pyproject.toml#L4-L9).

That defeats the CMake-provided dependency paths and makes a normal install depend on Python packaging state and possible package-index access. This is risky for TheRock/offline/package builds, where the CMake build may have already supplied the exact dependency sources but the install step is expected to be deterministic.

## Suggested Inline Comment

Target: `projects/hipdnn/python/CMakeLists.txt`, line 79.

```text
This install-time `pip wheel` still runs with PEP 517 build isolation enabled. `--no-deps` skips project runtime dependencies, but pip can still create an isolated build env and resolve the `build-system.requires` entries from `pyproject.toml`, which bypasses the dependency sources/paths CMake just configured and can require package-index access during `cmake --install`. For TheRock/package builds, could we either make the wheel build an explicit packaging step or run it with build isolation disabled after ensuring the required build tools are already present?
```

## Verification

* Refreshed `origin/develop` and `refs/remotes/pr/7352`.
* Checked PR metadata: open, not draft, mergeable, review required.
* Checked existing top-level and inline review comments to avoid duplicating the nanobind/TheRock and CMake variable-propagation threads.
* Reviewed changed hipDNN CMake, dependency, and Python packaging files.
* Ran `git -c safe.directory=* diff --check origin/develop...refs/remotes/pr/7352`; passed.
