# RFC0010 Test Runner Migration Handoff

Date: 2026-05-25

Scope: hand off the RFC0010 work to move project-specific test runner scripts
out of TheRock and into `rocm-systems` / `rocm-libraries`, plus the shared
test utility work that reduces duplicated runner boilerplate.

This is not about targeted/fast-lane CI. That is a separate effort.

## Executive Summary

The work has two related but separable tracks:

1. **Project-owned installed runners:** move scripts currently owned by TheRock
   under `build_tools/github_actions/test_executable_scripts/` into the
   owning super-repos, install them with the test artifacts, and then update
   TheRock to invoke the installed scripts.
2. **Shared test utilities:** land TheRock PR #5115 so migrated project-owned
   runners can optionally reuse generic helpers for CTest labels, sharding,
   GPU architecture discovery, artifact-group checks, and runner settings.

The guiding rule: project-specific test behavior belongs in the project-owned
runner scripts; generic test mechanics can live in shared utilities.

## Current Public Status

### Trackers

- TheRock#5090 tracks RFC0010 test runner migration PRs.
- TheRock#3968 tracks shared utilities / boilerplate cleanup context.

TheRock#5090 is stale as of this handoff. It still lists several merged PRs as
unchecked and should be updated before using it as the source of truth.

### TheRock PRs

| PR | Status | Meaning | Next action |
| --- | --- | --- | --- |
| TheRock#5115 - shared ROCm test runner utilities | Open, non-draft, approved, mergeable | Foundation shared utility API under `test_tools` | Shepherd to merge. This is the highest-leverage item. |
| TheRock#5258 - use packaged rocm-systems runners | Open draft, stale, mergeability unknown | Draft proof that TheRock can use installed rocm-systems runners and remove matching TheRock scripts | Rebase/refresh after current submodule bumps. Keep as validation until package coverage is clear. |

### rocm-systems Runner Install PRs

Merged:

- rocm-systems#5598 - `rocdecode`
- rocm-systems#5599 - `rocjpeg`
- rocm-systems#5600 - `hip-tests`
- rocm-systems#5602 - `rocprofiler-systems`
- rocm-systems#5651 - `rocr-debug-agent`
- rocm-systems#5604 - `rocprofiler-compute`

Still open:

- rocm-systems#5552 - `rocr-runtime` / `rocrtst`
- rocm-systems#5597 - `aqlprofile`
- rocm-systems#5601 - `amdsmi`
- rocm-systems#5605 - `rocprofiler-sdk`
- rocm-systems#5606 - `rccl` (draft)
- rocm-systems#5607 - `rccl-tests` (draft)

Recommended immediate rocm-systems adoption target in TheRock:

- Start with already-merged, lower-dispute scripts such as `hip-tests`,
  `rocdecode`, and `rocjpeg`.
- Keep `rocprofiler-systems` out of the first TheRock adoption PR if reviewers
  are still expecting more follow-up in that area.
- Do not point TheRock at a packaged runner until the submodule bump in TheRock
  contains the merged runner-install change.

### rocm-libraries Runner Install PRs

All listed install PRs are still open drafts:

- rocm-libraries#7040 - `rand`
- rocm-libraries#7041 - `prim`
- rocm-libraries#7042 - `fft`
- rocm-libraries#7043 - `sparse`
- rocm-libraries#7044 - `solver`
- rocm-libraries#7045 - `rocwmma`

Validation-only PRs:

- rocm-libraries#7305 - FFT shared-utils validation, open draft, mergeable but
  stale/noisy.
- rocm-libraries#7351 - MIOpen shared-utils validation, open draft and
  conflicting. This is the better convergence proof because MIOpen has more of
  the standardized filter logic that previously went through TheRock's
  `test_runner.py`.

## Intended Architecture

### Source Ownership

- TheRock owns CI orchestration and shared generic test helpers.
- `rocm-systems` and `rocm-libraries` own project-specific test runner scripts.
- TheRock should not keep long-term project-specific wrappers once installed
  runner scripts exist and have been validated.

### Runtime Flow

1. The super-repo installs its project-owned runner script with the relevant
   test payload.
