# PR Review: ROCm/TheRock#4570

* **PR:** https://github.com/ROCm/TheRock/pull/4570
* **Title:** `[ci] Adding determine_rocm_test_dependencies.py script`
* **Base:** `main`
* **Head:** `060a50d2056bf22f87db56e65c69a8cf336d5a3c`
* **Reviewed:** 2026-04-30
* **State at review:** OPEN

---

## Overall Assessment

**CHANGES REQUESTED** - The new dependency-selection script can silently drop CMake files on any read error. Because this script is meant to reduce downstream tests, silent degradation can become under-testing.

## Findings

### BLOCKING: CMake read failures are silently ignored

`parse_cmake_test_subprojects()` catches every exception from `cmake_file.read_text()` and continues at [`determine_rocm_test_dependencies.py#L27-L31`](https://github.com/ROCm/TheRock/blob/060a50d2056bf22f87db56e65c69a8cf336d5a3c/test_tools/determine_rocm_test_dependencies.py#L27-L31). If the script cannot read a relevant `CMakeLists.txt` due to encoding, path, filesystem, or environment issues, it returns an incomplete dependency map without failing the CI step.

That is risky for this feature specifically: a missing dependency entry means the caller may skip tests that should have run.

**Required action:** Fail fast on unexpected read errors. Prefer `read_text(encoding="utf-8")` and let exceptions propagate, or catch only a very narrow, justified exception and log enough context before re-raising.

## Verification

* Inspected the PR diff and changed CMake declarations.
* Ran `python test_tools\tests\determine_rocm_test_dependencies_test.py -v`; both tests passed locally.
