# PR Review: ROCm/TheRock#4905

* **PR:** https://github.com/ROCm/TheRock/pull/4905
* **Title:** `[ci] Removing ctest timeout`
* **Base:** `main`
* **Head:** `11ee8045c2a849910900f19526b95698f5a03d22`
* **Reviewed:** 2026-04-30
* **State at review:** MERGED

---

## Overall Assessment

**APPROVED / POST-MERGE NOTE** - No blocking issues found in the timeout removal itself. The workflow still has the component-level GitHub Actions timeout, and the removed `ctest --timeout` values were limited to the changed component scripts.

## Findings

### IMPORTANT: Stale timeout-maintenance comment remains

[`test_miopenprovider.py`](https://github.com/ROCm/TheRock/blob/11ee8045c2a849910900f19526b95698f5a03d22/build_tools/github_actions/test_executable_scripts/test_miopenprovider.py#L31-L32) still says that increasing the timeout in this script requires increasing the job timeout, but this PR removes the script-level `ctest --timeout` from that exact command. The real remaining timeout is the workflow step timeout in [`test_component.yml`](https://github.com/ROCm/TheRock/blob/11ee8045c2a849910900f19526b95698f5a03d22/.github/workflows/test_component.yml#L155-L157).

**Recommendation:** Remove or rewrite the comment so future readers do not go looking for a script timeout that no longer exists.

## Verification

* Inspected the full PR diff.
* Confirmed `test_component.yml` still applies `timeout-minutes` from the component matrix.
* Confirmed other scripts still intentionally carry their own timeout logic where unrelated to this PR.
