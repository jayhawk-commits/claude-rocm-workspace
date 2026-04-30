# rocm-libraries Test Runner Split

Date: 2026-04-29
Updated: 2026-04-30

## Context

We are extending the rocm-systems test runner split pattern to rocm-libraries.
The goal is the same: make each project own and install its runner instead of
keeping TheRock-specific copies under `test/therock`.

This follows the design direction from TheRock PR 4581 review feedback:

- Put runner scripts with the projects that own the tests.
- Install runners from the project's normal CMake install logic.
- Avoid `THEROCK_DIR` and `THEROCK_BIN_DIR` assumptions in project-owned code.
- Keep runner scripts directly executable, with a `main()` entry point and
  simple subprocess execution.

## Prepared Branches

| Area | Branch | Commit | Status | Main files |
| --- | --- | --- | --- | --- |
| rand | `users/jayhawk-commits/install-rand-test-runners` | `c8c4cf3256` | Rebased on 2026-04-30; local only; not pushed | `projects/hiprand/test/run_hiprand.py`, `projects/rocrand/test/run_rocrand.py`; removes the old rand copies from `test/therock` |
| fft | `users/jayhawk-commits/install-fft-test-runners` | `fc93597ac1` | Rebased on 2026-04-30; local only; not pushed | `projects/hipfft/clients/tests/run_hipfft.py`, `projects/rocfft/clients/tests/run_rocfft.py`; removes the old fft copies from `test/therock` |
| prim | `users/jayhawk-commits/install-prim-test-runners` | `70c1fd479f` | Rebased on 2026-04-30; local only; not pushed | `projects/hipcub/test/run_hipcub.py`, `projects/rocprim/test/run_rocprim.py`, `projects/rocthrust/test/run_rocthrust.py`; removes the old prim copies from `test/therock` |
| solver | `users/jayhawk-commits/install-solver-test-runners` | `41ac70df29` | Rebased on 2026-04-30; local only; not pushed | `projects/hipsolver/clients/gtest/run_hipsolver.py`, `projects/rocsolver/clients/gtest/run_rocsolver.py`; removes the old solver copies from `test/therock` |
| sparse | `users/jayhawk-commits/install-sparse-test-runners` | `8fd77f5129` | Rebased on 2026-04-30; local only; not pushed | `projects/hipsparse/clients/tests/run_hipsparse.py`, `projects/hipsparselt/clients/gtest/run_hipsparselt.py`, `projects/rocsparse/clients/tests/run_rocsparse.py`; removes the old sparse copies from `test/therock` |
| rocwmma | `users/jayhawk-commits/install-rocwmma-test-runner` | `de7ed5622c` | Rebased on 2026-04-30; local only; not pushed | `projects/rocwmma/test/run_rocwmma.py`; removes the old rocWMMA copy from `test/therock` |

The rand slice was chosen first because both runners are simple CTest wrappers
and both projects already install a `CTestTestfile.cmake` under
`${CMAKE_INSTALL_BINDIR}/${PROJECT_NAME}`.

## Pattern Used

- Add a project-owned `run_<project>.py` beside the relevant test CMake logic.
- Install the runner into the same installed test directory as that project's
  `CTestTestfile.cmake`.
- Derive `ROCM_PATH` from the installed runner location when possible, while
  still allowing an explicit `ROCM_PATH` override.
- Preserve existing test behavior such as CTest arguments, timeouts, retry
  policy, and quick-test filters.
- Delete the old `test/therock/test_<project>.py` copy when the new runner fully
  replaces it.

## Candidate Follow-up Slices

| Area | Candidate scripts | Notes |
| --- | --- | --- |
| blas | `test_hipblas.py`, `test_hipblaslt.py`, `test_hipblasltprovider.py`, `test_rocblas.py`, `test_rocroller.py`, `test_runner.py` | Larger and less uniform; likely needs more careful per-project review. |
| miopen | `test_miopen.py`, `test_miopenprovider.py` | `test_miopen.py` is one of the larger scripts and should be handled separately. |
| hipdnn and providers | `test_hipdnn.py`, `test_hipdnn_install.py`, `test_hipdnn_samples.py`, `test_hipkernelprovider.py` | Provider layout spans `projects/hipdnn` and `dnn-providers`; handle deliberately. |

`test_fusilliprovider.py` and `test_hipdnn_integration_tests.py` exist in the
current TheRock test script set but were not present in the rocm-libraries
`test/therock` copies checked at the start of this pass. They should be
considered when splitting the provider/integration-test area.

## Validation Performed

For the prepared branches:

- `python -m py_compile` was run for each new runner script.
- `git diff --check` was run before each commit.
- On 2026-04-30, all prepared branches were rebased onto
  `origin/develop` at `b6583d9c7b` and the same py_compile / diff-check
  validation was rerun.

Full hardware/package validation was not run locally. These runners need ROCm
install artifacts and suitable GPU hardware to exercise the actual test suites.

## Current Worktree

- `C:\Dev\rocm-libs-rand-runners`
- `C:\Dev\rocm-libs-fft-runners`
- `C:\Dev\rocm-libs-prim-runners`
- `C:\Dev\rocm-libs-solver-runners`
- `C:\Dev\rocm-libs-sparse-runners`
- `C:\Dev\rocm-libs-rocwmma-runner`

The branches are local only at the time of this note. No push or PR was created.

## Next Actions

1. Push the prepared rocm-libraries branches and open draft PRs only after
   explicit approval.
2. Continue the split with the remaining larger buckets: BLAS, MIOpen, and
   hipDNN/providers.
3. For the provider/integration-test area, include the newer TheRock-only
   scripts (`test_fusilliprovider.py` and `test_hipdnn_integration_tests.py`) in
   the ownership review even though they were not in the older rocm-libraries
   `test/therock` copy set.
4. After rocm-libraries PRs are prepared, revisit TheRock PR 4581 and simplify
   the TheRock-side design around project-owned installed runners.
