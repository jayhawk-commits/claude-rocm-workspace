# Code Review Guidelines

Use these guidelines for focused reviews and the
[review panel](../skills/review-panel/SKILL.md). Apply the user's current review
preferences and repository-specific requirements. Older examples in domain
checklists are investigation prompts, not automatic severity decisions.

## Review Status Levels

Lead with actionable findings, ordered by severity, and one recommendation:

- **APPROVED:** No substantive blocker found within the completed review scope.
  State meaningful verification limits; approval is not a guarantee of correctness.
- **CHANGES REQUESTED:** A supported defect or unmet applicable requirement needs
  correction before approval. Explain the concrete trigger and impact.
- **WAIT FOR EVIDENCE:** A material uncertainty or incomplete review prevents a
  recommendation. Name the specific test, CI result, source or reviewer needed.

A failed reviewer, scope skip, empty report or green CI run alone is not approval
evidence. Do not invent findings to populate a template.

## Issue Severity Categories

| Category | Use when |
| --- | --- |
| **BLOCKING** | A demonstrated or well-supported correctness, security, compatibility or critical performance defect must be fixed, or an authoritative required check is unmet. |
| **IMPORTANT** | A concrete issue merits correction but does not prevent approval; explain the impact. |
| **SUGGESTION** | An optional improvement is useful enough to mention. Omit personal preferences and low-value nits. |
| **FUTURE WORK** | The concern is existing behavior or independent work outside the change. Keep it separate from introduced defects. |

Severity follows impact and evidence, not the reviewer persona or a keyword.
Style deviations, unused parameters, missing comments, mock counts, version
numbers and additional test opportunities are not automatically blockers.

## Decision Framework

Before retaining a finding:

1. Establish the changed contract and a valid trigger. Compare base and head to
   distinguish an introduced defect from existing behavior or source-data issues.
2. Follow actual callers and consumers. Check whether production prerequisites
   or validation make the suspected case unreachable.
3. Seek a distinguishing test, relevant CI evidence or authoritative source.
   Describe uncertainty precisely when the available evidence is insufficient.
4. Explain the consequence and smallest useful correction. Separate optional
   redesign, unrelated cleanup and follow-up work.

### Key Principle: Cleanup Scope

Trace affected callers when removing a feature or changing an interface. A
remaining caller that fails is a defect; harmless dead code is not equivalent
to a runtime failure. Request cleanup in proportion to its consequences and any
verified repository rule. Do not demand unrelated refactoring.

### Key Principle: API Renames

For internal interfaces, verify affected callers in the repository. For public
or cross-repository interfaces, inspect actual consumers and determine whether
compatibility or coordinated migration is needed. Absence of an in-repository
caller does not establish that an exported interface is unused.

## Evidence-Based Review (CI Validation)

Use CI to test hypotheses from the diff. Record the run's source revision,
workflow, trigger and relevant platform. A passing run supports only the paths
it exercised; it does not disprove a finding on an untested path.

1. Fetch relevant job and step data, for example:

   ```bash
   gh api repos/OWNER/REPO/actions/jobs/JOB_ID \
     --jq '{steps: [.steps[] | {name, conclusion, started_at, completed_at}]}'
   ```

2. Compare with a suitable baseline on the actual target branch, accounting for
   trigger, runner and configuration differences. Do not assume the base is
   `main` or treat an unrelated green run as evidence for the reviewed head.
3. Investigate timing or cache anomalies using logs and artifact contents.
   A zero-duration cache step can mean a hit, skip or coarse timing; duration
   alone does not establish a defect.
4. Keep confirmed findings, drop disproven ones, and state remaining evidence
   gaps separately. Put test and CI details in verification notes unless the
   author needs them to understand the requested action.

| Signal | Follow-up evidence |
| --- | --- |
| Cache save/restore timing | Cache key, hit/miss, skipped conditions and logs |
| Build duration change | Runner/configuration differences, steps and repeated measurements |
| Failed or skipped step | Failure log, trigger and dependency conditions |
| Configure output | Effective options and source checkout consumed |
| Artifact size/content | Expected component ownership and actual packaged files |

When CI is unavailable, a source-level defect can still be actionable. Explain
its trigger and reasoning; do not elevate an untested possibility to a confirmed
failure. Use **WAIT FOR EVIDENCE** only when the missing evidence materially
prevents a recommendation.

## Linking to Source Code

Give the exact repository-relative path and current diff line(s) outside each
copy-pastable comment block. Distinguish changed lines where a comment can be
posted from unchanged supporting context. Recheck anchors against the latest
reviewed head before delivery.

