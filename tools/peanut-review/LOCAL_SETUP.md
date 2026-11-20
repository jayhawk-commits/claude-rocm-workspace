# Local Peanut Review profile

This profile runs the imported harness in Ubuntu WSL with two selected
workspace personas and one curator. It persists comments, verification notes,
runner logs, and a curated `result.md` outside the source repository. The
ordinary interactive review-panel skill remains useful for short reviews.

## Runtime and sign-in

The PowerShell entrypoint is `scripts/peanut-review.ps1` at the meta-workspace
root. By default it uses the sibling `.cache/peanut-review/runtime` directory
for an isolated Python environment (`venv/bin/python`) and Linux Codex
(`bin/codex`). Ubuntu needs Bash, Git and Python; the virtual environment needs
the dependencies listed in `pyproject.toml`. `-Distribution` and `-RuntimeRoot`
override the local runtime location without changing global shell settings.

### First-time setup

`setup-review-panel.ps1` installs skill discovery links only. Before using the
harness, open Ubuntu WSL in this meta-workspace and create its runtime:

```bash
set -eu
workspace_dir="$PWD"
runtime_dir="$(dirname "$workspace_dir")/.cache/peanut-review/runtime"
mkdir -p "$runtime_dir/bin"
python3 -m venv "$runtime_dir/venv"
"$runtime_dir/venv/bin/python" -m pip install -e "$workspace_dir/tools/peanut-review[dev]"
```

Use Python 3.10 or newer with working `venv`/`ensurepip` support; on Ubuntu,
install the matching `python3-venv` package if creation fails. Bash, Git, curl,
and a working HTTPS trust store are also required.

