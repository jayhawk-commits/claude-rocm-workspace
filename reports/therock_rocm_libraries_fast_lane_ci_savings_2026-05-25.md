# TheRock rocm-libraries Fast-Lane CI Savings

Date: 2026-05-25

## Summary

This report estimates the CI capacity and turnaround-time impact of a fast lane
for TheRock `rocm-libraries` submodule bump PRs.

The proposed fast lane would:

- Reuse a validated baseline for `foundation` and `compiler-runtime`.
- Rebuild only `rocm-libraries`-relevant stages: `math-libs` and `fusilli-libs`.
- Skip or prebuild non-`rocm-libraries` build stages such as `comm-libs`,
  `media-libs`, `debug-tools`, `profiler-apps`, and `wsl-rocdxg`.
- Run sanity plus `rocm-libraries`-relevant tests.
- Skip non-`rocm-libraries` validation tests by default, with an explicit
  escape hatch for broader coverage.

Using recent `rocm-libraries` bump PRs, the estimated savings are:

| Metric | Before | After | Saved | Reduction |
| --- | ---: | ---: | ---: | ---: |
| Build runner-hours, average completed PR | 16.8 h | 13.3 h | 3.6 h | 21.3% |
| GPU test runner-hours, average completed PR | 25.7 h | 22.9 h | 2.8 h | 11.0% |
| Combined runner-hours, average completed PR | 42.5 h | 36.1 h | 6.4 h | 15.1% |
| Build critical path, average completed PR | 278.5 min | 226.2 min | 52.4 min | 20.8% |
| GPU test execution critical path, sampled PRs | unchanged | unchanged | 0.0 min | 0.0% |

The main turnaround-time gain is the build critical path: about 52 minutes per
PR before accounting for the overhead of the `Copy Prebuilt Stages` job. The
test filtering gain is primarily capacity and signal quality: fewer occupied
GPU runners, fewer unrelated red checks, and less triage noise.

## Sample

The sampled TheRock `rocm-libraries` bump PRs were:

