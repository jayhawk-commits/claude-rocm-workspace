# CI contracts

Use for changed workflows, workflow helpers, runner routing, matrices, artifact
handoffs, and status summaries. Skip when the change does not affect those
contracts; select only the relevant portions of a mixed patch.

Investigate the changed path end to end:

- Which event supplies each input, and how do callers, reusable workflows and
  scripts interpret missing, empty, false or default values?
- Do runner labels and matrix filters select the intended platforms and GPU
  families? Can an empty matrix or skipped dependency produce a misleading
  success summary?
- Does each checkout feed the build or test that claims to use it? Trace source
  directories, revisions, working directories and downloaded artifacts.
- Are script dependencies available at the point of execution, including
  imports reached through local helpers?
- Can concurrent runs, retries, cache reuse or partial failures change the
  outcome? Follow artifact names, keys and completion conditions.

Use actual callers and consumers, the repository's workflow conventions, and
relevant PR/baseline CI as evidence. Compare equivalent configurations; a
successful run qualifies only the paths it exercised. Validate a style claim
against the current authoritative section before proposing a comment.

Avoid treating all inline code as prohibited, skipped tests as passing tests,
or a changed duration as proof of a cache regression. Describe the valid
trigger and concrete consequence before assigning severity.

Local context: [CI specialist](../../../../.claude/agents/ci-pipeline.md).
