"""Workspace policy tests: real snapshots, persistent bounds, no model calls."""
import json
import os
from pathlib import Path
import subprocess

import pytest

from peanut_review import launch, local_policy as policy, polling, runtime, session as sessions


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


@pytest.fixture
def review(tmp_path):
    repo = tmp_path / "source"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Pilot")
    git(repo, "config", "user.email", "pilot@example.invalid")
    git(repo, "config", "commit.gpgsign", "false")
    (repo / "source.txt").write_text("base\n")
    git(repo, "add", "source.txt")
    git(repo, "commit", "-m", "base")
    base = git(repo, "rev-parse", "HEAD")
    (repo / "source.txt").write_text("changed\n")
    git(repo, "commit", "-am", "change")
    directory = tmp_path / "session"
    agents = [{"name": name, "role": role, "runner": "codex", "model": "test-model",
               "reasoningEffort": "medium", "persona": "test.md"}
              for name, role in (("A", "reviewer"), ("B", "reviewer"), ("Curator", "curator"))]
    session, _ = sessions.create_session(workspace=str(repo), base_ref=base,
                                        agents=agents, session_dir=str(directory), timeout=300)
    policy.policy_directory(directory).mkdir(parents=True)
    (directory / policy.CONFIG_NAME).write_text('{"safeLocal": true}')
    return directory, session, repo


def reserve(review, names=("A",), dry_run=False):
    directory, session, _ = review
    agents = [agent for agent in session.agents if agent.name in names]
    with policy.launch_budget(directory, session, agents, dry_run=dry_run) as timeout:
        return timeout


def test_legacy_session_is_unchanged(review):
    directory, session, repo = review
    (directory / policy.CONFIG_NAME).unlink()
    (repo / "source.txt").write_text("dirty")
    session.agents[0].runner = "cursor"
    assert reserve(review) == 300
    assert not (directory / policy.STATE_NAME).exists()


def test_dry_run_does_not_start_clock_or_consume_launches(review):
    directory, _, _ = review
    assert reserve(review, dry_run=True) == 300
    assert not (directory / policy.STATE_NAME).exists()
    assert reserve(review) == 300
    state = json.loads((directory / policy.STATE_NAME).read_text())
    assert len(state["launches"]) == 1


@pytest.mark.parametrize("change,error", [
    (lambda s: setattr(s.agents[0], "runner", "cursor"), "local Codex"),
    (lambda s: setattr(s.agents[0], "model", ""), "explicit model"),
    (lambda s: setattr(s.agents[0], "reasoning_effort", ""), "reasoningEffort"),
    (lambda s: setattr(s.agents[2], "role", "reviewer"), "one or two reviewers"),
])
def test_rejects_unbounded_or_unsupported_lineup(review, change, error):
    directory, session, _ = review
    change(session)
    sessions.save_session(directory, session)
    with pytest.raises(ValueError, match=error):
        reserve(review)
    assert not (directory / policy.STATE_NAME).exists()


def test_checks_local_snapshot_and_cleanliness(review):
    directory, session, repo = review
    (repo / "source.txt").write_text("uncommitted\n")
    with pytest.raises(ValueError, match="clean source"):
        reserve(review)
    git(repo, "commit", "-am", "later change")
    with pytest.raises(ValueError, match="pinned review head"):
        reserve(review)
    assert not (directory / policy.STATE_NAME).exists()


def test_two_rounds_plus_one_failure_retry_survive_reload(review):
    directory, session, _ = review
    reserve(review)  # Failed first start: consumes a normal attempt.
    reserve(review)  # No completion: exactly one recovery retry.
    with pytest.raises(ValueError, match="retry limit"):
        reserve(review)
    polling.write_signal(directory, "A", "round-done")
    runtime.update_agent_meta(directory, "A", {"exit_code": 0, "process_state": "exited"})
    reserve(review)  # Successful recovery permits the second ordinary pass.
    with pytest.raises(ValueError, match="round limit"):
        reserve(review)
    state = json.loads((directory / policy.STATE_NAME).read_text())
    assert [item["kind"] for item in state["launches"]] == ["round", "retry", "round"]


def test_signaled_failure_uses_retry_allowance(review):
    directory, _, _ = review
    reserve(review)
    polling.write_signal(directory, "A", "round-done")
    runtime.update_agent_meta(directory, "A", {"exit_code": 7, "process_state": "failed"})
    reserve(review)
    state = json.loads((directory / policy.STATE_NAME).read_text())
    assert [item["kind"] for item in state["launches"]] == ["round", "retry"]


def test_curator_retry_does_not_block_next_ordinary_curation_pass(review):
    directory, session, _ = review
    reserve(review, ("Curator",))
    runtime.update_agent_meta(directory, "Curator", {"exit_code": 7, "process_state": "failed"})
    reserve(review, ("Curator",))  # Its one real failure retry.
    polling.write_signal(directory, "Curator", "round-done")
    runtime.update_agent_meta(directory, "Curator", {"exit_code": 0, "process_state": "exited"})
    reserve(review, ("A", "B"))
    # Real launch behavior invalidates old curator state on a reviewer pass.
    launch._prepare_curation_baseline(directory, session, session.agents[:2])
    reserve(review, ("Curator",))
    state = json.loads((directory / policy.STATE_NAME).read_text())
    assert [item["kind"] for item in state["launches"] if item["agent"] == "Curator"] == [
        "round", "retry", "round"]


def test_total_limit_rejects_whole_lineup_without_partial_reservation(review):
    directory, _, _ = review
    (directory / policy.CONFIG_NAME).write_text(json.dumps({
        "safeLocal": True, "limits": {"maxLaunches": 1}}))
    with pytest.raises(ValueError, match="total launch limit"):
        reserve(review, ("A", "B"))
    assert not (directory / policy.STATE_NAME).exists()


def test_live_duplicate_and_concurrency_guards(review):
    directory, session, _ = review
    session.agents[0].pid = os.getpid()
    sessions.save_session(directory, session)
    with pytest.raises(ValueError, match="live agent"):
        reserve(review)
    (directory / policy.CONFIG_NAME).write_text(json.dumps({
        "safeLocal": True, "limits": {"maxConcurrent": 1}}))
    with pytest.raises(ValueError, match="concurrent-agent"):
        reserve(review, ("B",))


def test_deadline_persists_and_limits_supervisor_timeout(review, monkeypatch):
    directory, _, _ = review
    monkeypatch.setattr(policy.time, "time", lambda: 1000)
    reserve(review)
    monkeypatch.setattr(policy.time, "time", lambda: 2795)
    assert reserve(review, ("B",)) == 5
    assert policy.remaining_timeout(directory, 300) == 5
    monkeypatch.setattr(policy.time, "time", lambda: 2801)
    with pytest.raises(ValueError, match="deadline exhausted"):
        reserve(review, ("Curator",))
    with pytest.raises(ValueError, match="deadline exhausted"):
        policy.remaining_timeout(directory, 300)


def test_policy_can_only_tighten_defaults_and_lineup_is_frozen(review):
    directory, session, _ = review
    (directory / policy.CONFIG_NAME).write_text(json.dumps({
        "safeLocal": True, "limits": {"maxLaunches": 10}}))
    with pytest.raises(ValueError, match="maxLaunches"):
        reserve(review)
    (directory / policy.CONFIG_NAME).write_text('{"safeLocal": true}')
    reserve(review)
    session.agents[0].model = "other-model"
    sessions.save_session(directory, session)
    with pytest.raises(ValueError, match="lineup/repository changed"):
        reserve(review)
