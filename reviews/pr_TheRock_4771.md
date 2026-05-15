# PR Review: ROCm/TheRock#4771

* **PR:** https://github.com/ROCm/TheRock/pull/4771
* **Title:** `Switch CI to artifact_manager.py push, remove therock-archives`
* **Base:** `main`
* **Head:** `35e1953e3831355bf8148563e6abb9043e98f275`
* **Reviewed:** 2026-05-14
* **State at review:** OPEN
* **Draft:** No

---

## Overall Assessment

**WAIT FOR EXISTING CI / EXTRACTION THREAD** - I do not see a new static review blocker beyond the issue already being discussed on the PR. The design direction is coherent: stop generating archive targets in CMake, build artifact directories, and let `artifact_manager.py push` compress/upload the produced artifacts.

The latest public checks are still failing in artifact test jobs, and there is already an inline thread about `.tar.zst` extraction/cleanup on Windows. I would wait for that thread and CI to settle before approving or posting another comment.

## Findings

### IMPORTANT, ALREADY COVERED: Windows artifact extraction/cleanup still needs resolution

The latest fetch path keeps downloaded archives through parallel extraction with `delete_archive=False` at [`artifact_manager.py#L412-L425`](https://github.com/ROCm/TheRock/blob/35e1953e3831355bf8148563e6abb9043e98f275/build_tools/artifact_manager.py#L412-L425), then removes the temporary download directory after extraction completes at [`#L442-L446`](https://github.com/ROCm/TheRock/blob/35e1953e3831355bf8148563e6abb9043e98f275/build_tools/artifact_manager.py#L442-L446).

That lines up with the existing public discussion about archive files remaining locked on Windows after extraction. Since that thread is already active, I would not duplicate it unless the author resolves it without a fix or without a successful rerun.

### LOW: stale archive wording remains in reporting/docs

The core `therock-archives` target removal looks complete, but a few non-critical strings still assume archive files. For example, the multi-arch Windows report step still lists `artifacts/*.tar.xz` at [`multi_arch_build_windows_artifacts.yml#L174-L180`](https://github.com/ROCm/TheRock/blob/35e1953e3831355bf8148563e6abb9043e98f275/.github/workflows/multi_arch_build_windows_artifacts.yml#L174-L180), which will usually print "No artifacts found" after this PR because the push step now creates archives later.

I would treat that as a cleanup suggestion, not a blocker.

## Suggested Review Comment

I would not post a new blocking comment right now. If you want to leave a small non-blocking note after the extraction thread is resolved:

```text
No new blocking comments from me beyond the active artifact extraction thread. Small cleanup: the multi-arch report steps still look for `artifacts/*.tar.xz`, but this PR moves archive creation to `artifact_manager.py push`, so those report snippets may now print "No artifacts found" even when artifact directories were produced.
```

## Verification

* Refreshed `origin/main` and `refs/remotes/pr/4771`.
* Checked latest PR metadata: open, not draft, mergeable, already approved by another reviewer.
* Checked top-level and inline comments. Existing discussion covers the duplicate archive design and the Windows `.tar.zst` extraction failure.
* Reviewed workflow changes, `artifact_manager.py`, CMake artifact target changes, and updated docs.
* Ran `git -c safe.directory=* diff --check origin/main...refs/remotes/pr/4771`; passed.
* Checked latest public PR checks. Artifact test jobs are still failing; attempts to fetch the full failed-job logs through `gh` hit stream errors, so I did not independently confirm the exact failure text.
