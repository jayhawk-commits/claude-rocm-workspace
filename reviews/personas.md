# Review personas

Personas define a review scope and evidence standard. Use the
[review-panel skill](../skills/review-panel/SKILL.md) for delegation, fixed
review inputs, run records, curation and stopping rules. Read only the persona
references selected for the change.

The [local Peanut Review harness](../tools/peanut-review/LOCAL_SETUP.md) uses
these same canonical files with two selected reviewers and a curator. Choose
it when persistent comments, resumable inspection or supervised processes are
useful. Keep the initial assessments independent and validate the curated
result against the recorded source snapshot.

| Role | Select for | Canonical reference |
| --- | --- | --- |
| CI contracts | Workflows, callers, runner routing, matrices and summaries | [ci-contracts](../skills/review-panel/references/personas/ci-contracts.md) |
| Build and packaging | Dependencies, build configuration, artifacts and installation | [build-packaging](../skills/review-panel/references/personas/build-packaging.md) |
| Test evidence | Behavioral changes, regression coverage and uncertain findings | [test-evidence](../skills/review-panel/references/personas/test-evidence.md) |
| Release contracts | Schemas, manifests and producer/consumer compatibility | [release-contracts](../skills/review-panel/references/personas/release-contracts.md) |
| GPU ISA / Lisa | Instruction, numerical, runtime and synchronization semantics | [gpu-isa](../skills/review-panel/references/personas/gpu-isa.md) |
| GPU modeling / Simone | Simulation state, scheduling, timing and model fidelity | [gpu-modeling](../skills/review-panel/references/personas/gpu-modeling.md) |

For a panel, start with two complementary roles plus the coordinating agent.
Add a third specialist only when the changed behavior justifies it and the
runtime's concurrency limit allows it. A focused ordinary review can use a
single reference without starting a panel. These are selection examples, not
mandatory combinations:

| Change | Useful starting lineup |
| --- | --- |
| Reusable workflow or runner selection | CI contracts + test evidence |
| Dependency or installed artifact change | Build and packaging + test evidence |
| Manifest/schema change with downstream consumers | Release contracts + test evidence |
| Artifact metadata and installation change | Release contracts + build and packaging |
| Instruction semantics or generator change | GPU ISA + test evidence |
| Simulator scheduling or timing change | GPU modeling + test evidence |
| Shared ISA and simulator execution behavior | GPU ISA + GPU modeling |

Lisa and Simone are optional display aliases for scoped roles. They do not
represent people participating in the review or separately trained experts.
The role content does not select a model, runtime or permission level.

Reviewers form their initial assessments independently from the same frozen
inputs. Different personas on the same model are not independent evidence of
correctness: source, tests, documentation and relevant CI must support the
conclusion. The coordinator validates findings, removes duplicates, preserves
substantive disagreements and writes the final comments in the user's voice.

Every role may skip an unrelated change. Record that outcome distinctly from
a completed review with no findings; a skipped, failed or incomplete review
does not support approval. Follow the existing
[review guidelines](REVIEW_GUIDELINES.md) and current workspace instructions
for evidence, severity and final output.
