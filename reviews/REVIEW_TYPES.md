# Review Types and Focus Areas

These focus areas guide what to inspect; they do not set severity by themselves.
Apply [REVIEW_GUIDELINES.md](REVIEW_GUIDELINES.md) for evidence, impact and output.
For requested personas or substantive changes crossing domains, use the
[review panel](../skills/review-panel/SKILL.md) and [persona selection](personas.md).
Keep small focused reviews lightweight and load only relevant domain references.

---

## Review Type Overview

| Review Type | Focus Area | Best For |
|-------------|------------|----------|
| **Comprehensive** | All aspects | Final automated review |
| **Style** | Code formatting, conventions, readability | Ensuring consistency |
| **Tests** | Test coverage, edge cases, test quality | Validating correctness |
| **Documentation** | Comments, docstrings, guides | Knowledge transfer |
| **Architecture** | Design, patterns, structure | Big picture evaluation |
| **Security** | Vulnerabilities, secrets, validation | Risk assessment |
| **Performance** | Efficiency, scaling, resources | Optimization review |

---

## How to Request Reviews

### Single Review Type

Ask for a specific focused review:

```
"Review this PR with a focus on test coverage"
"Do a security review of these changes"
```

### Multiple Reviews in Parallel

Request multiple review types to run simultaneously:

```
"Run style, tests, and documentation reviews in parallel"
"Review this for architecture and security in parallel"
```

### Comprehensive Review (Default)

A comprehensive review covers all aspects:

```
"Review this PR"
"Review the changes on my branch"
```

---

## Review Type Definitions

### 1. Comprehensive Review

**Covers:** All aspects of code quality

**What it examines:**
- All other review types

**Output:** Single comprehensive review file with all findings

**When to use:** Final automated review covering all aspects

---

### 2. Style Review

**Focus:** Project conventions, readability

**Reference:** Read the active repository's authoritative conventions. For TheRock, use its [style guides](https://github.com/ROCm/TheRock/tree/main/docs/development/style_guides); verify the relevant section before citing it.

