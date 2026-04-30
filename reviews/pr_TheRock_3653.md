# PR Review: ROCm/TheRock#3653

* **PR:** https://github.com/ROCm/TheRock/pull/3653
* **Title:** `Refactor new_amdgpu_family_matrix to use data classes instead of dictionary`
* **Base:** `main`
* **Head:** `ec6398c543f300d02330deaf465a7a4a61a5283a`
* **Reviewed:** 2026-04-30
* **State at review:** OPEN

---

## Overall Assessment

**COMMENT / VERIFY** - The finding below is related to the PR's replacement matrix data, but it is a parity issue rather than an active workflow regression: current workflow generation still imports the legacy `amdgpu_family_matrix.py`.

## Latest Comment Check

Checked latest PR state on 2026-04-30 at head `ec6398c5`. Existing review threads cover the family/default abstraction, runner inventory shape, strict vs partial lookups, style-guide items, and change-detector tests. I did not find an existing thread covering the TSAN `expect_failure` drift below.

## Findings

### IMPORTANT: PR-added TSAN entry is marked expected-failure while the legacy matrix is blocking

The PR-added data model sets `expect_failure=True` on the Linux `tsan` build variant at [`new_amdgpu_family_matrix_data.py#L85-L89`](https://github.com/ROCm/TheRock/blob/ec6398c543f300d02330deaf465a7a4a61a5283a/build_tools/github_actions/new_amdgpu_family_matrix_data.py#L85-L89), and `BuildVariantInfo.to_dict()` serializes that flag into the workflow-facing variant dictionary at [`new_amdgpu_family_matrix_types.py#L110-L115`](https://github.com/ROCm/TheRock/blob/ec6398c543f300d02330deaf465a7a4a61a5283a/build_tools/github_actions/new_amdgpu_family_matrix_types.py#L110-L115).

That does not match the current legacy source of truth: `amdgpu_family_matrix.py` defines Linux `tsan` with label, suffix, and preset only, with no `expect_failure` override ([`amdgpu_family_matrix.py#L104-L108`](https://github.com/ROCm/TheRock/blob/ec6398c543f300d02330deaf465a7a4a61a5283a/build_tools/github_actions/amdgpu_family_matrix.py#L104-L108)). Current consumers treat missing `expect_failure` as `False`, so TSAN failures remain blocking. This is not a current runtime break because the configure scripts still import the legacy matrix, but it is a PR-introduced parity drift in the replacement data. If a later PR wires this data into workflow generation, TSAN jobs would become `continue-on-error` unless that policy change is intentional.

**Suggested action before adopting this matrix:** remove `expect_failure=True` from the new TSAN variant, or intentionally make the same policy change in the legacy matrix/current workflow path with a test that proves TSAN expected-failure behavior is deliberate.

## Verification

* Refreshed PR metadata and comments on 2026-04-30.
* Fetched `refs/pull/3653/head` and reviewed local worktree at `ec6398c5`.
* Ran `python build_tools\github_actions\tests\new_amdgpu_family_matrix_test.py -v` - passed, 49 tests.
* Compared the new `all_build_variants.get("linux", "tsan").to_dict()` output against legacy `amdgpu_family_matrix.py`; the new output includes `expect_failure: True`, while the legacy variant does not.
* Checked imports: current `configure_ci.py` and `configure_multi_arch_ci.py` still consume `amdgpu_family_matrix.py`, so this is replacement-data drift rather than an already-active workflow behavior change.
* Latest GitHub checks show unit tests/pre-commit passing, with Multi-Arch CI test failures still present on the PR.

## Suggested GitHub Review

**Review state:** Comment

**Overall review body:**

Thanks for continuing to push this toward a typed source of truth. I checked the latest head and, since the active configure scripts still consume the legacy `amdgpu_family_matrix.py`, I would treat my remaining note as a parity/migration concern rather than a current workflow regression.

The one thing I would like to verify before this data becomes the workflow source of truth is the TSAN expected-failure setting. The new dataclass data marks Linux TSAN as expected-failure, while the current legacy matrix keeps TSAN blocking.

**Inline comment on `build_tools/github_actions/new_amdgpu_family_matrix_data.py`, line 89:**

This looks like a parity drift from the current matrix. In `amdgpu_family_matrix.py`, Linux `tsan` is defined without an `expect_failure` override, so current consumers treat TSAN as blocking. With this replacement data, `BuildVariantInfo.to_dict()` will serialize `expect_failure=True`, and a future migration would turn TSAN into a continue-on-error job unless that policy change is deliberate.

Since current workflow generation still uses the legacy matrix, I do not think this is an active workflow regression in this PR. Could we either remove this flag for parity, or add an explicit test/comment showing that making TSAN expected-failure is intentional before the new matrix is wired into CI generation?
