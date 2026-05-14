# TheRock PR 4541 - WSL ROCDXG Stage

Date: 2026-05-05

## Context

- PR: https://github.com/ROCm/TheRock/pull/4541
- Title: Add a dedicated multi-arch stage for WSL rocdxg
- Worktree: `C:\Dev\TheRock-pub\.worktrees\wsl-rocdxg-4541`
- Branch: `wsl-rocdxg-stage-rebase`
- PR head at last pushed check: `0a7bf1a9ac33ea150b005c389244e7de35a40644`
- Local branch was later rebased onto `publish/main` (`537c7f47`) to match the
  CI unit-test version of the path-filter code.

## Current Local Delta

- `BUILD_TOPOLOGY.toml`: move `wsl-rocdxg` from feature group `CORE` to `WSL`
  and make the `wsl-rocdxg` artifact group depend on `base`.
- `CMakeLists.txt`: add `THEROCK_ENABLE_WSL`, default `OFF`.
- `README.md`: document both `THEROCK_ENABLE_WSL` and
  `THEROCK_ENABLE_WSL_ROCDXG`.
- `.github/workflows/multi_arch_build_portable_linux.yml`: make the WSL stage
  depend on `foundation`, so the base artifact exists before the WSL job fetches
  inbound artifacts.
- `base/CMakeLists.txt`: remove the PR's `THEROCK_ENABLE_BASE` early return,
  because WSL now follows the normal staged-build path with `BASE=ON`.

## Flag / Feature Decision

TheRock docs distinguish flags from features:

- Features (`THEROCK_ENABLE_*`) control what subprojects/artifacts are included.
- Flags (`THEROCK_FLAG_*`) control how already-included subprojects are configured.

WSL ROCDXG is a standalone artifact/subproject, so the clean fit is feature
gating, not a new `THEROCK_FLAG_*`. The local change keeps the generated
stage config aligned with other downstream stages because
`configure_stage.py --stage wsl-rocdxg` emits:

```text
-DTHEROCK_ENABLE_ALL=OFF
-DTHEROCK_ENABLE_BASE=ON
-DTHEROCK_ENABLE_WSL_ROCDXG=ON
```

Normal default configures avoid WSL ROCDXG because `THEROCK_ENABLE_WSL` defaults
to `OFF`.

## Base Artifact Decision

Conclusion: avoid a WSL-specific `BASE=OFF` path. WSL should consume the `base`
artifact the same way other non-foundation stages do.

- Other stages such as `math-libs` get `THEROCK_ENABLE_BASE=ON` from inbound
  artifact dependencies, then fetch/bootstrap `base` from `foundation`.
- Bootstrapping writes prebuilt markers next to stage directories such as
  `base/half/stage` and `base/rocm-cmake/stage`, so CMake can enter `base/`
  without rebuilding those projects from source.
- WSL now declares `artifact_group_deps = ["base"]` and the workflow has
  `needs: foundation`, so the WSL stage gets the same prebuilt-base behavior.
- The workflow still passes `-DTHEROCK_BUNDLE_SYSDEPS=OFF`, so bundled sysdeps
  remain disabled for WSL.

## Feature-Gating Pattern

`THEROCK_ENABLE_CORE` is a feature group default, not a directory-level guard.
It is consumed by generated per-artifact feature declarations such as
`THEROCK_ENABLE_BASE`, `THEROCK_ENABLE_CORE_RUNTIME`, and
`THEROCK_ENABLE_HIP_RUNTIME`.

The closer established pattern for this PR is topology-driven inbound artifacts:
declare the dependency in `BUILD_TOPOLOGY.toml`, let `configure_stage.py` enable
the generated feature variables, and let CI bootstrap prebuilt inbound artifacts.

## Verification So Far

- `python build_tools/topology_to_cmake.py --validate-only` passes.
- `python build_tools/configure_stage.py --stage wsl-rocdxg --platform linux ...`
  emits `THEROCK_ENABLE_BASE=ON` and `THEROCK_ENABLE_WSL_ROCDXG=ON` plus dist
  target args and `THEROCK_ENABLE_ALL=OFF`.
- Direct `get_stage_features(..., "wsl-rocdxg", platform_name="linux")` returns
  `["BASE", "WSL_ROCDXG"]`.
- Direct topology check shows `wsl-rocdxg` source sets remain `["rocm-systems"]`
  and inbound artifacts are `["base"]`.
- `git diff --check` passes for the current local delta.
- WSL ROCDXG multi-arch build passed on PR CI after the staged-base changes.
- Unit Tests later failed because current `main` has a path-filter unit test
  requiring every CI-transitive reusable workflow to be listed in
  `_GITHUB_WORKFLOWS_CI_FILENAMES`.

## Checkpoint - 2026-05-11

Current local TheRock delta over the PR branch follows the staged-base approach:

- `BUILD_TOPOLOGY.toml`: move `wsl-rocdxg` from `CORE` to `WSL` and add
  `artifact_group_deps = ["base"]`.
- `CMakeLists.txt`: add top-level `THEROCK_ENABLE_WSL`, default `OFF`.
- `README.md`: document `THEROCK_ENABLE_WSL` and `THEROCK_ENABLE_WSL_ROCDXG`.
- `.github/workflows/multi_arch_build_portable_linux.yml`: add
  `needs: foundation` to the WSL job.
- `base/CMakeLists.txt`: remove the `THEROCK_ENABLE_BASE` early return from the
  PR branch.

Important nuance: the WSL workflow already configures with
`-DTHEROCK_BUNDLE_SYSDEPS=OFF`, so the sysdeps build path is explicitly disabled
there. The remaining question is whether the `base/CMakeLists.txt` guard is
strictly required for WSL, or whether WSL can work with BASE left alone when
sysdeps bundling is disabled.

Superseded experiment: dropping the base guard while WSL had no inbound `base`
artifact would leave top-level configure entering `base/` without either base
sources or prebuilt base stages. Adding the topology dependency on `base` fixes
that by making WSL mirror the normal downstream-stage behavior.

## Checkpoint - Unit Test Metadata

The PR added `.github/workflows/multi_arch_build_wsl_rocdxg_artifacts.yml` and
wired it into `multi_arch_build_portable_linux.yml`. Current `main` has a
build-tools unit test that scans `ci.yml` / `multi_arch_ci.yml` transitive
workflow uses and compares them with
`build_tools/github_actions/configure_ci_path_filters.py`.

Local fix after rebasing onto `publish/main`:

- Add `"multi_arch_build_wsl_rocdxg_artifacts.yml"` to
  `_GITHUB_WORKFLOWS_CI_FILENAMES`.
- Verified with:

```text
python -m pytest build_tools/github_actions/tests/configure_ci_path_filters_test.py
7 passed
```

The PR branch was force-pushed with a single squashed commit:
`eaf190262e3fd7893d265454bf162301e4945d0d`.

## Checkpoint - WSL Development Documentation

Local documentation draft added after the squashed push:

- `docs/development/wsl_rocdxg.md`: focused maintainer note for the WSL ROCDXG
  CI stage.
- `docs/development/README.md`: link from the development docs index.
- `docs/development/ci_overview.md`: short pointer from the CI overview.
- `docs/development/windows_support.md`: cross-link clarifying that native
  Windows source builds are separate from the WSL ROCDXG CI stage.

The doc explains the Windows runner vs WSL Ubuntu shell boundary, why Linux
`foundation` / `base` artifacts are consumed, the expected configure arguments,
and the differences from portable Linux and native Windows artifact workflows.

The documentation change was committed as `0a7bf1a9` and pushed to the PR
branch.
