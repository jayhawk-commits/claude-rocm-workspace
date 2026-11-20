#!/usr/bin/env python3
"""Create a fictional, bounded review replay; never calls a model or remote.

The generated repository contains only review inputs. Expected outcomes stay in
the caller's evaluation record. A successful replay checks these examples, not
general review quality.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess


BASE = {
    'history.py': '''"""Keep historical ticket identities readable across payload format updates.

History is permanent. Only resuming active work requires current payload data.
"""


def validate_identity(record):
    if not isinstance(record.get("ticket"), int) or record["ticket"] < 1:
        raise ValueError("invalid ticket identity")


def validate_active(record):
    validate_identity(record)


def ticket_numbers(records):
    for record in records:
        validate_identity(record)
    return [record["ticket"] for record in records]


def allocate(records, payload_digest):
    number = max(ticket_numbers(records), default=0) + 1
    record = {"ticket": number, "payload_digest": payload_digest}
    validate_active(record)
    records.append(record)
    return number


def resume(record):
    validate_active(record)
    return record["ticket"]
''',
    'transfer.py': '''"""Publish one package into its own mutable remote mapping.

Successful publication requires an exact filename/content inventory. Incomplete
packages may be retried with a changed file set; completed packages are immutable.
"""


def verify(files, remote):
    if dict(files) != dict(remote):
        raise ValueError("package inventory does not match")


def publish(files, remote, *, completed=False):
    if completed:
        verify(files, remote)
        return
    remote.clear()
    remote.update(files)
    verify(files, remote)
''',
    'jobs.py': '''"""Dispatch selected jobs. An empty selection is valid and performs no work."""


def validate_jobs(jobs):
    if not isinstance(jobs, list) or any(not isinstance(j, str) or not j for j in jobs):
        raise ValueError("expected a list of nonempty job names")


def run_jobs(jobs, dispatch):
    validate_jobs(jobs)
    return [dispatch(job) for job in jobs]
''',
}


def candidate_sources():
    files = dict(BASE)
    files['history.py'] = files['history.py'].replace(
        'def validate_active(record):\n    validate_identity(record)\n',
        'def validate_active(record):\n    validate_identity(record)\n'
        '    if not record.get("payload_digest"):\n'
        '        raise ValueError("active payload digest is required")\n',
    ).replace('        validate_identity(record)\n', '        validate_active(record)\n')
    files['transfer.py'] = files['transfer.py'].replace(
        '    remote.clear()\n    remote.update(files)\n',
        '    for name, content in files.items():\n'
        '        if remote.get(name) != content:\n'
        '            remote[name] = content\n',
    )
    files['jobs.py'] = files['jobs.py'].replace(
        '    return [dispatch(job) for job in jobs]\n',
        '    if not jobs:\n        return []\n'
        '    return [dispatch(job) for job in jobs]\n',
    )
    return files


def _create(output: Path, base_sources, new_sources):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)

    def git(*args):
        return subprocess.check_output(['git', '-C', str(output), *args], text=True).strip()

    git('init', '-b', 'base')
    git('config', 'user.name', 'Review Fixture')
    git('config', 'user.email', 'fixture@example.invalid')
    git('config', 'core.autocrlf', 'false')
    for name, content in base_sources.items():
        (output / name).write_text(content, encoding='utf-8')
    git('add', '.')
    git('commit', '-m', 'Initial package service')
    base = git('rev-parse', 'HEAD')
    git('checkout', '-b', 'candidate')
    for name, content in new_sources.items():
        (output / name).write_text(content, encoding='utf-8')
    git('add', '.')
    git('commit', '-m', 'Validate service inputs and reuse transfer helpers')
    return {'source': str(output), 'base': base, 'head': git('rev-parse', 'HEAD')}


def create(output: Path):
    return _create(output, BASE, candidate_sources())


INTEGRATION_BASE = {
    'common.py': '''import hashlib
import json


def legacy_id(recipe):
    return hashlib.sha256(json.dumps(recipe, sort_keys=True).encode()).hexdigest()
''',
    'service.py': '''"""Invalid requests must not consume a ticket or change stored history."""


def validate(recipe):
    if set(recipe) != {"components"} or not isinstance(recipe["components"], list):
        raise ValueError("unsupported recipe")


def reserve(recipe, history):
    validate(recipe)
    ticket = len(history) + 1
    history.append(ticket)
    return ticket
''',
    'transfer.py': '''"""Transfers tolerate up to three transient OSError failures before success."""


def run_transfer(send):
    for attempt in range(4):
        try:
            return send()
        except OSError:
            if attempt == 3:
                raise
''',
    'jobs.py': BASE['jobs.py'],
}


def integration_candidate_sources():
    files = dict(INTEGRATION_BASE)
    files['backfill.py'] = '''"""Read published builds from the companion producer.

Both legacy and pinned-tooling records remain valid backfill inputs.
"""
from common import legacy_id


def validate(record, recipe):
    if record["fingerprint"] != legacy_id(recipe):
        raise ValueError("recipe identity does not match")
    return record["build"]
'''
    files['service.py'] = files['service.py'].replace('    validate(recipe)\n', '').replace(
        '    history.append(ticket)\n', '    history.append(ticket)\n    validate(recipe)\n')
    files['transfer.py'] = '''"""Transfers tolerate up to three transient OSError failures before success."""


def retry(send, attempts=1):
    for attempt in range(attempts):
        try:
            return send()
        except OSError:
            if attempt == attempts - 1:
                raise


def run_transfer(send):
    return retry(send)
'''
    files['jobs.py'] = candidate_sources()['jobs.py']
    return files


RELATED_BASE = {'producer.py': '''import hashlib
import json


def fingerprint(recipe, automation=""):
    payload = recipe if not automation else {"recipe": recipe, "automation": automation}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def make(recipe):
    return {"build": "build-7", "format": "legacy", "fingerprint": fingerprint(recipe)}


def validate(record, recipe):
    return record["fingerprint"] == fingerprint(recipe, record.get("automation", ""))
'''}
RELATED_CANDIDATE = {'producer.py': RELATED_BASE['producer.py'].replace(
    'return {"build": "build-7", "format": "legacy", "fingerprint": fingerprint(recipe)}',
    'return {"build": "build-7", "format": "pinned", "automation": "tools-v2", '
    '"fingerprint": fingerprint(recipe, "tools-v2")}')}


def create_integration(output: Path):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    primary = _create(output / 'consumer', INTEGRATION_BASE, integration_candidate_sources())
    related = _create(output / 'producer', RELATED_BASE, RELATED_CANDIDATE)
    return {**primary, 'related_sources': [related]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New repository directory')
    parser.add_argument('--scenario', choices=('history', 'integration'), default='history')
    args = parser.parse_args()
    create_fixture = create_integration if args.scenario == 'integration' else create
    print(json.dumps(create_fixture(args.output), indent=2))


if __name__ == '__main__':
    main()
