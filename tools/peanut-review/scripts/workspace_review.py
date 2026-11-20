#!/usr/bin/env python3
"""Bounded, local-only workspace profile for Peanut Review (Linux/WSL)."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone

TOOL_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = TOOL_ROOT.parents[1]
sys.path.insert(0, str(TOOL_ROOT))
from peanut_review import agent_control, curator, launch, local_policy, review_coverage, runtime, session, store

PERSONAS = WORKSPACE_ROOT / 'skills/review-panel/references/personas'
SESSION_ROOT = WORKSPACE_ROOT.parent / '.cache/peanut-review/sessions'
RUNNING = {runtime.PROCESS_RUNNING, runtime.PROCESS_LAUNCHING}
MAX_RELATED_SOURCES = 4


def write_json(path: Path, value: dict) -> None:
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def git(source: Path, *arguments: str) -> str:
    return session._run_git(str(source), *arguments)


def disjoint(source: Path, directory: Path) -> None:
    if source == directory or source in directory.parents or directory in source.parents:
        raise ValueError('source and session directories must not overlap')


def clean_source(source: Path) -> None:
    if Path(git(source, 'rev-parse', '--show-toplevel')).resolve() != source:
        raise ValueError('--source must be the repository root')
    if git(source, 'status', '--porcelain', '--untracked-files=all', '--ignore-submodules=none'):
        raise ValueError('review requires a clean source checkout; preserve dirty work separately')


def related_snapshots(source: Path, directory: Path, paths: list[str]) -> list[dict]:
    if len(paths) > MAX_RELATED_SOURCES:
        raise ValueError(f'at most {MAX_RELATED_SOURCES} related sources are supported')
    roots = [source]
    snapshots = []
    for value in paths:
        related = Path(value).resolve()
        disjoint(related, directory)
        if any(related == root or related in root.parents or root in related.parents for root in roots):
            raise ValueError('related sources must be distinct, non-overlapping repository roots')
        clean_source(related)
        snapshots.append({'path': str(related), 'head': session.resolve_git_ref(str(related)), 'clean': True})
        roots.append(related)
    return snapshots


def snapshot_current(directory: Path) -> None:
    current = session.load_session(directory)
    source = Path(session.repo_path(current)).resolve()
    disjoint(source, directory.resolve())
    clean_source(source)
    if session.resolve_git_ref(str(source)) != current.current_head:
        raise ValueError('review is stale: source HEAD changed; initialize a new snapshot')
    snapshot = json.loads((local_policy.policy_directory(directory) / 'workspace-snapshot.json').read_text())
    if (current.current_head != snapshot['head'] or current.topic_ref != snapshot['head']
            or current.base_ref != snapshot['base']):
        raise ValueError('review is stale: session snapshot differs from initialized source; create a new session')
    if session.resolve_git_ref(str(source), snapshot['baseInput']) != snapshot['base']:
        raise ValueError('review is stale: base ref changed; initialize a new snapshot')
    for item in snapshot.get('relatedSources', []):
        related = Path(item['path']).resolve()
        if str(related) != item['path']:
            raise ValueError('review is stale: related source path changed; initialize a new snapshot')
        disjoint(related, directory.resolve())
        try:
            clean_source(related)
            head = session.resolve_git_ref(str(related))
        except (ValueError, RuntimeError, OSError) as error:
            raise ValueError(f'review is stale: related source changed or unavailable: {related}: {error}') from error
        if head != item['head']:
            raise ValueError(f'review is stale: related source HEAD changed: {related}; initialize a new snapshot')


def initialize(args) -> Path:
    source = Path(args.source).resolve()
    directory = (Path(args.session).resolve() if args.session else
                 Path(args.session_root).resolve() / (
                     datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-') + uuid.uuid4().hex[:8]))
    disjoint(source, directory)
    clean_source(source)
    if directory.exists():
        raise ValueError('session path already exists; choose a new path or resume with run')
    related = related_snapshots(source, directory, getattr(args, 'related_source', None) or [])
    base = session.resolve_git_ref(str(source), args.base)
    head = session.resolve_git_ref(str(source))
    merge_base = git(source, 'merge-base', base, head)
    if not git(source, 'diff', '--name-only', f'{merge_base}..{head}'):
        raise ValueError('snapshot has no changes to review')
    roles = args.persona or ['release-contracts', 'test-evidence']
    if len(roles) != 2 or len(set(roles)) != 2:
        raise ValueError('select exactly two distinct --persona roles')
    for role in roles:
        if role not in {p.stem for p in PERSONAS.glob('*.md')}:
            raise ValueError(f'unknown persona: {role}')
    if not args.model.strip() or not args.effort.strip():
        raise ValueError('explicit nonempty --model and --effort are required')
    if not 1 <= args.timeout <= args.max_seconds <= 1800:
        raise ValueError('require 1 <= timeout <= max-seconds <= 1800')
    agents = [dict(name=role, model=args.model, reasoningEffort=args.effort,
                   runner='codex', persona=role + '.md') for role in roles]
    agents.append(dict(name='Curator', role='curator', model=args.model,
                       reasoningEffort=args.effort, runner='codex'))
    session.create_session(workspace=str(source), base_ref=base, topic_ref=head,
                           agents=agents, personas_dir=str(PERSONAS), timeout=args.timeout,
                           session_dir=str(directory), session_id=directory.name,
                           include_curator=True, retain_git=False)
    # Enable bounds before this entrypoint can launch anything.
    local_policy.policy_directory(directory).mkdir(parents=True, exist_ok=True)
    write_json(directory / local_policy.CONFIG_NAME, {
        'safeLocal': True, 'limits': {**local_policy.DEFAULT_LIMITS, 'maxSeconds': args.max_seconds}})
    write_json(local_policy.policy_directory(directory) / 'workspace-snapshot.json', {
        'baseInput': args.base, 'base': base, 'mergeBase': merge_base, 'head': head,
        'personas': roles, 'model': args.model, 'reasoningEffort': args.effort,
        'relatedSources': related, 'coverage_contract': 1})
    appendix = ('\n\n# Workspace review contract\n'
                'Use the following local review guidance for evidence, severity, and final comment style. '
                'Keep public findings grounded in public source evidence. Never publish remotely. '
                'Keep source read-only; record findings and verification limits in this session.\n'
                + '\n'.join(f'- Read {shlex.quote(str(WORKSPACE_ROOT / p))}' for p in (
                    'reviews/REVIEW_GUIDELINES.md',
                    'skills/review-panel/references/worker-contract.md')) + '\n'
                'For changed contracts or broad mechanical edits, read the relevant probes in '
                + shlex.quote(str(WORKSPACE_ROOT / 'skills/review-panel/references/regression-probes.md'))
                + '. Apply only reachable scenarios; record distinguishing evidence and '
                'compatible controls, not a checklist of speculative findings.\n')
    if related:
        manifest = local_policy.policy_directory(directory) / 'workspace-snapshot.json'
        appendix += ('\n# Related source inputs\n'
                     'Read the pinned primary and related repository inputs in '
                     + shlex.quote(str(manifest)) + '. These are local, read-only inputs, '
                     'not findings or proof that the changes work together. Inspect the related '
                     'source at its recorded HEAD where it produces or consumes an interface changed '
                     'by this review. Check combined compatibility as well as each change alone; '
                     'do not assume a textually clean merge establishes semantic compatibility. '
                     'Do not edit any source or Git refs, fetch, publish, or expand to unrelated repositories. '
                     'Record which interactions were exercised and any remaining evidence gaps.\n')
    templates = directory / 'templates'
    templates.mkdir()
    for name in ('agent-prompt.md', 'curator-prompt.md'):
        original = TOOL_ROOT / 'peanut_review/templates' / name
        (templates / name).write_text(original.read_text() + appendix)
    review_coverage.configure(directory, has_related=bool(related))
    snapshot_current(directory)
    return directory


def completed(snapshot: dict) -> bool:
    # A signal alone is insufficient: a worker can signal and then hang or fail.
    return (snapshot['signal'] and snapshot['process_state'] == runtime.PROCESS_EXITED
            and snapshot['exit_code'] == 0 and not snapshot['reviewer_live']
            and not snapshot['supervisor_live'])


def wait_completed(directory: Path, names: list[str], deadline: float) -> None:
    while True:
        current = {a.name: a for a in session.load_session(directory).agents}
        remaining = []
        for name in names:
            state = runtime.inspect_agent_runtime(directory, current[name])
            if completed(state):
                continue
            if state['process_state'] not in RUNNING and not state['supervisor_live']:
                raise RuntimeError(f'{name} did not complete successfully ({state["process_state"]})')
            remaining.append(name)
        if not remaining:
            return
        if time.time() >= deadline:
            raise RuntimeError('review deadline reached with unfinished agents: ' + ', '.join(remaining))
        time.sleep(min(1.0, max(0.0, deadline - time.time())))


def deadline_for(directory: Path) -> float:
    state = json.loads((directory / local_policy.STATE_NAME).read_text())
    return state['deadline']


@contextmanager
def controller_lock(directory: Path):
    with (directory / 'workspace-run.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError('a workspace run controller is already active for this session') from error
        yield


def pending_agents(directory: Path, agents, *, retry_failed: bool) -> list[str]:
    selected = []
    for agent in agents:
        state = runtime.inspect_agent_runtime(directory, agent)
        if completed(state) or state['process_state'] in RUNNING or state['supervisor_live']:
            continue
        if state['process_state'] != runtime.PROCESS_PENDING and not retry_failed:
            raise ValueError(f'{agent.name} failed or was incomplete; inspect logs before --retry-failed')
        selected.append(agent.name)
    return selected


def run_review(args) -> Path | None:
    directory = Path(args.session).resolve()
    if not local_policy.enabled(directory):
        raise ValueError('this entrypoint requires an initialized safe-local session')
    with controller_lock(directory):
        snapshot_current(directory)
        current = session.load_session(directory)
        reviewers = curator.reviewers(current.agents)
        coordinator = curator.ensure_curator_agent(current.agents)
        selected = pending_agents(directory, reviewers, retry_failed=args.retry_failed)
        if args.dry_run:
            if selected:
                launch.rerun_agents(directory, template_path=directory / 'templates/agent-prompt.md',
                                     agent_names=selected, dry_run=True)
            launch.launch_curator(directory, template_path=directory / 'templates/curator-prompt.md',
                                  dry_run=True)
            print(json.dumps({'dryRun': True, 'reviewers': selected,
                              'curator': coordinator.name, 'model': coordinator.model,
                              'reasoningEffort': coordinator.reasoning_effort,
                              'limits': local_policy._limits(directory)}, indent=2))
            return None
        try:
            if selected:
                launch.rerun_agents(directory, template_path=directory / 'templates/agent-prompt.md',
                                     agent_names=selected)
            wait_completed(directory, [a.name for a in reviewers], deadline_for(directory))
            # Curation always follows a fresh reviewer attempt, even if a prior curator completed.
            current = session.load_session(directory)
            coordinator = curator.ensure_curator_agent(current.agents)
            if selected or pending_agents(directory, [coordinator], retry_failed=args.retry_failed):
                launch.launch_curator(directory, template_path=directory / 'templates/curator-prompt.md')
            wait_completed(directory, [coordinator.name], deadline_for(directory))
            snapshot_current(directory)
            assessment = review_coverage.assess(directory, current)
            report = export_result(directory, assessment=assessment)
            write_json(directory / 'workspace-result.json', {'status': 'complete', 'report': str(report),
                       'head': current.current_head, 'recommendation': assessment['recommendation'],
                       'materialGaps': assessment['gaps'], 'completedAt': datetime.now(timezone.utc).isoformat()})
            return report
        except (Exception, KeyboardInterrupt):
            agent_control.kill_agents(directory)
            write_json(directory / 'workspace-result.json', {'status': 'incomplete'})
            raise


def export_result(directory: Path, assessment: dict | None = None) -> Path:
    current = session.load_session(directory)
    assessment = assessment if assessment is not None else review_coverage.assess(directory, current)
    comments = [c for c in store.read_all_comments(directory) if not c.deleted]
    lines = ['# Curated local review', '', f'Head: `{current.current_head}`', '']
    if assessment['recommendation'] is not None:
        lines.extend([f'Recommendation: **{assessment["recommendation"]}**', ''])
    lines.extend(['Reviewers and curator completed. Human review is required before publication.', ''])
    if assessment['gaps']:
        lines.extend(['## Material evidence gaps', ''])
        lines.extend('- ' + str(gap) for gap in assessment['gaps'])
        lines.append('')
    for comment in comments:
        if (assessment['recommendation'] not in {None, 'approve'} and not comment.file
                and (comment.category == 'approve' or
                     comment.body.strip().lower() in {'lgtm', 'lgtm.', 'approved', 'approved.'})):
            continue
        if comment.file:
            lines.extend([f'{comment.file}:{comment.line}' +
                          (f'-{comment.end_line}' if comment.end_line else ''), ''])
        lines.extend(['````markdown', comment.body, '````', ''])
    if not comments:
        lines.extend(['No retained comments. Check verification notes before treating this as approval.', ''])
    lines.extend(['## Verification and curation notes', ''])
    for note in store.read_all_notes(directory):
        lines.extend([f'### {note.author}', '', note.body, ''])
    target = directory / 'result.md'
    target.write_text('\n'.join(lines))
    return target


def doctor() -> int:
    checks = {name: shutil.which(name) for name in ('git', 'bash', 'codex')}
    checks['python'] = sys.executable
    checks['pygments'] = importlib.util.find_spec('pygments') is not None
    authenticated = False
    if checks['codex']:
        result = subprocess.run(['codex', 'login', 'status'], capture_output=True, text=True, timeout=20)
        authenticated = result.returncode == 0
        version = subprocess.run(['codex', '--version'], capture_output=True, text=True, timeout=10)
        checks['codexVersion'] = version.stdout.strip()
    checks['authenticated'] = authenticated
    checks['personas'] = sorted(p.stem for p in PERSONAS.glob('*.md'))
    print(json.dumps(checks, indent=2))
    if not authenticated:
        print('Linux Codex login is required before live review; use the installed codex login --device-auth.',
              file=sys.stderr)
    return 0 if all(checks.values()) else 1


def status(directory: Path) -> None:
    current = session.load_session(directory)
    rows = []
    for agent in current.agents:
        state = runtime.inspect_agent_runtime(directory, agent)
        rows.append({'name': agent.name, 'role': agent.role, 'process': state['process_state'],
                     'signal': state['signal'], 'complete': completed(state)})
    try:
        snapshot_current(directory)
        freshness = 'current'
    except (ValueError, RuntimeError, OSError) as error:
        freshness = str(error)
    overall = ('stale' if freshness != 'current' else
               'complete' if rows and all(row['complete'] for row in rows) else 'incomplete')
    assessment = (review_coverage.assess(directory, current) if overall == 'complete' else
                  {'recommendation': None, 'gaps': []})
    print(json.dumps({'status': overall, 'head': current.current_head, 'snapshot': freshness, 'agents': rows,
                      'recommendation': assessment['recommendation'], 'materialGaps': assessment['gaps'],
                      'report': str(directory / 'result.md') if (directory / 'result.md').exists() else None}, indent=2))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest='command', required=True)
    commands.add_parser('doctor')
    create = commands.add_parser('init', help='create a pinned session without launching workers')
    create.add_argument('--source', required=True)
    create.add_argument('--related-source', action='append', default=[],
                        help='Clean local companion repository snapshot; repeat up to four times')
    create.add_argument('--base', required=True)
    create.add_argument('--model', required=True)
    create.add_argument('--effort', required=True)
    create.add_argument('--persona', action='append')
    create.add_argument('--session')
    create.add_argument('--session-root', default=str(SESSION_ROOT))
    create.add_argument('--timeout', type=int, default=900)
    create.add_argument('--max-seconds', type=int, default=1800)
    run = commands.add_parser('run', help='run or resume reviewers, then curate and export')
    run.add_argument('--session', required=True)
    run.add_argument('--retry-failed', action='store_true')
    run.add_argument('--dry-run', action='store_true')
    for command in ('status', 'cancel'):
        sub = commands.add_parser(command)
        sub.add_argument('--session', required=True)
    return result


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    os.environ['GIT_OPTIONAL_LOCKS'] = '0'
    runtime_root = Path(os.environ.get('PEANUT_REVIEW_RUNTIME',
                         WORKSPACE_ROOT.parent / '.cache/peanut-review/runtime'))
    certificate = runtime_root / 'ca-bundle.pem'
    if certificate.is_file():
        os.environ.setdefault('CODEX_CA_CERTIFICATE', str(certificate))
    try:
        if args.command == 'doctor':
            return doctor()
        if args.command == 'init':
            print(initialize(args))
        elif args.command == 'run':
            report = run_review(args)
            if report:
                print(report)
        elif args.command == 'status':
            status(Path(args.session).resolve())
        elif args.command == 'cancel':
            directory = Path(args.session).resolve()
            results = agent_control.kill_agents(directory)
            print(json.dumps(results, indent=2))
            return int(any(r['status'] == 'error' for r in results))
        return 0
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print('Review interrupted; session is incomplete.', file=sys.stderr)
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
