"""Opt-in bounds for this workspace's local Codex review profile.

This limits process launches and elapsed time, not provider tokens or spend.
The session owner enables it with .codex/peanut-review/safe-local.json containing
{"safeLocal": true}. Codex treats .codex as protected within a writable root;
verify that boundary with the installed sandbox. Preserve the review ledger.
"""
from __future__ import annotations

from contextlib import contextmanager
import fcntl
import json
import math
from pathlib import Path
import time

from . import curator, runtime, session as sessions


CONFIG_NAME = ".codex/peanut-review/safe-local.json"
STATE_NAME = ".codex/peanut-review/safe-local-state.json"
DEFAULT_LIMITS = {
    "maxSeconds": 1800,
    "maxConcurrent": 3,
    "maxLaunches": 9,
    "maxRounds": 2,
    "maxRetriesPerAgent": 1,
}


def policy_directory(session_dir: str | Path) -> Path:
    return Path(session_dir) / ".codex" / "peanut-review"


def _read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text())
    except (OSError, ValueError) as error:
        raise ValueError(f"cannot read local review policy {path.name}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return value


def enabled(session_dir: str | Path) -> bool:
    path = Path(session_dir) / CONFIG_NAME
    if not path.exists():
        return False
    config = _read_json(path)
    if config.get("safeLocal") is not True:
        raise ValueError("safe-local.json must explicitly set safeLocal to true")
    return True


def _limits(session_dir: Path) -> dict:
    config = _read_json(session_dir / CONFIG_NAME)
    overrides = config.get("limits", {})
    if not isinstance(overrides, dict) or set(overrides) - DEFAULT_LIMITS.keys():
        raise ValueError("unknown or invalid safeLocal limits")
    result = {**DEFAULT_LIMITS, **overrides}
    for name, ceiling in DEFAULT_LIMITS.items():
        minimum = 0 if name == "maxRetriesPerAgent" else 1
        value = result[name]
        if type(value) is not int or not minimum <= value <= ceiling:
            raise ValueError(f"safeLocal {name} must be an integer from {minimum} to {ceiling}")
    return result


def _lineup(session) -> list[dict]:
    agents = session.agents
    if not 1 <= len(curator.reviewers(agents)) <= 2 or len(curator.curators(agents)) > 1:
        raise ValueError("safeLocal requires one or two reviewers and at most one curator")
    names = [agent.name for agent in agents]
    if len(names) != len(set(names)):
        raise ValueError("safeLocal agent names must be unique")
    result = []
    for agent in agents:
        if agent.role not in {"reviewer", "curator"}:
            raise ValueError("safeLocal supports only reviewer and curator roles")
        if agent.runner != "codex" or agent.ssh_target:
            raise ValueError("safeLocal permits only local Codex agents")
        if not agent.model.strip() or not agent.reasoning_effort.strip():
            raise ValueError("safeLocal requires an explicit model and reasoningEffort for every agent")
        result.append({key: getattr(agent, key) for key in
                       ("name", "role", "runner", "model", "reasoning_effort", "persona")})
    return result


def remaining_timeout(session_dir: str | Path, timeout: int) -> int:
    """Recheck the deadline immediately before starting each supervisor."""
    state_path = Path(session_dir) / STATE_NAME
    if not enabled(session_dir) or not state_path.exists():
        return timeout
    remaining = math.floor(_read_json(state_path)["deadline"] - time.time())
    if remaining < 1:
        raise ValueError("safeLocal review deadline exhausted")
    return min(timeout, remaining)


@contextmanager
def launch_budget(session_dir, session, agents, *, dry_run=False):
    """Validate and reserve attempts under one lock through subprocess startup.

    Yield the effective per-process timeout. Call before clearing old runtime
    state, and keep this context open through all supervisor PID updates.
    Failed spawn attempts deliberately retain their reservation. An ordinary
    second pass and one failed-run retry per agent are the largest allowance.
    Upstream sessions without the opt-in file retain their existing behavior.
    """
    directory = Path(session_dir)
    if not enabled(directory):
        yield session.timeout
        return

    with (policy_directory(directory) / "safe-local.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        # Reload after acquiring the lock: a concurrent launch may have updated PIDs.
        session = sessions.load_session(directory)
        limits = _limits(directory)
        lineup = _lineup(session)
        selected = {agent.name for agent in agents}
        known = {agent.name for agent in session.agents}
        if not selected or not selected <= known:
            raise ValueError("safeLocal launch must select configured agents")
        if type(session.timeout) is not int or session.timeout <= 0:
            raise ValueError("safeLocal agent timeout must be a positive integer")
        repo = sessions.repo_path(session)
        if sessions.resolve_git_ref(repo, "HEAD") != session.current_head:
            raise ValueError("safeLocal workspace HEAD does not match pinned review head; migrate explicitly")
        if sessions._run_git(repo, "status", "--porcelain", "--untracked-files=all",
                             "--ignore-submodules=none").strip():
            raise ValueError("safeLocal requires a clean source checkout")

        snapshots = {agent.name: runtime.inspect_agent_runtime(directory, agent)
                     for agent in session.agents}
        live = {name for name, snapshot in snapshots.items()
                if snapshot["reviewer_live"] or snapshot["supervisor_live"]
                or snapshot["process_state"] in {runtime.PROCESS_RUNNING, runtime.PROCESS_LAUNCHING}}
        if live & selected:
            raise ValueError("safeLocal cannot relaunch live agent(s): " + ", ".join(sorted(live & selected)))
        if len(live | selected) > limits["maxConcurrent"]:
            raise ValueError("safeLocal concurrent-agent limit exceeded")

        state_path = directory / STATE_NAME
        now = time.time()
        state = _read_json(state_path) if state_path.exists() else {
            "version": 1, "startedAt": now, "deadline": now + limits["maxSeconds"],
            "lineup": lineup, "repository": str(Path(repo).resolve()), "launches": [],
        }
        if state.get("version") != 1 or not isinstance(state.get("launches"), list):
            raise ValueError("invalid safeLocal launch ledger")
        if state.get("lineup") != lineup or state.get("repository") != str(Path(repo).resolve()):
            raise ValueError("safeLocal lineup/repository changed; preserve the original review ledger")
        # Tightening a configured duration never extends an existing deadline.
        deadline = min(state["deadline"], state["startedAt"] + limits["maxSeconds"])
        remaining = math.floor(deadline - now)
        if remaining < 1:
            raise ValueError("safeLocal review deadline exhausted")
        previous = state["launches"]
        if len(previous) + len(selected) > limits["maxLaunches"]:
            raise ValueError("safeLocal total launch limit exhausted")
        # Starting reviewers invalidates/clears the previous curator runtime.
        # Preserve observed outcomes before that reset so a later ordinary
        # curation pass does not consume its failed-run retry allowance.
        for name, snapshot in snapshots.items():
            history = [item for item in previous if item["agent"] == name]
            if history and snapshot["has_final_meta"] and name not in live:
                history[-1]["successful"] = bool(snapshot["signal"] and snapshot["exit_code"] == 0)
        reservations = []
        for name in sorted(selected):
            history = [item for item in previous if item["agent"] == name]
            retry = bool(history) and not history[-1].get("successful", False)
            kind = "retry" if retry else "round"
            allowance = limits["maxRetriesPerAgent"] if retry else limits["maxRounds"]
            if sum(item["kind"] == kind for item in history) >= allowance:
                raise ValueError(f"safeLocal {kind} limit exhausted for {name}")
            reservations.append({"agent": name, "kind": kind, "at": now,
                                 "head": session.current_head})
        if not dry_run:
            state["launches"] = previous + reservations
            state["deadline"] = deadline
            temporary = state_path.with_suffix(".tmp")
            temporary.write_text(json.dumps(state, indent=2) + "\n")
            temporary.replace(state_path)
        yield min(session.timeout, remaining)
