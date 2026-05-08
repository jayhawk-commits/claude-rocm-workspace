# PR Review: ROCm/TheRock#4570

* **PR:** https://github.com/ROCm/TheRock/pull/4570
* **Title:** `[ci] Adding determine_rocm_test_dependencies.py script`
* **Base:** `main`
* **Head:** `b972362a8b68e1cc5c996f0a0db3d40844b36c1f`
* **Reviewed:** 2026-05-06
* **State at review:** OPEN

---

## Overall Assessment

**NO NEW BLOCKING FINDINGS** - The original review finding was addressed: `parse_cmake_test_subprojects()` no longer catches and suppresses CMake file read errors. I would not repeat that comment.

## Latest Comment Check

Checked latest PR state on 2026-05-06 at head `b972362a`. Existing comments cover the move from `build_tools` to `test_tools` and the previously requested fail-fast behavior for the broad `try` block. The broad `try` block is gone in the latest source.

## Findings

No remaining blocking findings in the latest head.

## Notes

The invalid `--therock-dir` case is not worth holding the PR on. A typo in `--therock-dir` currently returns only the changed project instead of failing:

```powershell
$ python test_tools\determine_rocm_test_dependencies.py --projects rocBLAS
["hipblas", "rocblas", "rocsolver"]

$ python test_tools\determine_rocm_test_dependencies.py --therock-dir .\does-not-exist --projects rocBLAS
["rocblas"]
```

That could be hardened later by validating that `therock_dir` exists and contains CMake files, but I would treat it as optional because the CI caller controls this value and a bad workspace/root should fail quickly elsewhere.

The parser currently uses `\w+` for both the declared subproject name and `TEST_SUBPROJECTS` entries. That works for the BLAS entries in this PR, but it will not be safe for future names containing hyphens. If this helper expands beyond the current BLAS/Sparse cases, add tests for hyphenated TheRock target/test names before relying on it for those projects.

## Verification

* Refreshed `origin/main`, `refs/remotes/pr/4570`, PR metadata, and inline review comments on 2026-05-06.
* Reviewed local worktree at `b972362a`.
* Confirmed the prior broad `try/except` around `cmake_file.read_text()` was removed.
* Ran `python test_tools\tests\determine_rocm_test_dependencies_test.py -v` - passed, 2 tests.
* Ran `python -m py_compile test_tools\determine_rocm_test_dependencies.py test_tools\tests\determine_rocm_test_dependencies_test.py` - passed.
* Ran `git -c safe.directory=* diff --check origin/main...HEAD` - passed.
* Latest GitHub checks show pre-commit and unit tests passing; larger Multi-Arch CI still has failures at review time.
