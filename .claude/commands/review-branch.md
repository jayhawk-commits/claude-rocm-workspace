---
description: Review the current local branch
allowed-tools: Bash(git:*), Read, Write, Glob, Grep, Task
argument-hint: [--base <ref>] [review-type ...]
---

Review local branch changes using the workspace's evidence and output conventions.
A review request authorizes local review artifacts, not implementation or commits.

## Arguments

- `$ARGUMENTS`: `[--base <ref>] [review-type ...]`.
- Optional types: `style`, `tests`, `documentation`, `architecture`, `security`,
  `performance`; absent a focus, review relevant aspects of the whole change.
- Explicit personas or substantive changes crossing domain boundaries can use
  the [review panel](../../skills/review-panel/SKILL.md). Keep small focused
  reviews lightweight.

## Establish the Reviewed Snapshot

Determine the target repository and inspect its state without changing it:

```bash
git branch --show-current
git status --short
git rev-parse HEAD
```

Resolve the intended base from `--base`, the user's task, or PR/repository context.
A tracking branch can be the feature branch itself and is not automatically the
review base. Do not assume `main`. Ask only if the base remains ambiguous after
checking available context.

Freeze the actual target base and head SHAs, then compute the merge base:

```bash
git rev-parse <base-ref>
git merge-base <base-sha> <head-sha>
git log --oneline <merge-base-sha>..<head-sha>
git diff --stat <merge-base-sha> <head-sha>
git diff <merge-base-sha> <head-sha>
```

Run from the target repository, or use `git -C <repository>` from the workspace.
Record all three SHAs; use this immutable range for every reviewer. Read committed
source from that head, separately from any requested working-tree snapshot. If no merge
base is available, explain the missing history rather than guessing a range.

Do not silently omit requested uncommitted changes. For a request about the
working tree, also capture staged and unstaged patches and the requested untracked
files as a separate snapshot; record their scope and whether it changed during
review. Never commit, reset or clean the worktree just to prepare a review.

## Review Setup

- Read `reviews/README.md`, `reviews/REVIEW_GUIDELINES.md`, and relevant target
  repository instructions. Read focus/domain guidelines only as needed.
- Scan `reviews/local_*.md` for the next counter (001, 002, etc.). Preserve review
  history for a re-review instead of overwriting unrelated work.
- Replace `/` in the branch label with `-` and sanitize other filename-invalid
  characters for the host OS. Use a descriptive snapshot label for detached HEAD.
- Save `reviews/local_{COUNTER}_{branch-name}.md`, or append `_{TYPE}` for a
  focused review.
- For a panel, follow its selection, run records and completion rules; see
  [personas](../../reviews/personas.md). Do not start an unbounded reviewer lineup.

## Review and Reconcile

Trace the changed behavior through callers and consumers, compare base and head,
and use relevant tests or CI to confirm or reject candidate findings. Focus on
actual consequences and applicable requirements, not speculative cleanup.

For multiple focus areas, combine supported findings in one report. If separate
reviewers are useful, give them the same frozen inputs and reconcile their results
using the review-panel workflow. Do not treat repeated opinions as independent
evidence or a skipped/failed review as approval.

Before delivery, recheck the base ref, HEAD and any included worktree snapshot. If they changed,
review the relevant new changes and repair anchors, or state that the result
applies only to the recorded snapshot. Preserve other sessions' edits.

## Deliver the Review

Follow `reviews/REVIEW_GUIDELINES.md`: actionable findings in severity order,
recommendation to approve/request changes/wait for specific evidence, exact paths
and current lines outside concise copy-pastable comment blocks, and a separate
overall review comment. Record the base, merge-base, head, scope, verification and
limits. Working-tree-only lines must be labeled as such rather than called GitHub
diff anchors. Report the file location and meaningful unresolved issues.

## Examples

```text
/review-branch
/review-branch --base origin/develop tests security
Review my branch with the build and packaging persona against origin/main.
```
