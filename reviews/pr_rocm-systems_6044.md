# PR Review: ROCm/rocm-systems#6044

* **PR:** https://github.com/ROCm/rocm-systems/pull/6044
* **Title:** `build(rocjitsu): Add emulation project mapping and build options in t...`
* **Base:** `develop`
* **Head:** `1c2a38a4bc57b154bcd024e981148fab438cc579`
* **Reviewed:** 2026-05-14
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**CHANGES REQUESTED** - The new emulation mapping has a path typo. The repository subtree is `emulation/rocjitsu`, but the PR maps `emulation/rocjistu`, so changes under the actual rocJITsu tree will not match the intended narrow emulation project mapping.

## Findings

### BLOCKING: rocJITsu subtree mapping is misspelled

The PR adds the path map entry as [`"emulation/rocjistu": "emulation"`](https://github.com/ROCm/rocm-systems/blob/1c2a38a4bc57b154bcd024e981148fab438cc579/.github/scripts/therock_matrix.py#L4), but the repository directory is `emulation/rocjitsu`.

The difference is the `s`/`t` order near the end:

```diff
- emulation/rocjistu
+ emulation/rocjitsu
```

`therock_configure_ci.py` matches changed files with `path.startswith(subtree)`, so the misspelled entry will not match actual `emulation/rocjitsu/...` paths. For PR/push events this defeats the intended narrow project selection and falls back to broader project evaluation; for manual subtree selection, `emulation/rocjitsu` would not map to any project.

**Required action:** change the key to `emulation/rocjitsu`, and ideally add or update a matrix test that exercises a changed path under `emulation/rocjitsu/`.

## Suggested Inline Comment

Target line: `.github/scripts/therock_matrix.py`, line 4.

```text
This path looks misspelled. The repository subtree is `emulation/rocjitsu`, but this mapping uses `emulation/rocjistu` (`tsu` vs `stu` near the end). Since `therock_configure_ci.py` matches changed files with `path.startswith(subtree)`, changes under the actual rocJITsu directory will not hit the intended emulation mapping. Could we update this to `emulation/rocjitsu` and add a small matrix test for an `emulation/rocjitsu/...` changed path?
```

## Verification

* Refreshed `origin/develop` and `refs/remotes/pr/6044`.
* Checked latest PR metadata: open, not draft, mergeable, review required.
* Reviewed changed file: `.github/scripts/therock_matrix.py`.
* Confirmed the PR tree contains `emulation/rocjitsu`, not `emulation/rocjistu`, via `git ls-tree -d refs/remotes/pr/6044:emulation`.
* Ran `git -c safe.directory=* diff --check origin/develop...refs/remotes/pr/6044`; passed.
* Checked latest public PR checks; package/configure jobs are passing or pending, with Windows PAL and Linux sanity still pending at review time.
