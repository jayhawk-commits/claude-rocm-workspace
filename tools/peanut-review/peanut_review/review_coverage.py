"""Evidence accounting for new workspace sessions; completion is not approval."""
from __future__ import annotations

import json
from pathlib import Path

from . import session


CONTRACT = '.codex/peanut-review/coverage-contract.json'
AREAS = {
    'producer_consumer': 'Trace produced identities, schemas, paths and capabilities into actual consumers.',
    'entrypoints': 'Inspect alternate and deployed entrypoints, including older writers during a cutover.',
    'effects_order': 'Check validation before irreversible allocation, publication or deletion.',
    'moved_behavior': 'Compare retries, authentication, permissions, timeouts and lock duration before/after moving work.',
    'shared_callers': 'Trace shared helper changes through all callers, including unrelated publication modes.',
    'related_integration': 'Compare declared related revisions together, including checkout contents and persisted records.',
}


def configure(directory: Path, has_related: bool) -> None:
    directory = Path(directory)
    review = session.load_session(directory)
    contract = {'version': 1, 'head': review.current_head, 'base': review.base_ref,
                'has_related': has_related, 'areas': AREAS}
    path = directory / CONTRACT
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(contract, indent=2) + '\n')
    (directory / 'coverage').mkdir()
    appendix = (
        '\n\n# Required coverage record before completion\n'
        'Read the coverage contract at ' + str(path) + '. Before signaling round-done, '
        'write `${SESSION}/coverage/${AGENT}.json` with this structure:\n'
        '```json\n{"head":"' + review.current_head + '","base":"' + review.base_ref
        + '","verdict":"approve|request_changes|wait_for_evidence","areas":['
        '{"id":"producer_consumer","status":"checked|not_applicable|unverified",'
        '"material":true,"evidence":"Specific caller/revision, probe and result; or why inapplicable/unverified."}]}'
        '\n```\n'
        'Include every area ID in the contract exactly once. A checked area needs '
        'concrete source/probe evidence, not only passing test counts. Mark an area '
        'not_applicable with a reason when outside this change; do not invent findings '
        'to fill the record. Mark unverified material contracts honestly. When related '
        'sources are supplied, related_integration must be checked or unverified, '
        'and report compatibility or incompatibility of those exact revisions. '
        'A detected incompatibility can be checked evidence supporting request_changes. '
        'Use available source to compare policy and caller contracts; lack of a live '
        'runner is not a substitute for that comparison. Separate a specific material '
        'unknown from live deployment outside the requested scope. '
        'Only claim approve within the stated review scope. Missing, stale or materially '
        'unverified coverage prevents approval even if processes exit successfully. '
        'The curator must read reviewer coverage records, record its own decision and '
        'evidence, and preserve material gaps; do not turn absent coverage into LGTM. '
        'Keep findings in the normal comment store. These records account for coverage; '
        'they do not prove that a claimed check was correct.\n'
    )
    for name in ('agent-prompt.md', 'curator-prompt.md'):
        target = directory / 'templates' / name
        target.write_text(target.read_text() + appendix)


def assess(directory: Path, current) -> dict:
    """Return a conservative recommendation without relabeling process success."""
    directory = Path(directory)
    if not (directory / CONTRACT).exists():
        snapshot = directory / '.codex/peanut-review/workspace-snapshot.json'
        if snapshot.exists() and json.loads(snapshot.read_text()).get('coverage_contract'):
            return {'recommendation': 'wait_for_evidence', 'gaps': ['Required coverage contract is missing']}
        return {'recommendation': None, 'gaps': []}  # Earlier sessions keep their provenance.
    contract = json.loads((directory / CONTRACT).read_text())
    gaps = []
    verdicts = {}
    for agent in current.agents:
        path = directory / 'coverage' / f'{agent.name}.json'
        try:
            if path.stat().st_size > 65536:
                raise ValueError('record exceeds 64 KiB')
            record = json.loads(path.read_text())
            if not isinstance(record, dict):
                raise ValueError('record must be an object')
            if record.get('head') != current.current_head or record.get('base') != current.base_ref:
                raise ValueError('record is for a different source snapshot')
            verdict = record.get('verdict')
            if verdict not in {'approve', 'request_changes', 'wait_for_evidence'}:
                raise ValueError('invalid verdict')
            areas = record.get('areas')
            if not isinstance(areas, list) or any(not isinstance(a, dict) for a in areas):
                raise ValueError('areas must be a list of objects')
            ids = [a.get('id') for a in areas]
            if len(ids) != len(AREAS) or any(not isinstance(i, str) for i in ids) or set(ids) != set(AREAS):
                raise ValueError('each required area must occur exactly once')
            for area in areas:
                state = area.get('status')
                if state not in {'checked', 'not_applicable', 'unverified'}:
                    raise ValueError('invalid area status')
                if not isinstance(area.get('material'), bool):
                    raise ValueError('material must be boolean')
                if not isinstance(area.get('evidence'), str) or not area['evidence'].strip():
                    raise ValueError('area evidence/reason is required')
                required_related = contract['has_related'] and area['id'] == 'related_integration'
                if required_related and state != 'checked':
                    gaps.append(f'{agent.name}: related integration was not checked')
                elif state == 'unverified' and area['material']:
                    gaps.append(f"{agent.name}: {area['id']} remains materially unverified: {area['evidence']}")
            verdicts[agent.name] = verdict
        except (OSError, ValueError, TypeError) as error:
            gaps.append(f'{agent.name}: missing or invalid coverage record ({error})')
    curator_verdict = verdicts.get('Curator')
    for name, verdict in verdicts.items():
        if name != 'Curator' and verdict == 'wait_for_evidence':
            gaps.append(f'{name}: reviewer still requests evidence')
    if curator_verdict == 'request_changes':
        recommendation = 'request_changes'
    elif gaps or curator_verdict != 'approve':
        recommendation = 'wait_for_evidence'
    else:
        recommendation = 'approve'
    return {'recommendation': recommendation, 'gaps': gaps}
