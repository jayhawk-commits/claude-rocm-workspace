# RFC0010 Shared Test Utilities / Boilerplate Cleanup Plan

Date: 2026-05-07

## Position

Work on shared utilities in parallel with the RFC0010 runner migration, but do
not block project-owned installed runner PRs on the utility extraction.

The first utility PR should be deliberately boring: copy stable, reusable
testing helpers out of TheRock's current `test_runner.py` and testing-adjacent
runtime helpers out of `build_tools/github_actions` into an importable module
under `test_tools`, add focused unit tests, and validate the module with
`py_compile` / `compileall`.

Important packaging constraint: the source of truth for this helper can live in
TheRock, but the helper must also be usable by runner scripts that live in
`rocm-systems` / `rocm-libraries` and are packaged into test artifacts. That
means the helper needs a deliberate runtime packaging story, not just a
TheRock-repo import path.

## Goals

- Give the boilerplate cleanup work a concrete first PR.
- Preserve behavior from `test_runner.py` while making the logic importable and
  testable without module-level CI environment side effects.
- Create a helper surface that can be adopted by migrated project-owned runners
  after their installed-layout contract is proven.
- Keep the helper repo-neutral at runtime so packaged runner scripts do not need
  a TheRock source checkout, `THEROCK_DIR`, `THEROCK_BIN_DIR`, or
  `TEST_COMPONENT` routing to use it.

## Non-Goals

- Do not move every runner to the helper in the first PR.
- Do not design a full framework or base class before multiple runner shapes
  stabilize.
- Do not centralize project-specific quick/exclude policy in a TheRock table.
- Do not replace project-owned runner PRs with a new generic `TEST_COMPONENT`
  router.
- Do not put project-specific executable paths, test directories, environment
  overrides, timeout choices, quick/exclude lists, skip lists, or component
  dispatch logic in `test_tools/test_utils.py`.
- Do not turn `test_tools/test_utils.py` into a new home for GitHub Actions
  API/workflow plumbing.

## Proposed Module

Add an importable Python module in TheRock:

```text
test_tools/test_utils.py
test_tools/tests/test_utils_test.py
```

If `test_tools` is intended to be imported as a normal package, add an empty
`test_tools/__init__.py`. Otherwise confirm the repo already relies on
namespace-package imports and keep the directory as-is.

Use a function library, not a script:

- no module-level reads of required CI env vars;
- no module-level `sys.exit()`;
- no subprocess execution during import;
- no project dispatch table as public API;
- functions take explicit arguments and return values or raise clear exceptions.
- no project names, component maps, or project-specific defaults.

Use a public module name that is not tied to the legacy `test_runner.py`
router. In the TheRock repo, `test_tools/test_utils.py` is enough context; any
future runtime namespace should be decided by the packaging/import boundary, not
by the source filename.

## First PR: Extract Pure/Testable Utilities

Copy and adapt the stable testing pieces from
`build_tools/github_actions/test_executable_scripts/test_runner.py`:

- `VALID_TEST_CATEGORIES`
- `TestRunSettings`, an immutable settings object for common CI/test runner
  state that callers can construct from env plus project-owned facts like
  `test_dir` and `rocm_path`
- `normalize_test_category(test_type: str | None) -> str`
- `extract_gpu_arch(amdgpu_families: str | None) -> str`
- `find_matching_gpu_arch(gpu_arch: str, available_gpu_archs: set[str]) -> str | None`
- `gtest_shard_env(shard_index: str | int = 1, total_shards: str | int = 1) -> dict[str, str]`
- `build_ctest_label_args(category, gpu_arch, available_gpu_archs, exclude_labels) -> list[str]`
- `ctest_shard_args(shard_index: str | int = 1, total_shards: str | int = 1) -> list[str]`
- `build_test_env(settings, ...) -> dict[str, str]`
- `build_ctest_command(settings: TestRunSettings) -> list[str]`
- `run_ctest(settings: TestRunSettings, ...)`

The helper can own common runner mechanics, including generic CTest command
construction and execution. The caller still owns project-specific facts and
policy: test directory, ROCm root, cwd, environment overrides, executable path,
timeout/parallel values, and any special CTest/GTest/pytest arguments. Put those
facts into `TestRunSettings` or explicit helper inputs; do not hide them in
TheRock-owned tables.

Keep subprocess-backed discovery separate from pure command construction:

