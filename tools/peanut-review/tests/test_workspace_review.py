"""Behavioral checks for the local workspace profile."""
import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from peanut_review import session
from peanut_review.models import Comment

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


@pytest.fixture
def related_source(source, tmp_path):
    path = tmp_path / 'related source'
    profile.git(source, 'clone', '--no-hardlinks', str(source), str(path))
    profile.git(path, 'config', 'user.name', 'Fixture')
    profile.git(path, 'config', 'user.email', 'fixture@example.invalid')
    return path


def related_args(source, related, directory):
    return profile.parser().parse_args(['init', '--source', str(source), '--base', 'trunk',
        '--session', str(directory), '--model', 'test-model', '--effort', 'high',
        '--related-source', str(related)])


def test_related_inputs_are_pinned_and_delivered_without_source_mutation(source, related_source, tmp_path):
    before = {root: profile.git(root, 'show-ref') for root in (source, related_source)}
    args = related_args(source, related_source, tmp_path / 'review')
    directory = profile.initialize(args)
    manifest = profile.local_policy.policy_directory(directory) / 'workspace-snapshot.json'
    snapshot = json.loads(manifest.read_text())
    assert snapshot['relatedSources'] == [{
        'path': str(related_source.resolve()), 'head': profile.git(related_source, 'rev-parse', 'HEAD'),
        'clean': True}]
    for name in ('agent-prompt.md', 'curator-prompt.md'):
        template = (directory / 'templates' / name).read_text()
        assert str(manifest) in template
        assert 'Combined compatibility' in template or 'combined compatibility' in template
        assert 'local, read-only inputs' in template
    for root in (source, related_source):
        assert profile.git(root, 'show-ref') == before[root]
        assert profile.git(root, 'status', '--porcelain') == ''
    profile.snapshot_current(directory)


@pytest.mark.parametrize('kind', ['primary', 'duplicate', 'nested', 'session-overlap', 'limit', 'dirty'])
def test_related_inputs_reject_invalid_scope_before_creating_session(source, related_source, tmp_path, kind):
    args = related_args(source, related_source, tmp_path / 'review')
    if kind == 'primary':
        args.related_source = [str(source)]
    elif kind == 'duplicate':
        args.related_source *= 2
    elif kind == 'nested':
        args.related_source = [str(source / '.git')]
    elif kind == 'session-overlap':
        args.session = str(related_source / 'review')
    elif kind == 'limit':
        args.related_source *= profile.MAX_RELATED_SOURCES + 1
    else:
        (related_source / 'untracked').write_text('preserve this work')
    with pytest.raises(ValueError):
        profile.initialize(args)
    assert not Path(args.session).exists()
    if kind == 'dirty':
        assert (related_source / 'untracked').read_text() == 'preserve this work'


@pytest.mark.parametrize('mutation', ['dirty', 'head'])
def test_related_source_movement_invalidates_snapshot(source, related_source, tmp_path, mutation):
    directory = profile.initialize(related_args(source, related_source, tmp_path / 'review'))
    (related_source / 'code.py').write_text('value = 3\n')
    if mutation == 'head':
        profile.git(related_source, 'commit', '-am', 'new related revision')
    with pytest.raises(ValueError, match='related source'):
        profile.snapshot_current(directory)


def test_related_source_change_prevents_successful_final_export(source, related_source, tmp_path, monkeypatch):
    directory = profile.initialize(related_args(source, related_source, tmp_path / 'review'))
    monkeypatch.setattr(profile, 'pending_agents', lambda _, agents, **__: [a.name for a in agents])
    monkeypatch.setattr(profile.launch, 'rerun_agents', lambda *_, **__: None)
    monkeypatch.setattr(profile.launch, 'launch_curator', lambda *_, **__: None)
    monkeypatch.setattr(profile, 'deadline_for', lambda _: 1000)
    monkeypatch.setattr(profile.agent_control, 'kill_agents', lambda _: None)

    def wait(_, names, deadline):
        if names == ['Curator']:
            (related_source / 'code.py').write_text('value = 3\n')
            profile.git(related_source, 'commit', '-am', 'moved during review')

    monkeypatch.setattr(profile, 'wait_completed', wait)
    with pytest.raises(ValueError, match='related source HEAD changed'):
        profile.run_review(SimpleNamespace(session=str(directory), retry_failed=False, dry_run=False))
    assert json.loads((directory / 'workspace-result.json').read_text())['status'] == 'incomplete'
    assert not (directory / 'result.md').exists()


