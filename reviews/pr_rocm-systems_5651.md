# PR Review: ROCm/rocm-systems#5651

* **PR:** https://github.com/ROCm/rocm-systems/pull/5651
* **Title:** `[rocr-debug-agent] Migrate and adjust CI script`
* **Base:** `develop`
* **Head:** `2771be9aafb6be0f8bab664380061983866e2bd5`
* **Reviewed:** 2026-05-06
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**NO BLOCKING FINDINGS / VERIFY FOLLOW-UP** - The migration is directionally sound: the rocr-debug-agent test wrapper now lives with the project and is installed next to the test payload, which is the right shape before TheRock stops carrying a copy. I did not find a code-level blocker in the latest source.

## Latest Comment Check

Checked the latest PR state on 2026-05-06 at head `2771be9a`. Existing inline discussion already covers the `--use-rocm-path` / `--try-rocm-path` naming and fallback semantics, plus a resolved question about the installed script destination. I would not repeat those comments.

## Findings

### SUGGESTION: Add an explicit check before deleting the TheRock copy

The newly added wrapper is installed from rocr-debug-agent's tree at [`projects/rocr-debug-agent/test/CMakeLists.txt#L257-L260`](https://github.com/ROCm/rocm-systems/blob/2771be9aafb6be0f8bab664380061983866e2bd5/projects/rocr-debug-agent/test/CMakeLists.txt#L257-L260), and it discovers the installed test payload under `<rocm-root>/tests/rocm-debug-agent` at [`test_rocr-debug-agent.py#L154-L163`](https://github.com/ROCm/rocm-systems/blob/2771be9aafb6be0f8bab664380061983866e2bd5/projects/rocr-debug-agent/.github/scripts/test_rocr-debug-agent.py#L154-L163).

The latest rocm-systems TheRock CI is green, but the workflow still configures its component matrix from a pinned TheRock checkout: [`therock-test-packages.yml#L29-L45`](https://github.com/ROCm/rocm-systems/blob/2771be9aafb6be0f8bab664380061983866e2bd5/.github/workflows/therock-test-packages.yml#L29-L45), [`#L64`](https://github.com/ROCm/rocm-systems/blob/2771be9aafb6be0f8bab664380061983866e2bd5/.github/workflows/therock-test-packages.yml#L64). That TheRock configuration still maps `rocr-debug-agent` to `build_tools/github_actions/test_executable_scripts/test_rocr-debug-agent.py` ([`fetch_test_configurations.py#L206-L211`](https://github.com/ROCm/TheRock/blob/903ee444eb935adf456bf5df724e1b6f5c2ce962/build_tools/github_actions/fetch_test_configurations.py#L206-L211)), and the reusable test workflow runs the configured `test_script` at [`therock-test-component.yml#L113`](https://github.com/ROCm/rocm-systems/blob/2771be9aafb6be0f8bab664380061983866e2bd5/.github/workflows/therock-test-component.yml#L113).

So I would treat the passing CI as validating the package/test artifacts, but not necessarily as validating that the newly installed project-local wrapper is the runner being invoked. That is fine for this staging PR, but before removing TheRock's copy, I would add one explicit smoke path that invokes the installed `tests/rocm-debug-agent/test_rocr-debug-agent.py` from a fetched/installed artifact layout, or make the TheRock-side follow-up switch the component `test_script` and verify it in CI.

## Notes

The script's default discovery is now much simpler than the old TheRock-side version. It no longer needs `THEROCK_BIN_DIR` or the old split `--test-bin` / `--test-script` override pair; instead it resolves a ROCm tree root from `--try-rocm-path`, `OUTPUT_ARTIFACTS_DIR`, or the installed script location, then expects both `rocm-debug-agent-test` and `run-test.py` under `tests/rocm-debug-agent`. That matches the CMake install layout already used by the rocr-debug-agent test target.

The existing review thread settled on `--try-rocm-path`, and the current implementation matches that name: it uses `ROCM_PATH` only when requested, preserving protection against accidentally testing a system ROCm tree in artifact-based CI.

## Verification

* Refreshed `origin/develop`, `refs/remotes/pr/5651`, PR metadata, and inline review comments on 2026-05-06.
* Reviewed local worktree at `2771be9a`.
* Ran `git -c safe.directory=* diff --check origin/develop...HEAD` - passed.
* Ran `python -m py_compile projects\rocr-debug-agent\.github\scripts\test_rocr-debug-agent.py` - passed.
* Latest GitHub checks are passing, including Linux package build and `rocr-debug-agent` test jobs.
* Did not run the wrapper end-to-end locally because this environment does not have a Linux ROCm artifact layout/GPU test context for rocr-debug-agent.
