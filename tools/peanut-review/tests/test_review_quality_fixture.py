"""Distinguishing behaviors behind the fictional review replay, without models."""
import importlib.util
from pathlib import Path
import subprocess

import pytest


spec = importlib.util.spec_from_file_location(
    'review_quality_fixture', Path(__file__).resolve().parents[1] / 'scripts/review_quality_fixture.py')
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


def module(files, name):
    namespace = {}
    exec(compile(files[name], name, 'exec'), namespace)
    return namespace


def test_existing_history_can_allocate_on_base_but_not_candidate():
    for files, broken in ((fixture.BASE, False), (fixture.candidate_sources(), True)):
        history = module(files, 'history.py')
        records = [{'ticket': 4}, {'ticket': 8, 'payload_digest': 'old-digest'}]
        if broken:
            with pytest.raises(ValueError, match='digest'):
                history['allocate'](records, 'new-digest')
            assert len(records) == 2
        else:
            assert history['allocate'](records, 'new-digest') == 9


def test_active_validation_is_a_valid_new_requirement():
    history = module(fixture.candidate_sources(), 'history.py')
    with pytest.raises(ValueError, match='digest'):
        history['resume']({'ticket': 4})
    assert history['resume']({'ticket': 4, 'payload_digest': 'digest'}) == 4
    assert history['allocate']([], 'digest') == 1


def test_smaller_retry_converges_on_base_but_not_candidate():
    for files, broken in ((fixture.BASE, False), (fixture.candidate_sources(), True)):
        transfer = module(files, 'transfer.py')
        remote = {'old.bin': b'old', 'keep.bin': b'keep'}
        desired = {'keep.bin': b'keep'}
        if broken:
            with pytest.raises(ValueError, match='inventory'):
                transfer['publish'](desired, remote)
            assert remote['old.bin'] == b'old'
        else:
            transfer['publish'](desired, remote)
            assert remote == desired
        # Completed checkpoints remain immutable even when verification fails.
        before = dict(remote)
        with pytest.raises(ValueError, match='inventory'):
            transfer['publish']({'other.bin': b'new'}, remote, completed=True)
        assert remote == before


@pytest.mark.parametrize('files', [fixture.BASE, fixture.candidate_sources()])
def test_empty_selection_is_a_valid_negative_control(files):
    jobs = module(files, 'jobs.py')
    dispatched = []
    assert jobs['run_jobs']([], dispatched.append) == []
    assert dispatched == []
    with pytest.raises(ValueError, match='list'):
        jobs['run_jobs']({}, dispatched.append)
    jobs['run_jobs'](['compile'], dispatched.append)
    assert dispatched == ['compile']


def test_generator_creates_clean_pinned_source_and_refuses_reuse(tmp_path):
    output = tmp_path / 'source'
    manifest = fixture.create(output)
    git = lambda *args: subprocess.check_output(['git', '-C', str(output), *args], text=True).strip()
    assert manifest['base'] == git('rev-parse', 'base')
    assert manifest['head'] == git('rev-parse', 'HEAD')
    assert not git('status', '--porcelain')
    assert sorted(p.name for p in output.iterdir() if p.name != '.git') == sorted(fixture.BASE)
    with pytest.raises(FileExistsError):
        fixture.create(output)


def test_independent_branches_pass_but_composed_record_is_rejected():
    consumer = module(fixture.integration_candidate_sources(), 'common.py')
    # Execute actual generated consumer code against its real generated dependency.
    import sys
    from types import ModuleType
    from unittest import mock
    common = ModuleType('common')
    common.__dict__.update(consumer)
    with mock.patch.dict(sys.modules, {'common': common}):
        backfill = module(fixture.integration_candidate_sources(), 'backfill.py')
    old = module(fixture.RELATED_BASE, 'producer.py')
    new = module(fixture.RELATED_CANDIDATE, 'producer.py')
    recipe = {'components': ['board']}
    assert backfill['validate'](old['make'](recipe), recipe) == 'build-7'
    assert new['validate'](new['make'](recipe), recipe)
    with pytest.raises(ValueError, match='identity'):
        backfill['validate'](new['make'](recipe), recipe)


def test_invalid_request_only_mutates_history_after_regression():
    for sources, expected in ((fixture.INTEGRATION_BASE, []), (fixture.integration_candidate_sources(), [1])):
        service = module(sources, 'service.py')
        history = []
        with pytest.raises(ValueError, match='unsupported'):
            service['reserve']({'components': [], 'old_layout': True}, history)
        assert history == expected
        assert service['reserve']({'components': []}, []) == 1


def test_extraction_loses_transient_retry_policy_but_not_permanent_errors():
    for sources, expected_attempts in ((fixture.INTEGRATION_BASE, 4), (fixture.integration_candidate_sources(), 1)):
        transfer = module(sources, 'transfer.py')
        attempts = []
        def send():
            attempts.append(1)
            if len(attempts) < 4:
                raise OSError('transient')
            return 'sent'
        if expected_attempts == 4:
            assert transfer['run_transfer'](send) == 'sent'
        else:
            with pytest.raises(OSError):
                transfer['run_transfer'](send)
        assert len(attempts) == expected_attempts
        with pytest.raises(ValueError):
            transfer['run_transfer'](lambda: (_ for _ in ()).throw(ValueError('invalid')))


def test_integration_generator_has_distinct_clean_pinned_inputs(tmp_path):
    result = fixture.create_integration(tmp_path / 'inputs')
    assert result['source'] != result['related_sources'][0]['source']
    for record in (result, *result['related_sources']):
        source = record['source']
        assert subprocess.check_output(['git', '-C', source, 'rev-parse', 'HEAD'], text=True).strip() == record['head']
        assert not subprocess.check_output(['git', '-C', source, 'status', '--porcelain'], text=True).strip()
    jobs = module(fixture.integration_candidate_sources(), 'jobs.py')
    assert jobs['run_jobs']([], lambda _: pytest.fail('empty work dispatched')) == []
