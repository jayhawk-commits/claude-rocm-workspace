# PR Review: ROCm/rocm-libraries#7219

* **PR:** https://github.com/ROCm/rocm-libraries/pull/7219
* **Title:** `[ci] Adding test dependency script to rocm-libraries`
* **Base:** `develop`
* **Head:** `162f9dbb4acfe47e71b25fd326b25408fe5bb765`
* **Reviewed:** 2026-05-11
* **State at review:** OPEN

---

## Summary

This PR updates rocm-libraries CI to query TheRock's ROCm test dependency helper and use those results to expand `projects_to_test`. It also bumps the pinned TheRock checkout in the TheRock CI workflows to a commit that contains the helper.

## Overall Assessment

**CHANGES REQUESTED** - The dependency lookup is being applied at the wrong granularity. The PR computes test dependencies across all changed components, then assigns that union to every project matrix row, so a row that only built/downloaded one artifact group can try to run tests for unrelated groups.

## Findings

### BLOCKING: TheRock-derived test dependencies are assigned to every matrix row

`collect_projects_to_run()` first collects `tests_per_component` for every changed subtree at [`therock_matrix.py#L205-L218`](https://github.com/ROCm/rocm-libraries/blob/162f9dbb4acfe47e71b25fd326b25408fe5bb765/.github/scripts/therock_matrix.py#L205-L218). Later, inside the loop that emits each project matrix row, it unconditionally adds every dependency list from `tests_per_component` into that row's `projects_to_test` at [`therock_matrix.py#L287-L299`](https://github.com/ROCm/rocm-libraries/blob/162f9dbb4acfe47e71b25fd326b25408fe5bb765/.github/scripts/therock_matrix.py#L287-L299).

That is okay only when the changed components all collapse into a single build row. When the PR touches CI files or otherwise selects multiple independent project groups, each row receives the global dependency union even though its `cmake_options` still build only that row's project group. The current PR CI shows the failure mode: a Linux test job tried to run `./build/bin/hipblas-test` and failed immediately with `FileNotFoundError` because that test executable was not present in the artifacts downloaded for that row:

```text
INFO:root:++ Exec [...]$ ./build/bin/hipblas-test ...
FileNotFoundError: [Errno 2] No such file or directory: './build/bin/hipblas-test'
```

Public job evidence: https://github.com/ROCm/rocm-libraries/actions/runs/25692469298/job/75435412230?pr=7219

**Required action:** Keep dependency expansion scoped to the project row/component group that will build and download those artifacts. Alternatively, if a dependency requires a different artifact group, merge the corresponding build/test rows before assigning `projects_to_test`. Add a regression test with at least two independent output rows where only one component has TheRock-derived dependencies, and assert that the unrelated row does not inherit them.

## Notes

The new unit tests cover single-row cases and a mixed BLAS fallback case, but not the multi-row case that is failing in CI. The focused `therock_matrix_test.py` suite passed locally from the PR snapshot, so the missing coverage is specifically around independent project rows rather than the helper import itself.

## Verification

* Refreshed `origin/develop` and `refs/remotes/pr/7219`.
* Checked latest PR metadata, top-level comments, reviews, and inline comments.
* Ran `git diff --check origin/develop...refs/remotes/pr/7219`; passed.
* Ran the focused matrix tests:

```text
python -m unittest discover -s .github\scripts\tests -p "therock_matrix_test.py"
```

Result: 10 tests passed.

* Sampled a failed public CI job and confirmed the failure is a missing test executable in the row's downloaded artifacts, not a test assertion failure.
