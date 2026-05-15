# Test Filter Standardization Open PR Audit

Date: 2026-05-14

Scope: open PRs in `ROCm/TheRock`, `ROCm/rocm-libraries`, and
`ROCm/rocm-systems` related to test filter standardization or adjacent
test-runner convergence work owned by other contributors.

Excluded from the action list:

- `users/jayhawk-commits/*` validation or migration branches.
- PRs whose primary purpose is tracking our own RFC0010 helper work.
- Broad unrelated CI/test PRs that only matched search terms incidentally.

Useful tracker:

- ROCm/TheRock#5090 tracks RFC0010 test-runner migration PRs, but this audit is
  focused on work owned by others that may need review or unblock help.

## Summary

The best candidates for assistance are PRs that are either close to review or
blocked by narrow CI/pre-commit issues:

- rocm-libraries#7215, rocm-libraries#7315, and rocm-libraries#7458 look like
  good review-assistance candidates once pending checks finish.
- rocm-libraries#7076 and rocm-libraries#7132 likely need small formatting or
  check-failure triage before deeper review.
- rocm-libraries#7037 has concrete Windows rocprim failures and may benefit
  from focused failure analysis.
- rocm-systems#6063 is a good review candidate after pending checks finish.
- TheRock#4812 appears close, pending long-running TheRock CI and review.

Several older TheRock draft branches are heavier: they either have merge
conflicts, broad CI failures, or known design questions. Those are less likely
to unblock quickly without author rework.

## Most Assistable Soon

| PR | Owner branch | Current state | Blocker | Suggested help |
| --- | --- | --- | --- | --- |
| ROCm/TheRock#4812 - Add test filter standardisation to rocrtst | `users/dravindr/tr_rocr` | Open, non-draft, mergeable, review required | TheRock CI still had long-running compiler-runtime jobs | Review after CI settles; likely close to unblock |
| ROCm/rocm-systems#6063 - test_runner: add CE suite support, gtest-style suite filtering, and docs | `users/atulkulk/ce-test-runner` | Open, non-draft, mergeable, review required | Pending checks | Review once checks complete |
| ROCm/rocm-libraries#7215 - Add test filter standardization to rocthrust | `users/dravindr/tf_rocthrust` | Open draft | Pending checks, no failures seen in latest summary | Ask whether author wants early review/help promoting from draft |
| ROCm/rocm-libraries#7315 - Add test filter standardisation to rocwmma | `users/dravindr/rocwmma` | Open draft | Pending checks, no failures seen in latest summary | Review once checks complete |
| ROCm/rocm-libraries#7458 - hipSPARSELt spmm-specific filters | `users/vinhuang/spmm_test_filter` | Open, non-draft, review required | Pending checks, no failures seen in latest summary | Good candidate for review assistance |

## Blocked But Likely Fixable

| PR | Owner branch | Current state | Blocker | Suggested help |
| --- | --- | --- | --- | --- |
| ROCm/rocm-libraries#7076 - hiprand test filter standardization | `users/dravindr/tf_hiprand` | Open draft, mergeable | `pre-commit` and Jenkins failures | Triage formatting/check output first; then rerun |
| ROCm/rocm-libraries#7132 - rocrand test filter standardization | `users/dravindr/tf_rocrand` | Open draft, mergeable | `pre-commit`, Jenkins, and hiprand test failure | Separate mechanical failures from real test regression |
| ROCm/rocm-libraries#7158 - hipfft test filter standardization | `users/dravindr/tf_hipfft` | Open draft, mergeable | Jenkins failure | Determine if infra-only or branch issue |
| ROCm/rocm-libraries#7159 - rocfft test filter work | `users/dravindr/tf_rocfft` | Open draft, mergeable | Jenkins failure | Same triage pattern as hipfft |
| ROCm/rocm-libraries#7037 - rocprim test filter standardization | `users/dravindr/tf_rocprim` | Open, non-draft | Windows rocprim test failures | Focused Windows failure triage could unblock |
| ROCm/rocm-systems#3107 - Enable CTest tag-based test filtering | `jungx098/catch2label_cmake` | Open, non-draft, stale label | Windows hip-tests failure | Needs owner activity plus targeted Windows hip-tests analysis |

## Heavier / Wait For Author Rework

| PR | Owner branch | Current state | Why it is heavier |
| --- | --- | --- | --- |
| ROCm/TheRock#4694 - RCCL filter standardisation | `users/dravindr/tr_rccl` | Open draft, conflicting | Needs rebase before useful review |
| ROCm/TheRock#4947 - pytest test filter support | `pytest-test-filter-support` | Open draft | Many CI failures, including unit tests and pre-commit |
| ROCm/TheRock#4964 - Rocsolver test filter | `rocsolver-test-filter` | Open draft | Multiple TheRock CI failures |
| ROCm/TheRock#5054 - Use test filter modules within test scripts | `users/dravindr/tr_runner` | Open draft | Known design questions plus CI/pre-commit failures |
| ROCm/TheRock#4699 - hipblas test categorization | `users/madkasul/hipblas_testFilters` | Open, non-draft | Changes requested and failing tests |
| ROCm/TheRock#4407 - rocroller test filtering support | `users/dravindr/tr_rocroller` | Open, non-draft | Unknown mergeability and several failing TheRock checks |
| ROCm/rocm-libraries#6943 - rocSOLVER test filter standardization | `test-filter-rocsolver` | Open draft | Changes requested plus broad CI failures |
| ROCm/rocm-libraries#6945 - Tensile/Tensilite pytest categories | `pytest-test-filter-support` | Open draft | Broad failures; likely depends on pytest-filter direction |
| ROCm/rocm-libraries#6190 - rocroller test filter standardization | `users/dravindr/tf_rocroller` | Open, non-draft | Unknown mergeability, failed rocBLAS check, pending checks |

## Recommended Next Actions

1. Ask authors of rocm-libraries#7215 and rocm-libraries#7315 whether they want
   review help while still in draft.
2. Triage the easy mechanical failures in rocm-libraries#7076 and
   rocm-libraries#7132, especially pre-commit.
3. Review rocm-systems#6063 once its pending checks finish.
4. Review TheRock#4812 after the pending TheRock compiler-runtime jobs finish.
5. For older TheRock draft branches, wait for author rebase/cleanup before
   investing deep review time.

