# TheRock Submodule Bump Initiative Workplan

Date: 2026-05-27

## Summary

The goal is to improve the turnaround time and reliability of TheRock
`rocm-libraries` and `rocm-systems` submodule bumps. Bump PRs are already
created automatically twice per day, and the team already has a rotation for
watching them. The bottleneck is after creation: deciding whether each bump can
merge, whether red CI is caused by the bump, and whether the super-repo CI
signal is trustworthy.

Within one month, the team should make routine bumps same-day decisions:

- every scheduled bump candidate gets reviewed and dispositioned the day it
  opens;
- non-regressing candidates merge once actionable CI signal exists;
- known failures are allowed through only when categorized, owned, scoped, and
  time-limited;
- stale or superseded bump PRs are closed quickly;
- pinned TheRock refs remain the stability model for super-repos, but they are
  complete, current, and easy to audit;
- routine `rocm-libraries` bumps get faster CI by reusing unchanged prebuilt
  stages and skipping unrelated tests where safe;
- recurring CI failures are turned into owned issues or fixes instead of being
  re-triaged on every bump.

The four engineers should work as two pairs:

| Pair | Focus | Goal |
| --- | --- | --- |
| Pair 1 | Decision throughput | Make every bump PR quickly decidable. |
| Pair 2 | CI turnaround and signal quality | Make routine bump CI faster, quieter, and easier to trust. |

The pair split is intentional. The work inside each pair is tightly connected,
so the plan should avoid making four artificial silos.

## Current Starting Point

The existing automation is a strong base:

- TheRock creates scheduled `rocm-libraries` and `rocm-systems` bump PRs twice
  per day.
- Bump automation can also be run manually.
- A rotation already watches bump PRs.
- TheRock multi-arch CI already has concepts like `prebuilt_stages`,
  `baseline_run_id`, and `external_repo`.
- Super-repos already use pinned TheRock refs for stability.
- Super-repos already have TheRock CI workflows, path filtering, and source
  overlay support.

The remaining gaps are:

- red CI often waits too long for classification;
- recurring failures are not always categorized consistently;
- accepted red CI needs stronger owner, scope, issue, and expiry hygiene;
- stale bump PRs and stale TheRock ref PRs need faster cleanup;
- super-repo CI needs clearer proof of which source and TheRock ref were
  tested;
- routine bumps still rebuild and retest unchanged work;
- queue-time savings are not yet measured.

## Pair 1: Decision Throughput

### Mission

Make every bump PR quickly decidable.

This pair owns the operating model for the bump train: daily status, PR
disposition, issue categories, accepted-red hygiene, stale PR cleanup, and
recurring failure burn-down. The existing monitoring rotation stays in place;
this pair makes that rotation easier to operate.

### Responsibilities

#### Bump Train Operations

Each bump PR should end the day in one of these states:

- ready to merge;
- accepted red with tracked follow-up;
- blocked by a real regression;
- waiting on actionable CI;
- superseded by a newer candidate.

Suggested disposition labels:

- `bump:ready`
- `bump:accepted-red`
- `bump:blocked`
- `bump:superseded`

The pair should also keep stale bump PRs under control. Close or supersede
older bump candidates when:

- a newer bump contains the same or newer submodule commits;
- a bump lands and older candidates are no longer useful;
- a candidate is blocked by an upstream issue and a cleaner candidate exists.

#### Failure Categorization

Use one primary category per failure cluster:

| Category | Meaning |
| --- | --- |
| `ci:infra-flake` | Runner, cache, network, artifact, or GitHub Actions problem. |
| `ci:known-unrelated` | Known issue that is not caused by this bump. |
| `ci:bump-regression` | The new submodule SHA caused a real failure. |
| `ci:false-green-risk` | CI may not be testing the intended source. |
| `ci:false-red-routing` | CI ran an irrelevant job or used bad routing. |
| `ci:workflow-hygiene` | Stale ref, mutable ref, wrong SHA, or workflow drift. |

Each accepted red failure should have:

- category;
- owner;
- tracking issue;
- affected repo and component;
- first seen date;
- expiry or review date;
- evidence that it is unrelated to the bump.

#### Recurring Failure Burn-Down

The pair should classify failures from recent relevant bump PRs and build a
short recurring-failure backlog. For the highest-cost failures, the pair should
either:

- prepare a fix;
- route the issue to the right owner;
- file a clear rocm-libraries, rocm-systems, or TheRock issue;
- document why an accepted red is safe and when it expires.

Priority failure types:

- recurring infrastructure flakes;
- flaky or pre-existing tests blocking unrelated bumps;
- false red routing where CI runs irrelevant jobs;
- failures that need rocm-libraries or rocm-systems issues;
- failures where TheRock needs a local workflow or dependency fix.

#### Ref Hygiene

Pinned TheRock refs are intentional and should stay. The pair should make sure
the team can see:

- which TheRock ref each super-repo bump is using;
- whether a ref update PR is stale;
- whether duplicate ref/hash PRs should be closed;
- whether ref propagation missed a known location.

### Deliverables

