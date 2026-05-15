# PR Review: ROCm/rocm-libraries#7215

* **PR:** https://github.com/ROCm/rocm-libraries/pull/7215
* **Title:** `Add test filter standardization to rocthrust`
* **Base:** `develop`
* **Head:** `836ef0942236655a87c7e88859c34921324fb65e`
* **Reviewed:** 2026-05-15
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**CHANGES REQUESTED / SAME STACK AS #7132** - The rocThrust categorization intent is in scope, but this PR has two issues before it is ready for approval: the generated category tests can be skipped on a fresh configure because the runtime output directory does not exist yet, and the reusable TheRock workflows are pinned to a mutable user branch. Since this is part of the same test-filter standardization stack as #7132, it may be best to wait for the author/other reviewers to settle the shared fix once.

## Findings

### BLOCKING: category tests may never be generated on a fresh configure

The new loop gets each test target's `RUNTIME_OUTPUT_DIRECTORY` and passes it directly to `apply_test_category_labels()` at [`projects/rocthrust/test/CMakeLists.txt#L359-L363`](https://github.com/ROCm/rocm-libraries/blob/836ef0942236655a87c7e88859c34921324fb65e/projects/rocthrust/test/CMakeLists.txt#L359-L363). Those targets set the runtime output directory to `${CMAKE_BINARY_DIR}/test/` at [`#L97-L100`](https://github.com/ROCm/rocm-libraries/blob/836ef0942236655a87c7e88859c34921324fb65e/projects/rocthrust/test/CMakeLists.txt#L97-L100).

The shared helper validates that `working_dir` is already an existing directory and returns without generating category tests if it is not, at [`shared/ctest/TestCategories.cmake#L25-L30`](https://github.com/ROCm/rocm-libraries/blob/836ef0942236655a87c7e88859c34921324fb65e/shared/ctest/TestCategories.cmake#L25-L30). On a fresh configure, `${CMAKE_BINARY_DIR}/test/` is an output directory, not something this PR creates before calling the helper, so the new `*_quick_suite` and `*_standard_suite` tests can be skipped entirely.

### BLOCKING: TheRock test workflows are pinned to a mutable user branch

The PR also changes the TheRock checkout in both reusable package-test workflows to `users/dravindr/tr_rand_cub_thrust`:

* [`.github/workflows/therock-test-component.yml#L73`](https://github.com/ROCm/rocm-libraries/blob/836ef0942236655a87c7e88859c34921324fb65e/.github/workflows/therock-test-component.yml#L73)
* [`.github/workflows/therock-test-packages.yml#L46`](https://github.com/ROCm/rocm-libraries/blob/836ef0942236655a87c7e88859c34921324fb65e/.github/workflows/therock-test-packages.yml#L46)

That makes the reusable CI path depend on mutable branch state outside this PR, and it leaves these two workflows out of sync with the other TheRock workflow refs.

## Suggested Inline Comments

Target: `projects/rocthrust/test/CMakeLists.txt`, line 361.

```text
On a fresh build tree this can return before generating any category tests. `_rt_dir` comes from `RUNTIME_OUTPUT_DIRECTORY`, which is `${CMAKE_BINARY_DIR}/test/`, but the shared helper checks `IS_DIRECTORY` during configure and returns if that output directory does not already exist. Could we create the directory before calling the helper, or relax the helper so output directories only need to exist by test time?
```

Target: `.github/workflows/therock-test-component.yml`, line 73. Mention the same issue also applies to `.github/workflows/therock-test-packages.yml`, line 46.

```text
This should not land pointing at a mutable user branch. These reusable TheRock test workflows become non-reproducible if the branch moves or disappears, and they can start validating behavior unrelated to this rocThrust PR. Could we pin this back to the intended TheRock commit, or update all TheRock workflow refs together to a reviewed upstream commit?
```

## Verification

* Refreshed `origin/develop` and `refs/remotes/pr/7215`.
* Checked PR metadata: open, not draft, mergeable, review required.
* Checked top-level and inline comments; no existing inline review comments at review time.
* Reviewed changed workflow and rocThrust CTest categorization files.
* Ran `git -c safe.directory=* diff --check origin/develop...refs/remotes/pr/7215`; passed.
* Checked required PR checks; they were green at review time.