Install Linux Codex using the [official standalone installer](https://learn.chatgpt.com/docs/codex/cli).
The [installer location setting](https://learn.chatgpt.com/docs/config-file/environment-variables#installer-variables)
places the visible command in this runtime; its package cache and sign-in state
remain in the normal Linux Codex home. The following pins the version validated
with this profile, `0.164.0-alpha.11.1`:

```bash
curl -fsSL https://chatgpt.com/codex/install.sh -o "$runtime_dir/codex-install.sh"
CODEX_INSTALL_DIR="$runtime_dir/bin" sh "$runtime_dir/codex-install.sh" --release 0.164.0-alpha.11.1
"$runtime_dir/bin/codex" --version
"$runtime_dir/bin/codex" login --device-auth
```

An existing authorized Linux installation can instead be linked at
`runtime/bin/codex`; retain its complete package and companion resources.
Do not substitute a Windows executable. Before adopting another CLI version,
run the runner tests and sandbox probe below; this profile uses version-sensitive
CLI flags. The initial validation used WSL2 Ubuntu and Python 3.14.4.

Back in PowerShell, from the meta-workspace:

```powershell
.\scripts\peanut-review.ps1 doctor
```

Linux Codex needs its own supported sign-in. If `doctor` reports it missing,
run the installed Linux `codex login --device-auth` interactively and finish
the displayed sign-in instructions. Windows credential-store login is not
automatically available in WSL. The harness does not extract or copy credentials.
`doctor` reports authentication availability, never credential contents.
The PowerShell entrypoint writes a runtime-only Git defaults file containing
just Windows global `core.autocrlf` and `core.eol` (with system defaults as
fallback), then sets `GIT_CONFIG_GLOBAL`
for its WSL process. This keeps Windows-created checkouts consistent without
copying credential helpers or changing repository configuration. Repository
settings and `.gitattributes` still take precedence. Direct Linux invocation
uses the caller's existing Git configuration.
If the Linux runtime needs an additional trusted public certificate bundle,
place it at `runtime/ca-bundle.pem`. The entrypoint sets `CODEX_CA_CERTIFICATE`
for its child process only when that variable is not already configured.
It does not change the system trust store or contain private keys.

## Create and run a review

Use the currently authorized model and reasoning effort explicitly. Choose
two complementary roles from `reviews/personas.md`; the defaults are
`release-contracts` and `test-evidence`. GPU work can select `gpu-isa` (Lisa)
and `gpu-modeling` (Simone) where those concerns match the change.

```powershell
.\scripts\peanut-review.ps1 init --source C:\Dev\example-repo --base trunk `
  --model '<authorized-model>' --effort '<authorized-effort>' `
  --persona release-contracts --persona test-evidence
```

`init` prints the new session path and launches no workers. Paths passed via
`--source`, `--session` and `--session-root` may be Windows or Linux paths.
The checkout must be clean and at the head to review. Its base, merge-base,
head, model and roles are recorded. No source files or retention refs are
written. Keep the checkout available and unchanged until the review finishes.

Use the printed path for the next commands:

```powershell
.\scripts\peanut-review.ps1 run --session '<session-path>' --dry-run
.\scripts\peanut-review.ps1 run --session '<session-path>'
.\scripts\peanut-review.ps1 status --session '<session-path>'
.\scripts\peanut-review.ps1 cancel --session '<session-path>'
```

`run` starts the reviewers, waits for successful process exits and completion
signals, then does the same for the curator. It exports the curated result
only after checking the source snapshot again. A completion signal from a
still-running or failed process is insufficient. An interrupted controller can
resume with `run`; failed workers need log inspection and an explicit
`--retry-failed`. Failures remain incomplete, never approval evidence.
Codex has up to 30 seconds after its completion signal to exit cleanly, capped
by its existing deadline. A process killed during shutdown is still incomplete.

## Boundaries and iteration

### Related changes and coverage

For a review that depends on another pending producer, consumer or workflow
change, pass each available clean checkout at initialization:

```powershell
.\scripts\peanut-review.ps1 init --source C:\Dev\consumer --base main `
  --related-source C:\Dev\producer --model '<authorized-model>' --effort '<authorized-effort>'
```

Up to four related sources are pinned by canonical path and HEAD in the
protected session snapshot. Both reviewers and curator receive a neutral input
manifest. Dirty or changed related sources invalidate the review, just like a
changed primary source. No source is fetched or modified by this option. Supply
only relevant authorized inputs; private tracker content is not review context.

New sessions require `coverage/<agent>.json` from both reviewers and curator,
covering producer/consumer contracts, alternate entrypoints, validation before
effects, moved workflow behavior, shared callers and declared integrations.
The generated prompt supplies the schema. Applicable areas need concrete
evidence; inapplicable areas need a reason. Missing/stale records, materially
unverified contracts or unchecked declared integrations withhold approval.
`complete` still means that processes and curation finished; the separately
exported `recommendation` may be `wait_for_evidence` or `request_changes`.
Coverage is reviewer-attested and cannot guarantee correctness. Existing
sessions retain their original provenance and are not retroactively regraded.

The integration replay can be generated with:

```sh
python scripts/review_quality_fixture.py --scenario integration --output /path/to/new-inputs
```

Pass its primary source/base and its `related_sources` checkout to normal init.
This case checks interacting metadata changes, validation before allocation,
and policy lost while extracting a helper, alongside a compatible empty-work
control. Keep the expected outcomes outside the source shown to reviewers.

- Default per-agent timeout: 15 minutes; overall deadline: 30 minutes from
  the first launch. `init --timeout` and `--max-seconds` can tighten these.
- The persisted policy permits at most three concurrent worker processes,
  nine launches, two normal attempts per agent and one failed-run retry per
  agent. Reopening a session does not reset its deadline or launch history.
  Policy, launch ledger and source snapshot live under the session's protected
  `.codex/peanut-review` directory, outside worker write access.
- The Codex process starts in session scratch and can write only within the
  session. Source and session roots must be disjoint. This is write isolation;
  the legacy sandbox does not confine reads to only the source repository.
- Shell network access is disabled. Model-provider communication still uses
  the authenticated Codex runtime. The profile disables SSH and other runners.
- Ambient user/project approval rules and user configuration are not inherited;
  managed restrictions still apply. Nested agents, connected apps, browser and
  computer control, and web search are disabled for these local review workers.
- These are process/time bounds, not a provider token or monetary spend cap.
  Run on demand; do not schedule unattended reviews with this profile.
- Read the result and verification notes before publishing. This entrypoint
  exposes no GitHub write operation and makes no commits or source edits.

For authorized development, use a reviewed finding ID to record a fix or
rebuttal, make changes outside the review workers, and run relevant tests.
A changed source snapshot needs a new initialized session; retain the prior
session and record the relationship when carrying findings forward. The native
review-panel workflow also supports focused follow-up reviews of uncommitted
patches. Neither workflow treats old anchors as current after a head change.

Sessions and runtime dependencies belong in local ignored cache storage.
Do not upload private source, logs, or tracker context in shared review files.
The shared personas contain review priorities, not private knowledge-base
content. A synthetic lifecycle test demonstrates orchestration behavior;
it does not establish model review quality or measured cost savings.

## Verification

### Learning from later feedback

Use the review panel's [feedback-learning workflow](../../skills/review-panel/references/feedback-learning.md)
to distinguish a missed scenario from an incomplete run, changed source, or a
known-answer closure check. Keep case evidence local. Session initialization
copies the selected personas and routes both reviewers and curator to the
applicable [regression probes](../../skills/review-panel/references/regression-probes.md).
This changes review instructions; it does not train model weights.

For a small fictional replay, create a fresh repository outside the harness:

```sh
python scripts/review_quality_fixture.py --output /path/to/new-replay-source
```

The command prints the source, base and candidate SHAs. Pass that source and
base to the normal PowerShell `init` and `run` commands above. Keep the expected
outcomes outside the review source: the fixture's behavioral tests establish two
defects and a compatible empty-selection control. Compare retained comments with
those outcomes only after reviewers and curator finish. Record missed defects
and false positives; a passing replay qualifies these examples, not overall
review quality. The generator never invokes a model or a remote service.

From the tool directory in the isolated WSL runtime:

```sh
python -m pytest -o addopts= -q tests/test_local_policy.py tests/test_codex_runner.py tests/test_workspace_review.py
python scripts/local_pilot.py
python scripts/check_sandbox.py
```

The lifecycle pilot uses a clearly identified fake model runner. The sandbox
probe executes disposable fixtures through the installed Codex CLI's local
`command/exec` API with the runner's legacy write/network policy; it makes no
model call. It checks session writes, source/policy/outside write denial and
network denial. A live model review also requires working Linux sign-in.
See [upstream provenance](UPSTREAM.md) before updating the imported source.
