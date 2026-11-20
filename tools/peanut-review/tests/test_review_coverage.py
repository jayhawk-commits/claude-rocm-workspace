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
