# TheRock PR 4541 - WSL ROCDXG Stage

Date: 2026-05-05

## Context

- PR: https://github.com/ROCm/TheRock/pull/4541
- Title: Add a dedicated multi-arch stage for WSL rocdxg
- Worktree: `C:\Dev\TheRock-pub\.worktrees\wsl-rocdxg-4541`
- Branch: `wsl-rocdxg-stage-rebase`
- PR head at last check: `82caf145074b3ee7601d6acce717505af249a4ee`

## Current Local Delta

- `BUILD_TOPOLOGY.toml`: move `wsl-rocdxg` from feature group `CORE` to `WSL`.
- `CMakeLists.txt`: add `THEROCK_ENABLE_WSL`, default `OFF`.

## Flag / Feature Decision

TheRock docs distinguish flags from features:

- Features (`THEROCK_ENABLE_*`) control what subprojects/artifacts are included.
- Flags (`THEROCK_FLAG_*`) control how already-included subprojects are configured.

WSL ROCDXG is a standalone artifact/subproject, so the clean fit is feature
gating, not a new `THEROCK_FLAG_*`. The local change keeps the generated
stage config working because `configure_stage.py --stage wsl-rocdxg` emits:

```text
-DTHEROCK_ENABLE_ALL=OFF
-DTHEROCK_ENABLE_WSL_ROCDXG=ON
```

Normal default configures avoid WSL ROCDXG because `THEROCK_ENABLE_WSL` defaults
to `OFF`.

## BASE=OFF Verification

Conclusion: the PR's `base/CMakeLists.txt` early return is required for the
WSL-only `THEROCK_ENABLE_BASE=OFF` case under the current top-level structure.

- The top-level `CMakeLists.txt` still calls `add_subdirectory(base)`
  unconditionally.
- Without the early return, `base/CMakeLists.txt` declares base subprojects and
  provides the `base` artifact even when `THEROCK_ENABLE_BASE=OFF`.
- The WSL stage generated args do not enable `BASE`, so this guard is needed to
  keep a WSL-only stage from pulling base into the build graph.

## Feature-Gating Pattern

`THEROCK_ENABLE_CORE` is a feature group default, not a directory-level guard.
It is consumed by generated per-artifact feature declarations such as
`THEROCK_ENABLE_BASE`, `THEROCK_ENABLE_CORE_RUNTIME`, and
`THEROCK_ENABLE_HIP_RUNTIME`.

The closer established pattern is therefore to guard artifact sections with the
generated artifact feature variable. `base/CMakeLists.txt` now follows that
shape with an `if(THEROCK_ENABLE_BASE) ... endif(THEROCK_ENABLE_BASE)` wrapper
instead of a top-level early return.

There are many early-return examples in dual-mode third-party and sysdeps
CMakeLists files, but those are not the closest pattern for generated feature
gates.

## Verification So Far

- `python build_tools/topology_to_cmake.py --validate-only` passes.
- `python build_tools/configure_stage.py --stage wsl-rocdxg --platform linux ...`
  emits only `THEROCK_ENABLE_WSL_ROCDXG=ON` plus dist target args and
  `THEROCK_ENABLE_ALL=OFF`.
- Direct `get_stage_features(..., "wsl-rocdxg", platform_name="linux")` returns
  `["WSL_ROCDXG"]`; `BASE` is intentionally absent.
- `git show HEAD^:base/CMakeLists.txt | Select-String ...` confirms the
  pre-change base file had no `THEROCK_ENABLE_BASE` guard before declaring base
  subprojects and `artifact-base`.
- `git diff --check` passes for the current local delta.
- PR check status shows current failure in the WSL ROCDXG stage, but logs were
  unavailable while the run was still in progress.
