# PR Review: ROCm/TheRock#5132

* **PR:** https://github.com/ROCm/TheRock/pull/5132
* **Title:** `[debug-tools] Refactor container options and split rocgdb tests into CPU and GPU runners`
* **Base:** `main`
* **Head:** `5de9b6e3589ac2497d6a31f10b7cebde8992ccba`
* **Reviewed:** 2026-05-14
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**NO BLOCKING FINDINGS / COMMENT** - The design is reasonable for the current goal: container options move into the Python-generated component config, GPU-only Docker options are omitted for CPU-only jobs, and `rocgdb` is split into explicit CPU and GPU test entries.

The remaining design concern I see is already covered in the PR discussion: the CPU runner is currently hardcoded as `ubuntu-24.04` in the reusable workflow instead of flowing through a named input such as `linux_cpu_runner`. I would not repeat that as a new review finding.

## Findings

None.

## Review Notes

The split jobs are validating in CI: the latest Multi-Arch run shows both `rocgdb-cpu` and `rocgdb-gpu` passing. The run still has unrelated component failures in Linux `hip-tests`, `rocblas`, `rocprofiler-compute`, `rocsolver`, `rocsparse`, and Windows sanity, but the `rocgdb` split itself is not the failing path.

The container option refactor also keeps the prior Linux base options centralized and appends GPU device/group options only when `cpu_runner` is not set. The focused configuration tests pass after the refactor.

## Suggested Review Comment

```text
I do not have additional blocking comments on the latest diff. The CPU/GPU rocgdb split looks coherent to me: the CPU job drops the GPU container options, the GPU job preserves them, and the current CI run shows both rocgdb jobs passing.

The one design point I would still track is the existing discussion about making the CPU runner configurable instead of hardcoding `ubuntu-24.04` in the workflow. Since that is already called out on the PR, I would not duplicate it as a separate thread.
```

## Verification

* Refreshed `origin/main` and `refs/remotes/pr/5132`.
* Checked latest PR metadata: open, not draft, mergeable, review required.
* Reviewed changed files:
  * `.github/workflows/test_artifacts.yml`
  * `.github/workflows/test_component.yml`
  * `build_tools/github_actions/fetch_test_configurations.py`
* Ran `git -c safe.directory=* diff --check origin/main...refs/remotes/pr/5132`; passed.
* Ran focused unit tests from a PR snapshot:

```text
python -m unittest discover -s build_tools\github_actions\tests -p "fetch_test_configurations_test.py"
```

Result: 20 tests passed.

* Checked latest public PR checks; `rocgdb-cpu` and `rocgdb-gpu` passed, while broader Multi-Arch CI still has unrelated failing jobs.
