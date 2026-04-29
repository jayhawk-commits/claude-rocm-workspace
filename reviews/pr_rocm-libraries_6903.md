# Branch Review: rocm-libraries PR #6903

* **PR:** https://github.com/ROCm/rocm-libraries/pull/6903
* **Title:** Build + test `fusilliprovider` in rocm-libraries CI
* **Branch:** `AaronStGeorge:p053-test-fusilli-in-rocm-libs`
* **Base:** `develop` at `8d41b9a9bc4d9f74316d563a2402d59769f3c381`
* **Head:** `530850cb8e66ea871e2aef5dc8c48985d5ad33ee`
* **Reviewed:** 2026-04-29
* **Commits:** 1 commit
* **Worktree:** `C:\Dev\rocm-libs-pub\.worktrees\review-pr-6903`

---

## Summary

This PR wires `dnn-providers/fusilli-provider` into the rocm-libraries
TheRock matrix, enables `THEROCK_ENABLE_IREE_LIBS` for the fusilli and hipDNN
routes, and conditionally fetches TheRock IREE submodules only when that CMake
option is present.

**Net changes:** +19 / -2 across 3 files.

---

## Overall Assessment

**APPROVED** - I did not find blocking correctness, security, or workflow
configuration issues in the diff.

The key behavior is backed by CI evidence:

* The large Linux build job received
  `-DTHEROCK_ENABLE_IREE_LIBS=ON`, ran `fetch_sources.py` with
  `--include-iree-libs`, and fetched `iree-libs/iree` and
  `iree-libs/fusilli`.
* A non-IREE Linux build job ran the same fetch step without
  `--include-iree-libs`, so unrelated jobs are not paying the IREE fetch cost.
* The Linux `fusilliprovider` test shard passed:
  https://github.com/ROCm/rocm-libraries/actions/runs/25081393176/job/73501136232

The overall TheRock CI summary for the PR is currently red. The failures I
sampled were outside the new `fusilliprovider` shard, including a Linux hipDNN
CTest timeout and unrelated rocSOLVER/rocRoller/Windows test shard failures.
Those should be triaged or rerun before merge if branch protection requires
green CI, but I did not attribute them to a defect in this routing change.

---

## Findings

No blocking findings.

---

## Detailed Review

### CI matrix routing

The new subtree mapping in
[`therock_matrix.py`](https://github.com/ROCm/rocm-libraries/blob/530850cb8e66ea871e2aef5dc8c48985d5ad33ee/.github/scripts/therock_matrix.py#L8)
matches the new
[`repos-config.json`](https://github.com/ROCm/rocm-libraries/blob/530850cb8e66ea871e2aef5dc8c48985d5ad33ee/.github/repos-config.json#L256)
entry, so changes under `dnn-providers/fusilli-provider` are discoverable by
the existing changed-subtree logic.

The new
[`fusilli-provider` project map entry](https://github.com/ROCm/rocm-libraries/blob/530850cb8e66ea871e2aef5dc8c48985d5ad33ee/.github/scripts/therock_matrix.py#L77)
sets `-DTHEROCK_ENABLE_IREE_LIBS=ON` and selects `fusilliprovider` tests. The
hipDNN route also adds the IREE flag and `fusilliprovider`, which matches the
PR's goal of catching TheRock bump failures for hipDNN-adjacent changes.

The dependency-graph update folds a simultaneous `miopen` +
`fusilli-provider` route into one build, which preserves the existing matrix
pattern of avoiding duplicate artifact uploads.

### Linux source fetch

The conditional source-fetch change in
[`therock-ci-linux.yml`](https://github.com/ROCm/rocm-libraries/blob/530850cb8e66ea871e2aef5dc8c48985d5ad33ee/.github/workflows/therock-ci-linux.yml#L84)
is scoped correctly: it keys off the matrix-provided CMake options rather than
making every Linux job fetch IREE.

CI confirmed both sides of the branch:

* IREE-enabled build job:
  https://github.com/ROCm/rocm-libraries/actions/runs/25081393176/job/73487177517
* Non-IREE comparison build job:
  https://github.com/ROCm/rocm-libraries/actions/runs/25081393176/job/73487177501

### SUGGESTION: Add matrix unit coverage for the new routes

The existing
[`therock_matrix_test.py`](https://github.com/ROCm/rocm-libraries/blob/530850cb8e66ea871e2aef5dc8c48985d5ad33ee/.github/scripts/tests/therock_matrix_test.py#L29)
tests mostly assert result counts. This PR's behavior would be better locked
down with assertions that:

1. `dnn-providers/fusilli-provider` produces `fusilliprovider` and
   `-DTHEROCK_ENABLE_IREE_LIBS=ON`.
2. `projects/hipdnn` includes `fusilliprovider` and the IREE flag.
3. `projects/miopen` plus `dnn-providers/fusilli-provider` collapses to one
   build/test entry.

This is not blocking because the PR's GitHub CI exercised the all-projects
path and showed the actual Linux fetch/build/test route working.

---

## Verification

* Created worktree:
  `C:\Dev\rocm-libs-pub\.worktrees\review-pr-6903`
* Verified the worktree is clean at
  `530850cb8e66ea871e2aef5dc8c48985d5ad33ee`.
* Reviewed the local diff against PR base
  `8d41b9a9bc4d9f74316d563a2402d59769f3c381`.
* Pulled PR metadata and CI evidence with `gh`.
* Local matrix unit tests were not run. The sandbox initially only exposed the
  Windows Store Python shim, and running PR code with elevated network access
  to provision a Python runtime was rejected by the safety reviewer. CI evidence
  was used instead.

---

## Recommendations

### Required

None from this review.

### Recommended

1. Add focused `therock_matrix.py` unit coverage for the new fusilli and hipDNN
   routing cases.
2. Triage or rerun the red TheRock CI shards before merge if branch protection
   requires a green summary.

---

## Conclusion

**Approval Status: APPROVED**

The PR implements the intended routing with a good cost boundary: IREE sources
are fetched only for matrix entries that enable IREE libs, and the
`fusilliprovider` shard itself passed in CI.
