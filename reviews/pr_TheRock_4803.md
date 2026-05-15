# PR Review: ROCm/TheRock#4803

* **PR:** https://github.com/ROCm/TheRock/pull/4803
* **Title:** `[WIP] packaging: add Windows MSI installer for ROCm runtimes`
* **Base:** `main`
* **Head:** `8f1ea2970f7431b08a3a06d33cad1a497f04a5b7`
* **Reviewed:** 2026-05-14
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**WAIT / NOT READY TO APPROVE** - This PR is still labeled WIP in the title and the latest source still overlaps heavily with existing design review threads. I would not add a broad new design comment unless you want to reinforce the already-open feedback.

The main unresolved themes already covered on the PR are: land/reference the Windows packaging RFC, define the System32 cleanup/deletion policy before implementing it, avoid checked-in generated/debug MSI outputs, derive package contents from the build/artifact manifest instead of manual hardcoded lists, and avoid placeholder product/version identity.

## Findings

### BLOCKING, ALREADY COVERED: System32 deletion is still implemented

The latest generator still defines legacy System32 patterns at [`generate_msi_wxs.py#L42-L48`](https://github.com/ROCm/TheRock/blob/8f1ea2970f7431b08a3a06d33cad1a497f04a5b7/build_tools/packaging/windows/generate_msi_wxs.py#L42-L48) and schedules a deferred delete action at [`#L402-L445`](https://github.com/ROCm/TheRock/blob/8f1ea2970f7431b08a3a06d33cad1a497f04a5b7/build_tools/packaging/windows/generate_msi_wxs.py#L402-L445). The usage docs also state that the installer removes those files automatically at [`README.md#L132-L137`](https://github.com/ROCm/TheRock/blob/8f1ea2970f7431b08a3a06d33cad1a497f04a5b7/build_tools/packaging/windows/README.md#L132-L137).

This is already under discussion on the PR. I would not duplicate it unless the thread gets marked resolved without a code change.

### BLOCKING, ALREADY COVERED: generated/debug MSI output is checked in

The PR still adds `build_tools/packaging/windows/amdrocm-runtimes.wixpdb`, and it also checks in a generated `amdrocm-runtimes.wxs`. The `.wixpdb` point is already covered by an existing inline comment.

### IMPORTANT: generated WiX IDs are not deterministic

`make_id()` uses Python's salted process-local `hash()` at [`generate_msi_wxs.py#L85-L89`](https://github.com/ROCm/TheRock/blob/8f1ea2970f7431b08a3a06d33cad1a497f04a5b7/build_tools/packaging/windows/generate_msi_wxs.py#L85-L89). That means regenerating the `.wxs` in another process can produce different element IDs for identical input files.

This is probably easy to fix with a stable digest such as `hashlib.sha256(str(path).encode()).hexdigest()[:8]`.

### IMPORTANT: usage docs do not match the script layout or file selection model

The generator lives under `build_tools/packaging/windows/`, but the usage guide invokes `python build_tools\generate_msi_wxs.py` at [`msi-generator-usage.md#L17-L23`](https://github.com/ROCm/TheRock/blob/8f1ea2970f7431b08a3a06d33cad1a497f04a5b7/build_tools/packaging/windows/msi-generator-usage.md#L17-L23) and again in the examples at [`#L64-L71`](https://github.com/ROCm/TheRock/blob/8f1ea2970f7431b08a3a06d33cad1a497f04a5b7/build_tools/packaging/windows/msi-generator-usage.md#L64-L71).

The docs also say the generated MSI packages all regular files under `bin/` and `lib/`, but the script first loads an explicit allowlist at [`generate_msi_wxs.py#L320-L321`](https://github.com/ROCm/TheRock/blob/8f1ea2970f7431b08a3a06d33cad1a497f04a5b7/build_tools/packaging/windows/generate_msi_wxs.py#L320-L321) and only includes files present in that list. That is a design choice, but the docs should not claim newly added runtime files are picked up automatically if the allowlist must also be updated.

## Suggested Review Comment

If posting anything new, I would keep it narrow and avoid repeating the open design threads:

```text
One implementation detail I noticed while reading the latest generator: `make_id()` uses Python's built-in `hash()` when constructing WiX element IDs. Since that hash is salted per process, regenerating the `.wxs` can produce different IDs for the same inputs. Could we switch that to a deterministic digest such as `hashlib.sha256(...).hexdigest()[:8]`?

Also, the usage guide appears to invoke `build_tools\generate_msi_wxs.py`, but the script lives under `build_tools\packaging\windows\`. While updating that, the file-selection docs should probably mention the explicit allowlist, since the generator does not currently package every regular file under `bin/` and `lib/` automatically.
```

## Verification

* Refreshed `origin/main` and `refs/remotes/pr/4803`.
* Checked latest PR metadata: open, not draft, mergeable, review required.
* Checked top-level and inline comments. Existing comments already cover the major design concerns and several implementation details.
* Reviewed changed files under `build_tools/packaging/windows/`.
* Ran `git -c safe.directory=* diff --check origin/main...refs/remotes/pr/4803`; passed.
* Checked latest public PR checks. Pre-commit is failing because formatting hooks modify files; early Windows/Linux build jobs also fail.
