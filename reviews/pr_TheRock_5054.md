# PR Review: ROCm/TheRock#5054

* **PR:** https://github.com/ROCm/TheRock/pull/5054
* **Title:** `Use test filter modules within test scripts`
* **Base:** `main`
* **Head:** `13051c224199e49fdd9531af0e8a64000d5c8384`
* **Reviewed:** 2026-05-05
* **State at review:** OPEN
* **Draft:** Yes

---

## Overall Assessment

**DRAFT REVIEW / POC CONVERGENCE CONTEXT** - This is a useful proof of concept for moving away from the current `TEST_COMPONENT` router in `test_runner.py`: it extracts the label filtering behavior and lets component scripts own their environment setup. Since this is a POC, I would not read the current file placement or component coverage as the intended final architecture.

The updated assumption is that the final test script will live in the super-repo, but that work is not done yet. With that in mind, the main review question is whether the POC preserves behavior well enough to validate the design, and whether the extracted helper is shaped so it can later become the super-repo-owned implementation without carrying forward accidental regressions.

## Latest PR State

Checked the current PR state again on 2026-05-06 at head `13051c22`.

* No top-level comments, review comments, or submitted reviews are currently present.
* Unit-test jobs are passing.
* Pre-commit is failing because Black reformats `test_rocprofiler_compute.py`.
* Linux `rocblas`, `rocprim`, and `rocprofiler-compute` component tests are failing.
* Windows `gfx110X-all` sanity failed, so the Multi-Arch summary is failing.

## POC / Convergence Read

### What Aligns

* The label selection logic is separated from `TEST_COMPONENT` routing.
* `run_ctest()` takes `test_dir`, `env`, and `cwd` instead of discovering everything through TheRock-specific globals.
* Component scripts can preserve component-specific setup before delegating to common CTest filtering.
* The helper keeps behaviors we wanted to preserve: `TEST_TYPE` categories, GPU label matching, sharding, timeouts, and CTest label discovery.

### What Is Still Open For The Real Design

* The final super-repo script location and invocation contract are not represented yet.
* The POC switches four components at once before proving parity for each migrated wrapper.
* The POC does not yet explain when `test_runner.py`/`test_filter_utils.py` should be replaced by the super-repo-owned script.
* The boundary between generic super-repo filtering and project-specific behavior still needs to be explicit, especially for components with custom quick/exclude rules.

## Findings

### IMPORTANT: rocBLAS and hipSPARSELt lose `ROCM_PATH` from the generic runner path

