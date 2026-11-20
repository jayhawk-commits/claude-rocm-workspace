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
- For a tooling cutover, trace the revisions actually executed by existing
  callers. Check whether landing this PR first requires an interface available
  only in an unmerged companion; testing the combined stack does not establish
  that either intermediate deployment works.
- For empty-work gates, check false, true and explicitly selected historical
  inputs. A bypass before validation must not turn malformed or missing input
  into an empty success; a moving default must not suppress an explicit backfill.
- Follow credential scope through setup and dependency installation, not only
  the command that uses the secret. Prefer the narrow consuming step when other
  steps execute third-party installation code with no need for that credential.
- When a selector or shared constant changes, trace selective path filters and
  gate triggers as consumers too. A helper-only change must reach the validation
  that protects its resulting platform or publication selection.
- When extracting a job, compare the old effective environment and call chain
  with the new one: retry ownership/window, credentials, working directory,
  permission boundaries and parent lock lifetime. Follow reusable calls through
  completion; moving work after publication can still hold its caller's lock.
- Trace validation to the first durable mutation. A later build validation does
  not prevent invalid input from consuming a reservation in an earlier job.

Use actual callers and consumers, the repository's workflow conventions, and
relevant PR/baseline CI as evidence. Compare equivalent configurations; a
successful run qualifies only the paths it exercised. Validate a style claim
against the current authoritative section before proposing a comment.

Avoid treating all inline code as prohibited, skipped tests as passing tests,
or a changed duration as proof of a cache regression. Describe the valid
trigger and concrete consequence before assigning severity.

Local context: [CI specialist](../../../../.claude/agents/ci-pipeline.md).