- Daily bump checklist.
- Disposition labels.
- CI category and label proposal.
- Known-failure ledger.
- Current failure-cluster report.
- Stale bump PR and stale ref PR cleanup rules.
- Daily bump status template.

### Done When

- Every bump candidate gets same-day attention.
- Red bump PRs can be categorized within an hour of actionable CI.
- Accepted red CI has owner, issue, scope, and expiry.
- Superseded bump PRs are closed quickly.
- Repeat failures are not rediscovered from scratch on every bump.

## Pair 2: CI Turnaround And Signal Quality

### Mission

Make routine bump CI faster, quieter, and easier to trust.

This pair owns the CI impact model, prebuilt baseline reuse, workflow
integration, test impact mapping, source-overlay guardrails, and timing
measurement.

### Responsibilities

#### CI Impact Model

Build the shared model that tells CI what a change can affect. This should live
in TheRock and should not be duplicated in each super-repo.

Suggested file:

- `build_tools/_therock_utils/topology_impact.py`

Suggested functions:

- `map_changed_files_to_source_sets(...)`
- `map_source_sets_to_artifact_groups(...)`
- `map_artifact_groups_to_build_stages(...)`
- `compute_stage_impact(...)`
- `format_stage_impact_summary(...)`

The stage impact interface should be stable early:

```text
changed_paths
affected_source_sets
rebuild_stages
copy_stages
full_rebuild_required
reasons
```

Fall back to full CI when:

- changed paths are ambiguous;
- build tooling changed;
- `BUILD_TOPOLOGY.toml` changed;
- workflow files changed;
- source-set ownership cannot be proven.

#### Prebuilt Baseline Reuse

Build the code that finds a safe previous workflow run and reuses artifacts for
unchanged stages.

Suggested file:

- `build_tools/github_actions/baseline_runs.py`

Suggested functions:

- `select_last_successful_baseline_run(...)`
- `validate_baseline_artifacts(...)`
- `validate_platform_and_gpu_families(...)`
- `resolve_copy_prebuilt_plan(...)`

A valid baseline should match workflow, branch or ref policy, platform, GPU
targets, required artifact groups, relevant SHAs, and successful conclusion.

Start with opt-in behavior through a label, workflow input, or repository
variable. Fall back to full CI when no safe baseline exists.

#### Test Impact Mapping

Identify test noise that should not block routine bumps. For pure
`rocm-libraries` bumps, classify tests that are owned by unchanged systems,
media, profiler, debug, or communication stages.

Examples to classify carefully:

- `hip-tests`
- `rocrtst`
- `rocprofiler-sdk`
- `rocprofiler-compute`
- `rocprofiler-systems`
- `aqlprofile`
- `rocgdb`
- `rocr-debug-agent`
- `rocdecode`
- `rocjpeg`
- `rccl`

Suggested file:

- `build_tools/github_actions/test_impact.py`

Suggested functions:

- `map_stages_to_test_components(...)`
- `map_artifacts_to_test_components(...)`
- `compute_test_matrix_filter(...)`
- `format_test_impact_summary(...)`

Test filtering should start as dry-run output, then become opt-in. It should
become default only after ownership and dependency mapping are clear.

#### Super-Repo Signal Guardrails

Super-repo CI should show:

- the intended super-repo PR source;
- the intended pinned TheRock ref;
- the resolved TheRock SHA;
- the source overlay path;
- the submodule fetch or skip mode.

The super-repos can detect changed subtrees or pass changed paths, but the
build topology logic should live in TheRock.

Relevant files:

- `rocm-libs-pub/.github/scripts/therock_configure_ci.py`
- `rocm-libs-pub/.github/scripts/therock_matrix.py`
- `rocm-sys-pub/.github/scripts/therock_configure_ci.py`
- `rocm-sys-pub/.github/scripts/therock_matrix.py`

#### Timing And Savings Measurement

The next savings report should include queue time as well as execution time.
Persist:

- workflow run and attempt;
- job name;
- stage or test family;
- runner label;
- `queued_at`;
- `started_at`;
- `completed_at`;
- whether the job was rebuilt, copied, skipped, or forced.

### Deliverables

- Stage impact helper.
- Full-CI fallback rules.
- Dry-run impact summary.
- Baseline run selector.
- Opt-in prebuilt stage reuse.
- Test impact mapping prototype.
- Super-repo source/ref summary.
- Queue-time and execution-time timing data.
- Savings report update.

### Done When

- CI can explain which stages a bump affects and why.
- Eligible `rocm-libraries` bumps can reuse safe prebuilt stages.
- Ambiguous changes fall back to full CI.
- Super-repo CI shows which TheRock ref and source overlay were tested.
- Test filtering decisions are backed by ownership and dependency mapping.
- The next report can show execution-time and queue-time savings.

## Weekly Plan

### Week 1: Make Current Bumps Decidable

Pair 1:

- Start the daily bump status.
- Define disposition labels.
- Apply issue categories to recent relevant bump PR failures.
- Start the known-failure ledger.
- Identify the highest-cost recurring failure clusters.
- Draft the first test-noise inventory.
- Inventory stale bump PRs and stale TheRock ref/hash PRs.

Pair 2:

