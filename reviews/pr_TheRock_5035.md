# PR Review: ROCm/TheRock#5035

* **PR:** https://github.com/ROCm/TheRock/pull/5035
* **Title:** `[ci] Adding test reporting from gtest and ctest`
* **Base:** `main`
* **Head:** `59551b124fa6ed5b1fb8439ed4d0d5efd87aaedc`
* **Reviewed:** 2026-05-14
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**COMMENT / CLARIFY REPORT CONSUMER** - The parser itself has focused tests and they pass. The main integration question is where the structured `test-metrics.json` is consumed. The workflow writes it under `./build/test-results/`, and the script prints a log summary, but I did not find a workflow step that uploads the file, appends it to the job summary, or otherwise exposes it as a durable artifact.

If the expected consumer scrapes the job log, this may be fine with a comment. If the expected consumer needs the JSON file, I would ask for the upload/collection step in this PR.

## Findings

### IMPORTANT: clarify how `test-metrics.json` is collected

The new failure-reporting step writes metrics to `./build/test-results/test-metrics.json` at [`test_component.yml#L199-L203`](https://github.com/ROCm/TheRock/blob/59551b124fa6ed5b1fb8439ed4d0d5efd87aaedc/.github/workflows/test_component.yml#L199-L203). I do not see a follow-up step in this PR that uploads that directory, appends the JSON to a summary, or passes it to another action.

That means the structured output appears to be ephemeral unless an external runner-side collector knows to read this exact workspace path. The script does print the metrics to the job log, so this is not necessarily broken, but the contract should be explicit.

**Suggested action:** either add the intended upload/collection path, or document that the report is intentionally log-only / runner-collected and that no GitHub artifact is expected.

### LOW: timeout counts are double counted inside `parse_stdout_log()`

`parse_stdout_log()` copies `parsed.timeout_count` into `result.timeout_count`, then increments it again while converting each timeout test into a `FailedTest` at [`report_failed_tests.py#L247-L254`](https://github.com/ROCm/TheRock/blob/59551b124fa6ed5b1fb8439ed4d0d5efd87aaedc/test_tools/report_failed_tests.py#L247-L254). The current metrics output does not emit the aggregate count, so this is not a visible reporting bug yet, but it is worth fixing while the helper is new and adding a test assertion for the count.

## Suggested Review Comment

```text
The parser tests look good to me, but can we clarify the integration contract for the structured output? The workflow writes `./build/test-results/test-metrics.json` and the script prints a summary to the job log, but I do not see a step that uploads that file, appends it to the job summary, or otherwise exposes it as a durable artifact.

If an external collector is expected to read this path directly, could we document that in the workflow or helper? Otherwise I think this PR should wire the metrics file into the intended upload/collection path so the structured report is actually consumable after the job exits.

Small bug while here: `parse_stdout_log()` copies `parsed.timeout_count` and then increments it again for each timeout while building `FailedTest` records, so timeout counts are doubled if the aggregate is used later.
```

## Verification

* Refreshed `origin/main` and `refs/remotes/pr/5035`.
* Checked latest PR metadata: open, not draft, mergeable, review required.
* Checked top-level and inline comments; no existing review comments at review time.
* Reviewed changed files:
  * `.github/workflows/test_component.yml`
  * `test_tools/report_failed_tests.py`
  * `test_tools/tests/report_failed_tests_test.py`
* Ran `git -c safe.directory=* diff --check origin/main...refs/remotes/pr/5035`; passed.
* Ran focused tests from a PR snapshot:

```text
python -m pytest -q test_tools\tests\report_failed_tests_test.py
```

Result: 9 tests passed, with pytest collection warnings for enum/dataclass names beginning with `Test`.

* Ran `python -m py_compile test_tools\report_failed_tests.py`; passed.
* Sampled a failing Windows sanity job; it failed before the `Test` step in the driver/GPU sanity check, so it did not exercise the new report step.
