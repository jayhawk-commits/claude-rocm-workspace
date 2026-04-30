# rocm-systems Test Runner Split

Date: 2026-04-28
Updated: 2026-04-30

## Context

TheRock PR 4581 raised the question of where test runner scripts should live.
Scott's review feedback pointed away from adding a generic TheRock install hook
for copied scripts, and toward having each rocm-systems project install the
runner it owns. We pivoted the work to rocm-systems project-owned runner
scripts with separate branches/PRs by project.

Related context:

- ROCm/rocm-systems#5541, `Sync copied TheRock test scripts 2026-04-28`, was
  merged on 2026-04-28. That PR synchronized copied scripts but is no longer the
  main design direction.
- ROCm/rocm-systems#5552 is open for the first project-owned runner:
  `rocr-runtime: install rocrtst test runner`.
- TheRock PR 4581 has not been updated by these local branches. The intended
  follow-up is to remove the TheRock-side copied-script installation approach
  after the rocm-systems runner PRs are in place.

## Pattern Used

Each branch follows the same basic pattern:

- Move or recreate the runner under the owning rocm-systems project.
- Install the runner from that project's normal CMake install logic, usually in
  the tests component.
- Remove the old copied `test/therock/*.py` script when the replacement branch
  fully owns that old runner.
- Remove `THEROCK_DIR` / `THEROCK_BIN_DIR` assumptions where practical.
- Derive paths from `ROCM_PATH`, the installed runner location, or explicit CLI
  arguments.
- Use a normal `main()` entry point rather than pytest test classes for scripts
  that are meant to be invoked directly by CI.

## Prepared Branches

| Project | Branch | Commit | PR status | Main files |
| --- | --- | --- | --- | --- |
| rocr-runtime / rocrtst | `users/jayhawk-commits/install-rocrtst-test-runner` | `9ef2a7668d` | PR #5552 updated on 2026-04-30 | `projects/rocr-runtime/rocrtst/suites/test_common/run_rocrtst.py`; deletes `test/therock/test_rocrtst.py` |
| aqlprofile | `users/jayhawk-commits/install-aqlprofile-test-runner` | `e3c7cd9231` | PR #5597 updated on 2026-04-30 | `projects/aqlprofile/test/run_aqlprofile.py`; deletes `test/therock/test_aqlprofile.py` |
| rocdecode | `users/jayhawk-commits/install-rocdecode-test-runner` | `e1d8c3d3d2` | PR #5598 updated on 2026-04-30 | `projects/rocdecode/test/run_rocdecode.py`; moves `test/therock/test_rocdecode.py` |
| rocjpeg | `users/jayhawk-commits/install-rocjpeg-test-runner` | `3cede0d2c3` | PR #5599 updated on 2026-04-30 | `projects/rocjpeg/test/run_rocjpeg.py`; moves `test/therock/test_rocjpeg.py` |
| hip-tests | `users/jayhawk-commits/install-hiptests-test-runner` | `74611122b6` | PR #5600 updated on 2026-04-30 | `projects/hip-tests/catch/packaging/run_hiptests.py`; deletes `test/therock/test_hiptests.py` |
| amdsmi | `users/jayhawk-commits/install-amdsmi-test-runner` | `b57aa0a2c6` | PR #5601 updated on 2026-04-30 | `projects/amdsmi/tests/amd_smi_test/run_amdsmi.py`; deletes `test/therock/test_amdsmi.py` |
| rocprofiler-systems | `users/jayhawk-commits/install-rocprofiler-systems-test-runner` | `93c7b17501` | PR #5602 updated on 2026-04-30 | `projects/rocprofiler-systems/tests/run_rocprofiler_systems.py`; deletes `test/therock/test_rocprofiler_systems.py` |
| rocr-debug-agent | `users/jayhawk-commits/install-rocr-debug-agent-test-runner` | `dc178a87f9` | Branch updated on 2026-04-30; PR #5603 is closed and superseded | `projects/rocr-debug-agent/test/run_rocr_debug_agent.py`; moves `test/therock/test_rocr-debug-agent.py` |
| rocprofiler-compute | `users/jayhawk-commits/install-rocprofiler-compute-test-runner` | `c5c2f002e5` | PR #5604 updated on 2026-04-30 | `projects/rocprofiler-compute/tests/run_rocprofiler_compute.py`; deletes `test/therock/test_rocprofiler_compute.py` |
| rocprofiler-sdk | `users/jayhawk-commits/install-rocprofiler-sdk-test-runner` | `3f655777b1` | PR #5605 updated on 2026-04-30 | `projects/rocprofiler-sdk/tests/run_rocprofiler_sdk.py`; deletes `test/therock/test_rocprofiler_sdk.py` |
| rccl | `users/jayhawk-commits/install-rccl-test-runner` | `dc66b6fec6` | PR #5606 updated on 2026-04-30 | `projects/rccl/test/run_rccl.py`; deletes `test/therock/test_rccl.py` |
| rccl-tests | `users/jayhawk-commits/install-rccl-tests-test-runner` | `7349861e45` | PR #5607 updated on 2026-04-30 | `projects/rccl-tests/test/run_rccl_tests.py` |

