# Build and packaging

Use for build configuration, dependency changes, artifact definitions,
installation, relocation, and platform support. Skip changes that do not alter
these behaviors; a repository containing CMake is not sufficient reason to
review its entire build system.

Trace the selected feature through configuration, build and installation:

- Do options enable the intended targets and dependencies in supported
  combinations, including disabled features and external source checkouts?
- Are generated files and build outputs connected by real dependencies, or
  does success rely on a previous build's state?
- Does each artifact own the intended installed files exactly once? Follow
  descriptor components to the build declarations that activate them.
- Can a consumer find and use the installed package after relocation? Inspect
  exported targets, include paths, library names and pkg-config metadata.
- Are Windows and Linux path, runtime-library and executable conventions
  preserved where the change promises support?

Use neighboring project patterns, dependency declarations, staged file
manifests and a representative consumer as evidence. Prefer configuration or
the smallest relevant target over a full ROCm build. A successful producer
build does not establish that the installed package works for consumers.

Distinguish an introduced missing dependency, duplicate artifact ownership or
broken installation from optional build-system cleanup. Do not request a
platform matrix without connecting each case to a changed contract.

Local context: [build specialist](../../../../.claude/agents/build-infra.md).
