# TheRock Submodule Update Cadence Plan

Date: 2026-05-19

Scope: improve turnaround time for TheRock `rocm-libraries` and `rocm-systems` submodule bumps within one month, using roughly four people in parallel, with the goal of supporting daily, multiple bump attempts and same-day merge or rejection decisions.

## Executive Summary

TheRock already creates `rocm-libraries` and `rocm-systems` bump PRs automatically twice per day. The bottleneck is no longer candidate creation; it is quickly deciding whether each candidate can merge, whether red CI is caused by the bump, and whether the super-repo CI signal is trustworthy.

Within one month, the team should move to a bump train where:

- Every scheduled candidate is reviewed the day it opens.
- Non-regressing candidates merge the same day once actionable CI signal exists.
- At least one `rocm-libraries` and one `rocm-systems` bump lands per day when upstream is not broken.
- On clean days, both scheduled candidates for a repo can land.
- Known failures are allowed through only when they are categorized, owned, scoped, tracked, and time-limited.
- `rocm-libraries` bumps use multi-arch prebuilt stages so they do not rebuild or retest unchanged compiler/runtime/system-only work.

With four people, the plan should run as one operating lane plus three implementation lanes from day one:

1. Bump train and triage.
2. Reference propagation and stale PR hygiene.
3. Multi-arch fast lanes.
4. Super-repo CI signal hardening.

## Current Assessment

The existing automation is a strong base:

- TheRock has scheduled bump automation every 12 hours, plus `workflow_dispatch`.
- The bump automation creates TheRock submodule bump PRs and updates TheRock references in the super-repos after a bump lands.
- TheRock multi-arch CI already supports `prebuilt_stages`, `baseline_run_id`, and `external_repo`.
- The external repo path can overlay `rocm-libraries` or `rocm-systems` source and skip fetching the submodule being supplied externally.
- The super-repos already have TheRock CI workflows, path filtering, and source-overlay support.

The recent bump candidate set points to four gaps:

- **Decision latency:** candidates are created regularly, but red CI often waits for human interpretation.
- **Reference drift:** super-repo TheRock ref/hash PRs can accumulate, and static ref lists can miss newer central or multi-arch workflow locations.
- **Signal quality:** some failures are unrelated to the bump, while some green paths may not sufficiently prove the PR source was tested.
- **Turnaround time:** routine library bumps are not yet consistently using topology-aware prebuilt stages to avoid unchanged lower layers.

The plan should optimize the post-creation path: classify, decide, close stale candidates, propagate refs, and make CI faster and more trustworthy.

## Workstreams

| Lane | Owner Focus | First-Week Output | Month-One Output |
| --- | --- | --- | --- |
| Bump train and triage | Make every candidate decidable | Categorize current open bumps, start known-failure ledger, publish first daily report | Same-day disposition for routine bumps; accepted-red policy in use |
| Reference propagation | Make ref bumps complete and self-cleaning | Inventory all TheRock refs in `rocm-libraries` and `rocm-systems`; identify automation gaps | Complete ref propagation, full-SHA validation, stale external ref/hash PR cleanup |
| Multi-arch fast lanes | Reduce CI time for routine bumps | Stage impact table from `BUILD_TOPOLOGY.toml`; first `rocm-libraries` fast-lane experiment | Eligible `rocm-libraries` bumps use prebuilt lower stages by default, with safe fallback |
| Super-repo signal | Make green and red results trustworthy | First source-overlay assertion; first routing/default/label regression test queued or landed | Guardrails for source overlays, path maps, dispatch defaults, labels, dependency scoping, and runner ownership |

## Candidate Classification

Every red bump candidate should be classified within 1 hour of actionable CI signal:

- **Infrastructure flake:** runner, artifact, cache, network, or GitHub Actions transient issue. Rerun once, then file with runner/platform/job details.
- **Known unrelated failure:** present on baseline or unrelated nightly lane. Link owner, issue, scope, and expiry before allowing merge.
- **Bump-caused regression:** new submodule SHA breaks TheRock build, package, or tests. Block, identify first failing stage, and route upstream.
- **False green risk:** CI may be testing a pinned submodule, mutable branch, or wrong runner/script path. Fix before trusting the result.
- **False red or routing bug:** irrelevant test, bad matrix dependency, label drift, dispatch default, or path-routing issue. Fix or explicitly waive impacted lanes.
- **Workflow hygiene defect:** inconsistent SHA, stale ref PR, mutable branch, or matrix parity drift. Repair before relying on the path.

## Four-Week Plan

### Week 1: Start The Train

Goals:

