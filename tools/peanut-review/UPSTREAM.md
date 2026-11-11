# Upstream provenance and local changes

Imported from [sjain-stanford/claude-workspace](https://github.com/sjain-stanford/claude-workspace/tree/213a4604c6e97521634af4b873b07b45d3ce7db0/tools/peanut-review)
at revision `213a4604c6e97521634af4b873b07b45d3ce7db0`, retaining its source
layout and [Apache-2.0 license](LICENSE). The harness originates in
[kuhar/agent-workspace](https://github.com/kuhar/agent-workspace/tree/b5939837aeb58bff0590e7bc91e669fae3fb5814/tools/peanut-review).
The latter revision was the comparison baseline, not a second import.

The upstream [README](README.md) describes the general harness. Our
[local setup](LOCAL_SETUP.md) is the supported profile for this workspace.
It adds a WSL entrypoint, shared workspace personas, a launch ledger with
execution bounds, clean pinned-source checks, and explicit curator/process
completion. The local Codex runner uses a session-only write sandbox; remote
Codex execution fails closed until its permission path is validated.
Session creation can opt out of upstream retention refs so this profile does
not modify the reviewed repository. Upstream provider and publishing code is
retained for provenance, but the local entrypoint does not expose those routes.

For an update, compare a new upstream revision with this pinned import,
reapply the local changes, and run the local policy, runner, entrypoint and
lifecycle tests before using it. Do not overwrite the folder from a moving
branch or import upstream account settings, credentials, or workspace rules.