**What it examines:**
- Adherence to language-specific style guides:
  - [Python Style Guide](https://github.com/ROCm/TheRock/blob/main/docs/development/style_guides/python_style_guide.md) - type hints, dataclasses, error handling, pathlib, etc.
  - [CMake Style Guide](https://github.com/ROCm/TheRock/blob/main/docs/development/style_guides/cmake_style_guide.md)
  - [Bash Style Guide](https://github.com/ROCm/TheRock/blob/main/docs/development/style_guides/bash_style_guide.md)
  - [GitHub Actions Style Guide](https://github.com/ROCm/TheRock/blob/main/docs/development/style_guides/github_actions_style_guide.md)
- Naming conventions (variables, functions, classes)
- Code formatting and consistency
- File organization
- Import order and grouping
- Line length and complexity
- Use of language idioms
- Comments quality (not quantity)

**Severity guidelines:**
- ❌ BLOCKING: Violates a verified mandatory requirement with a concrete consequence
- ⚠️ IMPORTANT: Hurts readability significantly
- 💡 SUGGESTION: Minor style improvements

**When to use:**
- After major refactoring
- For new contributors
- When establishing patterns

---

### 3. Test Coverage Review

**Focus:** Test completeness and quality

**What it examines:**
- Test coverage for new functionality
- Edge case testing
- Error condition testing
- Integration test coverage
- Test quality and clarity
- Test maintainability
- Mocking and fixture usage
- Test naming and organization
- Missing test scenarios

**Severity guidelines:**
- ❌ BLOCKING: No tests for new critical functionality
- ⚠️ IMPORTANT: Missing tests for likely edge cases
- 💡 SUGGESTION: Additional test scenarios for completeness

**When to use:**
- New features
- Bug fixes
- Critical code paths
- Before release

---

### 4. Documentation Review

**Focus:** Code documentation and knowledge transfer

**What it examines:**
- Function/class docstrings
- Module-level documentation
- README updates
- API documentation
- Code comments (when/why/how)
- Usage examples
- Configuration documentation
- Migration guides (for breaking changes)
- Help text and error messages
- Changelog updates

**Severity guidelines:**
- ❌ BLOCKING: Missing migration or contract information prevents correct use of a changed API
- ⚠️ IMPORTANT: Complex code without explanation
- 💡 SUGGESTION: Additional examples or clarification

**When to use:**
- Public API changes
- Complex algorithms
- New features
- Breaking changes

---

### 5. Architecture Review

**Focus:** High-level design, patterns, and structure

**What it examines:**
- Design patterns used
- Abstraction levels
- Module boundaries
- Dependency management
- Code organization
- Extensibility considerations
- Technical debt implications
- Consistency with existing architecture
- Separation of concerns
- Coupling and cohesion
- Future maintainability

**Severity guidelines:**
- ❌ BLOCKING: Breaks a required interface, dependency or ownership invariant
- ⚠️ IMPORTANT: Creates technical debt or coupling issues
- 💡 SUGGESTION: Alternative design approaches

**When to use:**
- New major features
- Refactoring work
- Adding new dependencies
- Changing module structure

---

### 6. Security Review

**Focus:** Security vulnerabilities and risks

**What it examines:**
- Input validation
- SQL injection risks
- XSS vulnerabilities
- Command injection
- Path traversal
- Authentication/authorization
- Secret management
- Cryptography usage
- Dependency vulnerabilities
- Data exposure
- OWASP Top 10 issues
- Permission checks

**Severity guidelines:**
- ❌ BLOCKING: A supported vulnerability has a reachable trigger and concrete impact
- ⚠️ IMPORTANT: A supported concern merits correction; label unconfirmed concerns as evidence gaps
- 💡 SUGGESTION: Defense-in-depth improvements

**When to use:**
- Authentication/authorization changes
- Input handling code
- File operations
- Network operations
- Before security releases

---

### 7. Performance Review

**Focus:** Efficiency and resource usage

**What it examines:**
- Algorithm complexity (Big O)
- Memory usage patterns
- Database query efficiency
- N+1 query problems
- Caching opportunities
- Resource leaks
- Scaling considerations
- I/O efficiency
- Unnecessary computations
- Batch processing opportunities
- Profiling concerns

**Severity guidelines:**
- ❌ BLOCKING: A supported regression materially harms a relevant critical path
- ⚠️ IMPORTANT: Inefficient algorithms with better alternatives
- 💡 SUGGESTION: Optimization opportunities

**When to use:**
- Hot code paths
- Database queries
- Large-scale processing
- Resource-intensive operations

---

## Review Output Format

Use the concise template in
[REVIEW_GUIDELINES.md](REVIEW_GUIDELINES.md#review-structure-template) for every
focus area. Record the actual base, merge-base and head SHAs and the reviewed
scope. Lead with supported findings in severity order and a recommendation to
approve, request changes, or wait for specific evidence.

For panel reviews, the coordinator reconciles and deduplicates findings into one
report; raw persona reports stay in the local run directory. Preserve substantive
disagreements and verification gaps. Separate reviewers or multiple models do not
replace source, test or CI evidence. A failed or skipped review cannot count as
approval. Keep path/line coordinates outside the concise posting-comment blocks.

## Tips for Effective Reviews

### For the Reviewer

1. **Stay focused:** When doing a focused review, ignore issues outside that scope
2. **Be thorough:** Within the focus area, be comprehensive
3. **Provide context:** Explain why something matters from this perspective
4. **Select relevant reviewers:** Use the bounded panel when independent perspectives help
5. **Cross-reference:** Note when issues overlap between focus areas

### For the Requester (Human)

1. **Choose appropriate type:** Match review type to the change nature
2. **Use parallel reviews selectively:** Match the panel to actual domain boundaries
3. **Sequence reviews:** Do style/tests first, then architecture
4. **Save bandwidth:** Don't run all review types for trivial changes
5. **Iterate:** Fix blocking issues, then run focused reviews again

---

## Examples

### Example 1: New Feature

```
"Run architecture, tests, and documentation reviews in parallel"
```

This examines:
- Design is sound (architecture)
- Feature is properly tested (tests)
- Feature is properly documented (documentation)

### Example 2: Bug Fix

```
"Run tests and security reviews in parallel"
```

This examines:
- Fix is tested including edge cases (tests)
- Fix doesn't introduce vulnerabilities (security)

### Example 3: Refactoring

```
"Do a style review of this refactoring"
```

Focuses on:
- Code readability and consistency
- Naming conventions
- Organization improvements

### Example 4: Performance Optimization

```
"Run performance and tests reviews in parallel"
```

This examines:
- Optimization is effective (performance)
- Optimization doesn't break functionality (tests)

### Example 5: Final Automated Review

```
"Run a comprehensive review"
```

Covers all aspects in a single automated review pass.