Use commit-permalink links for supporting public source, especially files outside
the diff. If citing a convention, read the authoritative section, verify that it
applies, and include its Markdown link in the comment. Keep private context out
of public review artifacts.

## Review Structure Template

Record repository/PR or branch, target base SHA, merge-base SHA, reviewed head
SHA, date and scope. Present the recommendation and supported findings in severity
order. For each comment worth posting, use this shape:

````markdown
**CHANGES REQUESTED** — The changed input is not passed by an existing caller.

`.github/workflows/example.yml`, lines 42–44 (changed lines at the reviewed head)

```markdown
The existing caller omits `target`, so this path cannot select a runner after the change. Please update that caller or preserve a compatible default.
```

Overall review comment:

```markdown
The new input needs to reach the existing caller before this can merge. Please address that path and verify its workflow invocation.
```

Verification: relevant source, tests and CI, plus material limits.
````

The example is illustrative, not a finding. Each comment should be one or two
plain-language sentences with the impact and requested action. Preserve literal
backticks around identifiers. Keep coordinates, severity, test details and caveats
outside the comment unless needed by the author.

Include a separate one- or two-sentence overall comment even for an approval.
Write in the user's voice, respect established decisions, and do not invent
prior agreement or authorship. Claim independent review only when another agent
performed it. Review requests do not authorize source edits or GitHub publishing.

## Specialized Review Guidelines

Read only relevant domain guidance. Apply the evidence and severity rules above
if an older checklist uses blanket blocking language.

| PR Type | Guideline File |
| --- | --- |
| Tests | [guidelines/tests.md](guidelines/tests.md) |
| Documentation | [guidelines/documentation.md](guidelines/documentation.md) |
| Artifacts | [guidelines/pr_patterns.md](guidelines/pr_patterns.md#pattern-adds-or-modifies-artifacts) |
| GitHub Actions | [guidelines/github_actions.md](guidelines/github_actions.md) |
| PR hygiene | [guidelines/pr_hygiene.md](guidelines/pr_hygiene.md) |
| Common PR patterns | [guidelines/pr_patterns.md](guidelines/pr_patterns.md) |
| Security | [guidelines/security.md](guidelines/security.md) |

### Tests and Documentation

Check whether tests distinguish the changed behavior from a plausible incorrect
implementation. Mocks should not replace the behavior being verified; a mock
count only prompts investigation. Prefer realistic inputs and useful regression
tests over tests that reproduce implementation details.

Flag documentation that misleads users about behavior or leaves an important
migration unsupported. Dated examples and versioned contracts can be appropriate;
concrete numbers are not inherently stale.

### GitHub Actions

Trace dependencies through imported helpers, reusable-workflow callers,
event-specific input types and defaults, and the checkout consumed by build/test
steps. Verify summary and failure propagation for skipped jobs. Changing an input
context alone does not establish a regression; check the trigger and values.

TheRock's [workflow logic guidance](https://github.com/ROCm/TheRock/blob/main/docs/development/style_guides/github_actions_style_guide.md#prefer-python-scripts-over-inline-bash)
prefers testable Python scripts where practical and leaves trivial Bash to
judgment. It is not a blanket prohibition on inline code. Explain the relevant
maintainability or testing consequence when proposing extraction.

### Python Error Handling

Trace what callers observe on failure. For TheRock, consult the
[fail-fast guidance](https://github.com/ROCm/TheRock/blob/main/docs/development/style_guides/python_style_guide.md#fail-fast-behavior).
Silent partial output or swallowed failures can be substantive defects; an
isolated `sys.exit`, warning or `except` does not establish one without its
execution context and applicable requirements.

### Security and Artifacts

Inspect possible credential exposure and reachable injection paths without
reproducing secret values. Opaque extensions alone do not prove private material
is present; inspect authorized evidence or name the gap.

For artifacts, compare ownership for the same stage path and component, check
that components are activated, and trace old descriptors after a split. Confirm
package behavior before calling overlapping patterns a duplicate-file defect.

## Review Checklist

- [ ] Recommendation is approve, request changes, or wait for specific evidence.
- [ ] Base, merge-base, head and scope are recorded; current anchors match.
- [ ] Findings describe valid triggers, actual consumers, impact and evidence.
- [ ] Introduced defects, existing behavior, data issues and follow-ups are distinct.
- [ ] CI claims apply to the reviewed revision and relevant execution path.
- [ ] Posting comments and the overall comment are concise and copy-pastable.
- [ ] Style claims cite the verified authoritative section.
- [ ] Failed or skipped reviewer work is stated, not treated as approval.
- [ ] Artifacts preserve the workspace's confidentiality boundaries.
