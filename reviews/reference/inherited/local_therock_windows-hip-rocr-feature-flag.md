# Branch Review: users/jayhawk-commits/windows-hip-rocr-feature-flag

* **Branch:** `users/jayhawk-commits/windows-hip-rocr-feature-flag`
* **Base:** `main`
* **Reviewed:** 2026-04-27
* **Commits:** 1 commit (`2d19e968`)
* **CI:** No CI run data available

---

## Summary

This branch adds a CI-only feature flag `WINDOWS_HIP_ROCR_TESTS` (an env var, not a CMake flag) that gates the informational `hip-tests (ROCR)` matrix entry on Windows CI. Previously the ROCR entry was emitted unconditionally alongside the PAL entry; now PAL is always emitted and ROCR is opt-in via the flag. `test_artifacts.yml` exposes a corresponding `windows_hip_rocr_tests` workflow input (default `'false'`) for both `workflow_dispatch` and `workflow_call` triggers. The change also updates and extends the existing unit tests.

**Net changes:** +44 lines, -18 lines across 3 files.

---

## Overall Assessment

**✅ APPROVED** - The implementation is correct, safe, and complete. No blocking issues found. All callers are unaffected because the new input is optional with a `false` default that preserves the previous behavior (ROCR suppressed). Tests are behavioral and well-structured.

**Strengths:**

- Correct use of an optional workflow input with a safe default — existing callers require zero changes.
- Input declared in **both** `workflow_dispatch` and `workflow_call` sections, correctly wired through `${{ inputs.windows_hip_rocr_tests }}` (which resolves for both trigger types in GitHub Actions).
- `str2bool` is a pre-existing, well-tested utility from `github_actions_api.py` — re-using it is the right call.
- The new test `test_windows_hip_tests_default_emits_pal_only` is a genuine behavioral test: it exercises the gate being off and confirms only PAL is emitted. Not a change-detector.
- Existing tests properly updated to set `WINDOWS_HIP_ROCR_TESTS=true` so they continue testing the ROCR-enabled path.
- `tearDown` in the test class does a full env restore (`os.environ.clear()` + `os.environ.update(self._orig_env)`), so there is no env pollution between tests.
- The comment update in `fetch_test_configurations.py` accurately describes the new behavior.

**No Blocking or Important Issues.**

---

## Detailed Review

### 1. `.github/workflows/test_artifacts.yml` — Input Declaration

The input `windows_hip_rocr_tests` is added with `type: string` and `default: 'false'` in both the `workflow_dispatch` block (lines 34-36) and the `workflow_call` block (lines 68-70), and is correctly wired to the env var at the configure step (line 123):

```yaml
WINDOWS_HIP_ROCR_TESTS: ${{ inputs.windows_hip_rocr_tests }}
```

In GitHub Actions, `${{ inputs.* }}` resolves correctly for both `workflow_dispatch` and `workflow_call` triggers — this is the right idiom (unlike the historical `github.event.inputs.*` pitfall). No issue here.

### 2. Caller Verification

All callers of `test_artifacts.yml` were checked:

| Caller | Passes `windows_hip_rocr_tests`? | Impact |
|--------|----------------------------------|--------|
| `ci_linux.yml` | No | Unaffected — Linux never hits the Windows hip-tests branch. Default `'false'` harmless. |
| `ci_windows.yml` | No | Unaffected — defaults to `'false'`, ROCR entry stays suppressed (same behavior as desired). |
| `multi_arch_ci_linux.yml` | No | Unaffected — Linux only. |
| `multi_arch_ci_windows.yml` | No | Unaffected — defaults to `'false'`, ROCR stays suppressed. |

None of the callers need to be updated because:
1. The input is optional with a `'false'` default.
2. The `'false'` default reproduces the **new desired behavior** — ROCR off — not a regression.

The only caller that would ever want to pass `windows_hip_rocr_tests: 'true'` is a future manual dispatch or a dedicated experimental workflow. That is by design.

### 3. `fetch_test_configurations.py` — Python Logic

The change is a one-liner env read + guard:

