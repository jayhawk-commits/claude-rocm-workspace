# PR Review: ROCm/rocm-libraries#6985

* **PR:** https://github.com/ROCm/rocm-libraries/pull/6985
* **Title:** `[stinkytofu] Use BUILD_SHARED_LIBS, add invoke build --static option`
* **Base:** `develop`
* **Head:** `1ad3bc742bf18e4e4caea243f5ec1759d3d6e93a`
* **Reviewed:** 2026-05-04
* **State at review:** OPEN

---

## Overall Assessment

**COMMENT / NO BLOCKING FINDINGS** - The latest head expands the original StinkyTofu shared/static toggle into rocisa coverage as well: StinkyTofu now follows `BUILD_SHARED_LIBS`, `invoke build --static` still covers standalone static mode, and CI now smoke-tests rocisa builds/imports on Linux and Windows. I did not find a blocker in the implementation.

## Findings

No blocking findings.

## Delta Since Prior Review

The previous review notes were for head `9e72833a`. The latest head is `1ad3bc74` and adds rocisa-specific changes: the workflow now triggers for rocisa PR changes, installs `nanobind`, builds/import-tests rocisa on both Linux and Windows, switches standalone rocisa Python discovery to `Development.Module`, forces the embedded StinkyTofu dependency to shared for rocisa, and copies `stinkytofu.dll` next to `_rocisa.pyd` on Windows.

## Design Notes

Using `BUILD_SHARED_LIBS` for the standalone StinkyTofu target is consistent with normal CMake behavior and removes the older Windows-only static special case ([`shared/stinkytofu/CMakeLists.txt#L108-L111`](https://github.com/ROCm/rocm-libraries/blob/1ad3bc742bf18e4e4caea243f5ec1759d3d6e93a/shared/stinkytofu/CMakeLists.txt#L108-L111)). The export model already had a `STINKYTOFU_STATIC` path, and the static compile definition is `PUBLIC`, which is the important part for avoiding `dllimport` annotations when static consumers include public headers.

The rocisa integration deliberately forces StinkyTofu shared before adding the StinkyTofu subdirectory ([`projects/hipblaslt/tensilelite/rocisa/CMakeLists.txt#L103-L107`](https://github.com/ROCm/rocm-libraries/blob/1ad3bc742bf18e4e4caea243f5ec1759d3d6e93a/projects/hipblaslt/tensilelite/rocisa/CMakeLists.txt#L103-L107)). That means a caller's `BUILD_SHARED_LIBS=OFF` request will not make rocisa's embedded StinkyTofu static, but this looks intentional for the current package/runtime design: rocisa sets RPATHs for a sibling StinkyTofu shared library on ELF platforms and now copies the DLL beside `_rocisa.pyd` on Windows ([`#L120-L134`](https://github.com/ROCm/rocm-libraries/blob/1ad3bc742bf18e4e4caea243f5ec1759d3d6e93a/projects/hipblaslt/tensilelite/rocisa/CMakeLists.txt#L120-L134), [`#L152-L155`](https://github.com/ROCm/rocm-libraries/blob/1ad3bc742bf18e4e4caea243f5ec1759d3d6e93a/projects/hipblaslt/tensilelite/rocisa/CMakeLists.txt#L152-L155)). I would not block on that, but it is the main design tradeoff in the latest head.

The `invoke` interface still maps cleanly to CMake by passing `-DBUILD_SHARED_LIBS=OFF` only when `--static` is requested, while preserving shared as the default ([`shared/stinkytofu/tasks.py#L160-L191`](https://github.com/ROCm/rocm-libraries/blob/1ad3bc742bf18e4e4caea243f5ec1759d3d6e93a/shared/stinkytofu/tasks.py#L160-L191)). The workflow exercises that static path on Windows and now also adds rocisa standalone build/import coverage on both Linux and Windows ([`stinkytofu-ci.yml#L71-L86`](https://github.com/ROCm/rocm-libraries/blob/1ad3bc742bf18e4e4caea243f5ec1759d3d6e93a/.github/workflows/stinkytofu-ci.yml#L71-L86), [`#L135-L156`](https://github.com/ROCm/rocm-libraries/blob/1ad3bc742bf18e4e4caea243f5ec1759d3d6e93a/.github/workflows/stinkytofu-ci.yml#L135-L156)). That closes the biggest gap from the first review pass.

## Latest Comment Check

Checked latest PR state on 2026-05-04 at head `1ad3bc74`. The PR has one Codecov bot top-level comment and no inline review comments. Current-head human approvals exist from `hcman2`, `aazz44ss`, and `bstefanuk`; the earlier `cycheng` approval is on older commit `22141700`. There were no human comment threads to avoid duplicating.

## Verification

* Refreshed PR metadata, review comments, inline comments, and check status on 2026-05-04.
* Fetched latest `origin/develop` and `refs/pull/6985/head`; reviewed local worktree at `1ad3bc74`.
* Latest GitHub checks for the current head show StinkyTofu CI on Linux and Windows passing, along with pre-commit and required summary checks.
* Ran `git -c safe.directory=* diff --check origin/develop...HEAD` - passed.
* Ran `python -m py_compile shared\stinkytofu\tasks.py` - passed.
