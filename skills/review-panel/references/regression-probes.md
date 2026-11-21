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
| Permanent history and evolving schemas | Carry a real record with explicit output definitions and per-output fingerprints through every reader, gate and aggregate-set validator after the plan algorithm changes. Cover legacy records separately; a legacy-only fixture can bypass modern validation. Historical readers use the recorded contract while active resume stays strict. |
| Empty work and audience selection | Distinguish a valid empty inventory from malformed types, duplicate identities, an unknown selection and a populated inventory filtered to no work. Check emptiness before selecting the first entry, and verify all-complete retries avoid empty matrices while still recovering downstream work. |
| Publication guards | Evaluate meaningful true/false combinations in the actual workflow or shell path. Invert an operator in scratch and see whether the proposed coverage distinguishes it. A substring check can accept the unsafe condition too. |
| Exact-inventory resume | Start with an incomplete upload, retry after a rename or removal, and verify convergence within that destination. Preserve siblings and immutable completed checkpoints. |
| Generated files and user paths | Materialize a selected payload using a path reserved for generated metadata. Verify rejection or namespace separation before any payload is overwritten. |
| Restored provenance | Restore a record with and without each revision field; verify that reported source, proposed change and tooling identities retain their meanings rather than substituting a different available hash. |
| Credential scope | Follow secrets into dependency installation and setup; check whether only consuming steps receive them. Establish the code and trust boundary before describing exposure. |
| Selective validation triggers | Change a shared selector or policy dependency alone and trace which gates actually run. Test-file registration and a manual full-suite pass are separate from event/path-filter coverage. |
| Broad mechanical edits | Inspect unintended encoding or content churn outside the feature and exercise affected runtime strings. Distinguish a visible behavior regression from comment-only cleanup. |
| Guard placement and restored requests | Trace all work before a guard, including checkout, dependency installation and credentialed reads. Exercise both fresh and restored paths; a guard inside a skipped resolver cannot protect retries. Preserve allowed read-only or dry-run entrypoints. |
| Bounded maintenance | Test a backlog at the limit and above it across successive invocations. A cap should preserve the documented progress policy, not silently prevent all cleanup forever; retain per-operation authority checks and protected records. |
| Credential interface compatibility | Use distinct synthetic values when both old and new secret names are supplied, then test each name alone and neither. Follow actual historical helpers and reusable declarations; equal fixtures can hide accidental aliasing. Require fallback only where the supported caller contract promises it. |
| Per-output completion and downstream jobs | Establish whether publication is atomic or independent per output. For independent outputs, test mixed success, failure, skipped builds, invalid or unreadable receipts, all-complete retry and cancellation. Follow implicit job-success gating as well as explicit conditions, preserve failure visibility, and verify completion before expensive work. Do not invent a partial-publication policy. |
| State inferred from observations | Replay at least two reads: queued/unknown, then preview/empty/final; let an unrelated operation finish before the intended one becomes visible. Unknown is not proof of a negative classification. Follow classification into pending-hold removal and retry selection, not only the classifier's return value. |
| Ambiguous write outcome | Persist an identity or counter, then fail, cancel or lose the acknowledgement before the operation reports success. Feed the real durable state to the real retry consumer. A failed step does not prove no allocation exists; also retain a genuinely rejected-before-write control. |
| Classified and paginated search | Put only excluded records before the wanted record, both at cap-plus-one and across a page boundary. An early-stop predicate must use the same classification as the final selector. Exhaustion must report an incomplete decision rather than silently masquerading as absence or a different read failure. |
| Cache and attempt identity | Change the execution attempt or revision between listing and detail reads. Check empty and transient detail results before caching them as final; distinguish a completed summary from complete evidence for the same attempt. Preserve valid immutable-result reuse. |

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

New sessions record these stateful checks under temporal_contracts, with a
sequence and independent oracle for each applicable scenario. Review the
remaining changed invariants after finding an issue. On a re-review, distinguish
known-comment closure, newly introduced assumptions and same-head misses.
