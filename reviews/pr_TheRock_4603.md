# PR Review: ROCm/TheRock#4603

* **PR:** https://github.com/ROCm/TheRock/pull/4603
* **Title:** `[ci] Adding host-asan for postsubmit`
* **Base:** `main`
* **Head:** `ba19e92ce8bad1504e89eb7e697de84ebab241dc`
* **Reviewed:** 2026-04-30
* **State at review:** OPEN

---

## Overall Assessment

**CHANGES REQUESTED** - The push-triggered host-ASAN path can include a family that is not declared to support `host-asan`, so the postsubmit workflow can build the wrong target set after merge.

## Latest Comment Check

Checked latest PR state on 2026-04-30 at head `ba19e92c`. There are no issue comments. Existing inline review threads cover host-ASAN vs ASAN explanatory context, runner capacity for the new push trigger, TSAN follow-up scope, and future dynamic runner lookup / runner label refactoring.

None of the current threads covers the effective-variant filtering issue below: the PR-added push remap changes the effective variant from `asan` to `host-asan`, but `_expand_build_config_for_platform()` still filters families using `ci_inputs.build_variant`. The finding remains distinct and current on the latest head.

## Findings

### BLOCKING: Push host-ASAN still filters families using `asan`

This is tied to the PR's diff: it adds `host-asan` as a distinct build variant and adds the push-only remap from `asan` to `host-asan` in `expand_build_configs()` at [`configure_multi_arch_ci.py#L926-L930`](https://github.com/ROCm/TheRock/blob/ba19e92ce8bad1504e89eb7e697de84ebab241dc/build_tools/github_actions/configure_multi_arch_ci.py#L926-L930). After that remap, the function passes the original `ci_inputs` object into `_expand_build_config_for_platform()` at [`#L946-L950`](https://github.com/ROCm/TheRock/blob/ba19e92ce8bad1504e89eb7e697de84ebab241dc/build_tools/github_actions/configure_multi_arch_ci.py#L946-L950). `_expand_build_config_for_platform()` reads `build_variant` from `ci_inputs.build_variant` at [`#L789`](https://github.com/ROCm/TheRock/blob/ba19e92ce8bad1504e89eb7e697de84ebab241dc/build_tools/github_actions/configure_multi_arch_ci.py#L789), so the per-family support check at [`#L806-L807`](https://github.com/ROCm/TheRock/blob/ba19e92ce8bad1504e89eb7e697de84ebab241dc/build_tools/github_actions/configure_multi_arch_ci.py#L806-L807) still tests for `asan`, not the new effective `host-asan` variant.

That matters because `gfx950` in the postsubmit matrix supports `asan` and `tsan`, but not `host-asan` ([`amdgpu_family_matrix.py#L252-L260`](https://github.com/ROCm/TheRock/blob/ba19e92ce8bad1504e89eb7e697de84ebab241dc/build_tools/github_actions/amdgpu_family_matrix.py#L252-L260)). A direct local invocation of the push path produced a `host-asan` build config with `dist_amdgpu_families` set to `gfx94X-dcgpu;gfx950-dcgpu`, even though only `gfx94x` declares `host-asan` support.

**Required action:** Pass the effective build variant into `_expand_build_config_for_platform()` or otherwise update `ci_inputs` before filtering. Add a regression test where a push ASAN target selection includes `gfx950` and asserts it is excluded unless `host-asan` is explicitly added to that family.

## Verification

* Refreshed the PR ref on 2026-04-30.
* Ran a direct local invocation of `select_targets()` plus `expand_build_configs()` for `event_name='push'`, `build_variant='asan'`; it emitted `gfx94X-dcgpu;gfx950-dcgpu` for a `host-asan` config.
* Checked GitHub run history for `Multi-Arch CI ASAN` on the PR branch; only an older cancelled `workflow_dispatch` run was found, so there is no successful host-ASAN workflow evidence for this branch.
* Attempted focused unittest execution, but this local environment lacks `yaml`/PyYAML needed by the test harness.
