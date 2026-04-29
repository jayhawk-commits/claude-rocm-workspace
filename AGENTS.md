# Codex Instructions for This Workspace

This repository is a meta-workspace for ROCm build infrastructure work. The
source repositories usually live beside this repo, not inside it. Start by
reading `directory-map.md`, then open the relevant task, review, or plan docs.

`CLAUDE.md` remains the broad domain context for this workspace. Use it for
ROCm and review-system knowledge, but adapt Claude-specific mechanics to Codex:

- Claude slash commands in `.claude/commands/` are workflow recipes for Codex.
  Treat requests like `/review-pr`, `/review-branch`, `/task`, and `/wip` as
  natural-language instructions, not as commands Codex can execute directly.
- Claude subagents in `.claude/agents/` are specialist notes. Read them when
  they match the task. Do not spawn Codex subagents unless the user explicitly
  asks for delegated or parallel agent work.
- Output styles under `.claude/output-styles/` are Claude-specific. Follow the
  user's current tone and the normal Codex response rules.

## Workspace Rules

- Check the active repository with `git status --short` before editing.
- Never revert, reset, amend, push, or force-push unless the user explicitly
  asks for that operation.
- Prefer relative paths in commands and patches where practical. When reporting
  changed files, use clickable absolute links.
- Use `rg`/`rg --files` for searches.
- Use `git -C <path>` when operating on sibling ROCm repositories from this
  meta-workspace.
- Run Git operations sequentially. Do not use parallel tool calls for `git`
  staging, committing, worktree, fetch, push, or PR-related commands, even when
  they target different worktrees. On this Windows sandbox, parallel Git can
  collide on locks or abort with pipe/signal errors and make progress look
  stalled.
- Avoid long ROCm builds unless the user asks for them or confirms the scope.
  Configure and inspect first; build the smallest useful target.

## GitHub And Network Access

The Codex sandbox may block outbound sockets and may not see the Windows
keyring token used by `gh`. If a sandboxed `gh` or remote Git command fails with
a socket or auth error, rerun the same operation with sandbox escalation instead
of trying to work around the sandbox.

Useful checks:

```powershell
gh auth status
gh api user --jq .login
git -C C:\Dev\TheRock-pub ls-remote --exit-code origin HEAD
```

## Review Workflow

For PR reviews, follow `reviews/README.md`, `reviews/REVIEW_GUIDELINES.md`, and
`reviews/REVIEW_TYPES.md`.

- Fetch PR metadata with `gh pr view <URL> --json ...`.
- Fetch diffs with `gh pr diff <URL>`.
- When available, use CI evidence from `gh api`/`gh run` to confirm or reject
  hypotheses from the diff.
- Write the result to `reviews/pr_{REPO}_{NUMBER}.md` or a focused
  `reviews/pr_{REPO}_{NUMBER}_{TYPE}.md`.

For local branch reviews:

- Determine the target repository and base branch before diffing.
- Use the next `reviews/local_{COUNTER}_{branch-name}.md` name.
- Lead with findings, ordered by severity, with precise file/line references.

## Task Workflow

Tasks live under `tasks/active/` and `tasks/completed/`. When the user switches
tasks, read the task file, note any `repositories:` frontmatter, and summarize
status, blockers, and likely next steps before changing code.

## Commit Attribution

Do not add the Claude Code commit footer from `CLAUDE.md` to Codex-generated
commits. If the user asks Codex to commit and wants AI attribution, ask which
footer style they prefer before committing.
