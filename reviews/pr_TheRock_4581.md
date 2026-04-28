# PR Review: ROCm/TheRock#4581

* **PR:** https://github.com/ROCm/TheRock/pull/4581
* **Title:** RFC0010: package initial core test scripts in artifacts
* **Author:** jayhawk-commits
* **Reviewed:** 2026-04-28
* **Updated:** 2026-04-28
* **Merge base:** `main` at `de74a0b8c1b960d7c2ab5dc88a92c15d1d85cad7`
* **Current `origin/main`:** `14354eb3de2e61fd6040c4edeb0296dd24c1d1e7`
* **Head:** `users/jayhawk-commits/package-test-scripts-in-artifacts` at `2b13e4eaf758356a3ccb436c160a990f32949e9f`
* **Worktree:** `C:\Dev\TheRock-pr-4581`
* **Commits:** 11

---

## Summary

This PR adds subproject support for packaging test scripts into component
artifacts under `share/therock-scripts`, then switches the `hip-tests` and
`rocrtst` test matrix entries to execute those packaged scripts from
`./build/share/therock-scripts`.

**Current net changes:** +57 / -9 across 5 files.

---

## Overall Assessment

**CONDITIONALLY APPROVED: merge after the `rocm-systems` submodule pointer
includes ROCm/rocm-systems#5541.**

The CMake-side blocker from the first review has been fixed by
`2b13e4ea` (`fix(ci): track packaged test script inputs`). Packaged script
files are now part of subproject fingerprints, CMake configure dependencies,
and stage install dependencies.

The remaining merge precondition is the selected `rocm-systems` source revision
for the packaged `rocrtst` script. The script fix has now merged in
ROCm/rocm-systems#5541, but PR 4581 still points at an older `rocm-systems`
submodule revision. If this PR merges before TheRock advances that submodule to
include rocm-systems merge commit `06d2a72ad3`, it will still package the
broken `test_rocrtst.py`.

This does **not** require TheRock-local test script edits in PR 4581. The clean
resolution is to merge only after TheRock's `rocm-systems` submodule pointer
includes ROCm/rocm-systems#5541, whether by a separate submodule update or by a
regular submodule roll-forward.

---

## Current Merge Precondition

### 1. Packaged `rocrtst` script source is still stale in TheRock

**MERGE PRECONDITION: Merging with the current submodule pointer would still
package a `rocrtst` script that can fail for unlisted AMDGPU families.**

PR 4581 changes `rocrtst` to run:

```text
./build/share/therock-scripts/test_rocrtst.py
```

and installs that file from:

```text
${THEROCK_ROCM_SYSTEMS_SOURCE_DIR}/test/therock/test_rocrtst.py
```

The PR branch currently records:

```text
rocm-systems -> 92b74318762433ef4b353489b4a1c5a79690b991
```

Current `origin/main` records:

```text
rocm-systems -> d39c282dc2e7487612766f02e43f115fb923190a
```

Both revisions predate the rocm-systems fix merged as:

```text
06d2a72ad3b98184aa1fc56684bb4174a249ab15
```

At the stale revisions, `test_rocrtst.py` only initializes
`exclude_filter` inside the ignore-list branch and then uses it unconditionally.
That still raises `NameError` for families not present in `TEST_TO_IGNORE`, such
as `gfx120X-all`.

**Required before merge:** Ensure TheRock's `rocm-systems` submodule
pointer includes ROCm/rocm-systems#5541 (`06d2a72ad3` or later). This can happen
outside PR 4581; the important part is that 4581 should not merge while
packaging the older script.

---

## Resolved Issue

### 2. Packaged script contents now participate in rebuild/fingerprint inputs

**RESOLVED by `2b13e4ea`.**

The original review noted that `INSTALL_TEST_SCRIPT_FILES` were installed into
the generated subproject init file but were not included in the subproject
fingerprint or stage install dependencies. That could leave incremental builds
with stale packaged scripts.

The current PR head fixes that by:

- appending `_install_test_script_files` to `_fprint_files`;
- adding the files to `CMAKE_CONFIGURE_DEPENDS`;
- adding the files to the stage install custom command `DEPENDS`.

That addresses the stale artifact/rebuild concern.

---

## Non-Blocking Notes

- The PR branch is behind current `origin/main`; the merge base is still
  `de74a0b8`, while current `origin/main` is `14354eb3`.
- `gh pr checks 4581 --repo ROCm/TheRock` currently reports pending Multi-Arch
  jobs and `mergeStateStatus=UNSTABLE`. No new code-review blocker is inferred
  from pending CI alone; the PR still needs a green CI result before merge.
- `git diff --check origin/main...HEAD` is clean.

---

## Recommendation

Keep PR 4581 limited to packaging mechanics. Do not add TheRock-local test
script edits just to work around the stale packaged source.

Before merge, ensure TheRock is using a `rocm-systems` submodule revision that
contains ROCm/rocm-systems#5541. Once that is true and CI is green, I do not see
another legitimate blocker in the current PR diff.

---

## Conclusion

**Approval Status: CONDITIONALLY APPROVED once the packaged `rocrtst` source
revision includes the merged rocm-systems fix.**

The earlier CMake/fingerprint blocker is resolved. The remaining concern is a
real merge precondition, but it should be satisfied by a submodule update rather
than by widening PR 4581.
