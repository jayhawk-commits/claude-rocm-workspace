#!/usr/bin/env python3
"""Verify the installed Codex write/network boundary without a model call."""
import argparse
import json
from pathlib import Path
import queue
import shutil
import subprocess
import tempfile
import threading
import time


def run_legacy_command(codex, command, task, session, root):
    """Run a model-free command through the same legacy sandbox policy as exec.

    `codex sandbox --permission-profile` selects the newer policy system and
    ignores legacy sandbox_workspace_write keys. The local app-server's
    standalone command/exec API accepts the legacy SandboxPolicy directly.
    No thread, turn, model request, or authentication operation is created.
    """
    policy = {
        'type': 'workspaceWrite',
        'writableRoots': [str(session)],
        'excludeSlashTmp': True,
        'excludeTmpdirEnvVar': True,
        'networkAccess': False,
    }
    messages = queue.Queue()
    with (root / 'app-server.stderr.log').open('w') as errors:
        process = subprocess.Popen(
            [codex, 'app-server', '--stdio', '-c', 'approval_policy="never"'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors,
            text=True, cwd=task,
        )

        def receive():
            for line in process.stdout:
                messages.put(line)
            messages.put(None)

        threading.Thread(target=receive, daemon=True).start()

        def send(value):
            process.stdin.write(json.dumps(value) + '\n')
            process.stdin.flush()

        def response(request_id):
            deadline = time.monotonic() + 45
            while True:
                line = messages.get(timeout=max(0, deadline - time.monotonic()))
                if line is None:
                    raise RuntimeError('local app-server exited before returning the probe result')
                value = json.loads(line)
                if value.get('id') != request_id:
                    continue
                if 'error' in value:
                    raise RuntimeError(str(value['error']))
                return value['result']

        try:
            send({'id': 1, 'method': 'initialize', 'params': {
                'clientInfo': {'name': 'peanut-sandbox-probe', 'version': '1'},
                'capabilities': {'experimentalApi': True},
            }})
            response(1)
            send({'method': 'initialized'})
            send({'id': 2, 'method': 'command/exec', 'params': {
                'command': command, 'cwd': str(task), 'sandboxPolicy': policy,
                'timeoutMs': 30000, 'env': {'TMPDIR': str(task / 'tmp')},
            }})
            return response(2), policy
        finally:
            process.stdin.close()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', help='new directory in which to retain probe evidence')
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(tempfile.mkdtemp(prefix='peanut-sandbox-'))
    if args.root:
        root.mkdir(parents=True, exist_ok=False)
    source = root / 'source'
    session = root / 'session'
    task = session / 'logs/probe'
    policy = session / '.codex/peanut-review'
    source.mkdir()
    task.mkdir(parents=True)
    (task / 'tmp').mkdir()
    policy.mkdir(parents=True)
    (source / 'marker').write_text('unchanged')
    (policy / 'safe-local.json').write_text('{"safeLocal":true}')
    script = task / 'probe.py'
    script.write_text('''import json, pathlib, socket, sys
source, session, policy = map(pathlib.Path, sys.argv[1:])
checks = {}
checks['source_read'] = (source / 'marker').read_text() == 'unchanged'
try:
    (session / 'allowed').write_text('allowed')
    checks['session_write'] = True
except OSError:
    checks['session_write'] = False
for name, target in [('source_write_denied', source / 'marker'),
                     ('policy_write_denied', policy / 'safe-local.json'),
                     ('outside_write_denied', source.parent / 'outside')]:
    try:
        with target.open('a') as output:
            output.write('unexpected')
        checks[name] = False
    except OSError:
        checks[name] = True
try:
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    checks['network_denied'] = False
    sock.close()
except OSError:
    checks['network_denied'] = True
print(json.dumps(checks))
sys.exit(0 if all(checks.values()) else 1)
''')
    codex = shutil.which('codex')
    if not codex:
        raise RuntimeError('codex is not on PATH')
    command = ['python3', str(script), str(source), str(session), str(policy)]
    result, sandbox_policy = run_legacy_command(codex, command, task, session, root)
    report = {'passed': result['exitCode'] == 0, 'exitCode': result['exitCode'],
              'mechanism': 'local app-server command/exec with explicit legacy SandboxPolicy',
              'sandboxPolicy': sandbox_policy,
              'codexVersion': subprocess.check_output([codex, '--version'], text=True).strip(),
              'stdout': result['stdout'].strip(), 'stderr': result['stderr'].strip(),
              'sourceUnchanged': (source / 'marker').read_text() == 'unchanged',
              'policyUnchanged': (policy / 'safe-local.json').read_text() == '{"safeLocal":true}'}
    report['passed'] = report['passed'] and report['sourceUnchanged'] and report['policyUnchanged']
    (root / 'sandbox-result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