- Draft the stage-impact interface.
- Prototype changed-path to source-set and stage mapping.
- Define full-CI fallback triggers.
- Draft baseline validation rules.
- Identify how to select a safe previous workflow run.
- Add or design timing fields for queue-time measurement.
- Draft super-repo source/ref summary output.

Week 1 target:

- Current bump failures are categorized.
- The bump rotation has a daily status format.
- CI impact and baseline interfaces are agreed.
- The team knows the top recurring failure clusters.

### Week 2: Make The Process Repeatable

Pair 1:

- Run the daily bump status process.
- Ensure every red bump candidate has a category or linked categorized issue.
- Close superseded candidates quickly.
- Produce the first recurring failure report.
- Route or fix the highest-cost failure clusters.
- File clean follow-up issues for new rocm-libraries, rocm-systems, or TheRock
  failures.
- Validate accepted-red entries have owner, scope, and expiry.

Pair 2:

- Add dry-run stage impact output to CI.
- Show rebuild, copy, skip, and fallback reasons.
- Add baseline selection and validation prototype.
- Add source-overlay and pinned-ref summary output.
- Start recording timing fields needed for queue-time savings.
- Start test impact mapping in dry-run form.

Week 2 target:

- Bump PR decisions use consistent categories.
- CI stage decisions are visible before they change behavior.
- Super-repo CI starts proving what it tested.

### Week 3: Enable Safe Opt-In Improvements

Pair 1:

- Enforce same-day disposition for routine candidates.
- Track merge, block, accepted-red, and superseded counts.
- Keep stale bump and ref/hash PRs under control.
- Land fixes or issue follow-ups for top recurring failures.
- Confirm which unrelated tests can be skipped for pure `rocm-libraries` bumps.
- Report which failures still create the most triage delay.

Pair 2:

- Harden stage impact rules from dry-run results.
- Enable opt-in prebuilt stage reuse for eligible `rocm-libraries` bumps.
- Add opt-in test filtering only where ownership and dependency mapping are
  clear.
- Fall back to full CI on risky or ambiguous baseline choices.
- Record execution-time and queue-time data from opt-in runs.

Week 3 target:

- Eligible `rocm-libraries` bumps can use faster CI by opt-in.
- The team has cleaner evidence for unrelated failures.
- Queue-time and runner usage data starts becoming available.

### Week 4: Make The Routine Sustainable

Pair 1:

- Finalize the bump-train runbook.
- Finalize stale PR and ref/hash cleanup policy.
- Publish recurring failure trends.
- Recommend the next highest-value CI noise reduction.
- Confirm accepted-red hygiene is being enforced.
- Report whether same-day disposition is being met.

Pair 2:

- Recommend whether eligible `rocm-libraries` bumps should use prebuilt reuse
  by default.
- Recommend whether test filtering should become default for eligible cases.
- Publish the next savings report with execution-time and queue-time data.
- Confirm super-repo source/ref guardrails are in place.
- Finalize stage/test impact documentation and fallback behavior.

Week 4 target:

- Routine bumps have a clear daily process.
- Faster CI is either default for eligible cases or ready for default
  enablement.
- Recurring failure categories and metrics are part of normal bump review.
- Super-repo CI is easier to audit.

## Shared Interfaces

### Bump Decision Record

```text
pr_number
repo
old_sha
new_sha
ci_status
failure_category
linked_issue
owner
disposition
expiry
```

### Stage Impact Result

```text
changed_paths
affected_source_sets
rebuild_stages
copy_stages
full_rebuild_required
reasons
```

### Baseline Result

```text
baseline_run_id
baseline_commit
baseline_workflow
copied_stages
required_artifact_groups
validation_status
fallback_reason
```

### Super-Repo Signal Record

```text
super_repo
super_repo_pr_sha
therock_ref
therock_sha
overlay_path
submodule_fetch_mode
workflow_path
```

### Timing Result

```text
job_name
runner_label
stage_or_test_family
queued_at
started_at
completed_at
decision
```

## Guardrails

- Pinned TheRock refs remain the stability model for super-repo CI.
- Optimized CI paths must fall back to full CI when inputs are ambiguous.
- CI summaries must explain rebuilt, copied, skipped, and fallback decisions.
- Accepted red CI must have category, owner, issue, scope, and expiry.
- Super-repos should not duplicate TheRock build topology logic.
- Test filtering should not become default until test ownership and dependency
  mapping are clear.
- Queue-time and execution-time savings should be measured separately.

## Success Criteria

By the end of the month:

- 95 percent of red bump PRs are categorized within 1 hour of actionable CI.
- Non-regressing bump PRs get same-day merge or same-day explicit disposition.
- Accepted red failures have owner, tracking issue, scope, and expiry.
- Superseded bump PRs are closed quickly.
- Pinned TheRock ref propagation is complete and auditable.
- Super-repo CI shows which TheRock ref and source overlay were tested.
- Eligible `rocm-libraries` bumps can reuse safe prebuilt stages.
- Unrelated test noise is reduced or clearly identified for removal.
- The next report shows execution-time savings, queue-time savings, and failure
  noise trends.
