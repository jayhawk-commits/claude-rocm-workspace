"""Exercise wrapper scope checks and actual argv without calling a model."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from peanut_review import launch


def _paths(tmp_path):
    source = tmp_path / "source with spaces"
    source.mkdir()
    (source / "keep.txt").write_text("unchanged\n")
    return source, tmp_path / "session with spaces"


def _run(source, session, *args, env=None):
    return subprocess.run([
        launch._find_launcher_script("codex"),
        "--workspace", str(source), "--session-dir", str(session),
        "--model", "configured-model", "--reasoning-effort", "ultra",
        "--name", "reviewer", "--prompt", "inspect source", *args,
    ], capture_output=True, text=True, env=env)


def test_runner_limits_writes_to_session_and_preserves_model(tmp_path):
    source, session = _paths(tmp_path)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake = fake_bin / "codex"
    fake.write_text(
        f"#!{sys.executable}\n"
        "import json, os, pathlib, sys\n"
        "pathlib.Path(os.environ['ARGV_CAPTURE']).write_text(json.dumps(\n"
        " {'argv': sys.argv[1:], 'tmpdir': os.environ['TMPDIR']}))\n"
    )
    fake.chmod(0o755)
    capture = tmp_path / "argv.json"
    env = {**os.environ, "PATH": f"{fake_bin}:{os.environ['PATH']}", "ARGV_CAPTURE": str(capture)}
    result = _run(source, session, "--model", "configured-model", "--reasoning-effort", "ultra", env=env)
    assert result.returncode == 0, result.stderr
    recorded = json.loads(capture.read_text())
    args = recorded["argv"]
    assert args[:1] == ["exec"]
    assert {"--ignore-user-config", "--ignore-rules", "--ephemeral"} <= set(args)
    disabled = {args[i + 1] for i, item in enumerate(args) if item == "--disable"}
    assert {"multi_agent", "apps", "browser_use", "computer_use"} <= disabled
    assert args[args.index("--cd") + 1] == str(session / "log" / "reviewer")
    assert args[args.index("--sandbox") + 1] == "workspace-write"
    assert args[args.index("--add-dir") + 1] == str(session)
    assert args.count("--add-dir") == 1
    assert args[args.index("--model") + 1] == "configured-model"
    configs = [args[i + 1] for i, item in enumerate(args) if item == "-c"]
    assert set(configs) == {
        'web_search="disabled"',
        'approval_policy="never"',
        'model_reasoning_effort="ultra"',
        "sandbox_workspace_write.writable_roots=[]",
        "sandbox_workspace_write.exclude_slash_tmp=true",
        "sandbox_workspace_write.exclude_tmpdir_env_var=true",
        "sandbox_workspace_write.network_access=false",
    }
    assert recorded["tmpdir"] == str(session / "log" / "reviewer" / "tmp")
    assert (source / "keep.txt").read_text() == "unchanged\n"
    assert list(source.iterdir()) == [source / "keep.txt"]


@pytest.mark.parametrize("sandbox", ["danger-full-access", "read-only", "unknown"])
def test_runner_rejects_other_sandboxes_before_creating_session(tmp_path, sandbox):
    source, session = _paths(tmp_path)
    result = _run(source, session, "--sandbox", sandbox, "--dry-run")
    assert result.returncode != 0
    assert "requires the workspace-write sandbox" in result.stderr
    assert not session.exists()


@pytest.mark.parametrize("relationship", ["same", "child", "parent", "root", "symlink"])
def test_runner_rejects_overlapping_roots(tmp_path, relationship):
    source, session = _paths(tmp_path)
    if relationship == "same":
        session = source
    elif relationship == "child":
        session = source / "session"
    elif relationship == "parent":
        session = tmp_path
    elif relationship == "root":
        session = Path("/")
    else:
        session.symlink_to(source, target_is_directory=True)
    result = _run(source, session, "--dry-run")
    assert result.returncode != 0
    assert "must not overlap" in result.stderr
    assert list(source.iterdir()) == [source / "keep.txt"]


@pytest.mark.parametrize("escape", ["output", "extra-root", "task-symlink", "artifact-symlink", "name"])
def test_runner_rejects_writes_outside_session(tmp_path, escape):
    source, session = _paths(tmp_path)
    session.mkdir()
    args = []
    if escape == "output":
        args = ["--output-dir", str(tmp_path / "outside")]
    elif escape == "extra-root":
        args = ["--add-dir", str(tmp_path)]
    elif escape == "task-symlink":
        (session / "log").symlink_to(source, target_is_directory=True)
    elif escape == "artifact-symlink":
        task = session / "log" / "reviewer"
        task.mkdir(parents=True)
        (task / "stream.jsonl").symlink_to(source / "keep.txt")
    else:
        args = ["--name", "../../escape"]
    result = _run(source, session, *args, "--dry-run")
    assert result.returncode != 0
    assert (source / "keep.txt").read_text() == "unchanged\n"
    assert not (tmp_path / "outside").exists()


def test_runner_requires_explicit_session(tmp_path):
    source, _ = _paths(tmp_path)
    result = subprocess.run([
        launch._find_launcher_script("codex"), "--workspace", str(source),
        "--prompt", "inspect source", "--dry-run",
    ], capture_output=True, text=True)
    assert result.returncode != 0
    assert "--session-dir" in result.stderr
    assert list(source.iterdir()) == [source / "keep.txt"]
