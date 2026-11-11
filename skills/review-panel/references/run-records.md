# Source snapshots and run records

Resolve the meta-workspace through the canonical skill location. Store public
review scratch under its ignored `.cache/review-runs/<unique-run-id>/`. Use the
separate private destination for private evidence; `.gitignore` alone is not a
sharing boundary. Never overwrite another run.

For a PR, fetch `url`, `baseRefName`, `baseRefOid`, `headRefName`, `headRefOid`,
and repository identity through the existing authorized GitHub interface.
Use the correct account without changing global login. Local refs must contain
those objects before using the following read-only Git commands.

For a branch, choose the explicit requested base, linked PR base, or confirmed
target branch from repository context. Discover it before asking the user; ask
only when genuinely ambiguous. A tracking upstream may be the topic branch.

```text
git -C <repo> rev-parse --show-toplevel
git -C <repo> status --porcelain=v1 --untracked-files=all
git -C <repo> rev-parse --verify <base-ref>^{commit}
git -C <repo> rev-parse --verify HEAD^{commit}
git -C <repo> merge-base <base-sha> <head-sha>
git -C <repo> diff --stat <merge-base-sha> <head-sha>
git -C <repo> diff --no-ext-diff <merge-base-sha> <head-sha> -- <scope>
```

Quote revision arguments appropriately for the shell. Read from the pinned
objects (`git show <sha>:<path>`) or a stable matching worktree. Do not let a
shared live checkout drift while workers test or inspect it. Relevant dirty or
untracked files can contaminate tests even when `git diff` is pinned: preserve
them and use an isolated snapshot, or disclose the restricted verification.
Do not reset, clean, stash, commit or move user work merely to enable a review.

Use `manifest.json` (or equivalent concise structured data) for:

| Field | Contents |
| --- | --- |
| `run_id`, `started_at`, `deadline` | Unique identity and UTC timestamps |
| `mode`, `repository`, `pr_url` | Review-only/implementation, local checkout, PR if applicable |
| `base_ref`, `base_sha`, `merge_base_sha`, `head_sha`, `scope` | Exact reviewed inputs |
| `worktree_state`, `patch_sha256` | Clean/dirty state and hash if a local patch is captured |
| `reviewers` | Role, report path, completion status and source snapshot |
| `bounds` | At most 4 total agents, 2 rounds, 1 transient retry per worker, 30 minutes by default |
| `rounds`, `curation` | Actual attempts, validation and disposition records |
| `verification`, `usage` | Commands/evidence; measured usage or explicitly unavailable |
| `outcome` | Complete, incomplete or stale; recommendation separately |

Do not fabricate measured usage or write a model name inferred from a persona.
Record actual roles and observed runtime information. Keep raw reports in
separate role/round files. Track each finding's disposition (`confirmed`,
`rejected`, `fixed`, `reopened`, `deferred`, `unresolved`) and supporting reason.
Use the existing `reviews/pr_...md` or `reviews/local_...md` naming for the final
shareable result; preserve earlier results when a fresh review is requested.

For an authorized uncommitted implementation, capture binary-capable tracked
diffs and relevant untracked inputs in private/local scratch, hash the complete
reviewed input set, and make both reviewers use that same state. A tracked diff
alone does not capture untracked files. Prefer a stable committed snapshot when
one already exists; never imply authorization to commit for this purpose.

Before finalizing, recheck HEAD and relevant worktree state, plus the PR's live
base/head if applicable. A changed base can change the diff even with the same
head. Check report identities and curator completion. Scope skips and failed
runs cannot certify coverage. New code needs fresh evidence within the remaining
round/time budget; otherwise mark current review incomplete with the exact gap.
