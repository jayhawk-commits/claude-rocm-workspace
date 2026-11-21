# Release contracts

Use for manifests, schemas, package metadata, release selection, and changes
that cross producer/consumer or repository boundaries. Skip unrelated release
notes and presentation changes unless they change a supported user contract.

Follow a representative value from creation to use:

- Which producer writes each field, and which readers interpret it? Check
  validators, tooling, installation paths and downstream defaults.
- Trace authority across partial success: persist the record/counter, then
  fail before the step reports success. A failed or cancelled step is not proof
  of an absent reservation. Check real recovery and supersession consumers.
- Carry uncertain observations through classification, holds, search and retry
  decisions. Unknown is not a confirmed exclusion; a classification-sensitive
  selector cannot use a weaker pagination stopping rule. Test the wanted
  record beyond excluded records and at each applicable bound.
- Do identifiers, versions, platform names and package formats retain their
  meaning across conversion and serialization? Look for silently dropped or
  reinterpreted values.
- Are absent, empty, unknown and legacy values handled according to the
  supported schema? Verify whether a migration or coordinated rollout is
  needed instead of inventing compatibility requirements.
- Do selection and fallback rules choose a complete, compatible artifact set?
  Trace provenance and integrity metadata where consumers rely on them.
- What happens if only part of the new metadata or artifact set is available?
  Check that a failed operation does not masquerade as a complete release.
- For durable records, carry a valid older record through discovery, numbering,
  cleanup and active resume after a schema or fingerprint change. Historical
  identity checks and active payload validation can require different contracts;
  a newly written record alone cannot establish upgrade compatibility.
- Trace historical reads through aggregate output-set validators too. Exercise
  explicit package definitions and per-output plan fingerprints as well as legacy
  shapes; permissive legacy fixtures can skip the validator that rejects history.
- Check completion receipts before expensive rebuilds, then check downstream
  recovery on an all-complete retry. Distinguish absent, invalid and unreadable
  receipts, and use the documented per-output or atomic publication policy.
- For bounded cleanup, exercise more eligible objects than the cap and a second
  sweep. Verify progress, permanent history and authority checks before deletion.
- For resumable exact-inventory uploads, retry with a smaller or renamed file
  set. Check obsolete files, destination confinement, sibling preservation and
  completed checkpoints. For user-selected payload paths, check collisions with
  generated metadata as well as collisions between payloads.
- On restored runs, verify that each reported revision retains its original
  meaning. A merge, input or tooling revision is not a substitute for a missing
  original revision; preserve an explicit unknown when history lacks the field.
- When a backend changes, check that timestamps and publication predicates keep
  their meaning for every consumer, including historical selection after a
  copy. Follow listing depth down to remote enumeration and growth limits. Use
  the focused [backend migration guidance](../../../../reviews/guidelines/backend-migrations.md)
  for relevant transition probes and activation evidence.

Use actual schemas, representative manifests, producer/consumer call sites
and supported-version policy. Establish the revisions being compared and any
external consumer assumptions. Prefer a focused round trip or consumer check
over a synthetic parser-only test.

Separate a code regression from malformed source data and a proposed future
schema. Do not infer undocumented rollout guarantees or treat every metadata
addition as a breaking change.
