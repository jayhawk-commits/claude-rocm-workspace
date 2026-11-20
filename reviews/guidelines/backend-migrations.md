# Backend migration review

Use for storage or persistence adapters, data copies, backend flags and shadow
reads. Select the relevant probes below; this is not a requirement to exercise
live production infrastructure on every review.

## Identify the invariant, then the representation

Trace fields used for ordering, historical baselines, identity and publication
through their real consumers. Object arrival, last modification, original
creation and release time are different facts. A backend exposing a similarly
named timestamp does not establish equivalent semantics. Check a copy/backfill
with reordered arrival times and a later metadata rewrite: historical choices
should change only where the product contract permits it. Prefer preserved
source metadata where a consumer needs the original event time.

## Bound the backend work, not just the returned view

Follow an apparent shallow listing down to the remote request. If depth is
filtered after a recursive enumeration, all descendants still consume pages,
memory, time and key limits. Relate the bound to channel growth and retention,
then trace a cap or timeout through every caller: does one channel stop a whole
refresh? A small fixture with a reduced cap can expose this without a live
large dataset. Consider per-prefix or incremental enumeration when appropriate.

## Check transitions and adversarial shapes

- Follow the work before a final skip: incomplete entries may still trigger
  metadata reads, installer resolution or retries on every pass. Measure call
  counts and retained state, not just the final response.
- Compare publication predicates across services. Use metadata-only entries, an
  unrelated ZIP beside a missing expected payload, a missing side-car and a
  pre-existing cached record. Confirm that a successful listing does not invent
  a download URL for an absent object.
- Start from an existing store as well as an empty one. Check first-refresh
  workload, URL provenance, date stability, failure/recovery and rollback.
- Follow the actual await graph for shadow reads. A timeout budget bounds added
  latency; it does not make a join nonblocking. Distinguish compared-equal,
  different, failed and timed-out/not-compared outcomes. Quiet or throttled logs
  do not prove a complete migration; use an explicit comparison when needed.

## Separate code readiness from activation readiness

Record which modes and transitions the evidence exercised. If activation needs
environment evidence, name the unresolved property: reader access to published
URLs, exposure restrictions, role privileges, retention of committed objects,
the population/synchronization path, or a rollback procedure. Investigate only
relevant properties and do not infer deployed policy from example config or a
successful upload. Keep such evidence gaps distinct from demonstrated code
defects and from the default mode's merge recommendation.

Check the description and operational docs against actual behavior: changed
defaults and first-refresh costs, ordering/failure policy, timestamp meanings,
removed-module references and control coverage. A refactor can preserve data
while changing the request path or workload; “only imports changed” needs proof.

Passing controls establish the fixtures they contain. For each material
migration invariant, identify one witness that would fail under a plausible
incorrect implementation; do not replace this with assertion counts.
