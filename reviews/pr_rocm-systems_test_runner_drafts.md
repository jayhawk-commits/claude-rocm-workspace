# Batch Review: rocm-systems Test Runner Draft PRs

Reviewed PRs:

- ROCm/rocm-systems#5552 - rocr-runtime: install rocrtst test runner
- ROCm/rocm-systems#5597 - aqlprofile: install test runner
- ROCm/rocm-systems#5598 - rocdecode: install test runner
- ROCm/rocm-systems#5599 - rocjpeg: install test runner
- ROCm/rocm-systems#5600 - hip-tests: install catch test runner
- ROCm/rocm-systems#5601 - amdsmi: install test runner
- ROCm/rocm-systems#5602 - rocprofiler-systems: install test runner
- ROCm/rocm-systems#5603 - rocr-debug-agent: install test runner
- ROCm/rocm-systems#5604 - rocprofiler-compute: install test runner
- ROCm/rocm-systems#5605 - rocprofiler-sdk: install test runner
- ROCm/rocm-systems#5606 - rccl: install test runner
- ROCm/rocm-systems#5607 - rccl-tests: install test runner

## Overall Assessment

CHANGES REQUESTED for the batch before promoting the draft PRs to ready for
review.

The direction matches Scott's TheRock PR 4581 feedback: the runners now live in
owning subprojects, install from standalone subproject CMake, and avoid
`THEROCK_DIR` / `THEROCK_BIN_DIR` assumptions. The PR descriptions are also
consistent and explain the TheRock/RFC0010 motivation without putting TheRock
details into subproject code.

One correctness issue should be fixed before #5552 is ready, and two smaller
style/reliability issues are worth cleaning up before asking maintainers to
review the series.

## Findings

### [BLOCKING] #5552 rocrtst runner hard-codes the Linux executable name

File: `projects/rocr-runtime/rocrtst/suites/test_common/run_rocrtst.py:111`

The new runner discovers either `rocrtst64` or `rocrtst64.exe` while deriving
the ROCm prefix, and the filter table includes Windows-specific exclusions, but
the actual command is always:

```python
cmd = ["./rocrtst64"]
```

On Windows, `cwd=rocm_bin_dir` plus `./rocrtst64` will not launch
`rocrtst64.exe`. That means the installed runner will fail in the Windows
layout even though the script otherwise appears to support Windows.

Required action: resolve the executable path before launching, e.g. check
`rocm_bin_dir / "rocrtst64"` and `rocm_bin_dir / "rocrtst64.exe"` and pass the
resolved path to `subprocess.run`. This can mirror the helper used in the RCCL
runner.

### [IMPORTANT] #5600 hip-tests runner logs DLL copy failures but keeps going

File: `projects/hip-tests/catch/run_hiptests.py:112`

On Windows, the runner copies runtime DLLs into the catch test directory, but
`OSError` from `shutil.copy` is caught and only logged:

```python
except OSError as e:
    logging.info(f"++ Error copying {dll}: {e}")
```

If a matching DLL is found but cannot be copied, the tests will likely fail
later with a less helpful load error. The TheRock Python style guide prefers
fail-fast behavior for missing or incomplete runtime inputs.

Recommendation: let `shutil.copy` raise, or collect copy failures and raise a
single `RuntimeError` after attempting all copies.

### [IMPORTANT] #5603 rocr-debug-agent imports Unix-only `resource` at module load

File: `projects/rocr-debug-agent/test/run_rocr_debug_agent.py:8`

The runner imports `resource` at top level. That module is not available on
Windows, so merely importing the script fails there before any path handling or
help text can run. If rocr-debug-agent tests are Linux-only, this is not a
runtime problem for the intended environment, but it still makes the script less
portable than the rest of the batch.

Recommendation: move the import into `set_core_dump_limit()` and handle
`ImportError` as "core limit adjustment unavailable on this platform", or guard
the function with a platform check.

### [SUGGESTION] #5600 has an unused import

File: `projects/hip-tests/catch/run_hiptests.py:5`

`json` is imported but not used. This is minor, but it is easy cleanup before
asking reviewers to look at the PR.

### [SUGGESTION] #5552 PR description says "ctest filter"

PR body for #5552

The validation text says "ctest filter construction", but the rocrtst runner
constructs a GTest filter. Change this to "GTest filter construction" for
accuracy.

## No Blocking Findings

No blocking issues found in:

- #5597 aqlprofile
- #5598 rocdecode
- #5599 rocjpeg
- #5601 amdsmi
- #5602 rocprofiler-systems
- #5604 rocprofiler-compute
- #5605 rocprofiler-sdk
- #5606 rccl
- #5607 rccl-tests

## Test Gaps

The batch has good lightweight validation (`py_compile` and `git diff --check`),
but the PR descriptions correctly note that CMake configure/install packaging
checks and hardware-backed test execution have not been run. Before promoting
the drafts, run at least the relevant CMake install/package checks where
practical so the new install rules are verified by CMake, not just by diff
inspection.
