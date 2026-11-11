"""Behavioral checks for the local workspace profile."""
import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from peanut_review import session

spec = importlib.util.spec_from_file_location(
    'workspace_review', Path(__file__).resolve().parents[1] / 'scripts/workspace_review.py')
profile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profile)


@pytest.fixture
def source(tmp_path):
    path = tmp_path / 'source'
    path.mkdir()
    profile.git(path, 'init', '-b', 'trunk')
    profile.git(path, 'config', 'user.name', 'Fixture')
    profile.git(path, 'config', 'user.email', 'fixture@example.invalid')
    (path / 'code.py').write_text('value = 1\n')
    profile.git(path, 'add', 'code.py')
    profile.git(path, 'commit', '-m', 'base')
    profile.git(path, 'checkout', '-b', 'candidate')
    (path / 'code.py').write_text('value = 2\n')
    profile.git(path, 'commit', '-am', 'change')
    return path


def init_args(source, directory):
    return profile.parser().parse_args(['init', '--source', str(source), '--base', 'trunk',
        '--session', str(directory), '--model', 'test-model', '--effort', 'high'])


def test_init_pins_personas_and_does_not_modify_source_refs(source, tmp_path):
    before = profile.git(source, 'show-ref')
    directory = profile.initialize(init_args(source, tmp_path / 'review'))
    current = session.load_session(directory)
    assert profile.git(source, 'show-ref') == before
    assert current.git_common_dir == ''
    assert profile.git(source, 'status', '--porcelain') == ''
    assert [agent.persona for agent in current.agents[:2]] == ['release-contracts.md', 'test-evidence.md']
    assert len(current.agents) == 3
    snapshot = json.loads((profile.local_policy.policy_directory(directory) / 'workspace-snapshot.json').read_text())
    assert snapshot['head'] == current.current_head
    assert snapshot['mergeBase'] == profile.git(source, 'rev-parse', 'trunk')
    assert profile.local_policy.enabled(directory)
    assert 'Workspace review contract' in (directory / 'templates/agent-prompt.md').read_text()


def test_init_rejects_dirty_source_and_overlapping_session(source):
    with pytest.raises(ValueError, match='overlap'):
        profile.initialize(init_args(source, source / 'review'))
    (source / 'untracked').write_text('preserve me')
    with pytest.raises(ValueError, match='clean source'):
        profile.initialize(init_args(source, source.parent / 'review'))
    assert (source / 'untracked').read_text() == 'preserve me'


def test_base_movement_invalidates_review(source, tmp_path):
    directory = profile.initialize(init_args(source, tmp_path / 'review'))
    profile.git(source, 'branch', '-f', 'trunk', 'HEAD')
    with pytest.raises(ValueError, match='base ref changed'):
        profile.snapshot_current(directory)


def test_session_migration_cannot_relabel_old_completion(source, tmp_path):
    directory = profile.initialize(init_args(source, tmp_path / 'review'))
    (source / 'code.py').write_text('value = 3\n')
    profile.git(source, 'commit', '-am', 'later change')
    current = session.load_session(directory)
    current.current_head = profile.git(source, 'rev-parse', 'HEAD')
    current.topic_ref = current.current_head
    session.save_session(directory, current)
    with pytest.raises(ValueError, match='session snapshot differs'):
        profile.snapshot_current(directory)


def test_status_labels_stale_results_even_when_all_workers_completed(source, tmp_path, monkeypatch, capsys):
    directory = profile.initialize(init_args(source, tmp_path / 'review'))
    (directory / 'result.md').write_text('Previous review result')
    (source / 'code.py').write_text('value = 3\n')
    profile.git(source, 'commit', '-am', 'later change')
    monkeypatch.setattr(profile.runtime, 'inspect_agent_runtime', lambda *_: dict(
        signal=True, process_state='exited', exit_code=0, reviewer_live=False, supervisor_live=False))
    profile.status(directory)
    result = json.loads(capsys.readouterr().out)
    assert result['status'] == 'stale'
    assert all(row['complete'] for row in result['agents'])