- `count_ctest_tests(test_dir: Path, runner=subprocess.run) -> int`
- `read_ctest_labels(test_dir: Path, runner=subprocess.run) -> set[str]`
- `parse_ctest_labels(labels: Iterable[str]) -> CTestLabels`
- `discover_ctest_labels(test_dir: Path, runner=subprocess.run) -> CTestLabels`

Suggested small data type:

```python
@dataclass(frozen=True)
class CTestLabels:
    gpu_archs: set[str]
    exclude_labels: set[str]
```

This lets tests cover label parsing without invoking CTest.

Suggested caller shape:

```python
settings = test_utils.TestRunSettings.from_env(
    rocm_path=rocm_path,
    test_dir=test_dir,
).with_ctest(
    parallel=parallel,
    timeout_seconds=timeout_seconds,
    extra_args=["--tests-regex", project_regex],
)

env = test_utils.build_test_env(
    settings,
    base_env=os.environ,
    path_prepend={"PATH": [rocm_path / "bin"]},
    extra_env=project_env,
)

return test_utils.run_ctest(settings, env=env, discover_labels=True).returncode
```

This gives callers a single utility path for running common CTest-based tests
without making the shared helper responsible for component routing or installed
layout discovery.

Also audit `build_tools/github_actions` for helpers that are not intrinsically
GitHub Actions-specific. On current TheRock main, the old
`github_action_utils` shape appears to have converged into
`build_tools/github_actions/github_actions_api.py`; if working from an older
branch, apply the same split to the local filename.

Good candidates for the test utility module:

- `get_visible_gpu_count(...)`, adapted so command execution is injectable and
  no subprocess runs at import time.
- `get_first_gpu_architecture(...)`, adapted the same way.
- a pure `parse_rocminfo_gpu_archs(output: str) -> list[str]` helper so most
  behavior can be tested without invoking `rocminfo`.
- `is_asan(...)`, but reshaped as a pure helper such as
  `is_asan_artifact_group(artifact_group: str | None) -> bool` instead of
  reading `ARTIFACT_GROUP` directly inside the utility.
- `str2bool(...)` only if migrated test runners need boolean env parsing; keep
  any existing GitHub Actions callers working in place for now.

Things that should stay in `build_tools/github_actions`:

- `GitHubAPI`, `GitHubAPIError`, and GitHub REST/query behavior.
- `gha_*` workflow command helpers.
- GitHub event loading, workflow summary output, artifact metadata upload, and
  other CI-service integration details.
- broad utility functions heavily used by non-test workflow scripts unless a
  separate general-purpose utility migration is agreed.

The practical rule: move helpers that describe the test runtime, GPU discovery,
CTest/GTest argument construction, artifact flavor checks, or runner-local
parsing. Leave helpers that talk to GitHub Actions, format workflow output, or
manage CI service behavior.

## First PR Tests

Move the useful coverage currently aimed at `unit_test_runner.py` into
`test_tools/tests/test_utils_test.py`:

- exact and wildcard GPU arch matching;
- invalid/empty `TEST_TYPE` category normalization;
- `AMDGPU_FAMILIES` parsing;
- GTest shard env translation from 1-based CI shard index to 0-based GTest;
- CTest label parsing for `ex_gpu_*` and `*_exclude`;
- CTest argument-fragment construction with:
  - category include;
  - GPU include;
  - generic/empty GPU exclusion;
  - category-specific exclude label;
  - combined `-LE` OR regex such as `quick_exclude|ex_gpu`;
  - `--tests-information` sharding arguments from `ctest_shard_args()`.
- `TestRunSettings.from_env()` parsing of `TEST_TYPE`, `AMDGPU_FAMILIES`,
  `SHARD_INDEX`, and `TOTAL_SHARDS`;
- CTest command construction from `TestRunSettings`, including caller-provided
  parallelism, timeout, discovered labels, and extra CTest args;
- test environment construction with `ROCM_PATH`, GTest shard env vars,
  path prepends, and project-provided env overrides;
- `run_ctest()` with an injected runner, including optional CTest label
  discovery before final execution;
- rocminfo output parsing with one GPU, multiple GPUs, and no GPU records;
- visible GPU counting with a fake subprocess runner;
- first GPU architecture selection with a fake subprocess runner;
- ASAN artifact-group detection without reading process-global env vars;
- boolean env parsing if `str2bool` or a renamed equivalent is included.

Verification commands:

```powershell
python -m py_compile test_tools\test_utils.py test_tools\tests\test_utils_test.py
python -m unittest test_tools.tests.test_utils_test
```

