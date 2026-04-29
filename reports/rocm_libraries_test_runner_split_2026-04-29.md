# rocm-libraries Test Runner Split

Date: 2026-04-29

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

## First Prepared Slice

| Area | Branch | Commit | Status | Main files |
| --- | --- | --- | --- | --- |
| rand | `users/jayhawk-commits/install-rand-test-runners` | `f5d2adbbab` | Local only; not pushed | `projects/hiprand/test/run_hiprand.py`, `projects/rocrand/test/run_rocrand.py`; removes the old rand copies from `test/therock` |

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
| prim | `test_hipcub.py`, `test_rocprim.py`, `test_rocthrust.py` | Likely a good next batch; all are project-owned tests in the prim area. |
| fft | `test_hipfft.py`, `test_rocfft.py` | Small CTest-style wrappers; likely similar to rand. |
| solver | `test_hipsolver.py`, `test_rocsolver.py` | Keep as a separate slice because solver installs and clients may differ. |
| sparse | `test_hipsparse.py`, `test_rocsparse.py`, `test_hipsparselt.py` | Split `hipsparselt` separately if its install/test layout differs from the other sparse projects. |
| blas | `test_hipblas.py`, `test_hipblaslt.py`, `test_hipblasltprovider.py`, `test_rocblas.py`, `test_rocroller.py`, `test_runner.py` | Larger and less uniform; likely needs more careful per-project review. |
| miopen | `test_miopen.py`, `test_miopenprovider.py` | `test_miopen.py` is one of the larger scripts and should be handled separately. |
| hipdnn and providers | `test_hipdnn.py`, `test_hipdnn_install.py`, `test_hipdnn_samples.py`, `test_hipkernelprovider.py` | Provider layout spans `projects/hipdnn` and `dnn-providers`; handle deliberately. |
| rocwmma | `test_rocwmma.py` | Can likely stand alone. |

`test_fusilliprovider.py` and `test_hipdnn_integration_tests.py` exist in the
current TheRock test script set but were not present in the rocm-libraries
`test/therock` copies checked at the start of this pass. They should be
considered when splitting the provider/integration-test area.

## Validation Performed

For the rand branch:

- `python -m py_compile projects/hiprand/test/run_hiprand.py projects/rocrand/test/run_rocrand.py`
- `git diff --check origin/develop...HEAD`

Full hardware/package validation was not run locally. These runners need ROCm
install artifacts and suitable GPU hardware to exercise the actual test suites.

## Current Worktree

- `C:\Dev\rocm-libs-rand-runners`

The branch is local only at the time of this note. No push or PR was created.