2. TheRock downloads/install artifacts for testing.
3. TheRock exposes shared utilities through an explicit support path when they
   are available.
4. TheRock invokes the installed project-owned runner.
5. The project-owned runner uses shared utilities when available and local
   fallback logic when they are not.

### Shared Utility Boundary

Good shared utility content:

- CTest label argument construction.
- CTest/GTest sharding helpers.
- `TEST_TYPE` category normalization.
- GPU arch label matching.
- `rocminfo` parsing and visible GPU discovery.
- ASAN/TSAN artifact-group checks.
- Generic runner settings/env helpers.

Keep out of shared utilities:

- project-specific executable paths;
- project-specific test directories;
- project-specific skip lists;
- project-specific timeouts and parallelism defaults;
- `TEST_COMPONENT` dispatch tables;
- GitHub Actions API plumbing;
- decisions that require knowledge of a specific project test suite.

## Workstreams For Delegation

### Lane A: Shared Utilities Shepherd

Goal: get TheRock#5115 merged and documented enough for downstream consumers.

Owner tasks:

- Confirm latest PR #5115 checks and review state.
- Answer any remaining review comments.
- Keep the title/description focused on reusable test utilities, not
  project-specific migration.
- Update issue #3968 and/or #5090 after merge.
- After merge, publish a short "how to import optionally" snippet for
  super-repo runner authors.

Definition of done:

- PR #5115 is merged.
- `test_tools/test_utils.py` is available on TheRock `main`.
- Unit tests for `test_tools` run in TheRock unit-test CI.

### Lane B: rocm-systems Runner Installs

Goal: finish or triage the remaining rocm-systems install PRs and identify
which merged runners are ready for TheRock adoption.

Owner tasks:

- Update TheRock#5090 with actual merged/open statuses.
- For each open PR, determine whether it is ready for review, stale, blocked by
  design feedback, or should remain draft.
- For merged PRs, verify the installed script is present in the current TheRock
  submodule revision before asking TheRock to call it.
- Keep rocprofiler-sdk/rocprofiler-systems decisions separate if their review
  threads ask for more changes.

Definition of done:

- Every rocm-systems row in #5090 has a current status and owner.
- At least one small TheRock adoption PR uses installed `hip-tests`,
  `rocdecode`, or `rocjpeg` runners and deletes the matching old TheRock script.

### Lane C: rocm-libraries Runner Installs

Goal: revive the open draft runner-install PRs and hand them to project owners
or component-focused reviewers.

Owner tasks:

- For each draft PR #7040-#7045, refresh against current `develop`/target base
  and re-run pre-commit.
- Confirm the runner is installed with the test payload.
- Confirm standalone behavior without TheRock shared utilities.
- Decide whether to opportunistically use `test_utils` after PR #5115 lands.
- Keep project-specific logic in the project runner.

Definition of done:

- Each library runner PR has a current status: ready for review, blocked, or
  intentionally parked.
- At least one library runner is used in a TheRock validation/adoption branch.

### Lane D: TheRock Adoption And Deletion

Goal: update TheRock to prefer installed project-owned runners and remove the
matching old scripts, one small component group at a time.

Owner tasks:

- Wait for a super-repo runner install PR to be merged and included in TheRock's
  submodule revision.
- Update `fetch_test_configurations.py` or its current equivalent to point at
  the installed runner path.
- Delete the matching old script from
  `build_tools/github_actions/test_executable_scripts/`.
- Add or update tests proving TheRock resolves the installed runner.
- Verify the PR independently through the relevant component test workflow.

Definition of done:

- TheRock no longer owns that project's runner script.
- The matching TheRock test job invokes the packaged/installed script.
- CI or workflow-dispatch evidence is linked in the PR.

### Lane E: Shared-Utils Validation Branches

Goal: prove the helper-present and helper-absent paths before turning validation
branches into real adoption work.

Owner tasks:

- Refresh MIOpen validation PR #7351; it is currently conflicting.
- Ensure TheRock test configuration points at the built/packaged MIOpen runner,
  not a source-tree script that CI will not exercise.
- Preserve the old MIOpen script fallback behavior when shared utilities are
  not present.