def test_legacy_snapshot_without_related_inputs_still_validates(source, tmp_path):
    directory = profile.initialize(init_args(source, tmp_path / 'review'))
    manifest = profile.local_policy.policy_directory(directory) / 'workspace-snapshot.json'
    snapshot = json.loads(manifest.read_text())
    del snapshot['relatedSources']
    profile.write_json(manifest, snapshot)
    profile.snapshot_current(directory)


def write_covered_approval(directory):
    current = session.load_session(directory)
    for agent in current.agents:
        profile.write_json(directory / 'coverage' / f'{agent.name}.json', {
            'head': current.current_head, 'base': current.base_ref, 'verdict': 'approve',
            'areas': [{'id': name, 'status': 'not_applicable', 'material': False,
                       'evidence': 'Fixture changes only a constant; this contract is not reached.'}
                      for name in profile.review_coverage.AREAS]})


def test_missing_coverage_suppresses_approval_but_preserves_finding_and_raw_store(source, tmp_path):
    directory = profile.initialize(init_args(source, tmp_path / 'review'))
    profile.store.append_comment(directory, Comment(author='Curator', body='LGTM'))
    profile.store.append_comment(directory, Comment(author='Curator', category='approve',
                                                   body='Approved within the inspected scope.'))
    profile.store.append_comment(directory, Comment(author='release-contracts', file='code.py', line=1,
                                                   body='This caller still needs a compatible input.'))
    report = profile.export_result(directory).read_text()
    assert 'wait_for_evidence' in report
    assert 'missing or invalid coverage record' in report
    assert 'LGTM' not in report
    assert 'Approved within' not in report
    assert 'This caller still needs' in report
    assert len(profile.store.read_all_comments(directory)) == 3


def test_complete_coverage_allows_approval_export(source, tmp_path):
    directory = profile.initialize(init_args(source, tmp_path / 'review'))
    write_covered_approval(directory)
    profile.store.append_comment(directory, Comment(author='Curator', body='LGTM'))
    report = profile.export_result(directory).read_text()
    assert 'Recommendation: **approve**' in report
    assert 'LGTM' in report


@pytest.mark.parametrize('covered', [False, True])
def test_successful_process_flow_records_coverage_recommendation(source, tmp_path, monkeypatch, covered):
    directory = profile.initialize(init_args(source, tmp_path / 'review'))
    if covered:
        write_covered_approval(directory)
    monkeypatch.setattr(profile, 'pending_agents', lambda _, agents, **__: [a.name for a in agents])
    monkeypatch.setattr(profile.launch, 'rerun_agents', lambda *_, **__: None)
    monkeypatch.setattr(profile.launch, 'launch_curator', lambda *_, **__: None)
    monkeypatch.setattr(profile, 'deadline_for', lambda _: 1000)
    monkeypatch.setattr(profile, 'wait_completed', lambda *_: None)
    profile.run_review(SimpleNamespace(session=str(directory), retry_failed=False, dry_run=False))
    result = json.loads((directory / 'workspace-result.json').read_text())
    assert result['status'] == 'complete'
    assert result['recommendation'] == ('approve' if covered else 'wait_for_evidence')
    assert bool(result['materialGaps']) is not covered


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


def test_regression_guidance_reaches_reviewers_and_curator(source, tmp_path):
    directory = profile.initialize(init_args(source, tmp_path / 'review'))
    # These templates are the ones run_review passes to the actual launch APIs.
    # Check delivery to both roles, independently of persona wording or model output.
    guide = profile.WORKSPACE_ROOT / 'skills/review-panel/references/regression-probes.md'
    assert guide.is_file()
    for name in ('agent-prompt.md', 'curator-prompt.md'):
        template = (directory / 'templates' / name).read_text()
        assert str(guide) in template
        assert 'Apply only reachable scenarios' in template
    for agent in session.load_session(directory).agents[:2]:
        assert (directory / 'personas' / agent.persona).is_file()


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


def test_status_completion_does_not_claim_approval_without_coverage(source, tmp_path, monkeypatch, capsys):
    directory = profile.initialize(init_args(source, tmp_path / 'review'))
    monkeypatch.setattr(profile.runtime, 'inspect_agent_runtime', lambda *_: dict(
        signal=True, process_state='exited', exit_code=0, reviewer_live=False, supervisor_live=False))
    profile.status(directory)
    result = json.loads(capsys.readouterr().out)
    assert result['status'] == 'complete'
    assert result['recommendation'] == 'wait_for_evidence'
    assert len(result['materialGaps']) == 3


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
