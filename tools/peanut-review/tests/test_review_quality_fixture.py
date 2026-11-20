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


@pytest.mark.parametrize('restored', [False, True])
def test_dispatch_guard_protects_fresh_and_restored_paths(restored):
    for files, broken in ((fixture.LIFECYCLE_BASE, False), (fixture.lifecycle_candidate_sources(), True)):
        dispatch = module(files, 'dispatch.py')['run']
        events = []
        if broken and restored:
            assert dispatch('topic', False, restored, events) == 'restored'
        else:
            with pytest.raises(ValueError, match='stable'):
                dispatch('topic', False, restored, events)
        assert bool(events) == broken
        assert dispatch('topic', True, restored, []) in {'resolved', 'restored'}
        assert dispatch('stable', False, restored, []) in {'resolved', 'restored'}


def test_cleanup_cap_allows_progress_above_limit_with_authority_controls():
    for files, broken in ((fixture.LIFECYCLE_BASE, False), (fixture.lifecycle_candidate_sources(), True)):
        sweep = module(files, 'maintenance.py')['sweep']
        records = {str(i): {'terminal': True, 'protected': False} for i in range(5)}
        records['active'] = {'terminal': False, 'protected': False}
        records['completed'] = {'terminal': True, 'protected': True}
        if broken:
            with pytest.raises(ValueError, match='cap exceeded'):
                sweep(records, lambda _: True)
            assert len(records) == 7
        else:
            assert len(sweep(records, lambda _: True)) == 4
            assert len(sweep(records, lambda _: True)) == 1
            assert sweep(records, lambda _: True) == []
            assert set(records) == {'active', 'completed'}
        # At the cap, both versions still protect against a changed authority.
        small = {'one': {'terminal': True, 'protected': False}}
        with pytest.raises(ValueError, match='authority changed'):
            sweep(small, lambda _: False)
        assert 'one' in small


def test_explicit_historical_outputs_activate_validation_legacy_fixture_misses():
    for files, broken in ((fixture.LIFECYCLE_BASE, False), (fixture.lifecycle_candidate_sources(), True)):
        archive = module(files, 'archive.py')
        old = archive['make'](['north', 'south'], algorithm='v1')
        if broken:
            with pytest.raises(ValueError, match='active plan changed'):
                archive['read_published'](old)
        else:
            assert archive['read_published'](old) == 7
        with pytest.raises(ValueError, match='active plan changed'):
            archive['validate_active'](old)
        assert archive['read_published']({'id': 7}) == 7
        current = archive['make'](['north', 'south'])
        assert archive['read_published'](current) == 7
        archive['validate_active'](current)
        current['outputs'].pop()
        with pytest.raises(ValueError):
            archive['read_published'](current)


def test_empty_publication_reports_contract_error_before_selecting_entry():
    base = module(fixture.LIFECYCLE_BASE, 'selection.py')['select']
    candidate = module(fixture.lifecycle_candidate_sources(), 'selection.py')['select']
    with pytest.raises(ValueError, match='nonempty published set'):
        base({})
    with pytest.raises(StopIteration):
        candidate({})
    assert base({'north': 'record'}) == candidate({'north': 'record'}) == 'record'


def test_credential_contract_keeps_distinct_values_and_single_key_callers():
    base = module(fixture.LIFECYCLE_BASE, 'credentials.py')['keys']
    candidate = module(fixture.lifecycle_candidate_sources(), 'credentials.py')['keys']
    assert base('primary-test', 'legacy-test') == ('primary-test', 'legacy-test')
    assert candidate('primary-test', 'legacy-test') == ('primary-test', 'primary-test')
    assert base('', 'legacy-test') == ('legacy-test', 'legacy-test')
    with pytest.raises(ValueError):
        candidate('', 'legacy-test')
    for keys in (base, candidate):
        assert keys('primary-test') == ('primary-test', 'primary-test')
        with pytest.raises(ValueError):
            keys()


def verify_receipt(output, receipt):
    if receipt == 'unreadable':
        raise OSError('read failed')
    return receipt == output


def test_completion_precedes_expensive_build_and_all_complete_is_valid():
    for files, broken in ((fixture.LIFECYCLE_BASE, False), (fixture.lifecycle_candidate_sources(), True)):
        pipeline = module(files, 'pipeline.py')
        receipts = {'north': 'north', 'south': None, 'west': 'wrong', 'east': 'unreadable'}
        pending, ready, errors = pipeline['build_plan'](receipts, verify_receipt)
        if broken:
            assert pending == list(receipts)
        else:
            assert (pending, ready, errors) == (['south'], ['north'], ['west', 'east'])
        pending, ready, errors = pipeline['build_plan']({'north': 'north'}, verify_receipt)
        assert bool(pending) == broken


@pytest.mark.parametrize('build_status', ['failure', 'skipped'])
def test_independent_pages_recover_after_partial_failure_or_no_builds(build_status):
    receipts = {'north': 'north', 'south': None, 'west': 'wrong', 'east': 'unreadable'}
    for files, broken in ((fixture.LIFECYCLE_BASE, False), (fixture.lifecycle_candidate_sources(), True)):
        publish = module(files, 'pipeline.py')['publish_pages']
        pages, failed = publish(receipts, verify_receipt, build_status)
        assert pages == ([] if broken else ['north'])
        if not broken:
            assert failed
            assert publish({'north': 'north'}, verify_receipt, 'skipped') == (['north'], False)
        assert publish(receipts, verify_receipt, build_status, cancelled=True) == ([], False)
        assert publish({'north': 'north'}, verify_receipt, 'success') == (['north'], False)


def test_lifecycle_cli_generates_clean_review_inputs_without_answer_key(tmp_path):
    import json
    import sys
    result = subprocess.run([sys.executable, str(Path(fixture.__file__)), '--scenario', 'lifecycle',
                             '--output', str(tmp_path / 'source')], capture_output=True, text=True, check=True)
    manifest = json.loads(result.stdout)
    source = Path(manifest['source'])
    assert sorted(p.name for p in source.iterdir() if p.name != '.git') == sorted(fixture.LIFECYCLE_BASE)
    assert subprocess.check_output(['git', '-C', str(source), 'status', '--porcelain'], text=True) == ''
    for name in fixture.LIFECYCLE_BASE:
        assert (source / name).read_text() == fixture.lifecycle_candidate_sources()[name]
