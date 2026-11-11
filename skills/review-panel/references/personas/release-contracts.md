# Release contracts

Use for manifests, schemas, package metadata, release selection, and changes
that cross producer/consumer or repository boundaries. Skip unrelated release
notes and presentation changes unless they change a supported user contract.

Follow a representative value from creation to use:

- Which producer writes each field, and which readers interpret it? Check
  validators, tooling, installation paths and downstream defaults.
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

Use actual schemas, representative manifests, producer/consumer call sites
and supported-version policy. Establish the revisions being compared and any
external consumer assumptions. Prefer a focused round trip or consumer check
over a synthetic parser-only test.

Separate a code regression from malformed source data and a proposed future
schema. Do not infer undocumented rollout guarantees or treat every metadata
addition as a breaking change.
