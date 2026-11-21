"""Distinguishing behaviors and compatible controls for one frozen replay."""
import asyncio
import importlib.util
from pathlib import Path
import subprocess

import pytest

spec = importlib.util.spec_from_file_location(
    'temporal_fixture', Path(__file__).resolve().parents[1] / 'scripts/review_quality_fixture.py')
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


def module(files, name):
    result = {}
    exec(compile(files[name], name, 'exec'), result)
    return result


@pytest.mark.parametrize('broken', [False, True])
def test_two_reads_do_not_let_a_preview_clear_an_unlisted_submission(broken):
    files = fixture.temporal_candidate_sources() if broken else fixture.TEMPORAL_BASE
    policy = module(files, 'observations.py')
    leases = {'blue': {1}}
    rows = [{'id': 2, 'kind': 'unknown', 'status': 'queued'}]
    policy['observe'](leases, 'blue', rows)
    assert not policy['can_submit'](leases, 'blue', rows)
    rows[0].update(kind='preview', status='done')
    policy['observe'](leases, 'blue', rows)
    assert policy['can_submit'](leases, 'blue', rows) is broken
    # Confirmed work legitimately releases the lease; an old listed ticket does not.
    leases = {'blue': {1}}
    policy['observe'](leases, 'blue', [{'id': 1, 'kind': 'work'}])
    assert 'blue' in leases
    policy['observe'](leases, 'blue', [{'id': 3, 'kind': 'work'}])
    assert 'blue' not in leases


@pytest.mark.parametrize('broken', [False, True])
def test_search_reaches_work_after_cap_plus_one_previews(broken):
    files = fixture.temporal_candidate_sources() if broken else fixture.TEMPORAL_BASE
    newest = module(files, 'history.py')['newest']
    entries = [{'kind': 'preview'} for _ in range(4)] + [{'kind': 'work', 'id': 7}]
    assert newest(entries, lambda row: row['kind']) == (None if broken else entries[-1])
    assert newest([], lambda row: row['kind']) is None
    assert newest([{'kind': 'unknown'}], lambda row: row['kind']) == {'kind': 'unknown'}


@pytest.mark.parametrize('broken', [False, True])
def test_pagination_and_classification_share_the_same_stopping_contract(broken):
    files = fixture.temporal_candidate_sources() if broken else fixture.TEMPORAL_BASE
    gather = module(files, 'paging.py')['gather']
    preview = {'lane': 'blue', 'kind': 'preview', 'old': True}
    work = {'lane': 'blue', 'kind': 'work', 'old': True}
    others = [{'lane': 'red', 'kind': 'work', 'old': True}] * 3
    pages = {1: [preview, *others], 2: [work]}
    rows, complete = gather(pages.__getitem__, 'blue', lambda row: row['kind'])
    assert complete
    assert (work in rows) is not broken
    # Bound exhaustion and an empty lane are valid, explicit outcomes.
    assert gather(lambda _: others + others[:1], 'blue', lambda row: row['kind'], max_pages=1) == ([], False)
    assert gather(lambda _: [], 'blue', lambda row: row['kind']) == ([], True)


@pytest.mark.parametrize('broken', [False, True])
def test_failed_acknowledgement_keeps_real_durable_authority(broken):
    files = fixture.temporal_candidate_sources() if broken else fixture.TEMPORAL_BASE
    producer = module(files, 'ledger.py')
    consumer = module(files, 'authority.py')
    ledger = {'head': 4, 'items': {4}}
    def fail():
        raise OSError('acknowledgement lost after persistence')
    with pytest.raises(OSError):
        producer['reserve'](ledger, 5, fail)
    assert producer['resume'](ledger, 5) == 5
    with pytest.raises(ValueError, match='superseded'):
        producer['resume'](ledger, 4)
    result = consumer['classify']({'id': 5, 'write_failed': True}, ledger)
    assert result == ('unused' if broken else 'work')
    assert consumer['classify']({'id': 6, 'absence_confirmed': True}, ledger) == 'unused'
    assert consumer['classify']({'id': 6, 'preview': True}, ledger) == 'preview'


@pytest.mark.parametrize('broken', [False, True])
def test_lease_is_installed_while_submission_is_still_in_flight(broken):
    files = fixture.temporal_candidate_sources() if broken else fixture.TEMPORAL_BASE
    submit = module(files, 'submit.py')['submit']
    async def scenario():
        leases, sent = {}, []
        started, release = asyncio.Event(), asyncio.Event()
        async def slow():
            sent.append('first')
            started.set()
            await release.wait()
        async def second():
            sent.append('second')
        first = asyncio.create_task(submit(leases, 'blue', slow, []))
        await started.wait()
        accepted = await submit(leases, 'blue', second, [])
        release.set()
        assert await first
        assert accepted is broken
        assert sent == (['first', 'second'] if broken else ['first'])
    asyncio.run(scenario())


def test_attempt_cache_is_a_compatible_control_not_a_seeded_defect():
    for files in (fixture.TEMPORAL_BASE, fixture.temporal_candidate_sources()):
        details = module(files, 'details.py')['details']
        cache, calls = {}, []
        def fetch(execution, attempt):
            calls.append(attempt)
            return [{'attempt': attempt, 'done': True}]
        assert details(cache, 1, 1, fetch) == details(cache, 1, 1, fetch)
        assert calls == [1]
        assert details(cache, 1, 2, fetch)[0]['attempt'] == 2
        assert calls == [1, 2]
        assert details(cache, 2, 1, lambda *_: []) == []
        assert (2, 1) not in cache


def test_temporal_generator_keeps_all_cases_in_one_clean_head(tmp_path):
    result = fixture.create_temporal(tmp_path / 'source')
    source = result['source']
    assert not subprocess.check_output(['git', '-C', source, 'status', '--porcelain'], text=True).strip()
    assert set(Path(source).iterdir()) >= {Path(source) / name for name in fixture.TEMPORAL_BASE}
    diff = subprocess.check_output(['git', '-C', source, 'diff', '--name-only', result['base'], result['head']], text=True)
    assert set(diff.splitlines()) == {'observations.py', 'history.py', 'paging.py', 'authority.py', 'submit.py'}
