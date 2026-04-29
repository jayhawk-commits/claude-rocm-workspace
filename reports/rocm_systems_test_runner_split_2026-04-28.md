# rocm-systems Test Runner Split

Date: 2026-04-28

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
| rocr-runtime / rocrtst | `users/jayhawk-commits/install-rocrtst-test-runner` | `f7eae2e5b0` | Open PR #5552 | `projects/rocr-runtime/rocrtst/suites/test_common/run_rocrtst.py`; deletes `test/therock/test_rocrtst.py` |
| aqlprofile | `users/jayhawk-commits/install-aqlprofile-test-runner` | `51731c2636` | local only | `projects/aqlprofile/test/run_aqlprofile.py`; deletes `test/therock/test_aqlprofile.py` |
| rocdecode | `users/jayhawk-commits/install-rocdecode-test-runner` | `0373f227e5` | local only | `projects/rocdecode/test/run_rocdecode.py`; moves `test/therock/test_rocdecode.py` |
| rocjpeg | `users/jayhawk-commits/install-rocjpeg-test-runner` | `feb7c02c2b` | local only | `projects/rocjpeg/test/run_rocjpeg.py`; moves `test/therock/test_rocjpeg.py` |
| hip-tests | `users/jayhawk-commits/install-hiptests-test-runner` | `56668c8a93` | local only | `projects/hip-tests/catch/run_hiptests.py`; deletes `test/therock/test_hiptests.py` |
| amdsmi | `users/jayhawk-commits/install-amdsmi-test-runner` | `d0f8a76704` | local only | `projects/amdsmi/tests/amd_smi_test/run_amdsmi.py`; deletes `test/therock/test_amdsmi.py` |
| rocprofiler-systems | `users/jayhawk-commits/install-rocprofiler-systems-test-runner` | `d88aa7866b` | local only | `projects/rocprofiler-systems/tests/run_rocprofiler_systems.py`; deletes `test/therock/test_rocprofiler_systems.py` |
| rocr-debug-agent | `users/jayhawk-commits/install-rocr-debug-agent-test-runner` | `74491cccdc` | local only | `projects/rocr-debug-agent/test/run_rocr_debug_agent.py`; moves `test/therock/test_rocr-debug-agent.py` |
| rocprofiler-compute | `users/jayhawk-commits/install-rocprofiler-compute-test-runner` | `995eef5a2c` | local only | `projects/rocprofiler-compute/tests/run_rocprofiler_compute.py`; deletes `test/therock/test_rocprofiler_compute.py` |
| rocprofiler-sdk | `users/jayhawk-commits/install-rocprofiler-sdk-test-runner` | `bf2732c64e` | local only | `projects/rocprofiler-sdk/tests/run_rocprofiler_sdk.py`; deletes `test/therock/test_rocprofiler_sdk.py` |
| rccl | `users/jayhawk-commits/install-rccl-test-runner` | `35731cc431` | local only | `projects/rccl/test/run_rccl.py`; deletes `test/therock/test_rccl.py` |
| rccl-tests | `users/jayhawk-commits/install-rccl-tests-test-runner` | `4a1251a510` | local only | `projects/rccl-tests/test/run_rccl_tests.py` |

## Notable Design Decisions

- The old RCCL copied script mixed two owners: `rccl-UnitTests` from `rccl` and
  perf/correctness executables from `rccl-tests`. We split this into two
  branches. The `rccl` branch removes `test/therock/test_rccl.py`; the
  `rccl-tests` branch adds only the project-owned perf runner.
- `test_sanity.py` was intentionally left out. It runs TheRock-level sanity
  checks and does not map cleanly to a rocm-systems project owner.
- The prepared branches avoid updating TheRock submodule SHAs. Submodule and
  SHA updates remain out of scope for these fixes.
- PR creation was intentionally paused after local branch preparation. The user
  asked not to create PRs automatically without approval.

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

1. Review the local branches in the order above or in the order maintainers are
   most likely to accept.
2. Push and open PRs only after explicit approval.
3. Use concise PR descriptions:
   - move/install the runner under the owning project
   - remove the old copied script when applicable
   - note `py_compile` and `git diff --check` validation
   - note that full hardware execution was not run locally
4. After the rocm-systems PRs land, revisit TheRock PR 4581 and remove the
   copied-script install design.
