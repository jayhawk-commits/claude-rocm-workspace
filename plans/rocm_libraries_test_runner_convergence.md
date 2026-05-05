# rocm-libraries Test Runner Convergence

Date: 2026-05-04

## Goal

Converge the useful behavior from TheRock's generic `test_runner.py` into
project-owned installed runners without preserving the generic component router
as the long-term interface.

## Design Diagram

```mermaid
flowchart TD
    A[TheRock generic test_runner.py] --> B{Useful behavior}
    A --> C{Design debt}

    B --> B1[TEST_TYPE maps to CTest labels]
    B --> B2[GPU arch label matching]
    B --> B3[CTest sharding]
    B --> B4[Parallelism and timeout defaults]
    B --> B5[Installed CTest payload validation]

    C --> C1[TEST_COMPONENT routing table]
    C --> C2[THEROCK_DIR / THEROCK_BIN_DIR assumptions]
    C --> C3[One script owns many projects]
    C --> C4[Project behavior hidden outside project]

    B1 --> D[Small project CTest runner pattern]
    B2 --> D
    B3 --> D
    B4 --> D
    B5 --> D

    D --> E1[projects/rocblas/.../run_rocblas.py]
    D --> E2[projects/hipsparselt/clients/test/run_hipsparselt.py]
    D --> E3[projects/miopen/test/gtest/run_miopen.py]

    C1 -. retire .-> F[TheRock calls installed project runner]
    C2 -. retire .-> F
    C3 -. retire .-> F
    C4 -. retire .-> F

    E1 --> G[Project CMake installs runner next to test payload]
    E2 --> G
    E3 --> G

    G --> H[TheRock fetches artifacts and invokes run_<project>.py]
    F --> H
```

## Target Shape

- Each project owns a `run_<project>.py` script near the CMake logic that
  creates or installs its test payload.
- Each runner is installed beside the relevant executable, YAML file, or
  `CTestTestfile.cmake` that it executes.
- Runners derive `ROCM_PATH` from installed layout when possible, while allowing
  explicit `ROCM_PATH` for non-standard layouts.
- TheRock should treat installed runners as executable project artifacts, not as
  logic it needs to duplicate under `test/therock`.

## What We Keep From `test_runner.py`

- `TEST_TYPE` as the external CI knob.
- CTest category labels: `quick`, `standard`, `comprehensive`, `full`.
- GPU-specific label matching such as `gfx1151 -> gfx115X -> gfx11X`.
- CTest sharding through `--tests-information`.
- Conservative per-project defaults for timeout and parallelism.

## What We Do Not Keep

- A long-lived `TEST_COMPONENT` dispatch table.
- TheRock-specific path discovery in project-owned scripts.
- A single generic runner that silently changes behavior by environment.
- Shared abstraction before two or three project runners have stabilized.

## Migration Order

1. Finish the current hipSPARSELt correction in the sparse branch.
2. Split rocBLAS separately because it has ASAN behavior and YAML smoke-test
   handling.
3. Split MIOpen separately because its filtering logic is larger and more
   platform-specific.
4. Update TheRock component wiring one project at a time after the corresponding
   rocm-libraries runner lands.
5. Retire TheRock's generic `test_runner.py` after its remaining users have
   project-owned installed runners.