```python
windows_hip_rocr_tests = str2bool(os.getenv("WINDOWS_HIP_ROCR_TESTS", "false"))
```

and then wrapping the ROCR dict literal in `if windows_hip_rocr_tests:`. This is idiomatic and consistent with how `run_extended_tests` is handled three lines above. No Python style guide violations:

- No `sys.exit()`, no broad `except Exception`.
- No new function without type hints (no new functions at all).
- `os.getenv` with stdlib `os` is consistent with surrounding code.
- `str2bool` handles all edge cases including `None`, whitespace, and mixed case.

### 4. Test Quality

Three tests cover the Windows hip-tests contract:

| Test | What it verifies | Behavioral? |
|------|-----------------|-------------|
| `test_windows_hip_tests_default_emits_pal_only` (new) | Gate-off → only PAL emitted, correct fields | Yes |
| `test_windows_hip_tests_emits_pal_and_rocr_entries` (updated) | Gate-on → both PAL and ROCR, correct fields | Yes |
| `test_windows_hip_tests_quick_uses_single_shard` (updated) | Gate-on + quick mode → single shard per entry | Yes |

None of these are change-detector tests. They assert on output **semantics** (job names, `expect_failure` flag, shard counts), not on implementation structure. The new test covers the default path that was previously untested, which is the right thing to add when gating behavior behind a flag.

The `setUp`/`tearDown` pattern is robust: env state is saved at the start of each test and fully restored after, so `WINDOWS_HIP_ROCR_TESTS` set in one test cannot bleed into another.

One minor observation: `test_windows_hip_tests_default_emits_pal_only` does not set `AMDGPU_FAMILIES`, relying on the `setUp` default of `"gfx94X-dcgpu"`. This is fine — the Windows hip-tests path is triggered by `RUNNER_OS=Windows` + `TEST_LABELS` containing `hip-tests`, independent of GPU family. The shard counts (`total_shards=4`, `shard_arr=[1,2,3,4]`) are derived from the matrix config for that label, not from the family, so the test is not accidentally tied to an irrelevant fixture value.

---

## Recommendations

### ❌ REQUIRED (Blocking):

None.

### ✅ Recommended:

None.

### 💡 Consider:

1. **Add a `description:` to the `workflow_dispatch` input.** The other `workflow_dispatch` inputs with non-obvious semantics (e.g., `release_type`) have a `description:` field. Adding one like `"Emit hip-tests (ROCR) informational job on Windows (default: false)"` would help operators who trigger the workflow manually via the GitHub UI. This is purely a UX nicety — no functional impact.

### 📋 Future Follow-up:

1. **Remove the flag when ROCR becomes the primary test path.** Per the linked issue [#3587](https://github.com/ROCm/TheRock/issues/3587), ROCR is expected to eventually replace PAL as the pass/fail path. At that point the flag, the PAL-specific entry, and the `expect_failure: True` ROCR path can all be cleaned up in a single commit. The comment in `fetch_test_configurations.py` already points at this.

---

## Testing Recommendations

- **Manual workflow_dispatch verification:** Trigger `test_artifacts.yml` manually from the GitHub UI on a Windows runner with `windows_hip_rocr_tests` left at its default and confirm only `hip-tests (PAL)` appears in the matrix. Trigger again with `windows_hip_rocr_tests: 'true'` and confirm both entries appear.
- **Unit tests:** Run `python -m pytest build_tools/github_actions/tests/fetch_test_configurations_test.py -v` to confirm all three hip-tests tests pass.
- **Linux callers:** Confirm that `ci_linux.yml` and `multi_arch_ci_linux.yml` CI runs are unaffected (the Windows branch in `fetch_test_configurations.py` is only entered when `RUNNER_OS=Windows`).

---

## Conclusion

**Approval Status: ✅ APPROVED**

The change is correct, minimal, and well-tested. The feature flag correctly threads through both trigger types in `test_artifacts.yml`, all callers are unaffected by the optional default, and the tests cover the new behavior path as well as preserving coverage of the existing ROCR-enabled path. Ready to merge.