- Classify every currently open TheRock bump candidate.
- Start the daily bump report and known-failure ledger.
- Inventory all TheRock ref/hash locations in both super-repos.
- Run the first `rocm-libraries` fast-lane experiment using prebuilt stages and a known-good baseline.
- Add or queue the first source-overlay guardrail so super-repo CI proves it is testing PR source.

Deliverables:

- Daily bump report: open, merged, blocked, superseded, accepted-red.
- Known-failure ledger with owner, scope, issue, and expiry fields.
- Ref inventory and automation gap list.
- First fast-lane timing datapoint.
- First super-repo CI signal guardrail in progress or landed.

### Week 2: Make Fast Signal Repeatable

Goals:

- Use morning and afternoon decision windows for the twice-daily bump train.
- Start using on-demand `workflow_dispatch` bumps when an upstream fix lands between scheduled bumps.
- Update or stage the ref propagation automation for missed ref locations, full-SHA validation, and stale external PR cleanup.
- Wire the `rocm-libraries` fast lane into a normal PR or documented dispatch path.
- Add source-overlay and fetch-source skip checks in the super-repo CI paths.

Deliverables:

- Same-day decision process for all routine candidates.
- PR-ready automation patch or landed patch for ref propagation gaps.
- Operational `rocm-libraries` fast-lane path with baseline validation.
- CI summary that shows copied, rebuilt, skipped, and full-fallback stages.

### Week 3: Scale To Multiple Daily Landings

Goals:

- Treat both scheduled bump windows as merge opportunities.
- Close stale candidates within 1 hour of a better candidate or landed bump.
- Expand fast-lane coverage based on timing data: more target families, the second major platform, or the highest-cost stage.
- Fix the most expensive false-red causes: matrix dependency scoping, fresh-configure test discovery, dispatch defaults, labels, and path routing.

Deliverables:

- Repeatable morning/afternoon bump-train routine.
- Fast-lane timing report compared with full CI.
- Stale external ref/hash PR cleanup path.
- Focused tests or checks for the highest-frequency false green and false red patterns.

### Week 4: Make It The Default

Goals:

- Make fast-lane eligibility explicit in CI output and PR triage comments.
- Make eligible `rocm-libraries` bumps use the fast lane by default, with full CI fallback when baseline validation is ambiguous.
- Finish ref propagation hardening and duplicate external PR prevention.
- Publish the durable bump-train runbook and escalation path for real regressions.

Deliverables:

- Final bump-train runbook.
- Default eligible `rocm-libraries` fast-lane path.
- Complete ref propagation and stale PR hygiene checklist.
- "Green means tested" checklist for super-repo TheRock CI.
- Known-failure ledger policy enforced in review.

## Operating Rhythm

Daily:

- Review both scheduled bump windows.
- Classify failures within 1 hour of actionable signal.
- Merge, rerun, supersede, or block every candidate the same day when possible.
- Update the known-failure ledger for any accepted red.
- Close stale candidates after a better candidate appears or a bump lands.

Twice weekly:

- Review super-repo TheRock ref/hash PRs.
- Check that ref propagation covers active workflows.
- Rotate secondary reviewers across workstreams so no lane blocks on one person.

Weekly:

- Report p50 and p90 turnaround.
- Report merged, blocked, superseded, and accepted-red counts.
- Retire expired accepted-red entries.
- Move capacity toward the current bottleneck.

## Metrics

Target metrics by the end of the month:

- Initial response: 95 percent acknowledged within 30 minutes of visible CI signal.
- Classification: 95 percent categorized within 1 hour of actionable CI signal.
- Merge turnaround: p50 under 6 hours and p90 under 12 hours for non-regressing bumps after actionable CI signal exists.
- Cadence floor: at least one `rocm-libraries` and one `rocm-systems` bump merged per day when upstream is not broken.
- Cadence stretch: both scheduled candidates per repo are reviewed every day and can merge when signal is clean or accepted-red failures are fully categorized.
- Fast-lane signal: eligible `rocm-libraries` bumps get meaningful prebuilt-stage CI signal within 3 hours.
- Stale PR hygiene: superseded bump PRs close within 1 hour of a better candidate or landed bump.
- Accepted-red hygiene: 100 percent of accepted failures have owner, issue, scope, and expiry.

## Guardrails

- Fast lanes must fall back to full CI when the baseline is invalid, build tooling changes, topology changes, or source-set inputs are ambiguous.
- `rocm-libraries` fast lanes should reuse unchanged systems artifacts only when the source inputs match.
- Accepted red CI must not become a permanent waiver.
- Super-repo CI must prove it is testing the PR source overlay, not TheRock's pinned submodule.
- Manifest diff and blamelist work should support triage but should not become a new critical-path blocker.
