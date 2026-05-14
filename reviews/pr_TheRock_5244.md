# PR Review: ROCm/TheRock#5244

* **PR:** https://github.com/ROCm/TheRock/pull/5244
* **Title:** `[ci] Add more test dependency for test subprojects`
* **Base:** `main`
* **Head:** `9caf5f1eca06af32d8307e7d3380d2135a83ab81`
* **Reviewed:** 2026-05-14
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**NO BLOCKING FINDINGS / VERIFY CI** - I did not find a code-level blocker in the dependency metadata or helper changes. The script now supports empty `TEST_SUBPROJECTS` markers, still includes the changed project itself in `get_subprojects_to_test()`, and the focused unit tests pass from the PR snapshot.

I would still ask for the current CI failures to be retried or triaged before approval. The latest Multi-Arch CI summary is failing on Linux `rocblas`, Windows `gfx110X-all` sanity, and Windows `gfx110X-all` ROCm wheels. I did not find evidence tying those directly to the helper logic, but they keep the merge signal noisy.

## Findings

None.

## Review Notes

The `rocSPARSE` metadata no longer lists `rocSPARSE` inside `TEST_SUBPROJECTS`, but the public helper behavior still includes the changed component itself because `get_subprojects_to_test()` seeds the result with the changed project set before adding dependencies. From the PR snapshot:

```text
python test_tools\determine_rocm_test_dependencies.py --therock-dir . --changed rocSPARSE
["hipsolver", "hipsparse", "rocsolver", "rocsparse"]
```

That looks consistent with the intent: CMake metadata describes additional tests, while the script output contains self plus additional dependencies.

## Suggested Review Comment

```text
I do not have blocking comments on the dependency-script changes. I checked the empty `TEST_SUBPROJECTS` handling and the changed-project self-inclusion behavior; `--changed rocSPARSE` still returns `rocsparse` plus the new dependencies.

Before approval, could you please retry or triage the current Multi-Arch CI failures? The latest run is failing Linux `rocblas`, Windows `gfx110X-all` sanity, and Windows `gfx110X-all` ROCm wheels. I do not see a direct source-level blocker from the diff, but I would like the CI signal cleaned up or explained.
```

## Verification

* Refreshed `origin/main` and `refs/remotes/pr/5244`.
* Checked latest PR metadata: open, not draft, mergeable, review required.
* Reviewed changed files:
  * `math-libs/BLAS/CMakeLists.txt`
  * `math-libs/CMakeLists.txt`
  * `test_tools/determine_rocm_test_dependencies.py`
  * `test_tools/tests/determine_rocm_test_dependencies_test.py`
* Ran `git -c safe.directory=* diff --check origin/main...refs/remotes/pr/5244`; passed.
* Ran focused unit tests from a PR snapshot:

```text
python -m unittest discover -s test_tools\tests -p "determine_rocm_test_dependencies_test.py"
```

Result: 4 tests passed.

* Ran `--list-subprojects --show-deps` and `--changed rocSPARSE` from the PR snapshot to confirm empty markers and self-inclusion behavior.
* Checked latest public PR checks; Multi-Arch CI is failing, while unit tests and pre-commit are passing.