## Notable Design Decisions

- The old RCCL copied script mixed two owners: `rccl-UnitTests` from `rccl` and
  perf/correctness executables from `rccl-tests`. We split this into two
  branches. The `rccl` branch removes `test/therock/test_rccl.py`; the
  `rccl-tests` branch adds only the project-owned perf runner.
- `test_sanity.py` was intentionally left out. It runs TheRock-level sanity
  checks and does not map cleanly to a rocm-systems project owner.
- The prepared branches avoid updating TheRock submodule SHAs. Submodule and
  SHA updates remain out of scope for these fixes.
- Draft PRs were created on 2026-04-29 after explicit approval. PR descriptions
  use consistent motivation, changes, validation, and not-run sections.
- A 2026-04-29 cleanup pass made the runners more consistent with the rocrtst
  example and TheRock Python style guidance: executable shebangs, no stale
  TheRock path wording, no helper-level `sys.exit()`, and a fixed RCCL default
  GPU selection of `0,1` instead of `2,3`.
- The hip-tests branch was updated again after CI showed that
  `catch/packaging/CMakeLists.txt` tried to install
  `catch/packaging/run_hiptests.py`. The runner now lives beside that install
  logic at `catch/packaging/run_hiptests.py`, keeping the install rule as
  `${CMAKE_CURRENT_SOURCE_DIR}/run_hiptests.py`.
- A 2026-04-30 Copilot-review follow-up was applied locally across the runner
  PR branches. The follow-up removes silent source-tree fallbacks, treats empty
  `ROCM_PATH` values as unset, validates installed test files before execution,
  avoids direct `lib` assumptions where `lib64` may be used, fixes gtest filter
  construction, and uses Python-compatible typing syntax in new runner scripts.
  These commits were pushed to the rocm-systems branches on 2026-04-30. PR
  #5603 had already been closed and superseded, so its branch was updated but
  the PR remains closed.

## Validation Performed

For the prepared local branches:

- `python -m py_compile` was run for the new or modified runner scripts touched
  during this split.
- `git diff --check origin/develop...HEAD` passed for all runner branches.
- Each worktree was checked and was clean after its commit.
- On 2026-04-30, syntax compilation via Python `compile()` and `git diff
  --check` were rerun after the Copilot-review hardening commits.

Full hardware test execution was not run locally. Several runners require ROCm
install artifacts and suitable GPU hardware.

## Current Worktrees

All runner worktrees are under `C:\Dev`:

- `rocm-sys-rocrtst-runner`
- `rocm-sys-aqlprofile-runner`
- `rocm-sys-rocdecode-runner`
- `rocm-sys-rocjpeg-runner`
- `rocm-sys-hiptests-runner`
- `rocm-sys-amdsmi-runner`
- `rocm-sys-rocprofiler-systems-runner`
- `rocm-sys-rocr-debug-agent-runner`
- `rocm-sys-rocprofiler-compute-runner`
- `rocm-sys-rocprofiler-sdk-runner`
- `rocm-sys-rccl-runner`
- `rocm-sys-rccl-tests-runner`

## Next Steps

1. Review the draft PRs in the order above or in the order maintainers are most
   likely to accept.
2. Promote draft PRs to ready-for-review after any desired local/package
   validation.
3. Keep PR #5603 closed; rocr-debug-agent is covered by a superseding PR.
4. After the rocm-systems PRs land, revisit TheRock PR 4581 and remove the
   copied-script install design.
