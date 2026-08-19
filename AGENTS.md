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

- Treat private/NPI repositories, source trees, logs, branches, paths, aliases,
  and identifiers as confidential context. It is OK to inspect and use them
  inside this local workspace when they are relevant to the task, and workspace-
  local inventory files may record local aliases or paths for navigation. Do
  not quote, copy, or disclose NPI-only source, private workspace paths or
  aliases, internal branch names, non-public links or logs, or implementation
  details in user-facing output, review files, commits, PRs, or public
  artifacts. Public repository paths/worktrees are not NPI by themselves and may
  be recorded when useful; prefer repository-relative paths in shareable
  artifacts for portability.
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

## AI Efficiency And Workflow Control

- Use the most capable reasoning available for architecture, orchestration,
  cross-document synthesis, and constraint-heavy analysis. When model routing
  is available, use lighter models for routine implementation, extraction,
  formatting, classification, and bulk operations. For GPU kernel, assembly,
  ISA, RTL, and formal-verification work, prioritize demonstrated correctness
  over model downgrades.
- Optimize for end-to-end cost and quality, including context replay, retries,
  and rework. A cheaper generation model is not necessarily cheaper overall.
- Read large or unchanged files once when practical. Use targeted searches,
  retain concise findings, and summarize completed tool output instead of
  repeatedly replaying full logs or file contents.
- For long-running tasks, checkpoint a compact state summary before context is
  roughly half full. Prefer small state files or task notes over full transcript
  dumps, and continue from the checkpoint rather than reconstructing history.
- When authoring LLM prompts, put stable instructions, tool definitions, and
  examples before history and dynamic user data. If cache metrics are available,
  target a prompt-cache hit rate above 70% and investigate rates below 60%.
- Bound output explicitly when the interface supports it. Set max_tokens, a
  response-size target, and a concrete output format; request only the fields,
  changed lines, or artifact needed by the next step.
- Keep the active MCP/tool surface specific to the task. Trim oversized tool
  descriptions and prefer search-based or deferred loading when a workflow
  would otherwise expose roughly 30--40 or more tools.
- Enable extended thinking or high reasoning effort deliberately, with a stated
  budget or level. Compare it with a lighter setting before making it the
  default for a repeated or automated workflow.
- Automated workflows must define stopping conditions and ceilings for steps,
  wall-clock time, exploration, retries, and concurrent agents. Use exponential
  backoff with a maximum retry count; never retry indefinitely.
- Add cost/usage telemetry and a circuit breaker for repeated workflows when
  practical. Pause and surface anomalous runs rather than silently consuming
  several times the normal baseline.
- Require dry-run support and an explicit human approval point before automated
  commits, broad file writes, deployments, or other consequential actions.
- Do not rely on the same model instance to grade its own consequential output.
  Use deterministic checks, an independent reference, or a genuinely independent
  review pass, and break long chains into separately verifiable stages.

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
