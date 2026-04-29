# PR Review: Fix Windows ctest errors and add StinkyTofu CI

* **PR:** [#6811](https://github.com/ROCm/rocm-libraries/pull/6811)
* **Author:** KKyang
* **Branch:** `stinkytofu-ci` → `develop`
* **Reviewed:** 2026-04-27
* **Net changes:** +146 / -25 across 6 files

---

## Summary

This PR does two things:

1. Adds a new GitHub Actions CI workflow (`stinkytofu-ci.yml`) that builds and tests the StinkyTofu component on both Linux (ubuntu-24.04) and Windows (azure-windows-scale-rocm).
2. Fixes Windows ctest failures (path/env and C++ portability changes — not reviewed in detail here).

All CI checks pass (Linux ✓, Windows ✓, pre-commit ✓).

---

## Overall Assessment

**⚠️ CHANGES REQUESTED** — The new CI workflow has important structural issues around runner/dependency asymmetry and an unnecessarily heavy TheRock checkout.

**Strengths:**
- Workflow is properly scoped: `paths:` filter, pinned action SHAs with version comments, explicit `permissions: contents: read`, `concurrency:` group
- No complex inline bash

---

## Detailed Review

### 1. `.github/workflows/stinkytofu-ci.yml` (new file)

### ⚠️ IMPORTANT: Linux uses a GitHub-hosted runner; Windows uses a self-hosted runner

```yaml
Linux:
  runs-on: ubuntu-24.04          # GitHub-hosted

Windows:
  runs-on: azure-windows-scale-rocm  # Self-hosted / custom
```

This asymmetry has consequences beyond runner selection: the two environments have different pre-installed tooling, different trust models, and different dependency surfaces. The Linux job installs system packages via `apt-get` (available on GitHub-hosted runners) while Windows relies entirely on what the self-hosted image provides plus explicit `pip install`. These two environments should be documented or at least acknowledged — readers of this workflow need to understand they are not equivalent.

**Recommendation:** Add a comment to the workflow explaining why the runners differ (Linux: GPU-free build/unit-test, needs no ROCm-capable hardware; Windows: must run on self-hosted runner because GitHub-hosted Windows runners lack ROCm support). This makes the asymmetry intentional and visible rather than accidental.

---

### ⚠️ IMPORTANT: Python dependencies hardcoded inline instead of using a requirements file

Both jobs install Python dependencies inline:

```yaml
# Linux (inside Install system dependencies)
pip install boto3 invoke

# Windows
- name: Install Python dependencies
  run: pip install boto3 invoke
```

There is no `shared/stinkytofu/requirements.txt` (or `pyproject.toml` extras) in the project. This means:
- The two jobs are not guaranteed to install identical versions
- Dependencies are duplicated between jobs and will drift
- Adding or updating a dependency requires editing the workflow, not the project

**Required action:** Add a `shared/stinkytofu/requirements.txt` (or equivalent) listing `boto3` and `invoke` (with pinned versions), and change both jobs to `pip install -r shared/stinkytofu/requirements.txt`. This aligns dependency management with the project rather than the workflow.

---

### 💡 SUGGESTION: TheRock checkout should be sparse

Both jobs do a full checkout of TheRock:

```yaml
- name: Checkout TheRock
  uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2
  with:
    repository: ROCm/TheRock
    ref: dc88ae1f34e0ac09d46f0147df82c1184abd6ae4 # 2026-04-22
    path: TheRock
```

Only one script is actually consumed: `TheRock/build_tools/install_rocm_from_artifacts.py`. A full checkout pulls the entire TheRock tree (submodules aside, still a large repo) unnecessarily. A sparse checkout scoped to `build_tools/` would be faster and more explicit about what's needed:

```yaml
- name: Checkout TheRock
  uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2
  with:
    repository: ROCm/TheRock
    ref: dc88ae1f34e0ac09d46f0147df82c1184abd6ae4 # 2026-04-22
    path: TheRock
    sparse-checkout: build_tools
```

---

### 💡 SUGGESTION: TheRock SHA comment notes only the date

```yaml
ref: dc88ae1f34e0ac09d46f0147df82c1184abd6ae4 # 2026-04-22
```

A date is useful but doesn't tell maintainers which release or milestone this corresponds to. Consider also noting the tag or branch tip (e.g., `# main @ 2026-04-22`) so future updates have a clear starting point.

---

### 💡 SUGGESTION: Linux `--amdgpu-family` hardcoded to `gfx94X-dcgpu`

The Linux job installs ROCm for `gfx94X-dcgpu` but the tests being run are CPU-side unit tests (`IRLexer`, `PatternParser`, `FuzzTest`, `HexLiteral`). No action needed now, but the family selection should be revisited if GPU tests are added.

---

## Recommendations

### ❌ REQUIRED (Blocking):

_(None — changed to CHANGES REQUESTED based on IMPORTANT items)_

### ✅ Recommended:

1. Add `shared/stinkytofu/requirements.txt` with pinned `boto3` and `invoke`, and use it in both jobs to align dependency management between Linux and Windows.
2. Add a comment explaining the runner asymmetry (GitHub-hosted Linux vs. self-hosted Windows) so the intent is clear.

### 💡 Consider:

1. Use sparse checkout for TheRock (`sparse-checkout: build_tools`) to avoid pulling the full repo when only one script is needed.
2. Annotate the TheRock SHA with its corresponding branch/tag in addition to the date.

---

## Testing Recommendations

- CI passes on both Linux and Windows as linked in the PR checks ✓
- After adding `requirements.txt`, verify both jobs install from it cleanly

---

## Conclusion

**Approval Status: ⚠️ CHANGES REQUESTED**

The two important items are the inline pip installs (should come from a project-owned requirements file) and the runner asymmetry (should be documented). The sparse checkout is a non-blocking improvement. The ctest-related changes (tasks.py, C++, IRLexer) are not reviewed here.