If `test_tools` remains a non-package directory, use the repo's existing test
invocation pattern instead of dotted `unittest` module syntax.

## Second PR: Expose Helper Through Artifact Installation

Before letting super-repo runner scripts optionally import this helper, make the
helper available to TheRock CI without requiring a TheRock-specific install path
inside each project-owned test payload.

Do **not** start by hard-coding a runner dependency on
`<rocm-prefix>/share/therock/...`. That resembles the `share/therock-scripts`
direction that drew ownership-boundary concerns in TheRock#4581. It is still a
reasonable place for TheRock metadata, but it should not become the required
runtime contract for project-owned runners.

Preferred first runtime contract:

- TheRock owns `test_tools/test_utils.py`.
- `install_rocm_from_artifacts.py` materializes a TheRock test-tools support
  directory when test artifacts are requested.
- TheRock CI exposes that directory through an explicit environment variable:
  `THEROCK_TEST_TOOLS_DIR`.
- Runner scripts try that directory first.
- If the helper is not present, runner scripts use local fallback code and keep
  working.

This avoids settling the final artifact/install layout before the first helper
API proves useful.

Proposed install/reproduction behavior:

- When `install_rocm_from_artifacts.py` is run with `--tests`, copy
  `test_tools/test_utils.py` into a support directory under the artifact output
  root, for example:

  ```text
  <output-dir>/.therock-test-tools/test_utils.py
  ```

- Print the resolved support path clearly.
- In GitHub Actions, set or expose `THEROCK_TEST_TOOLS_DIR` to that path from
  the same workflow step that installs artifacts.
- For local reproduction, users can set `THEROCK_TEST_TOOLS_DIR` to the printed
  path or point it directly at a TheRock checkout's `test_tools` directory.

This keeps the dependency explicit, outside the ROCm install prefix, and tied to
the artifact-install step that already prepares the test environment.

Potential later layouts, in order of preference:

1. Explicit test-support directory created by `install_rocm_from_artifacts.py`
   and exposed via `THEROCK_TEST_TOOLS_DIR`.
2. Small installable Python package for ROCm test tooling.
3. A source copy vendored into rocm-systems and rocm-libraries if sync cost is
   acceptable.
4. `<rocm-prefix>/share/therock/test_tools` only if reviewers agree that
   TheRock-owned support files belong in the installed ROCm tree.

Then runner scripts installed under project test payload directories can use one
small optional-import helper based on explicit environment first, and only then
any project/installation-specific fallback paths.

The bootstrap remains intentionally tiny and project-owned. The shared helper
should not be responsible for discovering itself.

The helper must be optional. A project-owned runner should keep working when the
helper is not packaged, when a developer runs it from a standalone super-repo
build, or when someone only extracts that project's test artifact. Recommended
runner pattern:

```python
def _try_import_test_utils(rocm_path):
    candidate_dirs = []
    env_dir = os.environ.get("THEROCK_TEST_TOOLS_DIR")
    if env_dir:
        candidate_dirs.append(Path(env_dir))

    # Only add installed-layout guesses after the explicit environment
    # contract. Keep this list conservative until reviewers agree on a layout.
    if rocm_path:
        candidate_dirs.append(rocm_path / "test_tools")

    for candidate_dir in candidate_dirs:
        utils_path = candidate_dir / "test_utils.py"
        if not utils_path.exists():
            continue

        sys.path.insert(0, str(candidate_dir))
        try:
            import test_utils
            return test_utils
        except Exception as e:
            raise RuntimeError(
                f"Found {utils_path}, but failed to import it"
            ) from e
        finally:
            if sys.path[0] == str(candidate_dir):
                sys.path.pop(0)
    return None
```

Each runner then does:

```python
test_utils = _try_import_test_utils(rocm_path)
if test_utils is not None:
    label_args = test_utils.build_ctest_label_args(...)
    shard_args = test_utils.ctest_shard_args(...)
else:
    label_args = _build_ctest_label_args_fallback(...)
    shard_args = _ctest_shard_args_fallback(...)

cmd = ["ctest", *label_args, "--test-dir", str(test_dir), *shard_args, ...]
```

The fallback should be small and local to the script, preserving the script's
standalone behavior. This means the helper reduces duplication when present but
does not become a hard dependency for super-repo test runners.

If no candidate directory exists, or no `test_utils.py` exists in any candidate
directory, `_try_import_test_utils()` returns `None` and the runner uses its
fallback implementation. If a `test_utils.py` file is found but cannot be
imported, that is treated as a real error instead of silently falling back; this
prevents CI from hiding a broken packaged helper.