@pytest.mark.parametrize('changes', [
    {'process_state': 'running', 'reviewer_live': True},
    {'supervisor_live': True}, {'exit_code': 1, 'process_state': 'failed'}, {'signal': False},
])
def test_signal_alone_is_not_success(changes):
    state = dict(signal=True, process_state='exited', exit_code=0,
                 reviewer_live=False, supervisor_live=False)
    assert profile.completed(state)
    state.update(changes)
    assert not profile.completed(state)


def test_wait_rejects_signaled_failure(source, tmp_path, monkeypatch):
    directory = profile.initialize(init_args(source, tmp_path / 'review'))
    monkeypatch.setattr(profile.runtime, 'inspect_agent_runtime', lambda *_: dict(
        signal=True, process_state='failed', exit_code=1, reviewer_live=False, supervisor_live=False))
    with pytest.raises(RuntimeError, match='did not complete'):
        profile.wait_completed(directory, ['release-contracts'], 0)


def test_retry_requires_a_fresh_signal_from_actual_worker(source, tmp_path, monkeypatch):
    directory = profile.initialize(init_args(source, tmp_path / 'review'))
    fake_bin = tmp_path / 'fake-bin'
    fake_bin.mkdir()
    fake_codex = fake_bin / 'codex'
    # Exit successfully but deliberately never signal this round as complete.
    fake_codex.write_text('#!/bin/bash\nexit 0\n')
    fake_codex.chmod(0o755)
    monkeypatch.setenv('PATH', str(fake_bin) + os.pathsep + os.environ['PATH'])
    for name in ('release-contracts', 'test-evidence'):
        (directory / 'signals' / (name + '.round-done')).write_text('old failed attempt\n')
        profile.runtime.update_agent_meta(directory, name, {
            'process_state': 'failed', 'exit_code': 1, 'end': 'old attempt'})
    with pytest.raises(RuntimeError, match='did not complete successfully'):
        profile.run_review(SimpleNamespace(session=str(directory), retry_failed=True, dry_run=False))
    assert not (directory / 'signals/release-contracts.round-done').exists()
    assert profile.runtime.read_agent_meta(directory, 'release-contracts')['exit_code'] == 0
    assert not (directory / 'result.md').exists()
    assert not profile.runtime.read_agent_meta(directory, 'Curator')


def test_run_waits_for_curator_and_marks_failure_incomplete(source, tmp_path, monkeypatch):
    directory = profile.initialize(init_args(source, tmp_path / 'review'))
    calls = []
    monkeypatch.setattr(profile, 'pending_agents', lambda _, agents, **__: [a.name for a in agents])
    # The rerun API clears old runtime and completion signals only after policy
    # reserves the attempt. Plain launch would retain stale signals on retries.
    monkeypatch.setattr(profile.launch, 'rerun_agents', lambda *_, **__: calls.append('launch-reviewers'))
    monkeypatch.setattr(profile.launch, 'launch_curator', lambda *_, **__: calls.append('launch-curator'))
    monkeypatch.setattr(profile, 'deadline_for', lambda _: 1000)
    monkeypatch.setattr(profile.agent_control, 'kill_agents', lambda _: calls.append('cancel'))
    def wait(_, names, deadline):
        calls.append(('wait', names))
        if names == ['Curator']:
            raise RuntimeError('curator failed')
    monkeypatch.setattr(profile, 'wait_completed', wait)
    with pytest.raises(RuntimeError, match='curator failed'):
        profile.run_review(SimpleNamespace(session=str(directory), retry_failed=False, dry_run=False))
    assert calls == ['launch-reviewers', ('wait', ['release-contracts', 'test-evidence']),
                     'launch-curator', ('wait', ['Curator']), 'cancel']
    assert json.loads((directory / 'workspace-result.json').read_text())['status'] == 'incomplete'
    assert not (directory / 'result.md').exists()
