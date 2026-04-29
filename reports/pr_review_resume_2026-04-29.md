# PR Review Resume Notes - 2026-04-29

## Request

Review these open PRs using workspace review best practices:

- ROCm/TheRock#4905 - `[ci] Removing ctest timeout`
- ROCm/TheRock#4603 - `[ci] Adding host-asan for postsubmit`
- ROCm/TheRock#4570 - `[ci] Adding determine_rocm_test_dependencies.py script`
- ROCm/rocm-libraries#6133 - `[ci] Adding label support for PRs`
- ROCm/rocm-libraries#6063 - `[ci] skipping builds if artifacts are available and run tests directly`

The final truncated PR title resolved to ROCm/rocm-libraries#6063.

## Workspace State

- No source files or review files were edited by Codex during this pass.
- Existing dirty meta-workspace files were present before this note was added:
  - `AGENTS.md`
  - `CLAUDE.md`
  - `reports/rocm_libraries_test_runner_split_2026-04-29.md`
  - `reports/rocm_systems_test_runner_split_2026-04-28.md`

## Local Refs And Worktrees

Fetched refs:

- In `TheRock-pub`:
  - `refs/remotes/pr/4905`
  - `refs/remotes/pr/4603`
  - `refs/remotes/pr/4570`
- In `rocm-libs-pub`:
  - `refs/remotes/pr/6133`
  - `refs/remotes/pr/6063`

Created review worktrees:

- `TheRock-pub/.worktrees/review-pr-4905`
- `TheRock-pub/.worktrees/review-pr-4603`
- `TheRock-pub/.worktrees/review-pr-4570`
- `rocm-libs-pub/.worktrees/review-pr-6133`
- `rocm-libs-pub/.worktrees/review-pr-6063`

Note: `rocm-libs-pub/.worktrees/review-pr-6133` appeared populated, but `git worktree list` marked it locked after the initial worktree command timed out. It may need a quick status/safe-directory/worktree health check before use.

## Review Guidance Already Read

Read:

- `AGENTS.md`
- `directory-map.md`
- `reviews/README.md`
- `reviews/REVIEW_GUIDELINES.md`
- `reviews/REVIEW_TYPES.md`
- `reviews/guidelines/github_actions.md`
- `reviews/guidelines/pr_hygiene.md`
- `reviews/guidelines/pr_patterns.md`
- `reviews/guidelines/security.md`

Key review emphasis:

- Lead with findings, ordered by severity.
- For workflow changes, trace reusable workflow callers and input propagation.
- Check trigger coverage, especially `workflow_dispatch` and `workflow_call`.
- Check Python fail-fast behavior and runtime dependencies for workflow-called scripts.
- Use CI evidence when available to confirm workflow hypotheses.
- Write review files as `reviews/pr_{REPO}_{NUMBER}.md`.

## Where Review Paused

### ROCm/TheRock#4905

Diff inspected. It only removes `ctest --timeout` arguments from component test scripts.

Potential finding:

- `build_tools/github_actions/test_executable_scripts/test_miopenprovider.py` still has a stale comment saying that increasing the timeout there also requires increasing the job timeout, even though the script-level timeout was removed. Likely cleanup issue, probably IMPORTANT or SUGGESTION depending on review strictness.

Confirmed context:

- `.github/workflows/test_component.yml` still has a job step timeout at `fromJSON(inputs.component).timeout_minutes`.
- `rg -- "--timeout|timeout =" build_tools/github_actions/test_executable_scripts` shows other scripts still intentionally use timeout logic, so #4905 is not globally removing all `ctest` timeouts.

No review file written yet.

### ROCm/TheRock#4603

Metadata and changed files fetched. Diff inspection started but did not finish.

Changed files:

- `.github/workflows/build_portable_linux_artifacts.yml`
- `.github/workflows/multi_arch_build_portable_linux.yml`
- `.github/workflows/multi_arch_ci_asan.yml`
- `build_tools/github_actions/amdgpu_family_matrix.py`
- `build_tools/github_actions/configure_multi_arch_ci.py`
- `build_tools/github_actions/tests/configure_multi_arch_ci_test.py`

Observed changes needing review:

- `multi_arch_ci_asan.yml` adds `push` on `main`.
- `expand_build_configs()` maps push-triggered `asan` to `host-asan`, but may need careful tracing because `_expand_build_config_for_platform()` still receives `ci_inputs` with `build_variant == "asan"`.
- Build runner selection now treats any variant containing `san` as sanitizer.
- `iree-compiler` and `fusilli-libs` get skipped for `host-asan`.
- Tests include a duplicated `test_variant_filters_by_platform_and_family_support` method in the diff; verify final file behavior and whether one overwrites the other in `unittest`.

No final findings yet.

### ROCm/TheRock#4570

Not substantively reviewed yet.

Changed files:

- `cmake/therock_subproject.cmake`
- `math-libs/BLAS/CMakeLists.txt`
- `test_tools/determine_rocm_test_dependencies.py`
- `test_tools/tests/determine_rocm_test_dependencies_test.py`

Likely focus:

- Python script parsing CMake directly.
- Fail-fast behavior.
- Whether regex parsing is robust enough for intended CMake syntax.
- Test quality and whether tests use real files without becoming brittle change detectors.

### ROCm/rocm-libraries#6133

Not substantively reviewed yet.

Changed files:

- `.github/scripts/tests/therock_configure_ci_test.py`
- `.github/scripts/therock_configure_ci.py`
- `.github/scripts/therock_matrix.py`
- `.github/workflows/therock-ci.yml`

Likely focus:

- Label parsing and PR-only scoping.
- Whether labels combine with file detection correctly.
- Input propagation through `therock-ci.yml`.
- CI evidence from linked run in PR body.

### ROCm/rocm-libraries#6063

Not substantively reviewed yet.

Changed files:

- `.github/scripts/therock_configure_ci.py`
- `.github/workflows/therock-ci-linux.yml`
- `.github/workflows/therock-ci-windows.yml`
- `.github/workflows/therock-ci.yml`
- `.github/workflows/therock-test-packages.yml`
- `docs/ci_behavior_manipulation.md`

Likely focus:

- Skip-build/prebuilt-artifact path for `workflow_dispatch`.
- Required `artifact_run_id` behavior.
- Whether test jobs correctly run when builds are skipped and do not run after failed builds.
- Linux and Windows input propagation.
- Documentation accuracy.
- CI evidence from linked runs in PR body.

## Suggested Resume Steps

1. Re-check `git status --short` in the meta-workspace and target repos.
2. Verify rocm-libraries#6133 worktree health.
3. Continue #4603 diff review and run focused unit tests if lightweight.
4. Review #4570, #6133, and #6063 in order.
5. Write review files under `reviews/`.