- [ROCm/TheRock#5203](https://github.com/ROCm/TheRock/pull/5203)
- [ROCm/TheRock#5247](https://github.com/ROCm/TheRock/pull/5247)
- [ROCm/TheRock#5263](https://github.com/ROCm/TheRock/pull/5263)
- [ROCm/TheRock#5302](https://github.com/ROCm/TheRock/pull/5302)
- [ROCm/TheRock#5339](https://github.com/ROCm/TheRock/pull/5339)
- [ROCm/TheRock#5387](https://github.com/ROCm/TheRock/pull/5387)
- [ROCm/TheRock#5395](https://github.com/ROCm/TheRock/pull/5395)
- [ROCm/TheRock#5417](https://github.com/ROCm/TheRock/pull/5417)
- [ROCm/TheRock#5428](https://github.com/ROCm/TheRock/pull/5428)

Most aggregate averages below show both:

- all 9 PRs, including current/in-progress #5428;
- 8 completed or superseded PRs, excluding #5428.

## Build Runner-Hour Savings

Build runner-hours compare current release build-stage jobs against a fast lane
that rebuilds `math-libs` and `fusilli-libs`.

| Sample | Before | After | Saved | Reduction |
| --- | ---: | ---: | ---: | ---: |
| 9 sampled PRs including #5428 | 148.2 h | 115.8 h | 32.4 h | 21.9% |
| 8 completed PRs excluding #5428 | 134.6 h | 106.0 h | 28.6 h | 21.3% |
| Average completed PR | 16.8 h | 13.3 h | 3.6 h | 21.3% |

Savings split:

| Saved category | 9 PRs | 8 completed PRs |
| --- | ---: | ---: |
| Prebuild `foundation` + `compiler-runtime` | 13.0 h | 11.4 h |
| Skip or prebuild unrelated stages | 19.5 h | 17.2 h |
| Total build runner savings | 32.4 h | 28.6 h |

Per PR:

| PR | Before | After | Saved | Reduction |
| --- | ---: | ---: | ---: | ---: |
| #5428 | 13.6 h | 9.8 h | 3.8 h | 28.1% |
| #5417 | 16.1 h | 12.2 h | 3.9 h | 24.0% |
| #5395 | 12.4 h | 9.2 h | 3.2 h | 25.8% |
| #5387 | 15.1 h | 11.1 h | 4.0 h | 26.6% |
| #5339 | 12.6 h | 9.8 h | 2.8 h | 22.0% |
| #5302 | 16.1 h | 12.2 h | 3.9 h | 24.2% |
| #5263 | 22.9 h | 19.4 h | 3.5 h | 15.2% |
| #5247 | 19.6 h | 15.9 h | 3.8 h | 19.1% |
| #5203 | 19.8 h | 16.2 h | 3.6 h | 18.3% |

## GPU Test Runner-Hour Savings

GPU runner-hours compare all current completed `Multi-Arch CI` test jobs against
a test matrix that skips non-`rocm-libraries` validation by default.

Default skipped tests:

- `hip-tests`
- `rocrtst`
- `rocprofiler-sdk`
- `rocprofiler-compute`
- `rocprofiler-systems`
- `aqlprofile`
- `rocgdb`
- `rocr-debug-agent`
- `rocdecode`
- `rocjpeg`
- `rccl`

| Sample | Before | After | Saved | Reduction |
| --- | ---: | ---: | ---: | ---: |
| 9 sampled PRs including #5428 | 250.0 h | 222.0 h | 28.1 h | 11.2% |
| 8 completed PRs excluding #5428 | 205.6 h | 183.0 h | 22.7 h | 11.0% |
| Average completed PR | 25.7 h | 22.9 h | 2.8 h | 11.0% |

Per PR:

| PR | Before | After | Saved | Reduction |
| --- | ---: | ---: | ---: | ---: |
| #5428 | 44.4 h | 39.0 h | 5.4 h | 12.2% |
| #5417 | 23.7 h | 21.0 h | 2.7 h | 11.4% |
| #5395 | 19.1 h | 17.4 h | 1.8 h | 9.2% |
| #5387 | 20.7 h | 18.2 h | 2.5 h | 12.2% |
| #5339 | 31.6 h | 28.7 h | 2.9 h | 9.1% |
| #5302 | 32.2 h | 29.7 h | 2.5 h | 7.7% |
| #5263 | 28.2 h | 24.7 h | 3.6 h | 12.6% |
| #5247 | 24.7 h | 21.7 h | 3.0 h | 12.2% |
| #5203 | 25.4 h | 21.7 h | 3.8 h | 14.9% |

Largest skipped test contributors across the sample:

| Component | Sampled runner-minutes |
| --- | ---: |
| `hip-tests` | 685.9 |
| `rocprofiler-compute` | 331.5 |
| `rocgdb` | 205.6 |
| `rccl` | 127.5 |
| `rocrtst` | 97.4 |
| `rocprofiler-sdk` | 82.8 |
| `rocprofiler-systems` | 79.7 |

## Critical Path Savings

Critical path is the clearest turnaround-time estimate. This estimate models
the build path as:

- current path: lower stages, then the longest downstream build branch;
- fast lane: start library stages from a valid prebuilt baseline.

This does not include the overhead of copying prebuilt artifacts into the new
run, so the real net saving should be slightly lower. If the copy job costs
5-10 minutes, the practical build critical-path saving is still roughly
40-50 minutes for a routine `rocm-libraries` bump.

| Sample | Before | After | Saved | Reduction |
| --- | ---: | ---: | ---: | ---: |
| 9 sampled PRs including #5428 | 266.0 min | 213.7 min | 52.4 min | 22.0% |
| 8 completed PRs excluding #5428 | 278.5 min | 226.2 min | 52.4 min | 20.8% |

Per PR build critical path:

| PR | Before | After | Saved | Reduction |
| --- | ---: | ---: | ---: | ---: |
| #5428 | 165.9 min | 113.5 min | 52.4 min | 31.6% |
| #5417 | 200.4 min | 153.6 min | 46.8 min | 23.4% |
| #5395 | 174.5 min | 113.6 min | 60.9 min | 34.9% |
| #5387 | 271.2 min | 218.8 min | 52.4 min | 19.3% |
| #5339 | 177.9 min | 126.3 min | 51.6 min | 29.0% |
| #5302 | 265.2 min | 215.5 min | 49.8 min | 18.8% |
| #5263 | 296.6 min | 261.0 min | 35.6 min | 12.0% |
| #5247 | 463.4 min | 402.2 min | 61.2 min | 13.2% |
| #5203 | 379.1 min | 318.5 min | 60.6 min | 16.0% |

For GPU test execution critical path, the sampled jobs did not show a raw
wall-clock reduction from skipping non-`rocm-libraries` tests: the longest
remaining tests were still `rocm-libraries` tests. The value of test filtering
is still material because it removes 15-19 unrelated test jobs per PR, saves
about 2.8 GPU runner-hours per completed PR, and prevents unrelated failures
from creating extra triage loops.

## Combined Capacity Impact

For completed PRs, the average capacity reduction is:

| Category | Before | After | Saved | Reduction |
| --- | ---: | ---: | ---: | ---: |
| Build runners | 16.8 h | 13.3 h | 3.6 h | 21.3% |
| GPU test runners | 25.7 h | 22.9 h | 2.8 h | 11.0% |
| Combined | 42.5 h | 36.1 h | 6.4 h | 15.1% |

This is the best headline for resource planning:

> A `rocm-libraries` fast lane should save about 6.4 CI/GPU runner-hours per
> completed bump PR, reduce total sampled runner consumption by about 15%, and
> shorten the build critical path by about 52 minutes before copy overhead.

## Notes and Caveats

- The estimates use GitHub check start and completion times from recent
  `Multi-Arch CI` runs.
- The build critical-path estimate assumes a valid baseline run is available
  and compatible with the TheRock commit, package version, build topology,
  `rocm-systems` SHA, and selected GPU families.
- The build fast lane should fall back to full CI when the baseline is missing,
  stale, or ambiguous.
- The skipped test list should remain overrideable through explicit test labels
  or manual workflow dispatch.
- The numbers measure execution capacity and CI path length. They do not fully
  capture avoided human triage time from unrelated red checks, which is likely
  another meaningful win for bump turnaround.
