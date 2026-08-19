# AI Efficiency And Workflow Control

## Purpose And Scope

This document defines public-safe operating guidance for AI-assisted work in
this workspace. It records general engineering policy without reproducing
private source material, internal links, organization-specific observations, or
externally maintained numerical claims.

This is engineering guidance, not an approval process, fixed usage budget, or
compliance gate. Review it before deploying or scaling an automated workflow,
and apply any additional authoritative organizational checks outside this
public repository.

Normal interactive work and automated pipelines have different risk profiles.
The automation controls below apply to repeated or unattended workflows and
should not be imposed mechanically on every interactive session.

## Model Selection

Use task type, measured quality, and total workflow cost to choose a model:

- **Planning:** Use the most capable model available for architecture,
  cross-document synthesis, complex reasoning, constraint-heavy analysis, and
  orchestration logic.
- **Execution:** When quality evidence supports it, use a lighter model for
  routine implementation, formatting, log parsing, classification, extraction,
  bulk operations, and routine questions.
- **GPU and low-level engineering:** Treat GPU kernels, assembly, ISA reasoning,
  RTL generation, formal verification, kernel optimization, and ISA-level debug
  as a standing quality exception. Prefer the model that demonstrates adequate
  correctness rather than downgrading by default.
- **Total cost:** Include context replay, retries, correction cycles, and human
  rework. A lower generation price can still produce a more expensive workflow.
- **Cross-vendor evidence:** When comparable task-specific results exist, use
  them. Do not assume one vendor or model family is always the best choice.

## Token Efficiency For Interactive And Automated Work

### Prompt Caching

- Define and monitor a workload-appropriate prompt-cache objective when the
  platform exposes cache metrics.
- Confirm caching is actually active; configuration and fallback paths can
  silently disable it.
- Order prompt content as a stable prefix followed by changing content: system
  role and instructions, tool definitions, few-shot examples, history, then
  dynamic user or request data.
- Mark reusable static content with `cache_control` when the API supports it.
- Investigate unexpected cache misses before scaling the workflow; they may
  indicate a structural ordering problem.

### Context Growth

- Define a context-utilization checkpoint for long workflows and compact state
  well before the context limit.
- Treat sustained context growth as a quality and latency risk; measure the
  appropriate checkpoint for the model and workload.
- Read large, unchanged files once when practical and retain concise findings.
- Prefer a compact state artifact such as `state.json` or a task note over full
  transcript or output-log replay.
- Replace completed tool results with short summaries when the full result is no
  longer needed for verification.

### Output Length And Input Formats

- Set `max_tokens` explicitly whenever the interface exposes it.
- State the required output shape and size, such as JSON only, a short word
  limit, only changed lines, or only fields consumed by the next step.
- For repeated agent workflows, compare verbose reasoning output with a
  structured-result-only mode; keep verbose output only when it improves the
  measured result.
- Do not default to JSON for large model inputs. Compare compact formats such as
  CSV for flat data and YAML for nested data with the actual tokenizer, while
  preserving correctness and unambiguous parsing.
- Pre-convert PDFs and presentations to clean Markdown when appropriate, then
  measure the resulting token and quality impact for the workload.

### MCP, Tool Surface, And Reasoning Effort

- Configure only the MCP servers and tools needed for the workflow's task type.
- Keep invocation-time tool descriptions concise; move documentation that is not
  needed for selection or correct use out of the active description.
- If the configured tool surface makes selection noisy or adds substantial
  prompt overhead, prefer search-based discovery or deferred loading.
- Enable extended thinking or high reasoning effort deliberately. Set a specific
  effort level or budget instead of leaving the maximum as a default.
- Test extended thinking against a lighter setting and retain it only when the
  quality improvement justifies the full-run cost.
- In agentic workflows, estimate thinking usage across every step, not just one
  representative model call.

### System Prompt Design

- Keep the stable role, tools, and examples at the top and dynamic dates or user
  data at the bottom to preserve cacheability.
- Prefer scoped, conditional language over blanket, forceful instructions that
  can trigger unnecessary tools or reasoning.
- Add an explicit scope guardrail: do only what the request requires, without
  unsolicited features or defensive code.

## Additional Controls For Automated Workflows

### Execution Bounds

- Define explicit stopping conditions: maximum iterations or steps, success
  threshold, wall-clock limit, and, for optimization loops, a convergence rule.
- Set and enforce a maximum concurrent-agent count in orchestration code. When
  telemetry supports it, define an anomaly threshold that pauses unexpectedly
  concurrent runs.
- Enforce scope in orchestration or policy, not only in prompt text. Define the
  allowed repositories, paths, tools, actions, external systems, and mutation
  boundaries for the workflow.
- Bound exploration and debug loops so one failing item cannot consume
  unbounded tokens.
- Prefer demand-triggered execution over continuous polling. For scheduled work,
  document the frequency and estimated token cost per run.

### Failure And Cost Controls

- Use exponential backoff with a maximum retry count. Never retry indefinitely.
- Fail clearly on configuration errors instead of silently falling back to a
  different or unexpectedly expensive path.
- Define and document a workload-appropriate cost anomaly threshold. Treat a run
  that crosses it as a circuit-breaker event, not merely a warning.
- If a failure temporarily escalates work to a heavier model, record that state
  and reset it after the trigger clears.

### Human Review And Reliability

- Put human review checkpoints before consequential actions.
- Automated commits or file writes require a dry-run mode and an explicit
  approval path. Apply the same principle to deployments and external changes.
- Log results in a reviewable form rather than acting on them silently.
- When one AI step verifies another, use an independent reference or a different
  model family rather than having the same model grade itself.
- Break long chains into independently checked stages and define where a
  confident but wrong result will be caught before it propagates.
- Prefer deterministic validation when a specification, parser, test, schema, or
  invariant can establish correctness without another model call.

## Applying This In The Workspace

`AGENTS.md` and `CLAUDE.md` contain compact defaults for ordinary work. Read and
apply this full document before designing, reviewing, or scaling an LLM-backed
pipeline, scheduled agent, multi-agent system, or reusable prompt/tool surface.

Some controls depend on the surrounding product. An interactive agent may not
be able to change model routing, cache configuration, or `max_tokens` itself;
in that case, state the limitation rather than claiming the control is active.
