---
name: review-panel
description: Coordinate scoped persona reviews of PRs or local changes when independent specialist review is requested or a substantive change spans multiple domains.
---

# Review panel

Use the current agent runtime and its available delegation tools for an
interactive panel. Ordinary focused reviews can use one relevant persona
without starting a panel. For persistent findings, process supervision and
repeatable curation, use the installed
[Peanut Review harness](../../tools/peanut-review/LOCAL_SETUP.md). Both routes
use the persona references below. Preserve the authorized model/provider.

Resolve this skill's symlink/junction to its canonical directory first. The
meta-workspace is two parents above that directory. Read its
`reviews/README.md`, `reviews/REVIEW_GUIDELINES.md`, and `AI_EFFICIENCY.md`, plus
the target repository's applicable instructions. Current user instructions and
workspace review defaults take precedence over older templates.

## Select the scope

- Identify the target repository, review-only or authorized implementation
  mode, intended base, and current head. Never assume `main` or treat an
  upstream tracking branch as the PR base without checking.
- Read [run records](references/run-records.md) for snapshot commands, artifact
  fields and completion rules. Freeze the merge-base and head before dispatch.
  Dirty changes need a separately captured patch or a clearly labeled focused
  working-tree review; do not present them as a committed panel snapshot.
- Start with two complementary reviewers. Add a third only for a distinct
  uncovered risk, within the runtime's remaining slots. Count the coordinator
  toward a maximum of four concurrent agents. If delegation is unavailable,
  report that limitation and perform a focused review without claiming an
  independent panel.
- Keep the current authorized model/runtime. Persona names describe focus,
  not model identity or proven expertise. Do not silently change configured
  providers or model selections.

Read only the selected references:

| Change | Persona |
| --- | --- |
| Workflows, runner routing, matrices | [CI contracts](references/personas/ci-contracts.md) |
| CMake, dependencies, installation, artifacts | [Build and packaging](references/personas/build-packaging.md) |
| Behavioral changes, test quality, disputed evidence | [Test evidence](references/personas/test-evidence.md) |
| Manifests, schemas, cross-repository compatibility | [Release contracts](references/personas/release-contracts.md) |
| ISA, numerical behavior, runtime synchronization | [GPU ISA / Lisa](references/personas/gpu-isa.md) |
| Simulation, event ordering, timing fidelity | [GPU modeling / Simone](references/personas/gpu-modeling.md) |

## Review and reconcile

1. Create a local run directory and per-worker scratch directories before
   dispatch; a tool's working directory must already exist. Record the snapshot and selected roles.
   Give each reviewer [the worker contract](references/worker-contract.md),
   its persona, the task and frozen source inputs. Prefer fresh child context;
   do not seed the first pass with another reviewer's conclusions. Each worker
   writes only its own report/scratch or returns its report to the coordinator.
2. Review workers do not edit source, commit, resolve remote threads or publish.
   Retain existing sandbox/approval controls. Prompt restrictions do not create
   filesystem isolation; do not claim otherwise. Use per-worker scratch for
   tests and keep the source checkout stable during a round.
3. The coordinator curates after the selected reviewers finish: verify actual
   callers and consumers, compare the base, check relevant tests/CI, merge
   duplicates, and record reasons for rejected or unresolved findings. Reviewer
   agreement alone is not evidence. Preserve material disagreements and
   distinguish introduced defects, existing behavior and follow-up work.
4. Verify the snapshot again and, for a PR, re-fetch its head/base metadata
   before preparing current inline anchors. If it changed, mark results stale;
   re-review the affected scope within the remaining bounds or report that
   current-head review is incomplete. Do not silently relabel an old result.
5. Produce the workspace's normal concise review: actionable findings first,
   exact current diff locations, copy-pastable comments in the user's voice,
   a separate short overall comment, and verification/limitations outside it.
   Save only public-supported content in shareable review artifacts.

## Bounds and iteration

This is an interactive workflow. Default to one initial round, at most one
follow-up round, a 30-minute overall review budget, and one retry per worker
for a transient runner failure. Count head changes and failed attempts against
the same budget. Use shorter bounds if requested, and check elapsed time
before dispatching or retrying. At the limit, stop launching work and report
unresolved findings or incomplete coverage; never turn exhaustion into approval.
These are coordinator-enforced workflow bounds, not a process watchdog or a
spend cap. Do not schedule unattended runs with this skill alone.

For a harness run, use `scripts/peanut-review.ps1` from the meta-workspace.
Its local profile enforces launch, concurrency and wall-clock bounds and waits
for both reviewers and curator. It requires a clean committed snapshot and
an explicit model and effort; capture uncommitted work separately or use the
interactive route. A completed harness run is still subject to the evidence
and freshness checks above. Inspect surviving comments and the curation ledger
before preparing the normal author-facing review. Runtime limits are not a
token or spend cap. Do not bypass the local profile with upstream runner or
publication commands.

For author-owned changes, fixes are allowed only within existing implementation
authorization. After review workers finish, fix or rebut surviving findings,
run proportionate verification, capture the new state and re-review affected
behavior. Commit only when already authorized; this skill never requires a
commit or authorizes publishing. Preserve finding IDs and fix/rebuttal history.
An uncommitted fix needs a recorded patch and explicit coverage limits rather
than a false clean-head approval.

Completion requires the selected relevant reviewers and the coordinator to
finish against the recorded source state. Skipped, failed, stale or incomplete
reviews are not approval evidence. If a separate curator is used, wait for its
completion too. Prefer deterministic tests or authoritative source evidence to
another model vote.

## Private references

For a task that needs private domain evidence, read the meta-workspace's
`LOCAL_CONTEXT.md` if present to locate optional local routing. Use it only for
relevant authorized sources. Keep routing locations, source revisions and private evidence in the
private local destination specified by that routing. Do not preload a knowledge
base or copy its contents into personas. Public findings require independent
public evidence; removing names from a private-derived finding is insufficient.
If reference access is unavailable, report the evidence gap and continue the
parts of the review that do not depend on it.
