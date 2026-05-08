# PR Review: ROCm/rocm-libraries#7144

- PR: https://github.com/ROCm/rocm-libraries/pull/7144
- Title: `[ci] Adding 2-gpu runner for CI nightly only`
- Author: `geomin12`
- Base: `develop`
- Head: `9e00e16c4e536e7acee322f9da73e44c297a0a05`
- Reviewed: 2026-05-07

## Overall Assessment

No blocking findings from the workflow diff.

The PR is intentionally narrow: it changes the nightly TheRock CI workflow to route Linux `gfx94X-dcgpu` package testing to the new 2-GPU runner label, while leaving `gfx950-dcgpu` present without a test runner. The hard-code bypasses `fetch_package_targets.py`, but the PR labels it as temporary and nightly-only, which matches the stated goal of stabilizing this lane before wiring it through the shared target discovery path.

## Latest Discussion Check

- Latest PR state checked on 2026-05-07.
- Draft: no.
- Existing reviews: one approval from `tony-davis`.
- Top-level comments: none.
- Inline review comments: none.

## Findings

None.

## Design Notes

- The Linux nightly target generation is now hard-coded in [`therock-ci-nightly.yml#L66-L71`](https://github.com/ROCm/rocm-libraries/blob/9e00e16c4e536e7acee322f9da73e44c297a0a05/.github/workflows/therock-ci-nightly.yml#L66-L71) instead of using TheRock's `fetch_package_targets.py`.
- That makes the workflow less adaptive to runner-label or capacity changes, but the TODO explicitly scopes it as temporary runner stabilization work.
- `gfx950-dcgpu` still does not run Linux package tests because the reusable Linux workflow skips that family at [`therock-ci-linux.yml#L150-L156`](https://github.com/ROCm/rocm-libraries/blob/9e00e16c4e536e7acee322f9da73e44c297a0a05/.github/workflows/therock-ci-linux.yml#L150-L156). Keeping it in the nightly target list therefore still exercises the build side without enabling that skipped test lane.
- Current checks show the main TheRock CI summary failing because two `rocBLAS` shards failed on the new Linux `gfx94X-dcgpu` runner lane. Since this PR exists to validate that lane, I would inspect those logs before calling the PR fully ready, but the failures do not by themselves indicate a YAML/design issue in this diff.

## Verification

- Refreshed `origin/develop` and `refs/remotes/pr/7144`.
- Checked PR metadata, latest reviews, top-level comments, and inline comments.
- Reviewed `origin/develop...refs/remotes/pr/7144`.
- Ran `git diff --check origin/develop...refs/remotes/pr/7144`; passed.
- A temporary review worktree creation timed out and left a partial locked worktree, so this review used Git refs directly instead of that worktree.
