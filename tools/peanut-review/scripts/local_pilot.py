#!/usr/bin/env python3
"""Exercise the local harness with deterministic fake Codex subprocesses.

Runs real CLI/storage/supervisor/runner code without models or network access.
Uses only a newly created synthetic Git repository and sessions. This validates
plumbing, not model review quality or Codex sandbox enforcement.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time


PACKAGE = Path(__file__).resolve().parents[1]
PR = PACKAGE / "bin" / "peanut-review"
POLICY_DIRECTORY = Path(".codex/peanut-review")
POLICY_STATE = POLICY_DIRECTORY / "safe-local-state.json"


def fake_codex():
    """Called through the real Bash runner's `codex exec` command."""
    directory = Path(os.environ["PEANUT_SESSION"])
    name = os.environ["GIT_AUTHOR_NAME"]
    assert sys.argv[2] == "exec"
    assert "danger-full-access" not in sys.argv
    assert "--model" in sys.argv and "pilot-fake" in sys.argv

    def cli(*args):
        return subprocess.run([str(PR), "--session", str(directory), *args],
                              check=True, text=True, capture_output=True).stdout

    mode = os.environ.get("PEANUT_PILOT_MODE", "ok")
    if mode == "fail":
        cli("note", "--message", "Deterministic injected runner failure; no review completed.")
        return 7
    if mode == "hang":
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
        (directory / f"pilot-child-{name}.pid").write_text(str(child.pid))
        time.sleep(120)
        return 0

    cli("status")
    if name == "Curator":
        comments = json.loads(cli("comments", "--format", "json"))
        assert len(comments) == 2, comments
        keep, duplicate = comments
        cli("edit", keep["id"], "--body", "Synthetic pilot finding with combined evidence.")
        cli("delete", duplicate["id"])
        cli("note", "--message",
            f"Merged synthetic duplicate into {keep['id']}. Deleted comments: "
            f"{duplicate['id']} (source.py:1): same synthetic concern. Validation: deterministic fixture.")
    else:
        cli("add-comment", "--file", "source.py", "--line", "1", "--body",
            "Synthetic pilot finding; intentionally duplicated to test curation.")
        cli("note", "--message", "Test Execution: synthetic CLI fixture; no model review.")
    cli("signal", "round-done")
    if "--output-last-message" in sys.argv:
        Path(sys.argv[sys.argv.index("--output-last-message") + 1]).write_text("Offline plumbing pilot.\n")
    print(json.dumps({"type": "pilot.completed", "agent": name}))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="New empty destination (must not exist)")
    args = parser.parse_args()
    root = args.root.resolve() if args.root else Path(tempfile.mkdtemp(prefix="peanut-local-pilot-"))
    if args.root:
        root.mkdir(parents=True, exist_ok=False)
    # Use the same interpreter for CLI entry points and fake runner children.
    env = dict(os.environ, PR_PYTHON=sys.executable)
    env.pop("PEANUT_SESSION", None)
    env.pop("PEANUT_REVIEW_RUN_ID", None)
    env.pop("PEANUT_PILOT_MODE", None)
    fake_bin = root / "fake-bin"
    fake_bin.mkdir()
    executable = fake_bin / "codex"
    executable.write_text("#!/bin/sh\nexec " + shlex.quote(sys.executable) + " "
                          + shlex.quote(str(Path(__file__).resolve())) + ' --fake-codex "$@"\n')
    executable.chmod(0o755)
    env["PATH"] = str(fake_bin) + os.pathsep + env.get("PATH", "")
    repo = root / "source"
    repo.mkdir()

    def run(command, *, extra_env=None, expected=0):
        result = subprocess.run(command, env={**env, **(extra_env or {})}, text=True,
                                capture_output=True, timeout=45)
        if result.returncode != expected:
            raise AssertionError(f"Unexpected exit {result.returncode} for {command}:\n"
                                 f"{result.stdout}\n{result.stderr}")
        return result.stdout

    def git(*arguments):
        return run(["git", "-C", str(repo), *arguments]).strip()

    git("init", "-b", "main")
    git("config", "user.name", "Harness pilot")
    git("config", "user.email", "pilot@example.invalid")
    git("config", "commit.gpgsign", "false")
    git("config", "core.hooksPath", "/dev/null")
    (repo / "source.py").write_text("value = 1\n")
    git("add", "source.py")
    git("commit", "-m", "synthetic base")
    base = git("rev-parse", "HEAD")
    (repo / "source.py").write_text("value = 2\n")
    git("commit", "-am", "synthetic change")
    head = git("rev-parse", "HEAD")
    personas = root / "personas"
    personas.mkdir()
    (personas / "test.md").write_text("Synthetic test persona. Submit findings through the CLI.\n")
    sessions = []

    def cli(directory, *arguments, **kwargs):
        return run([str(PR), "--session", str(directory), *arguments], **kwargs)

    def create(name, *, reviewers=2, timeout=15, limits=None):
        directory = root / name
        agents = [{"name": f"Reviewer{index}", "runner": "codex", "model": "pilot-fake",
                   "reasoningEffort": "medium", "persona": "test.md"}
                  for index in range(reviewers)]
        if reviewers == 2:
            agents.append({"name": "Curator", "role": "curator", "runner": "codex",
                           "model": "pilot-fake", "reasoningEffort": "medium"})
        cli(directory, "init", "--workspace", str(repo), "--base", base, "--topic", head,
            "--agents", json.dumps(agents), "--personas-dir", str(personas),
            "--timeout", str(timeout), "--id", name)
        (directory / POLICY_DIRECTORY).mkdir(parents=True)
        (directory / POLICY_DIRECTORY / "safe-local.json").write_text(json.dumps({"safeLocal": True, "limits": limits or {}}))
        sessions.append(directory)
        return directory

    # Runtime helpers also detect Linux zombies as no longer live.
    sys.path.insert(0, str(PACKAGE))
    from peanut_review import runtime

    def until(check, description, timeout=15):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if check():
                return
            time.sleep(0.05)
        raise AssertionError("Timed out: " + description)

    def finished(directory, name):
        path = directory / "log" / name / "meta.json"
        if not path.exists():
            return False
        meta = json.loads(path.read_text())
        return ("exit_code" in meta and not runtime.is_process_live(meta.get("pid"))
                and not runtime.is_process_live(meta.get("supervisor_pid")))

    checks = []
    try:
        happy = create("persistence")
        cli(happy, "launch", "--dry-run")
        assert not (happy / POLICY_STATE).exists()
        cli(happy, "launch")
        cli(happy, "wait-all", "round-done", "--timeout", "15", "--poll", "0.1")
        for name in ("Reviewer0", "Reviewer1"):
            until(lambda name=name: finished(happy, name), name + " terminal")
        cli(happy, "curate")
        cli(happy, "wait", "round-done", "--timeout", "15", "--poll", "0.1",
            extra_env={"GIT_AUTHOR_NAME": "Curator"})
        until(lambda: finished(happy, "Curator"), "curator terminal")
        visible = json.loads(cli(happy, "comments", "--format", "json"))
        history = json.loads(cli(happy, "comments", "--include-deleted", "--format", "json"))
        notes = json.loads(cli(happy, "notes", "--format", "json"))
        assert len(visible) == 1 and len(history) == 2 and len(notes) == 3
        assert any(comment["deleted"] for comment in history)
        assert visible[0]["versions"], visible
        assert json.loads(cli(happy, "comments", "--format", "json")) == visible
        checks.append("persisted comments, edit history, duplicate deletion and curator ledger")

        cancel = create("cancellation", reviewers=1)
        cli(cancel, "launch", extra_env={"PEANUT_PILOT_MODE": "hang"})
        child_path = cancel / "pilot-child-Reviewer0.pid"
        until(child_path.exists, "fake reviewer and child start")
        cli(cancel, "launch", "--agent", "Reviewer0", expected=1)
        cli(cancel, "kill-agents", "--agent", "Reviewer0", "--dry-run")
        cli(cancel, "kill-agents", "--agent", "Reviewer0", "--timeout", "1")
        until(lambda: finished(cancel, "Reviewer0"), "cancelled supervisor terminal")
        assert not runtime.is_process_live(int(child_path.read_text()))
        cli(cancel, "rerun", "--agent", "Reviewer0")
        cli(cancel, "wait-all", "round-done", "--timeout", "15", "--poll", "0.1")
        until(lambda: finished(cancel, "Reviewer0"), "recovered reviewer terminal")
        attempts = json.loads((cancel / POLICY_STATE).read_text())["launches"]
        assert [attempt["kind"] for attempt in attempts] == ["round", "retry"]
        checks.append("live-launch rejection, verified group cancellation and one recovery retry")

        failure = create("failure", reviewers=1)
        cli(failure, "launch", extra_env={"PEANUT_PILOT_MODE": "fail"})
        cli(failure, "wait-all", "round-done", "--timeout", "15", "--poll", "0.1", expected=1)
        until(lambda: finished(failure, "Reviewer0"), "failed reviewer terminal")
        assert not (failure / "signals" / "Reviewer0.round-done").exists()
        assert not json.loads(cli(failure, "comments", "--format", "json"))
        checks.append("failed run remains incomplete without approval")

        deadline = create("deadline", reviewers=1, timeout=2, limits={"maxSeconds": 2})
        cli(deadline, "launch", extra_env={"PEANUT_PILOT_MODE": "hang"})
        cli(deadline, "wait-all", "round-done", "--timeout", "10", "--poll", "0.1", expected=1)
        until(lambda: finished(deadline, "Reviewer0"), "timed-out reviewer terminal")
        until(lambda: time.time() >= json.loads((deadline / POLICY_STATE).read_text())["deadline"],
              "policy deadline")
        cli(deadline, "rerun", "--agent", "Reviewer0", expected=1)
        checks.append("supervisor timeout cleanup and persistent overall deadline")

        bounded = create("bounded", limits={"maxLaunches": 1})
        cli(bounded, "launch", expected=1)
        assert not (bounded / POLICY_STATE).exists()
        cli(happy, "rerun", "--agent", "Reviewer0")
        cli(happy, "wait-all", "round-done", "--timeout", "15", "--poll", "0.1")
        until(lambda: finished(happy, "Reviewer0"), "second ordinary pass terminal")
        cli(happy, "rerun", "--agent", "Reviewer0", expected=1)
        checks.append("whole-lineup launch cap and two-pass bound")
        assert git("status", "--porcelain", "--untracked-files=all") == ""
        assert git("rev-parse", "HEAD") == head
        assert (repo / "source.py").read_text() == "value = 2\n"
        checks.append("reviewed source unchanged")
        report = {"passed": True, "kind": "offline plumbing only", "base": base, "head": head,
                  "checks": checks, "sessions": [str(path) for path in sessions]}
        (root / "pilot-result.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
    finally:
        for directory in sessions:
            subprocess.run([str(PR), "--session", str(directory), "kill-agents", "--timeout", "1"],
                           env=env, capture_output=True, text=True, timeout=15)
    return 0


if __name__ == "__main__":
    raise SystemExit(fake_codex() if len(sys.argv) > 1 and sys.argv[1] == "--fake-codex" else main())
