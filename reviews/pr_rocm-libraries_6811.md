# PR Review: ROCm/rocm-libraries#6811

* **PR:** https://github.com/ROCm/rocm-libraries/pull/6811
* **Title:** `Add StinkyTofu CI`
* **Base:** `develop`
* **Head:** `4e003cf65ab95ead87c67a298f15a9e2a97b0393`
* **Reviewed:** 2026-04-30
* **State at review:** OPEN

---

## Overall Assessment

**COMMENT / NO BLOCKING FINDINGS** - The latest workflow appears to address the previous review feedback around runner alignment, dependency file usage, and sparse TheRock checkout. I found one non-blocking scope note: the workflow triggers for all StinkyTofu changes, including Python bindings, but the jobs build with Python support disabled.

## Latest Comment Check

Checked latest PR state on 2026-04-30 at head `4e003cf6`. The only existing human review was on older head `75b7bd2` and covered splitting concerns, Linux/Windows runner alignment, dependency handling, and sparse TheRock checkout. The author replied that those were fixed, and I did not find any current inline review comments.

## Findings

### NON-BLOCKING: StinkyTofu CI triggers on Python binding changes but does not cover them yet

The new workflow runs for every `shared/stinkytofu/**` change on both push and pull request events ([`stinkytofu-ci.yml#L8-L13`](https://github.com/ROCm/rocm-libraries/blob/4e003cf65ab95ead87c67a298f15a9e2a97b0393/.github/workflows/stinkytofu-ci.yml#L8-L13)), but both jobs invoke the default build task without enabling Python bindings ([`#L58`](https://github.com/ROCm/rocm-libraries/blob/4e003cf65ab95ead87c67a298f15a9e2a97b0393/.github/workflows/stinkytofu-ci.yml#L58), [`#L111`](https://github.com/ROCm/rocm-libraries/blob/4e003cf65ab95ead87c67a298f15a9e2a97b0393/.github/workflows/stinkytofu-ci.yml#L111)). That default is `python=False` in `tasks.py`, which passes `-DSTINKYTOFU_BUILD_PYTHON=OFF` to CMake ([`tasks.py#L170`](https://github.com/ROCm/rocm-libraries/blob/4e003cf65ab95ead87c67a298f15a9e2a97b0393/shared/stinkytofu/tasks.py#L170), [`#L190`](https://github.com/ROCm/rocm-libraries/blob/4e003cf65ab95ead87c67a298f15a9e2a97b0393/shared/stinkytofu/tasks.py#L190)).

As a result, changes under `shared/stinkytofu/python_module/**` still trigger this CI, but the Python module and pytest-based CTest entries are skipped. The CMake test registration is gated on `STINKYTOFU_BUILD_PYTHON` ([`tests/CMakeLists.txt#L159`](https://github.com/ROCm/rocm-libraries/blob/4e003cf65ab95ead87c67a298f15a9e2a97b0393/shared/stinkytofu/tests/CMakeLists.txt#L159)), and the skipped path logs `Python module build disabled` ([`#L213`](https://github.com/ROCm/rocm-libraries/blob/4e003cf65ab95ead87c67a298f15a9e2a97b0393/shared/stinkytofu/tests/CMakeLists.txt#L213)). For an initial CI-enablement PR this should not block the workflow, but it is worth tracking so Python-binding changes do not appear fully covered by this check.

**Suggested follow-up:** Either enable the Python binding/test path later, for example by installing the needed pytest dependency and running `invoke build --python` before `ctest`, or narrow the workflow paths/name if this check is intended to cover only the C++ StinkyTofu build.

## Verification

* Refreshed PR metadata, comments, and inline review comments on 2026-04-30.
* Fetched `origin/develop` and `refs/pull/6811/head`; reviewed local worktree at `4e003cf6`.
* Confirmed the previous human review was on older commit `75b7bd2` and did not cover the Python-build coverage gap.
* Latest GitHub checks show `stinkytofu-ci` Linux and Windows passing on the current head; unrelated external Math CI contexts still show hipBLASLt/hipSPARSELt failures or pending status.
* Ran `git -c safe.directory=* diff --check origin/develop...HEAD` - passed.
* Ran `python -m py_compile shared\stinkytofu\tasks.py` - passed.
