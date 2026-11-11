---
description: Review a GitHub pull request
allowed-tools: Bash(gh:*), Bash(git:*), Read, Write, Glob, Grep, WebFetch, Task
argument-hint: <PR_URL> [review-type ...]
---

Review the requested PR using the workspace's evidence and output conventions.
A review request authorizes local review artifacts, not source edits or publishing.

## Arguments

- `$ARGUMENTS`: `<PR_URL> [review-type ...]`.
- Optional types: `style`, `tests`, `documentation`, `architecture`, `security`,
  `performance`; absent a focus, review the relevant aspects of the whole change.
- Explicit personas or a substantive change crossing domain boundaries can use
  the [review panel](../../skills/review-panel/SKILL.md). Keep small focused
  reviews lightweight; multiple requested types do not require extra agents.

## Establish the Reviewed Snapshot

Fetch PR metadata using the intended repository identity:

```bash
gh pr view <URL> --json number,title,author,body,files,additions,deletions,state,baseRefName,baseRefOid,headRefName,headRefOid
gh pr diff <URL>
```

Record target base and head SHAs. Since metadata and diff are separate reads,
re-read both SHAs after retrieval; retry with fresh inputs if they moved. When
using a checkout, verify it contains the recorded objects, compute the merge base
with `git merge-base <base-sha> <head-sha>`, and inspect
`git diff <merge-base-sha> <head-sha>`. Use the same frozen inputs for all reviewers.
Read supporting source with `git show <head-sha>:<path>` or from a checkout
verified to match that head without conflicting local edits. Do not reset or
overwrite local work to match the PR. If the diff is truncated or
required source is unavailable, record that scope limit rather than implying a
complete review.

## Review Setup

- Read `reviews/README.md` and `reviews/REVIEW_GUIDELINES.md`; read
  `reviews/REVIEW_TYPES.md` and domain guidelines only as relevant.
- Read applicable instructions in the target repository.
- Use `reviews/pr_{REPO}_{NUMBER}.md`, or append `_{TYPE}` for a focused review.
  Preserve existing review history when updating a previous report.
- For a panel, use its selection, run-record and completion workflow instead of
  launching ad hoc unbounded reviewers. See [personas](../../reviews/personas.md).

## Gather Evidence and Review

Trace changed contracts through actual callers and consumers. Compare base and
head to separate regressions from existing issues or source-data problems.
Review correctness, applicable conventions, tests and affected domain contracts;
do not manufacture findings for unaffected areas.

Discover relevant CI runs from the PR or workflow history. Verify the source SHA,
trigger and configuration before using a result as evidence. Compare a suitable
baseline on the actual target branch, not an assumed `main` branch. For example:

```bash
gh api repos/OWNER/REPO/actions/jobs/JOB_ID \
  --jq '{name, steps: [.steps[] | {name, conclusion, started_at, completed_at}]}'
```

Passing CI supports only exercised paths. Read logs or artifacts when timings or
statuses do not resolve a hypothesis. Source-level evidence can establish a bug
without CI; an untested possibility should remain an evidence gap.

## Deliver the Review

Re-read `baseRefOid` and `headRefOid` before delivery. If either changed, reconcile
the changed diff and current anchors, or clearly label the report as an earlier
snapshot and wait for the necessary re-review. Do not call stale lines current.

Follow the concise template in `reviews/REVIEW_GUIDELINES.md`:

- Lead with actionable findings in severity order and a recommendation to approve,
  request changes, or wait for named evidence.
- Record repository/PR, base, merge-base when available, reviewed head, date, scope
  and verification. State missing merge-base/source evidence when using API-only
  review instead of a checkout.
- Put exact repository-relative paths and current diff lines outside fenced
  `markdown` blocks. Each block contains only a one- or two-sentence posting
  comment, preserving literal backticks around identifiers.
- Include a separate concise overall review comment. Keep tests and caveats
  outside it unless the author needs them to assess the change.
- Report the review file location. Do not post comments or change PR state unless
  the user has authorized that action.

## Examples

```text
/review-pr https://github.com/ROCm/TheRock/pull/2761
/review-pr https://github.com/ROCm/TheRock/pull/2761 tests security
Review this PR with the CI contracts and test evidence personas.
```
