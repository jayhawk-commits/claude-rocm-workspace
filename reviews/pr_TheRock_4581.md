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

**DESIGN RECONSIDERATION REQUESTED.**

The CMake-side blocker from the first review has been fixed by
`2b13e4ea` (`fix(ci): track packaged test script inputs`). Packaged script
files are now part of subproject fingerprints, CMake configure dependencies,
and stage install dependencies.

A new design-level review asks whether this should be implemented in
`cmake/therock_subproject.cmake` at all. The concern is that the PR makes
TheRock install test scripts on behalf of subprojects, using TheRock-specific
paths and a new `INSTALL_TEST_SCRIPT_FILES` hook. The requested alternative is
for subprojects to install their own test scripts by convention, then for
CI/artifact packaging to consume those installed files.

My previous conditional approval is therefore superseded. The correctness fixes
are in reasonable shape, but the architectural question should be resolved with
the reviewer before merge.

---

## Current Design Review Concern

### 1. Superproject-installed test scripts may be the wrong ownership boundary

**DESIGN ISSUE: A new review asks to move script installation into the
subprojects themselves instead of extending `therock_subproject.cmake`.**

ScottTodd's review comment on `cmake/therock_subproject.cmake` asks why any
changes to that file are needed and suggests a different model:

https://github.com/ROCm/TheRock/pull/4581#discussion_r3156315893

Paraphrased concern:

- Subprojects should install their test scripts under a normal install-tree
  convention, for example `share/tests/`.
- The CI system should look for installed test scripts there.
- The subprojects should not need to know or care that TheRock is the
  superproject building them.
- Standalone subproject builds should install runnable test scripts too.
- A narrow `INSTALL_TEST_SCRIPT_FILES` hook could grow into a general
  superproject-managed side-channel for tests, benchmarks, dependencies, or
  other files.

This is a design objection, not just a naming nit. The current PR adds
TheRock-specific script installation behavior to the superproject wrapper, and
the reviewer is asking whether that whole ownership model should be inverted.

**Likely resolution paths:**

1. Rework the design so `rocm-systems` subprojects install their own test
   scripts into a conventional test-script location. TheRock would then only
   include those installed files in artifacts and point CI at them.
2. Keep the current design only if the reviewer agrees that this is an
   intentional transitional mechanism for RFC0010 and that standalone
   subproject installation is a follow-up.

Given the review wording, option 1 is probably the safer long-term direction.

---

## Remaining Merge Precondition If Current Design Continues

### 2. Packaged `rocrtst` script source is still stale in TheRock

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

**Required before merge if this design continues:** Ensure TheRock's
`rocm-systems` submodule pointer includes ROCm/rocm-systems#5541
(`06d2a72ad3` or later). This can happen outside PR 4581; the important part is
that 4581 should not merge while packaging the older script. If the design is
reworked so subprojects install their own scripts, this precondition still
applies to whatever `rocm-systems` revision supplies the installed script.

---

## Resolved Issue

### 3. Packaged script contents now participate in rebuild/fingerprint inputs

**RESOLVED by `2b13e4ea`.**

The original review noted that `INSTALL_TEST_SCRIPT_FILES` were installed into
the generated subproject init file but were not included in the subproject
fingerprint or stage install dependencies. That could leave incremental builds
with stale packaged scripts.

The current PR head fixes that by:

- appending `_install_test_script_files` to `_fprint_files`;
- adding the files to `CMAKE_CONFIGURE_DEPENDS`;
- adding the files to the stage install custom command `DEPENDS`.

That addresses the stale artifact/rebuild concern for the current design.

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

Pause merge and respond to the design review first.

The cleanest path is likely to move test-script installation responsibility into
the owning subprojects, then simplify the TheRock PR so it consumes installed
test scripts rather than installing source files from the superproject wrapper.
Do not add TheRock-local test script edits just to work around the stale
packaged source.

If the current design is kept after discussion, ensure TheRock is using a
`rocm-systems` submodule revision that contains ROCm/rocm-systems#5541 before
merge.

---

## Conclusion

**Approval Status: DESIGN RECONSIDERATION REQUESTED.**

The earlier CMake/fingerprint blocker is resolved, and the `rocrtst` script fix
exists in rocm-systems. The new review raises a broader ownership/design concern
that should be settled before treating PR 4581 as merge-ready.
