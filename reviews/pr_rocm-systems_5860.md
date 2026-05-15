# PR Review: ROCm/rocm-systems#5860

* **PR:** https://github.com/ROCm/rocm-systems/pull/5860
* **Title:** `Rocprof trace decoder API overhaul`
* **Base:** `develop`
* **Head:** `dd65f0a2e496eae54659c08907ccbcdb07e4b427`
* **Reviewed:** 2026-05-15
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**OUT OF REVIEW SCOPE FOR ME** - This PR is primarily a rocprof trace decoder API overhaul, so I should not take action on it unless explicitly asked. Notes below are kept only as scratch context.

**CHANGES REQUESTED** - This is a large API and packaging overhaul. The main blocker I found is in the new public `rocprof_trace_decoder_build_standalone()` API: invalid offsets can bypass validation through unsigned overflow and then drive out-of-bounds scans/copies. I also found a documentation/default mismatch for the new LLVM disassembly backend.

## Findings

### BLOCKING: `build_standalone()` can read past the input buffer for overflowing offsets

`rocprof_trace_decoder_build_standalone()` validates the cut range with `offset_begin + 8 >= offset_end` and `offset_end > data_size` at [`quick_scan_export.cpp#L266`](https://github.com/ROCm/rocm-systems/blob/dd65f0a2e496eae54659c08907ccbcdb07e4b427/projects/rocprof-trace-decoder/source/quick_scan_export.cpp#L266). Since the offsets are `uint64_t`, `offset_begin + 8` can wrap. A caller can pass an invalid `offset_begin` larger than `data_size` while keeping `offset_end <= data_size`, and the guard can miss it after wraparound.

The function then uses `offset_begin` as the byte count for `scan_gfx9()` at [`#L301-L305`](https://github.com/ROCm/rocm-systems/blob/dd65f0a2e496eae54659c08907ccbcdb07e4b427/projects/rocprof-trace-decoder/source/quick_scan_export.cpp#L301-L305) and later copies from `buf + offset_begin` at [`#L339`](https://github.com/ROCm/rocm-systems/blob/dd65f0a2e496eae54659c08907ccbcdb07e4b427/projects/rocprof-trace-decoder/source/quick_scan_export.cpp#L339). That can read far beyond the supplied trace buffer instead of returning `ERROR_INVALID_ARGUMENT`.

### IMPORTANT: README says LLVM disassembly defaults ON, but CMake defaults it OFF

The README documents `USE_LLVM_DISASM` as default ON at [`README.md#L36`](https://github.com/ROCm/rocm-systems/blob/dd65f0a2e496eae54659c08907ccbcdb07e4b427/projects/rocprof-trace-decoder/README.md#L36) and again describes LLVM-C as the default backend at [`#L47`](https://github.com/ROCm/rocm-systems/blob/dd65f0a2e496eae54659c08907ccbcdb07e4b427/projects/rocprof-trace-decoder/README.md#L47). The actual CMake option defaults to OFF at [`source/CMakeLists.txt#L103-L105`](https://github.com/ROCm/rocm-systems/blob/dd65f0a2e496eae54659c08907ccbcdb07e4b427/projects/rocprof-trace-decoder/source/CMakeLists.txt#L103-L105), so default builds still prefer the non-LLVM path when available.

That is a design-level mismatch: consumers following the README will expect the portable LLVM-C backend by default, while the build system selects a different backend unless the user explicitly enables `USE_LLVM_DISASM`.

## Suggested Inline Comments

Target: `projects/rocprof-trace-decoder/source/quick_scan_export.cpp`, line 266.

```text
This range check can be bypassed by unsigned overflow in `offset_begin + 8`. For example, an `offset_begin` larger than `data_size` can wrap this expression while `offset_end <= data_size`, after which the function scans `[buf, buf + offset_begin)` and later copies from `buf + offset_begin`. Could we validate the range without addition overflow, e.g. check `offset_begin < offset_end`, `offset_end <= data_size`, and only then apply any minimum-span/header-size rule using subtraction?
```

Target: `projects/rocprof-trace-decoder/source/CMakeLists.txt`, line 104.

```text
The README says `USE_LLVM_DISASM` defaults ON and describes LLVM-C as the default backend, but this option defaults OFF here. Which default is intended for this PR? We should align the CMake option and README so downstream users know which disassembly backend they get without extra flags.
```

## Verification

* Refreshed `origin/develop` and `refs/remotes/pr/5860`.
* Checked PR metadata: open, not draft, review required.
* Checked top-level and inline comments; no existing inline comments at review time.
* Reviewed the public C API implementation, trace-decoder CMake packaging changes, README, and unit-test wiring.
* Ran `git -c safe.directory=* diff --check origin/develop...refs/remotes/pr/5860`; passed.