The PR switches `rocblas` and `hipsparselt` from `test_runner.py` to component wrappers in `fetch_test_configurations.py` ([`#L86`](https://github.com/ROCm/TheRock/blob/13051c224199e49fdd9531af0e8a64000d5c8384/build_tools/github_actions/fetch_test_configurations.py#L86), [`#L252`](https://github.com/ROCm/TheRock/blob/13051c224199e49fdd9531af0e8a64000d5c8384/build_tools/github_actions/fetch_test_configurations.py#L252)). The old generic runner always set `ROCM_PATH = Path(THEROCK_BIN_DIR).resolve().parent` before running CTest ([`test_runner.py#L83-L87`](https://github.com/ROCm/TheRock/blob/13051c224199e49fdd9531af0e8a64000d5c8384/build_tools/github_actions/test_executable_scripts/test_runner.py#L83-L87)).

The new `test_rocblas.py` and `test_hipsparselt.py` wrappers set sharding, but do not set `ROCM_PATH` before calling `run_ctest()` ([`test_rocblas.py#L45-L53`](https://github.com/ROCm/TheRock/blob/13051c224199e49fdd9531af0e8a64000d5c8384/build_tools/github_actions/test_executable_scripts/test_rocblas.py#L45-L53), [`test_hipsparselt.py#L39-L47`](https://github.com/ROCm/TheRock/blob/13051c224199e49fdd9531af0e8a64000d5c8384/build_tools/github_actions/test_executable_scripts/test_hipsparselt.py#L39-L47)). MIOpen and rocprofiler-compute do preserve this setup.

If those tests load dependencies from the unpacked ROCm artifact, they may now accidentally use a system install or fail to locate runtime pieces. For parity, carry the old `ROCM_PATH` setup into both wrappers before running CTest.

### IMPORTANT: rocprofiler-compute now has two incompatible selection paths

`test_rocprofiler_compute.py` still defines explicit `EXCLUDED_TESTS` and `QUICK_TESTS` ([`#L26-L40`](https://github.com/ROCm/TheRock/blob/13051c224199e49fdd9531af0e8a64000d5c8384/build_tools/github_actions/test_executable_scripts/test_rocprofiler_compute.py#L26-L40)). The fallback path applies those through `--exclude-regex` and `--tests-regex` ([`#L81-L92`](https://github.com/ROCm/TheRock/blob/13051c224199e49fdd9531af0e8a64000d5c8384/build_tools/github_actions/test_executable_scripts/test_rocprofiler_compute.py#L81-L92)).

In normal CI, `test_filter_utils` is present, so the script exits through `run_ctest()` ([`#L112-L124`](https://github.com/ROCm/TheRock/blob/13051c224199e49fdd9531af0e8a64000d5c8384/build_tools/github_actions/test_executable_scripts/test_rocprofiler_compute.py#L112-L124)). That path ignores the explicit exclude and quick-test lists and relies entirely on CTest labels.

The CI log confirms that the helper path is active and runs `ctest -L quick -LE quick_exclude|ex_gpu`, selecting 21 quick-labeled tests. The old explicit quick list has 9 names. The failing test is `test_L1_cache_counters`, which is in the explicit quick list, so this is not only a "new failing test" issue; the larger point is that there are now two definitions of what quick/excluded means.

From the convergence perspective, this needs one source of truth. If project CTest labels now encode the intended quick/exclude behavior, remove the fallback lists or document that they are legacy. If they do not, the helper needs a supported way to carry component-specific include/exclude rules.

### MEDIUM: migrated scripts lose reduced CTest parallelism for `gfx1152` and `gfx1153`

The generic runner reduced CTest parallelism from 8 to 4 on `gfx1152` and `gfx1153` ([`test_runner.py#L70-L75`](https://github.com/ROCm/TheRock/blob/13051c224199e49fdd9531af0e8a64000d5c8384/build_tools/github_actions/test_executable_scripts/test_runner.py#L70-L75)). The new helper defaults to 8 in both command construction and execution ([`test_filter_utils.py#L155-L157`](https://github.com/ROCm/TheRock/blob/13051c224199e49fdd9531af0e8a64000d5c8384/build_tools/github_actions/test_executable_scripts/test_filter_utils.py#L155-L157), [`#L216-L218`](https://github.com/ROCm/TheRock/blob/13051c224199e49fdd9531af0e8a64000d5c8384/build_tools/github_actions/test_executable_scripts/test_filter_utils.py#L216-L218)), and the migrated scripts do not pass an override.

I would centralize the old parallelism rule in `test_filter_utils`, or make each wrapper pass the project-specific parallelism it expects.

### MEDIUM: the new helper is not covered by focused unit tests

The PR extracts logic into `test_filter_utils.py`, but the existing `unit_test_runner.py` still targets the old `test_runner.py` behavior and currently fails an existing expectation mismatch around `-LE quick_exclude|ex_gpu`. Add direct tests for the new helper's pure pieces: category resolution, GPU family extraction, wildcard matching, command construction, category exclude labels, GPU exclude labels, and sharding arguments.

That would also make the future super-repo script easier to compare against this POC helper.

### LOW: pre-commit needs the Black formatting fix

The failed pre-commit job reports only a Black rewrite for the final `logging.info(...)` call in `test_rocprofiler_compute.py`. That is mechanical, but should be fixed before asking for another review pass.

### NOTE: rocBLAS and rocPRIM CI failures need triage before using the run as design proof

The Linux `rocblas` job enters the new helper path and runs:

```text
ctest -L quick -LE ex_gpu --output-on-failure --parallel 8 --timeout 7200 --test-dir build/bin/rocblas -V --tests-information 1,,1
```

The single `rocblas-test_quick_suite` CTest test then hits its own 600-second timeout. Because main already used `test_runner.py` for rocBLAS, this failure may not be entirely introduced by PR 5054. It still should be understood before treating the POC as behavior-preserving.

The Linux `rocprim` failure timed out at the 30-minute job timeout. It is not directly tied to files changed by this PR, but it keeps the POC CI signal noisy.

## Recommendation

I would respond to the PR as supportive of the POC, with guardrails:

1. Keep PR 5054 draft until style and parity issues are fixed.
2. Add the missing environment/parallelism parity from `test_runner.py`.
3. Clarify whether CTest labels are now the only source of truth for rocprofiler-compute quick/exclude behavior.
4. Add focused tests for `test_filter_utils.py`.
5. Update the PR description to say this is a POC for a future super-repo-owned test script, not the finished runner architecture.

For our rocm-libraries work, this means we should not treat PR 5054 as a competing final design yet. It reinforces the useful behavior we should preserve while the super-repo script design firms up.

## Draft Review Comment

Suggested top-level review comment:

```text
Thanks for putting this POC together. I like the direction of separating the reusable CTest label/filter behavior from the current `TEST_COMPONENT` router, especially since the final test script is expected to live in the super-repo rather than preserving `test_runner.py` as the long-term interface.

For the POC, I think the main thing to tighten is behavior parity with the current runner path:

- `test_runner.py` always sets `ROCM_PATH` from `THEROCK_BIN_DIR`; the migrated rocBLAS and hipSPARSELt wrapper paths do not.
- `test_runner.py` reduces CTest parallelism for `gfx1152`/`gfx1153`; the helper currently defaults to 8 everywhere.
- rocprofiler-compute now has two definitions of quick/excluded tests: the old explicit lists and the new CTest label path. CI confirms the helper path is active and selects 21 quick-labeled tests, while the explicit quick list has 9 entries. I think this should be made one source of truth, or the PR should explain that the explicit lists are legacy fallback behavior.
- Please add focused tests for `test_filter_utils.py` itself so the extracted behavior is easy to validate before it moves toward the super-repo implementation.

The CI failures also make it hard to tell whether the POC is behavior-preserving yet. Pre-commit just needs Black formatting, but the rocBLAS timeout and rocprofiler-compute failure should be understood or called out before taking this out of draft.
```

Optional shorter inline/comment thread for rocprofiler-compute:

```text
Can we make this one source of truth? With `test_filter_utils` present, CI exits through `run_ctest()` and ignores the explicit `EXCLUDED_TESTS`/`QUICK_TESTS` lists below. If CTest labels are now authoritative, I would remove or clearly mark the old lists as legacy fallback behavior; otherwise the helper probably needs a way to carry component-specific include/exclude rules.
```

## Verification

* Refreshed PR metadata, comments, reviews, and checks on 2026-05-05 and 2026-05-06.
* Refreshed local `refs/remotes/pr/5054` and reviewed worktree at `13051c22`.
* Ran `git -c safe.directory=* diff --check origin/main...HEAD` - passed.
* Ran `C:\Dev\python-3.12.13\python.exe -m compileall -q build_tools\github_actions\test_executable_scripts build_tools\github_actions\fetch_test_configurations.py` - passed.
* Ran `C:\Dev\python-3.12.13\python.exe -m unittest build_tools\github_actions\tests\fetch_test_configurations_test.py` - passed, 20 tests.
* Ran `C:\Dev\python-3.12.13\python.exe -m unittest build_tools\github_actions\tests\unit_test_runner.py` - failed in existing `test_runner.py` coverage (`quick_exclude|ex_gpu` versus `quick_exclude`).
* Read failed pre-commit log: Black reformats `test_rocprofiler_compute.py`.
* Read failed `rocblas`, `rocprofiler-compute`, `rocprim`, and Windows sanity logs after Multi-Arch CI completed.
