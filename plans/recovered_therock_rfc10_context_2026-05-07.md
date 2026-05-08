# Recovered TheRock RFC0010 / Test Runner Context

Recovered: 2026-05-07

## Local Source Notes

- `plans/rocm_libraries_test_runner_convergence.md`
- `reviews/pr_TheRock_4581.md`
- `reviews/pr_TheRock_5054.md`
- `reviews/pr_TheRock_4570.md`
- `reviews/pr_rocm-systems_test_runner_drafts.md`
- `reviews/pr_rocm-systems_5651.md`
- `TheRock-pr-4581/docs/rfcs/RFC0010-Test-Scripts-Migration.md`

## Canonical Tracker

- [ROCm/TheRock#5090](https://github.com/ROCm/TheRock/issues/5090) - open
  tracking issue for the RFC0010 migration PRs.
- [ROCm/TheRock#3968](https://github.com/ROCm/TheRock/issues/3968) - related
  follow-up for extracting shared test utilities and reducing migrated runner
  boilerplate after the scripts live in their owning repositories.

## Current PR State Checked From GitHub

### TheRock

- [ROCm/TheRock#4570](https://github.com/ROCm/TheRock/pull/4570) - merged.
  Adds `test_tools/determine_rocm_test_dependencies.py`. Local review had no
  remaining blocker before merge.
- [ROCm/TheRock#4581](https://github.com/ROCm/TheRock/pull/4581) - open.
  GitHub currently reports `APPROVED`, but local notes say not to treat it as
  merge-ready until the ownership/design question is resolved.
- [ROCm/TheRock#5054](https://github.com/ROCm/TheRock/pull/5054) - open draft.
  POC extracting CTest filter behavior into `test_filter_utils.py`; useful
  convergence signal, not final architecture.
- [ROCm/TheRock#5064](https://github.com/ROCm/TheRock/pull/5064) - closed.
  No fresh review work needed.
- [ROCm/TheRock#4685](https://github.com/ROCm/TheRock/pull/4685) - open.
  Moves test orchestration from `build_tools` to `test_tools`.
- [ROCm/TheRock#4947](https://github.com/ROCm/TheRock/pull/4947) - open draft.
  Adds pytest filter standardization support for Tensile/Tensilite.
- [ROCm/TheRock#5088](https://github.com/ROCm/TheRock/pull/5088) - open draft.
  Proposes `ctest --parallel 1` for library test drivers.
- [ROCm/TheRock#4490](https://github.com/ROCm/TheRock/pull/4490) - open.
  Adds rocSPARSE/hipSPARSE to the old generic `test_runner.py`; treat as a
  transitional/generic-runner holdover.

### rocm-systems RFC0010 Runner Batch

Merged:

- [ROCm/rocm-systems#5600](https://github.com/ROCm/rocm-systems/pull/5600) -
  hip-tests catch runner.
- [ROCm/rocm-systems#5602](https://github.com/ROCm/rocm-systems/pull/5602) -
  rocprofiler-systems runner.
- [ROCm/rocm-systems#5604](https://github.com/ROCm/rocm-systems/pull/5604) -
  rocprofiler-compute runner.
- [ROCm/rocm-systems#5651](https://github.com/ROCm/rocm-systems/pull/5651) -
  rocr-debug-agent replacement/migration runner.

Closed/superseded:

- [ROCm/rocm-systems#5603](https://github.com/ROCm/rocm-systems/pull/5603) -
  rocr-debug-agent draft, replaced by #5651.

Still open:

- [ROCm/rocm-systems#5552](https://github.com/ROCm/rocm-systems/pull/5552) -
  rocr-runtime / rocrtst runner.
- [ROCm/rocm-systems#5597](https://github.com/ROCm/rocm-systems/pull/5597) -
  aqlprofile runner.
- [ROCm/rocm-systems#5598](https://github.com/ROCm/rocm-systems/pull/5598) -
  rocdecode runner.
- [ROCm/rocm-systems#5599](https://github.com/ROCm/rocm-systems/pull/5599) -
  rocjpeg runner.
- [ROCm/rocm-systems#5601](https://github.com/ROCm/rocm-systems/pull/5601) -
  amdsmi runner.
- [ROCm/rocm-systems#5605](https://github.com/ROCm/rocm-systems/pull/5605) -
  rocprofiler-sdk runner.
- [ROCm/rocm-systems#5606](https://github.com/ROCm/rocm-systems/pull/5606) -
  rccl runner, draft.
- [ROCm/rocm-systems#5607](https://github.com/ROCm/rocm-systems/pull/5607) -
  rccl-tests runner, draft.

Local batch review said the direction is right but called out:

- #5552: rocrtst command hard-coded Linux executable name.
- #5600: DLL copy failures should fail fast. This PR is now merged, so check
  whether it was fixed before relying on the runner.
- #5603: Unix-only `resource` import. Superseded by merged #5651.

### rocm-libraries Runner / Filter Work

Open draft installed-runner batch:

- [ROCm/rocm-libraries#7040](https://github.com/ROCm/rocm-libraries/pull/7040)
  - rand runners.
- [ROCm/rocm-libraries#7041](https://github.com/ROCm/rocm-libraries/pull/7041)
  - prim runners.
- [ROCm/rocm-libraries#7042](https://github.com/ROCm/rocm-libraries/pull/7042)
  - fft runners.
- [ROCm/rocm-libraries#7043](https://github.com/ROCm/rocm-libraries/pull/7043)
  - sparse runners.
- [ROCm/rocm-libraries#7044](https://github.com/ROCm/rocm-libraries/pull/7044)
  - solver runners.
- [ROCm/rocm-libraries#7045](https://github.com/ROCm/rocm-libraries/pull/7045)
  - rocWMMA runner.

Other related open drafts:

- [ROCm/rocm-libraries#6854](https://github.com/ROCm/rocm-libraries/pull/6854)
  - rocBLAS parallel runner.
- [ROCm/rocm-libraries#7054](https://github.com/ROCm/rocm-libraries/pull/7054)
  - generic `[test-runner]` placeholder/draft, body still templated.
- [ROCm/rocm-libraries#7082](https://github.com/ROCm/rocm-libraries/pull/7082)
  - RFC0010 golden reference validation draft.
- Filter standardization drafts are also active, including #7037, #7076,
  #7132, #7152, #7158, and #6943. Treat these as adjacent category/filter
  work, not necessarily the installed-runner ownership migration itself.

## Strategy Convergence

The settled direction is:

- RFC0010 wants test runner ownership moved out of TheRock and into the repos
  that own the tested components.
- Scott's feedback on TheRock#4581 changes the implementation boundary:
  subprojects should install their own test runners as normal project artifacts.
  TheRock should not inject arbitrary test scripts through
  `therock_subproject.cmake` / `INSTALL_TEST_SCRIPT_FILES` as the long-term
  mechanism.
- TheRock should consume installed runners from fetched test artifacts and call
  them, not own project-specific test behavior.
- Project runners should derive their ROCm tree from the installed layout where
  possible, optionally honoring explicit `ROCM_PATH`, and should avoid
  `THEROCK_DIR` / `THEROCK_BIN_DIR` assumptions.

Keep from TheRock's old generic `test_runner.py`:

- `TEST_TYPE` as the external CI knob.
- `quick`, `standard`, `comprehensive`, and `full` CTest labels.
- GPU arch family matching such as `gfx1151 -> gfx115X -> gfx11X`.
- Sharding via `--tests-information`.
- Conservative timeout and parallelism defaults.
- Installed CTest payload validation.

Do not preserve as the final interface:

- Long-lived `TEST_COMPONENT` dispatch table.
- TheRock-specific path discovery inside project-owned scripts.
- One generic script owning many project behaviors.
- Hidden project behavior outside the owning project.

TheRock#5054 supports this direction as a POC: it extracts reusable filtering
behavior from `test_runner.py`, but local review found parity issues around
`ROCM_PATH`, parallelism, rocprofiler-compute's quick/exclude source of truth,
and focused tests for `test_filter_utils.py`.

## Suggested Next Moves

1. Do not merge TheRock#4581 as the final ownership model unless the
   superproject-installed-script concern is explicitly resolved. It may need to
   be reworked or superseded by subproject-installed runner PRs.
2. Continue the subproject-installed runner batches. For rocm-systems, refresh
   the open PRs and check whether #5552's Windows executable issue is still
   present.
3. For rocm-libraries, use #7043 sparse as the first convergence slice, then
   handle rocBLAS separately because of ASAN/YAML/parallel-runner behavior, and
   MIOpen separately because its filtering is larger and platform-specific.
4. Treat TheRock#5054 as useful POC evidence, not a competing final design.
   Its helper behavior should inform installed/super-repo orchestration, but
   the final boundary should still keep project-specific logic with projects.
5. Before deleting TheRock copies, add an explicit smoke path that invokes an
   installed runner from a fetched artifact layout. Passing current TheRock CI
   may still be exercising the old TheRock-side script paths.
6. Keep filter/category standardization aligned with the installed-runner model:
   shared category semantics are okay, but project-specific test behavior
   should remain in the owning repo.

## Parallel Work Position

The shared utilities / boilerplate concern is valid and should be worked in
parallel, not postponed until every runner migration is complete.

Recommended split:

- Track A: keep landing project-owned installed runner PRs with minimal behavior
  changes. These PRs prove the ownership boundary and installed artifact
  contract.
- Track B: start the shared utility work from TheRock#3968 in draft/POC form,
  but keep it repo-neutral and avoid making the early migration PRs depend on
  it.
- Track C: once two or three migrated runners across rocm-systems and
  rocm-libraries have stabilized, adopt the shared helper in small follow-up
  PRs or in the still-open runner PRs where it is low risk.

Guardrails for Track B:

- Do not design the utility API around `THEROCK_DIR`, `THEROCK_BIN_DIR`, or the
  old `TEST_COMPONENT` router.
- Keep project-specific behavior in project-owned runners.
- Prefer low-level, stable helpers first: command logging, shard environment
  construction, ROCm install-root validation, CTest/GTest argument assembly, and
  clear fail-fast diagnostics.
- Treat common category semantics as shared, but avoid hiding project-specific
  quick/exclude policy in a central TheRock table.
- Do not make the utility extraction block runner migration unless a runner PR is
  already being reworked for other reasons.

Suggested meeting framing:

> I agree the boilerplate cleanup is real and should start now. The distinction
> is that the helper should be designed against the project-owned installed
> runner shape, not against today’s TheRock-side copies. Let’s run #3968 in
> parallel as a draft utility track while #5090 keeps landing installed runners,
> then adopt the helper after the first few runners prove the boundary.
