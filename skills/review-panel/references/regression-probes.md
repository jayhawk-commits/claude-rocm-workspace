# Regression probes for changed contracts

Use only the rows reached by the changed code. These are hypotheses to test,
not automatic findings or a request for unrelated hardening. Establish a valid
caller, distinguish the base, and retain a compatible negative control.

| Changed boundary | Distinguishing probe |
| --- | --- |
| Shared tooling or a new caller argument | Run the first deployable change against the currently selected callee revision, before companion changes land. Trace the actual checkout and capability; a combined-stack pass is separate evidence. |
| Concurrent producer/consumer changes | Compare each declared pending source alone and together. Feed a real new producer record into the real consumer without mocking identity/schema validation; cover older supported records too. Textual conflicts and individually passing branches do not establish compatibility. |
| Validation before durable effects | Feed an input that the selected runtime schema rejects, then check whether IDs, reservations or published state changed before rejection. Validate using the schema actually selected by orchestration, not only a metadata projection helper. |
| Extracted workflow or reusable job | Compare the previous caller's effective retry policy, credential scope, permissions, working directory, timeout and concurrency lifetime with the new call chain. A helper's passing tests do not establish that its caller retained required settings. |
| Legacy entrypoints during cutover | Enumerate still-runnable refs and commands that can mutate the same namespace. A guard in new code does not constrain older deployed writers; document or verify enforcement separately from operational advice. |
| Shared helper or namespace migration | Exercise an existing caller outside the feature's headline scope. Compare configured root names and lookup/create behavior; test missing prerequisites and preserve intentional identity/ownership decisions. |
| Permanent history and evolving schemas | Place a valid older record beside a new record, then discover, allocate and clean up. Check that active-resume validation remains strict without applying the latest payload schema to every historical identity. |
| Empty work and audience selection | Distinguish a valid empty inventory from malformed types, duplicate identities, an unknown selection and a populated inventory filtered to no work. Check explicit historical inputs independently of a moving default. |
| Publication guards | Evaluate meaningful true/false combinations in the actual workflow or shell path. Invert an operator in scratch and see whether the proposed coverage distinguishes it. A substring check can accept the unsafe condition too. |
| Exact-inventory resume | Start with an incomplete upload, retry after a rename or removal, and verify convergence within that destination. Preserve siblings and immutable completed checkpoints. |
| Generated files and user paths | Materialize a selected payload using a path reserved for generated metadata. Verify rejection or namespace separation before any payload is overwritten. |
| Restored provenance | Restore a record with and without each revision field; verify that reported source, proposed change and tooling identities retain their meanings rather than substituting a different available hash. |
| Credential scope | Follow secrets into dependency installation and setup; check whether only consuming steps receive them. Establish the code and trust boundary before describing exposure. |
| Selective validation triggers | Change a shared selector or policy dependency alone and trace which gates actually run. Test-file registration and a manual full-suite pass are separate from event/path-filter coverage. |
| Broad mechanical edits | Inspect unintended encoding or content churn outside the feature and exercise affected runtime strings. Distinguish a visible behavior regression from comment-only cleanup. |

Record the probe and the consumer it covers in a session note, including any
missing prerequisites. A source inspection or a synthetic probe can establish a
specific issue; neither qualifies an untested live deployment.

New workspace sessions also require a coverage record from each reviewer and
the curator. Record concrete source/probe evidence for applicable contracts;
passing test counts alone do not account for mocked boundaries. An unverified
material contract or unchecked declared integration prevents approval. This is
evidence accounting, not proof that an asserted check was performed correctly.
Name a specific missing contract when marking material evidence unverified.
Lack of live service access does not prevent inspecting retry inheritance,
checkout paths or lock scope in source; keep those checks separate from live
qualification outside the review scope.
