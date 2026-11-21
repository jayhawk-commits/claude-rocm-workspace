"""Prevent a successful process or LGTM from hiding missing review coverage."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from peanut_review import review_coverage as coverage


@pytest.fixture
def review(tmp_path):
    current = SimpleNamespace(current_head='a' * 40, base_ref='b' * 40,
                              agents=[SimpleNamespace(name=n) for n in ('one', 'two', 'Curator')])
    contract = tmp_path / coverage.CONTRACT
    contract.parent.mkdir(parents=True)
    contract.write_text(json.dumps({'version': 1, 'has_related': False}))
    (tmp_path / 'coverage').mkdir()
    for agent in current.agents:
        record = {'head': current.current_head, 'base': current.base_ref, 'verdict': 'approve',
                  'areas': [{'id': name, 'status': 'checked', 'material': True,
                             'evidence': 'Inspected the actual caller and consumer at the pinned revision.'}
                            for name in coverage.AREAS]}
        (tmp_path / 'coverage' / f'{agent.name}.json').write_text(json.dumps(record))
    return tmp_path, current


def change(review, edit, name='one'):
    root, _ = review
    path = root / 'coverage' / f'{name}.json'
    record = json.loads(path.read_text())
    edit(record)
    path.write_text(json.dumps(record))


def test_complete_records_allow_bounded_approval(review):
    assert coverage.assess(*review) == {'recommendation': 'approve', 'gaps': []}


@pytest.mark.parametrize('edit', [
    lambda r: r.update(head='stale'),
    lambda r: r.update(base='different'),
    lambda r: r.update(areas=[]),
    lambda r: r['areas'][0].update(evidence=''),
    lambda r: r['areas'][0].update(material='true'),
    lambda r: r['areas'][0].update(status='probably'),
    lambda r: r['areas'].__setitem__(1, r['areas'][0]),
])
def test_stale_or_invalid_record_cannot_approve(review, edit):
    change(review, edit)
    assert coverage.assess(*review)['recommendation'] == 'wait_for_evidence'


def test_missing_record_cannot_be_replaced_by_curator_lgtm(review):
    (review[0] / 'coverage/one.json').unlink()
    assert coverage.assess(*review)['recommendation'] == 'wait_for_evidence'


def test_new_session_missing_contract_does_not_look_like_legacy(review):
    root, current = review
    (root / coverage.CONTRACT).unlink()
    (root / '.codex/peanut-review/workspace-snapshot.json').write_text(json.dumps({'coverage_contract': 1}))
    assert coverage.assess(root, current)['recommendation'] == 'wait_for_evidence'


def test_curator_approval_does_not_erase_a_reviewer_evidence_request(review):
    change(review, lambda r: r.update(verdict='wait_for_evidence'))
    assert coverage.assess(*review)['recommendation'] == 'wait_for_evidence'


def test_unverified_material_work_downgrades_approval(review):
    change(review, lambda r: r['areas'][0].update(status='unverified', evidence='Consumer revision unavailable'))
    result = coverage.assess(*review)
    assert result['recommendation'] == 'wait_for_evidence'
    assert 'materially unverified' in result['gaps'][0]


def test_unneeded_or_nonmaterial_live_check_does_not_block(review):
    change(review, lambda r: r['areas'][0].update(status='unverified', material=False,
                                                evidence='Live deployment outside requested offline scope'))
    change(review, lambda r: r['areas'][1].update(status='not_applicable', material=False,
                                                evidence='Pure value conversion has no alternate deployment'))
    assert coverage.assess(*review)['recommendation'] == 'approve'


@pytest.mark.parametrize('state', ['not_applicable', 'unverified'])
def test_declared_related_inputs_must_be_examined(review, state):
    root, current = review
    (root / coverage.CONTRACT).write_text(json.dumps({'version': 1, 'has_related': True}))
    change(review, lambda r: r['areas'][-1].update(status=state, material=False,
                                                evidence='Only tested each branch independently'))
    assert coverage.assess(root, current)['recommendation'] == 'wait_for_evidence'


def test_confirmed_finding_survives_other_coverage_gaps(review):
    change(review, lambda r: r.update(verdict='request_changes'), name='Curator')
    (review[0] / 'coverage/one.json').unlink()
    assert coverage.assess(*review)['recommendation'] == 'request_changes'


def test_legacy_sessions_are_not_retroactively_relabelled(tmp_path):
    assert coverage.assess(tmp_path, SimpleNamespace()) == {'recommendation': None, 'gaps': []}


def temporal_review(review):
    root, current = review
    (root / coverage.CONTRACT).write_text(json.dumps({
        'version': 2, 'has_related': False, 'areas': coverage.AREAS,
        'temporal_cases': coverage.TEMPORAL_CASES}))
    for agent in current.agents:
        def populate(record):
            area = next(a for a in record['areas'] if a['id'] == 'temporal_contracts')
            area['scenarios'] = [dict(id=case, status='checked', material=True,
                sequence=['observe pending operation', 'observe committed result after an error'],
                oracle='Stored identity remains authoritative across the error.',
                evidence='Ran the producer and then the consumer; the same identity was retained.')
                for case in coverage.TEMPORAL_CASES]
        change(review, populate, agent.name)
    return root, current


def edit_temporal(record, edit):
    edit(next(a for a in record['areas'] if a['id'] == 'temporal_contracts'))


def test_v2_requires_transition_evidence_not_just_checked_prose(review):
    root, current = temporal_review(review)
    assert coverage.assess(root, current)['recommendation'] == 'approve'
    change(review, lambda r: edit_temporal(r, lambda a: a.pop('scenarios')))
    result = coverage.assess(root, current)
    assert result['recommendation'] == 'wait_for_evidence'
    assert 'temporal scenarios' in result['gaps'][0]


@pytest.mark.parametrize('edit', [
    lambda a: a.update(scenarios=[]),
    lambda a: a['scenarios'][0].update(sequence=['only one snapshot']),
    lambda a: a['scenarios'][0].update(sequence=['', 'later']),
    lambda a: a['scenarios'][0].update(oracle=''),
    lambda a: a['scenarios'][0].update(evidence=''),
    lambda a: a['scenarios'][0].update(material='true'),
    lambda a: a['scenarios'][0].update(status='maybe'),
    lambda a: a['scenarios'].__setitem__(1, a['scenarios'][0]),
    lambda a: [s.update(status='not_applicable') for s in a['scenarios']],
])
def test_v2_incomplete_or_self_describing_scenario_cannot_approve(review, edit):
    temporal_review(review)
    change(review, lambda r: edit_temporal(r, edit))
    assert coverage.assess(*review)['recommendation'] == 'wait_for_evidence'


def test_v2_material_ambiguity_survives_curator_approval(review):
    temporal_review(review)
    change(review, lambda r: edit_temporal(r, lambda a: a['scenarios'][1].update(
        status='unverified', evidence='Write acknowledgement lost; durable consumer not checked.')))
    result = coverage.assess(*review)
    assert result['recommendation'] == 'wait_for_evidence'
    assert 'ambiguous_effect remains materially unverified' in result['gaps'][0]


def test_v2_static_changes_need_a_reason_not_irrelevant_temporal_tests(review):
    temporal_review(review)
    for agent in review[1].agents:
        change(review, lambda r: edit_temporal(r, lambda a: a.update(
            status='not_applicable', material=False,
            evidence='Only a static display string changes; there is no stateful decision.')), agent.name)
    assert coverage.assess(*review)['recommendation'] == 'approve'


def test_existing_v1_six_area_contract_keeps_its_original_provenance(review):
    root, current = review
    original = {key: value for key, value in coverage.AREAS.items() if key != 'temporal_contracts'}
    (root / coverage.CONTRACT).write_text(json.dumps({'version': 1, 'has_related': False, 'areas': original}))
    for agent in current.agents:
        change(review, lambda r: r.update(areas=[a for a in r['areas'] if a['id'] in original]), agent.name)
    assert coverage.assess(root, current)['recommendation'] == 'approve'


def test_v2_scenario_inventory_is_pinned_for_existing_sessions(review, monkeypatch):
    temporal_review(review)
    monkeypatch.setattr(coverage, 'TEMPORAL_CASES', {**coverage.TEMPORAL_CASES,
        'future_probe': 'A future runtime may ask new sessions for more evidence.'})
    assert coverage.assess(*review)['recommendation'] == 'approve'
