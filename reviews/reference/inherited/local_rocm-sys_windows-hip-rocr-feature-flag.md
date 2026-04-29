# Branch Review: users/jayhawk-commits/windows-hip-rocr-feature-flag

* **Branch:** `users/jayhawk-commits/windows-hip-rocr-feature-flag`
* **Base:** `develop`
* **Reviewed:** 2026-04-27
* **Commits:** 2 commits
* **Companion PR:** [TheRock#4878](https://github.com/ROCm/TheRock/pull/4878)

---

## Summary

This branch opts the rocm-sys-pub CI into Windows ROCR hip-test runs when relevant
projects change (clr, hip, hip-tests, rocr-runtime subtree). It makes two changes:

1. **`therock-test-packages.yml`** — adds `WINDOWS_HIP_ROCR_TESTS: ${{ contains(inputs.projects_to_test, 'hip-tests') }}`
   to the "Configuring CI options" step env block, which tells `fetch_test_configurations.py`
   (in TheRock) to gate the `hip-tests (ROCR)` matrix entry on this flag. The companion
   TheRock PR (`users/jayhawk-commits/windows-hip-rocr-feature-flag`) adds the corresponding
   gating logic and emits `gpu_enable_pal` in the PAL matrix entry.

2. **`therock-test-component.yml`** — adds a conditional step "Set GPU_ENABLE_PAL for
   Windows hip-tests" that writes `GPU_ENABLE_PAL` to `$GITHUB_ENV` when
   `fromJSON(inputs.component).gpu_enable_pal != ''`. This mirrors the fix in
   TheRock's own `test_component.yml` (ROCm/TheRock#3587).

Evaluated against the companion TheRock PR branch, both changes are correct and complete.

**Net changes:** +10 lines, -1 deletion, across 2 files.

---

## Overall Assessment

**✅ APPROVED** — The new code is correct and complete when evaluated against the companion
TheRock PR branch (`users/jayhawk-commits/windows-hip-rocr-feature-flag`), which adds the
`WINDOWS_HIP_ROCR_TESTS` gate and emits `gpu_enable_pal` in the PAL matrix entry. A
pre-existing typo (`fromJSON(inputs. Component)` on line 119) was caught during review
and fixed in a follow-up commit on the same branch.

**Strengths:**

- Clean, minimal diff — adds exactly what is needed, nothing more.
- Correctly scoped: `contains(inputs.projects_to_test, 'hip-tests')` evaluates to
  `"true"` when clr, hip, hip-tests, or rocr-runtime subtrees are affected, because
  `therock_matrix.py` maps all of these to the `"runtimes"` project, which has
  `"hip-tests"` in its `projects_to_test` list.
- The `gpu_enable_pal != ''` guard is the established pattern for optional component
  fields (same idiom as `additional_requirements_files != ''` on line 100). Since
  `gpu_enable_pal` is absent from most component JSON objects (e.g., sanity, rocdecode,
  rocjpeg, rocrtst), the step correctly skips for those.
- No new inputs were added to either reusable workflow, so **no callers need updates**.
- `GPU_ENABLE_PAL` is correctly propagated: the "Set GPU_ENABLE_PAL" step writes it to
  `$GITHUB_ENV`, and the downstream "Test" step inherits it as part of the process
  environment. This is functionally equivalent to the TheRock approach of setting it
  in the Test step's `env:` block.
- Step comment references the correct issue (TheRock#3587) and explains the guard's
  purpose clearly.

**Issues found and resolved:**

- Pre-existing typo on line 119 (`inputs. Component` with a space) caused `TEST_COMPONENT`
  to be silently empty in all test runs. Caught during review and fixed in a second commit.

---

## Detailed Review

### 1. `therock-test-packages.yml` — WINDOWS_HIP_ROCR_TESTS expression

**Analysis of `contains(inputs.projects_to_test, 'hip-tests')` correctness:**

Tracing the data flow:

- `therock-ci.yml` → `setup` job runs `therock_configure_ci.py`, which imports
  `therock_matrix.py`
- `therock_matrix.py` maps `projects/clr`, `projects/hip`, `projects/hip-tests`, and
  `projects/rocr-runtime` to the `"runtimes"` logical project
- The `"runtimes"` project has `projects_to_test: "hip-tests, rocrtst, ..."`, so
  `"hip-tests"` is always present in the comma-separated string when runtimes-touching
  changes are detected
- `therock-ci.yml` passes `projects_to_test: ${{ matrix.projects.projects_to_test }}`
  → `therock-ci-windows.yml` → `therock-test-packages.yml`
- The expression `contains(inputs.projects_to_test, 'hip-tests')` evaluates to
  `"true"` when `"hip-tests"` appears in that string — correct

**Correctness against the companion TheRock branch:**

The companion TheRock PR (`users/jayhawk-commits/windows-hip-rocr-feature-flag`) adds
the gating logic to `fetch_test_configurations.py` so that the `hip-tests (ROCR)` matrix
entry is only emitted when `WINDOWS_HIP_ROCR_TESTS` is set to `"true"`. With that branch
in place, setting `WINDOWS_HIP_ROCR_TESTS: ${{ contains(inputs.projects_to_test, 'hip-tests') }}`
here is the correct and complete opt-in signal. The two PRs are designed to land together
(or in sequence), and the rocm-sys-pub side is correct as written.

**No new required inputs added** — this change only adds an env var to an existing
step. No caller updates are needed.

**Callers verified:**
- [`therock-ci-linux.yml`](https://github.com/ROCm/rocm-systems/blob/develop/.github/workflows/therock-ci-linux.yml)
  calls `therock-test-packages.yml` — not affected (`WINDOWS_HIP_ROCR_TESTS` is a
  Windows-specific variable that `fetch_test_configurations.py` reads on Windows only)
- [`therock-ci-windows.yml`](https://github.com/ROCm/rocm-systems/blob/develop/.github/workflows/therock-ci-windows.yml)
  calls `therock-test-packages.yml` — this is the intended call site, unaffected
  because no new inputs were added

### 2. `therock-test-component.yml` — GPU_ENABLE_PAL conditional step

**`gpu_enable_pal` field availability at the pinned SHA:**

Verified via `git show dc9faefc:build_tools/github_actions/fetch_test_configurations.py`:
the pinned SHA already emits `"gpu_enable_pal": "1"` for `hip-tests (PAL)` and
`"gpu_enable_pal": "0"` for `hip-tests (ROCR)`. All other component entries do not
include a `gpu_enable_pal` key. The `!= ''` comparison works correctly for missing
keys — GitHub Actions `fromJSON()` returns an empty string for absent fields, which
matches the established pattern already used for `additional_requirements_files`.

**GPU_ENABLE_PAL propagation to the Test step:**

The new step writes `GPU_ENABLE_PAL=<value>` to `$GITHUB_ENV`, which makes it
available to all subsequent steps in the same job (including the "Test" step). This
is a valid approach. By contrast, TheRock's own `test_component.yml` at the pinned SHA
sets `GPU_ENABLE_PAL` directly in the Test step's `env:` block. Both approaches
expose the variable to the test script — the rocm-sys-pub approach is slightly more
idiomatic for conditional env vars (avoiding setting `GPU_ENABLE_PAL=` to an empty
string for non-hip-tests components).

**Callers of `therock-test-component.yml` verified:**
- `therock-test-packages.yml` (lines 70, 87) — unaffected: passes `component` from
  matrix, which may or may not have `gpu_enable_pal`; the conditional step handles
  both cases correctly
- `therock-media-test-packages.yml` (lines 24, 45) — unaffected: the inline
  component JSON it passes (`rocdecode`, `rocjpeg`) does not include `gpu_enable_pal`,
  so `fromJSON(inputs.component).gpu_enable_pal != ''` evaluates to false and the step
  is skipped

**shell: bash annotation:**

The new step specifies `shell: bash`. The `defaults: run: shell: bash` is set at
the job level (line 57), so this annotation is redundant but not harmful. It's
consistent with existing explicit `shell:` annotations in this file (e.g., the
powershell steps).

### 3. Pre-existing typo on line 119 — fixed in second commit

**✅ FIXED: `fromJSON(inputs. Component)` → `fromJSON(inputs.component)`**

Line 119 originally had a space between `inputs.` and `Component` (capital C), making
it `inputs. Component` instead of `inputs.component`. In GitHub Actions expressions this
is not valid property access — `TEST_COMPONENT` was silently empty in every test run.
Since the env var is informational (used for display in test output), the impact was
limited to missing metadata, but it was a real bug.

Caught during review and corrected in a follow-up commit on the same branch
(`fix: correct inputs.Component typo in therock-test-component.yml`).

---

## Recommendations

### ❌ REQUIRED (Blocking):

_(None — no blocking issues.)_

### ✅ Recommended:

1. ~~Fix the pre-existing typo on line 119~~ — **Done** in second commit.

### 💡 Consider:

1. **Remove redundant `shell: bash`** from the new "Set GPU_ENABLE_PAL" step —
   the job-level `defaults: run: shell: bash` already applies. Minor style point only.

---

## Testing Recommendations

No CI data is available. Once both this PR and the companion TheRock PR are merged:

- **Verify the ROCR job appears** in the Windows test matrix when a clr/hip/rocr
  subtree change is made, and does NOT appear for unrelated changes (e.g., a profiler
  change that triggers `aqlprofile` tests but not `hip-tests`).
- **Verify `GPU_ENABLE_PAL=0`** reaches the ROCR test script by checking test output
  logs for the `hip-tests (ROCR)` job.
- **Verify `GPU_ENABLE_PAL=1`** reaches the PAL test script by checking the
  `hip-tests (PAL)` job logs.
- **Verify no regression** for `therock-media-test-packages.yml` callers (rocdecode,
  rocjpeg) — confirm the new step is skipped (shows as "skipped" in GHA UI, not
  "failed").

---

## Conclusion

**Approval Status: ✅ APPROVED**

The new code is correct, well-scoped, and follows established patterns. Evaluated against
the companion TheRock PR branch (`users/jayhawk-commits/windows-hip-rocr-feature-flag`),
the rocm-sys-pub changes are correct and complete — `WINDOWS_HIP_ROCR_TESTS` is the
right opt-in signal, and the `GPU_ENABLE_PAL` propagation is sound. A pre-existing typo
caught during review was fixed in a follow-up commit on the same branch.
