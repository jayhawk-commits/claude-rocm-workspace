# rocm-systems Test Runner Split

Date: 2026-04-28
Updated: 2026-04-29

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
| rocr-runtime / rocrtst | `users/jayhawk-commits/install-rocrtst-test-runner` | `f7eae2e5b0` | Draft PR #5552 | `projects/rocr-runtime/rocrtst/suites/test_common/run_rocrtst.py`; deletes `test/therock/test_rocrtst.py` |
| aqlprofile | `users/jayhawk-commits/install-aqlprofile-test-runner` | `51731c2636` | Draft PR #5597 | `projects/aqlprofile/test/run_aqlprofile.py`; deletes `test/therock/test_aqlprofile.py` |
| rocdecode | `users/jayhawk-commits/install-rocdecode-test-runner` | `4f2f3d9dcd` | Draft PR #5598 | `projects/rocdecode/test/run_rocdecode.py`; moves `test/therock/test_rocdecode.py` |
| rocjpeg | `users/jayhawk-commits/install-rocjpeg-test-runner` | `467f52e94c` | Draft PR #5599 | `projects/rocjpeg/test/run_rocjpeg.py`; moves `test/therock/test_rocjpeg.py` |
| hip-tests | `users/jayhawk-commits/install-hiptests-test-runner` | `622f697c9d` | Draft PR #5600 | `projects/hip-tests/catch/packaging/run_hiptests.py`; deletes `test/therock/test_hiptests.py` |
| amdsmi | `users/jayhawk-commits/install-amdsmi-test-runner` | `d0f8a76704` | Draft PR #5601 | `projects/amdsmi/tests/amd_smi_test/run_amdsmi.py`; deletes `test/therock/test_amdsmi.py` |
| rocprofiler-systems | `users/jayhawk-commits/install-rocprofiler-systems-test-runner` | `d7e15d4dfe` | Draft PR #5602 | `projects/rocprofiler-systems/tests/run_rocprofiler_systems.py`; deletes `test/therock/test_rocprofiler_systems.py` |
| rocr-debug-agent | `users/jayhawk-commits/install-rocr-debug-agent-test-runner` | `a13010eb10` | Draft PR #5603 | `projects/rocr-debug-agent/test/run_rocr_debug_agent.py`; moves `test/therock/test_rocr-debug-agent.py` |
| rocprofiler-compute | `users/jayhawk-commits/install-rocprofiler-compute-test-runner` | `7993246ec2` | Draft PR #5604 | `projects/rocprofiler-compute/tests/run_rocprofiler_compute.py`; deletes `test/therock/test_rocprofiler_compute.py` |
| rocprofiler-sdk | `users/jayhawk-commits/install-rocprofiler-sdk-test-runner` | `237bea75a9` | Draft PR #5605 | `projects/rocprofiler-sdk/tests/run_rocprofiler_sdk.py`; deletes `test/therock/test_rocprofiler_sdk.py` |
| rccl | `users/jayhawk-commits/install-rccl-test-runner` | `4041d54c06` | Draft PR #5606 | `projects/rccl/test/run_rccl.py`; deletes `test/therock/test_rccl.py` |
| rccl-tests | `users/jayhawk-commits/install-rccl-tests-test-runner` | `c90bde22d8` | Draft PR #5607 | `projects/rccl-tests/test/run_rccl_tests.py` |

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
  TheRock path wording, no helper-level `sys.exit()`, modern type syntax, and a
  fixed RCCL default GPU selection of `0,1` instead of `2,3`.
- The hip-tests branch was updated again after CI showed that
  `catch/packaging/CMakeLists.txt` tried to install
  `catch/packaging/run_hiptests.py`. The runner now lives beside that install
  logic at `catch/packaging/run_hiptests.py`, keeping the install rule as
  `${CMAKE_CURRENT_SOURCE_DIR}/run_hiptests.py`.

## Validation Performed

For the prepared local branches:

- `python -m py_compile` was run for the new or modified runner scripts touched
  during this split.
- `git diff --check origin/develop...HEAD` passed for all runner branches.
- Each worktree was checked and was clean after its commit.

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
3. After the rocm-systems PRs land, revisit TheRock PR 4581 and remove the
   copied-script install design.