Packaging choices:

- expose the `.py` source file through `THEROCK_TEST_TOOLS_DIR` first;
- make `install_rocm_from_artifacts.py` the source of the support directory in
  CI/reproduction flows;
- optionally run `compileall` during packaging or CI validation to prove the
  packaged helper compiles;
- do not rely on checked-in `.pyc` files as the source of truth;
- if bytecode-only distribution is desired later, make it an explicit follow-up
  after cross-platform import behavior is proven.

TheRock-side work in this PR:

- update `install_rocm_from_artifacts.py` to copy `test_tools/test_utils.py`
  into a deterministic support directory when `--tests` is requested;
- update the relevant workflow/test harness to set `THEROCK_TEST_TOOLS_DIR` to
  that support directory when invoking migrated runners;
- add a smoke import test from a temporary support directory;
- add a test proving runners continue to use fallback behavior when
  `THEROCK_TEST_TOOLS_DIR` is unset or invalid.

Independent verification for this PR:

- run the new/updated `install_rocm_from_artifacts.py` unit tests;
- run `py_compile` on `test_tools/test_utils.py` and
  `build_tools/install_rocm_from_artifacts.py`;
- run a local smoke test that invokes the artifact-install support-copy helper
  into a temporary output directory, sets `THEROCK_TEST_TOOLS_DIR`, and imports
  `test_utils` from there;
- run the same smoke test with `THEROCK_TEST_TOOLS_DIR` unset to verify callers
  can still fall back.

## Third PR: Adopt Helper in Project-Owned Runners Opportunistically

Do not mass-edit all active runner PRs. Adopt the helper where it is low risk:

- new runner PRs that are already being updated for review feedback;
- simple CTest wrappers in rocm-libraries slices such as rand/fft/prim/sparse;
- rocm-systems runners only after confirming they can import the helper from
  the intended installed/test environment.

For each adoption, keep project-specific behavior in the project runner:

- executable locations;
- special environment setup;
- custom quick/exclude policy that is not represented by CTest labels;
- ROCm install-root discovery from installed layout.
- timeout and parallelism choices;
- project-specific CTest/GTest/pytest flags.

Each adoption PR should verify both paths independently:

- helper-present path: set `THEROCK_TEST_TOOLS_DIR` to a directory containing
  `test_utils.py` and assert the runner uses the helper path;
- helper-absent path: leave `THEROCK_TEST_TOOLS_DIR` unset or point it at an
  empty directory and assert the runner still works through its local fallback.

Skip rewiring the legacy TheRock generic `test_runner.py`. That script is a
retirement target, and changing it to use the new utility module could add churn
to the wrong path. The new utilities should prove themselves in project-owned
scripts that represent the RFC0010 target architecture.

## Important Import Boundary

The intended import boundary is:

- TheRock owns the helper source.
- TheRock exposes the helper to TheRock CI through an explicit support path.
- Super-repo runner scripts import the helper from that explicit support path
  when it is available.
- Super-repo runner scripts keep local fallback behavior when it is not
  available.
- Standalone super-repo developers can either set
  `THEROCK_TEST_TOOLS_DIR`/`PYTHONPATH` to TheRock's `test_tools`, use an
  artifact-like install root, or run without the helper.

Alternatives if the packaged-helper path proves awkward:

1. Copied/vendored helper in rocm-systems and rocm-libraries: simple but creates
   sync debt.
2. Small installable test utility package: cleanest long-term shape, but more
   process/tooling work.

Recommended sequencing:

- First PR creates the TheRock-owned module and proves the function API.
- Second PR updates `install_rocm_from_artifacts.py` and workflows to expose the
  helper through an explicit support path without freezing an install layout.
- Later PRs adopt the helper from project-owned runners, with local fallbacks.

Next-week validation draft:

- create a draft PR that is explicitly not intended to merge;
- base it on the shared test utilities PR branch;
- change one or more migrated project-owned runner scripts to import and use
  the shared helper from the PR branch/support path;
- use it to prove the helper-present and helper-absent paths work from the
  super-repo runner context before committing to the real adoption series.

## Relationship To Trackers

- The migration PR list lives in
  [ROCm/TheRock#5090](https://github.com/ROCm/TheRock/issues/5090).
- The shared utilities / boilerplate cleanup lives in
  [ROCm/TheRock#3968](https://github.com/ROCm/TheRock/issues/3968).
