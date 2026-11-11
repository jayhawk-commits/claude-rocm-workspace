# ROCm Claude/Codex Workspace

A meta-workspace for using Claude Code or Codex to work on
[ROCm/TheRock](https://github.com/ROCm/TheRock) and related projects. This
repository serves as a "control center" that provides centralized context,
tooling, and documentation for AI-assisted development.

## Why a Meta-Workspace?

Build infrastructure work on ROCm involves multiple scattered repositories and
build directories. Rather than making any single ROCm project the AI assistant
workspace, this separate meta-repository:

- Provides centralized context and documentation for Claude Code and Codex
- Maps out where all the various directories live (see
  [`directory-map.md`](/directory-map.md))
- Contains workflows, notes, and helper scripts
- Stays version-controlled without polluting the actual ROCm repositories

## Directory Structure

```
claude-rocm-workspace/
├── CLAUDE.md              # Project context and instructions for Claude Code
├── directory-map.md       # Map of ROCm directories on your system
│
├── tasks/                 # Task management
│   ├── active/            # Currently active tasks
│   └── completed/         # Archived completed tasks
│
├── reviews/               # Code review system
│   ├── README.md          # Quick start guide
│   ├── REVIEW_GUIDELINES.md
│   ├── REVIEW_TYPES.md
│   ├── guidelines/        # Domain-specific review checklists
│   ├── pr_*.md            # PR reviews
│   └── local_*.md         # Local branch reviews
│
├── plans/                 # Implementation plans and design docs
├── reports/               # Audit reports and analyses
│
└── .claude/               # Claude Code configuration
    ├── commands/          # Slash commands (/task, /review-pr, etc.)
    ├── agents/            # Custom subagents (build-infra, ci-pipeline)
    └── settings.json      # Workspace settings
```

Agent guidance and Codex support:

- [`AGENTS.md`](/AGENTS.md) - Repo-local instructions that Codex reads
- [`AI_EFFICIENCY.md`](/AI_EFFICIENCY.md) - Shared model, token-efficiency, and
  automated-workflow guidance for Claude and Codex
- [`scripts/codex.bat`](/scripts/codex.bat) - Codex launcher with the workspace
  Python environment activated

## Key Features

### Code Review System

The [`reviews/`](/reviews/) directory contains a structured code review system.

**Quick start:**
```bash
/review-pr https://github.com/ROCm/TheRock/pull/1234  # Review a PR
/review-branch                                        # Review current branch
/review-branch style tests                            # Focused reviews
```

See [`reviews/README.md`](/reviews/README.md) for full documentation.

For specialist review, use the shared
[`review-panel` skill](skills/review-panel/SKILL.md). It selects a small set of
[personas](reviews/personas.md), records the reviewed revisions, and validates
their findings before producing the normal review. Examples:

```text
Use $review-panel to review this PR with CI and test-evidence personas.
Review my branch against origin/develop using build and packaging specialists.
Use Lisa for the ISA changes and Simone for the simulation timing changes.
```

Install local discovery links for Codex and Claude on Windows:

```powershell
.\scripts\setup-review-panel.ps1
# Also discover the skill when sessions start at the parent workspace:
.\scripts\setup-review-panel.ps1 -SessionRoot (Split-Path -Parent $PWD.Path)
```

The script creates local junctions under `.agents/skills/` and
`.claude/skills/`, pointing to the single tracked `skills/review-panel/`
source. It supports `-WhatIf`, is safe to rerun, and refuses to replace existing
unrelated paths. On systems with symlinks, link those same skill directories
to the canonical source. Restart the agent if a new skill does not appear.
Sibling source repositories may require direct invocation by the canonical
skill path when they do not inherit this workspace's discovery root.

Interactive run artifacts stay in ignored `.cache/review-runs/`; private
references use a separate local destination. For persistent comments and
supervised reviewer/curator processes, the
[Peanut Review harness](tools/peanut-review/LOCAL_SETUP.md) is included under
`tools/peanut-review/`, with [upstream provenance](tools/peanut-review/UPSTREAM.md).
The Windows entrypoint is `scripts/peanut-review.ps1`; it runs in WSL, uses the
same personas, and stores sessions outside source repositories. It requires an
explicit model and effort and does not publish reviews.

Inherited review notes from the source workspace are kept under
[`reviews/reference/inherited/`](/reviews/reference/inherited/). They remain
available as reference material, but are separated from review work produced in
this workspace.

### Codex Support

Codex reads [`AGENTS.md`](/AGENTS.md) automatically when working in this repo.
That file points Codex at the same task and review system while translating
Claude-specific pieces, such as slash commands and subagent notes, into Codex's
workflow.

Codex does not execute the Claude slash commands directly. Use natural-language
requests instead:

```text
Review PR https://github.com/ROCm/TheRock/pull/1234
Review my current branch with focus on tests and CI
Switch to task multi-arch-prebuilt
```

### Task Management

Track and switch between multiple tasks without losing context.

**Commands:**
```bash
/task task-name                    # Switch to a task
```

**Workflow:**
1. Create `tasks/active/your-task.md` (use
   [`example-task.md`](/tasks/example-task.md) as template)
2. Switch with `/task your-task` or "I'm working on your-task"
3. Move to `tasks/completed/` when done

### Custom Agents

Domain-specific subagents in [`.claude/agents/`](/.claude/agents/):

| Agent | Purpose |
|-------|---------|
| [`build-infra`](/.claude/agents/build-infra.md) | CMake, meson, pkg-config, ROCm build patterns |
| [`ci-pipeline`](/.claude/agents/ci-pipeline.md) | GitHub Actions, CI/CD workflows |

### Slash Commands

Available commands in [`.claude/commands/`](/.claude/commands/):

| Command | Description |
|---------|-------------|
| [`/task <name>`](/.claude/commands/task.md) | Switch to a task |
| [`/review-pr <URL>`](/.claude/commands/review-pr.md) | Review a GitHub PR |
| [`/review-branch`](/.claude/commands/review-branch.md) | Review current local branch |
| [`/wip`](/.claude/commands/wip.md) | Quick WIP commit |

## Setup

1. Clone this repository
2. Update `directory-map.md` with your actual directory paths
3. Customize `CLAUDE.md` and `AGENTS.md` with your project-specific context
4. Set up the Python environment (see below)
5. Run Claude Code or Codex using the launcher script

### Python Environment

A Python virtual environment ensures tools like `pytest` are available when
Claude or Codex runs commands.

**One-time setup (Windows):**
```powershell
cd C:\Dev\claude-rocm-workspace
py -V:3.12 -m venv 3.12.venv
.\3.12.venv\Scripts\activate.bat
pip install -r ..\TheRock-pub\requirements.txt
```

If the Windows Store `python` alias or the `py` launcher is unavailable in the
sandbox, use a workspace-local Python install instead:

```powershell
.\scripts\setup-python.ps1
```

**Launching Claude:**
```powershell
.\scripts\claude.bat
```

**Launching Codex:**
```powershell
.\scripts\codex.bat
```

The launcher scripts activate the venv before starting the assistant, so Python
tools are available in the session.

## Adapting for Your Project

This workspace pattern can be adapted for any multi-repository project:

1. Fork this repository
2. Replace ROCm-specific content in `CLAUDE.md` and `AGENTS.md`
3. Update `directory-map.md` for your environment
4. Customize the review guidelines for your project's conventions
5. Add task templates relevant to your work
