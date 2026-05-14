# PR Review: ROCm/TheRock#4541

* **PR:** https://github.com/ROCm/TheRock/pull/4541
* **Title:** `Add a dedicated multi-arch stage for WSL rocdxg`
* **Base:** `main` at `482ff586c261379e1132cf776f122e1d0972a8a0`
* **Head:** `90c861a41ceedfdb55730bd93e57df4549ca08ab`
* **Reviewed:** 2026-05-11
* **Review type:** Comprehensive self-review refresh

---

## Summary

This PR adds a dedicated `wsl-rocdxg` multi-arch Linux stage that starts on a
WSL-capable Windows runner, runs TheRock artifact fetch/configure/build/upload
inside WSL Ubuntu, and produces the WSL-only `rocdxg` bridge library from
`rocm-systems`.

The current branch also documents the stage, adds WSL feature gating, models the
artifact in `BUILD_TOPOLOGY.toml`, keeps the stage on the normal Linux
`foundation` / `base` artifact path, and wires the WSL workflow into the same
repository/ref/external-source contract as the other portable Linux stages.

## Overall Assessment

**NO BLOCKING FINDINGS IN THIS PASS** - The two blocking issues from the prior
self-review are addressed in the current head:

* The WSL stage now forwards `repository`, `ref`, and `external_repo_config`
  from `multi_arch_build_portable_linux.yml` into
  `multi_arch_build_wsl_rocdxg_artifacts.yml`.
* The WSL workflow now performs the external checkout, forwards external
  fetch-source args, and passes the external source directory override into
  CMake.
* The generated WSL build script now has the lightweight AMD/SPDX header and
  uses `set -euo pipefail`, so nested configure/build/install failures should
  fail the stage instead of being masked by a later copy.

## Findings

None from this refresh.

## Notes

* The PR diff in `multi_arch_build_portable_linux.yml` is now limited to adding
  the `wsl-rocdxg` job and passing existing workflow inputs into that job. The
  stale-looking top-level input declaration diff disappeared after the branch
  was updated from `main`.
* `configure_stage.py --stage=wsl-rocdxg --platform=linux` emits the intended
  minimal stage flags:

```text
-DTHEROCK_DIST_AMDGPU_FAMILIES="gfx94X-dcgpu;gfx110X-all"
-DTHEROCK_ENABLE_ALL=OFF
-DTHEROCK_ENABLE_BASE=ON
-DTHEROCK_ENABLE_WSL_ROCDXG=ON
```

* The WSL feature group defaults off for normal manual top-level configures
  (`THEROCK_ENABLE_WSL=OFF`), while the CI stage opts into the individual
  `THEROCK_ENABLE_WSL_ROCDXG` feature through topology-generated stage args.
* The documentation now clearly distinguishes native Windows source builds from
  the WSL Ubuntu shell used by this CI stage.
* Residual risk: the WSL job inherits the portable Linux build-variant preset
  input. The current wrapper drives the nested upstream `libhsakmt` ROCDXG
  configure directly, so sanitizer-variant behavior is not independently
  validated here. I do not consider this blocking for the release WSL stage, but
  reviewers may want to confirm whether WSL ROCDXG should participate in
  ASAN/TSAN variants or remain effectively release-style.

## Validation Performed

Local checks from the current branch:

```text
python build_tools/topology_to_cmake.py --validate-only
Topology validation successful!

python build_tools/configure_stage.py --stage=wsl-rocdxg --platform=linux --dist-amdgpu-families "gfx94X-dcgpu;gfx110X-all" --print
-DTHEROCK_DIST_AMDGPU_FAMILIES="gfx94X-dcgpu;gfx110X-all"
-DTHEROCK_ENABLE_ALL=OFF
-DTHEROCK_ENABLE_BASE=ON
-DTHEROCK_ENABLE_WSL_ROCDXG=ON

python -m pytest build_tools/github_actions/tests/configure_ci_path_filters_test.py
7 passed

python -m pytest build_tools/github_actions/tests/configure_multi_arch_ci_test.py
67 passed, 1 skipped

git diff --check publish/main...HEAD
passed
```

Focused pre-commit over the PR files passed after the hook normalized local
Windows line endings. The normalized repository diff was unchanged, and the
TheRock worktree was restored to clean afterward.

Current GitHub check state refreshed on 2026-05-11 at head `90c861a4`:

* `pre-commit`: passing.
* Unit Tests on Ubuntu and Windows: passing.
* CI summaries/setup/foundation stages visible in the check list: passing.
* Current long multi-arch jobs, including `wsl-rocdxg`, `compiler-runtime`, and
  Windows `compiler-runtime`, were still pending at review time.

## Recommendation

No code changes required from this review pass. Wait for the pending multi-arch
jobs, especially `Linux::release / Build Multi-Arch Stages / wsl-rocdxg`, before
marking the PR fully ready for merge.
