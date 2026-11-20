# Learning from later review feedback

Use when the user asks to improve review quality from later human or CI findings.

1. Keep a local evidence ledger with the original reviewed base/head, completed
   session and outcome, later feedback, affected revision and disposition. An
   incomplete session, a changed head or a post-feedback review is not evidence
   that the original harness missed that issue.
2. Validate each claim against code and callers. Separate defects, evidence gaps,
   optional improvements and design decisions. Record why a confirmed defect
   escaped: missing scenario, weak oracle, missed consumer, curation loss or an
   execution/coverage failure. If the cause is unknown, leave it unknown.
3. Add the smallest reusable probe to the relevant persona or
   [regression probes](regression-probes.md). Keep private case details, links and
   source in the private ledger; use independently written fictional examples
   for shared fixtures. Preserve existing guidance and avoid turning suggestions
   into universal blockers.
4. Verify the official harness actually supplies the changed guidance to both
   reviewers and curator. Keep prompt-delivery tests separate from quality
   evidence. Replay a small faulty and compatible case without giving the
   reviewer the answer key; record misses and false positives. Replaying a known
   example is a regression check, not proof of general review improvement.
   When the miss involved interacting changes, replay that interaction with two
   frozen sources and independently passing branches, not just another isolated
   helper bug. Test that missing material coverage withholds approval as well as
   testing that model reviewers can find the seeded defects.
5. Re-review changed real heads through the official entrypoint when requested.
   Report the exact head and completion of both reviewers and curator. Native
   checks, test passes and older sessions must keep their own labels. Updating
   guidance changes future runs; it does not train model weights or update an
   already initialized session's copied personas.