- Do not make the fallback depend on TheRock-only env vars.
- Keep FFT PR #7305 as prior validation unless someone wants to refresh it.

Definition of done:

- MIOpen validation CI actually invokes the packaged runner.
- The helper-present path uses `test_utils`.
- The helper-absent path remains usable outside TheRock.
- Findings are fed back into real PRs, not merged directly from the validation
  branch unless the team decides to promote it.

## Onboarding Checklist For New Contributors

Give each contributor:

- RFC0010 link and TheRock#5090.
- The shared utility PR #5115.
- One concrete component or lane, not the whole migration.
- The "project-specific logic stays in the project" rule.
- A validation checklist and expected commands.

Minimum local setup:

```powershell
gh auth status
git clone git@github.com:ROCm/TheRock.git TheRock
git clone git@github.com:ROCm/rocm-systems.git rocm-systems
git clone git@github.com:ROCm/rocm-libraries.git rocm-libraries
```

Useful per-PR checks:

```powershell
pre-commit run --files <changed files>
python -m py_compile <changed python files>
python -m unittest <focused test module>
```

For TheRock PRs, prefer focused unit tests in:

```text
build_tools/github_actions/tests/
test_tools/tests/
```

For super-repo runner PRs, also run the runner in both modes:

- with `THEROCK_TEST_TOOLS_DIR` pointing at a directory containing
  `test_utils.py`;
- without `THEROCK_TEST_TOOLS_DIR`.

## Review Checklist

For a super-repo runner install PR:

- Is the runner installed with the test artifact payload?
- Can the runner work without a TheRock checkout?
- Does it avoid hard dependencies on `THEROCK_DIR`, `THEROCK_BIN_DIR`, or
  `TEST_COMPONENT`?
- If it imports `test_utils`, is that import optional?
- Is fallback behavior equivalent to the old script?
- Are project-specific defaults kept in the project script?

For a TheRock adoption PR:

- Does the current submodule revision contain the installed runner?
- Does TheRock call the installed runner path?
- Was the matching old TheRock-owned script deleted?
- Is there focused test coverage for the resolved runner path?
- Does CI evidence show the installed runner was exercised?
- Is the PR scoped to a small component set?

For shared utility work:

- Is the helper generic and project-neutral?
- Does it avoid module-level CI env reads and subprocess execution?
- Are subprocess calls injectable for tests?
- Are pure parsers covered by unit tests?
- Does it preserve behavior copied from the old functions?

## Suggested Immediate Assignment

1. Person 1: shepherd TheRock#5115 to merge.
2. Person 2: update TheRock#5090 and triage remaining rocm-systems PRs.
3. Person 3: rebase/refresh TheRock#5258 for `hip-tests`, `rocdecode`, and
   `rocjpeg` only.
4. Person 4: refresh MIOpen validation PR #7351 and confirm it exercises the
   packaged runner plus shared-utils fallback behavior.
5. Person 5, if available: triage rocm-libraries draft PRs #7040-#7045 and
   assign each to an owning component reviewer.

## Risks And Guardrails

- Do not merge validation-only PRs by accident.
- Do not centralize project-specific behavior in `test_utils`.
- Do not delete TheRock scripts until the packaged replacement is present in
  TheRock's submodule revision.
- Do not depend on shared utilities being present in standalone super-repo
  runner execution.
- Do not rewire legacy `test_runner.py` as a prerequisite for PR #5115; it is a
  retirement target, not the desired long-term interface.

## Message To Colleagues

Suggested short intro:

```text
RFC0010 is moving project-specific test runner scripts out of TheRock and into
the projects that own the tests. TheRock should orchestrate CI and call
installed project-owned runners, not carry project-specific Python scripts
forever.

The shared utilities PR gives those project-owned runners optional generic
helpers for CTest labels, sharding, GPU detection, and artifact flavor checks.
Those helpers reduce boilerplate, but project-specific paths, defaults, and
skip behavior stay in the project runner.

Please take one lane/component at a time. A PR is done when the runner is
installed, works without TheRock-only state, TheRock can invoke it from the
artifact payload, and the old TheRock-owned copy can be removed safely.
```
