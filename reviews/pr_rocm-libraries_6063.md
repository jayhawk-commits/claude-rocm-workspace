# PR Review: ROCm/rocm-libraries#6063

* **PR:** https://github.com/ROCm/rocm-libraries/pull/6063
* **Title:** `[ci] skipping builds if artifacts are available and run tests directly`
* **Base:** `develop`
* **Head:** `6b8e1bf4ec11b1272042ce696b5f9314da9c1d43`
* **Reviewed:** 2026-04-30
* **State at review:** OPEN

---

## Overall Assessment

**CHANGES REQUESTED** - The skip-build path does not require an artifact run ID before skipping the build. A manual dispatch can therefore skip the only producer and then test against the current run ID, where no artifacts exist.

## Findings

### BLOCKING: Prebuilt-artifact mode can skip builds without a source artifact run

The workflow input `artifact_run_id` defaults to an empty string ([`therock-ci.yml#L34-L36`](https://github.com/ROCm/rocm-libraries/blob/6b8e1bf4ec11b1272042ce696b5f9314da9c1d43/.github/workflows/therock-ci.yml#L34-L36)), while the Linux caller passes it through unchanged and independently enables build skipping from the checkbox at [`therock-ci.yml#L152-L159`](https://github.com/ROCm/rocm-libraries/blob/6b8e1bf4ec11b1272042ce696b5f9314da9c1d43/.github/workflows/therock-ci.yml#L152-L159). The reusable Linux workflow then skips the build whenever `use_prebuilt_artifacts == 'false'` is not true at [`therock-ci-linux.yml#L27-L29`](https://github.com/ROCm/rocm-libraries/blob/6b8e1bf4ec11b1272042ce696b5f9314da9c1d43/.github/workflows/therock-ci-linux.yml#L27-L29).

If a user checks `linux_use_prebuilt_artifacts` but leaves `artifact_run_id` empty, `therock-test-packages.yml` falls back to `github.run_id` at [`#L73-L75`](https://github.com/ROCm/rocm-libraries/blob/6b8e1bf4ec11b1272042ce696b5f9314da9c1d43/.github/workflows/therock-test-packages.yml#L73-L75). In that run, the build job was skipped, so the fallback points at a run that did not upload the artifacts being tested.

The docs say the user should provide an artifact ID ([`docs/ci_behavior_manipulation.md#L21-L25`](https://github.com/ROCm/rocm-libraries/blob/6b8e1bf4ec11b1272042ce696b5f9314da9c1d43/docs/ci_behavior_manipulation.md#L21-L25)), but the workflow should enforce that contract before skipping the producer job.

**Required action:** Add an early setup validation that fails with a clear message when either prebuilt-artifacts checkbox is enabled and `artifact_run_id` is empty. Alternatively, make the build skip conditional require both `use_prebuilt_artifacts == 'true'` and a non-empty `artifact_run_id`.

## Verification

* Inspected Linux, Windows, caller, and test-package workflow input propagation.
* Checked current PR metadata; the latest rollup is blocked/failing, so the linked runs should not be treated as complete validation of this edge case.
