# PR Review: ROCm/rocm-libraries#7152

* **PR:** https://github.com/ROCm/rocm-libraries/pull/7152
* **Title:** `[hipcub]Add test filter categorisation for hipcub`
* **Base:** `develop`
* **Head:** `bb991fa48ae2782aec3037b2bb68e58c2313b05e`
* **Reviewed:** 2026-05-15
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**CHANGES REQUESTED / SAME STACK AS #7132** - The hipCUB categorization intent is in scope, but this PR has the same two readiness issues as the related rocThrust/rocRAND stack: category tests can be skipped on a fresh configure because the runtime output directory does not exist yet, and the reusable TheRock workflows are pinned to a mutable user branch.

## Findings

### BLOCKING: category tests may never be generated on a fresh configure

The PR collects hipCUB test targets and passes each target's `RUNTIME_OUTPUT_DIRECTORY` into `apply_test_category_labels()` at [`projects/hipcub/test/CMakeLists.txt#L144-L154`](https://github.com/ROCm/rocm-libraries/blob/bb991fa48ae2782aec3037b2bb68e58c2313b05e/projects/hipcub/test/CMakeLists.txt#L144-L154). Those hipCUB targets set their runtime output directory to `${CMAKE_BINARY_DIR}/test/hipcub` at [`projects/hipcub/test/hipcub/CMakeLists.txt#L78-L81`](https://github.com/ROCm/rocm-libraries/blob/bb991fa48ae2782aec3037b2bb68e58c2313b05e/projects/hipcub/test/hipcub/CMakeLists.txt#L78-L81).

The shared helper checks `IS_DIRECTORY` during configure and returns without generating the category CTest entries if the directory does not already exist at [`shared/ctest/TestCategories.cmake#L25-L30`](https://github.com/ROCm/rocm-libraries/blob/bb991fa48ae2782aec3037b2bb68e58c2313b05e/shared/ctest/TestCategories.cmake#L25-L30). Since this PR does not create `${CMAKE_BINARY_DIR}/test/hipcub` before the helper call, a fresh configure can skip the new `*_quick_suite` and `*_standard_suite` tests entirely.

### BLOCKING: TheRock test workflows are pinned to a mutable user branch

The PR also changes the TheRock checkout in both reusable package-test workflows to `users/dravindr/tr_rand_cub_thrust`:

* [`.github/workflows/therock-test-component.yml#L73`](https://github.com/ROCm/rocm-libraries/blob/bb991fa48ae2782aec3037b2bb68e58c2313b05e/.github/workflows/therock-test-component.yml#L73)
* [`.github/workflows/therock-test-packages.yml#L46`](https://github.com/ROCm/rocm-libraries/blob/bb991fa48ae2782aec3037b2bb68e58c2313b05e/.github/workflows/therock-test-packages.yml#L46)

That makes the reusable CI path depend on mutable branch state outside this PR, and it leaves these two workflows out of sync with the other TheRock workflow refs.

## Suggested Inline Comments

Target: `projects/hipcub/test/CMakeLists.txt`, line 149.

```text
On a fresh build tree this can return before generating any category tests. `_hc_dir` comes from `RUNTIME_OUTPUT_DIRECTORY`, which is `${CMAKE_BINARY_DIR}/test/hipcub`, but the shared helper checks `IS_DIRECTORY` during configure and returns if that output directory does not already exist. Could we create the directory before calling the helper, or relax the helper so output directories only need to exist by test time?
```

Target: `.github/workflows/therock-test-component.yml`, line 73. Mention the same issue also applies to `.github/workflows/therock-test-packages.yml`, line 46.

```text
This should not land pointing at a mutable user branch. These reusable TheRock test workflows become non-reproducible if the branch moves or disappears, and they can start validating behavior unrelated to this hipCUB PR. Could we pin this back to the intended TheRock commit, or update all TheRock workflow refs together to a reviewed upstream commit?
```

## Verification

* Refreshed `origin/develop` and `refs/remotes/pr/7152`.
* Checked PR metadata: open, not draft, mergeable, review required.
* Checked top-level and inline comments; no existing inline review comments at review time.
* Reviewed changed workflow and hipCUB CTest categorization files.
* Ran `git -c safe.directory=* diff --check origin/develop...refs/remotes/pr/7152`; passed.
* Checked required PR checks; they were green at review time.
