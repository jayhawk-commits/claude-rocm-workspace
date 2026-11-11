#!/usr/bin/env bash
# Modified for claude-rocm-workspace's local review profile; see UPSTREAM.md.
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: codex-task [OPTIONS] --workspace DIR --session-dir DIR [PROMPT...]

Run a codex agent non-interactively (`codex exec`) to produce a markdown file.
The agent's final message lands in output.md via --output-last-message; the
full event stream is captured in stream.jsonl for debugging.

Options:
  --model MODEL          Explicit Codex model id (required).
  --reasoning-effort EFFORT
                         Explicit model_reasoning_effort for this run (required).
  --fast-mode            Enable Codex fast mode for this run.
  --no-fast-mode         Disable Codex fast mode for this run.
                         Fast mode defaults to disabled.
  --workspace DIR        Reviewed source directory (read-only; required)
  --session-dir DIR      Writable review session, outside source (required)
  --output-dir DIR       Output directory (default: <session-dir>/log)
  --name NAME            Task name for the output subdirectory (default: timestamp)
  --timeout SECS         Timeout in seconds (default: 480)
  --prompt TEXT|FILE     Prompt text, or path to a prompt file (single token + exists)
  --prompt-file FILE     Read prompt from FILE
  --add-dir DIR          Compatibility option; must be inside the session.
  --sandbox MODE         Must be workspace-write (the default).
  --dry-run              Print the command without executing
  -h, --help             Show this help

The prompt can be provided as: --prompt, --prompt-file, or trailing positional
arguments. If multiple sources are given, the first one wins (in that order).
EOF
    exit "${1:-0}"
}

model=""
reasoning_effort=""
fast_mode="false"
workspace=""
session_dir=""
output_dir=""
task_name=""
timeout_secs=480
opt_prompt=""
opt_prompt_file=""
sandbox_mode="workspace-write"
dry_run=0
add_dirs=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --model)       model="$2"; shift 2 ;;
        --reasoning-effort) reasoning_effort="$2"; shift 2 ;;
        --fast-mode)   fast_mode="true"; shift ;;
        --no-fast-mode) fast_mode="false"; shift ;;
        --workspace)   workspace="$2"; shift 2 ;;
        --session-dir) session_dir="$2"; shift 2 ;;
        --output-dir)  output_dir="$2"; shift 2 ;;
        --name)        task_name="$2"; shift 2 ;;
        --timeout)     timeout_secs="$2"; shift 2 ;;
        --prompt)      opt_prompt="$2"; shift 2 ;;
        --prompt-file) opt_prompt_file="$2"; shift 2 ;;
        --add-dir)     add_dirs+=("$2"); shift 2 ;;
        --sandbox)     sandbox_mode="$2"; shift 2 ;;
        --dry-run)     dry_run=1; shift ;;
        -h|--help)     usage 0 ;;
        --)            shift; break ;;
        -*)            echo "Error: Unknown option: $1" >&2; usage 1 ;;
        *)             break ;;
    esac
done

positional_prompt="$*"

resolve_prompt_arg() {
    local text="$1"
    if [[ "$text" != *" "* && -f "$text" ]]; then
        cat "$text"
    else
        printf '%s' "$text"
    fi
}

if [[ -n "$opt_prompt" ]]; then
    prompt="$(resolve_prompt_arg "$opt_prompt")"
elif [[ -n "$opt_prompt_file" ]]; then
    if [[ ! -f "$opt_prompt_file" ]]; then
        echo "Error: --prompt-file not found: $opt_prompt_file" >&2
        exit 1
    fi
    prompt="$(cat "$opt_prompt_file")"
elif [[ -n "$positional_prompt" ]]; then
    prompt="$positional_prompt"
else
    prompt=""
fi

if [[ -z "$workspace" || -z "$session_dir" || -z "$prompt" || -z "$model" || -z "$reasoning_effort" ]]; then
    echo "Error: --workspace, --session-dir, --model, --reasoning-effort, and a prompt are required." >&2
    usage 1
fi

if [[ "$sandbox_mode" != "workspace-write" ]]; then
    echo "Error: the review runner requires the workspace-write sandbox." >&2
    exit 1
fi

workspace="$(realpath "$workspace")"
if [[ ! -d "$workspace" ]]; then
    echo "Error: workspace does not exist: $workspace" >&2
    exit 1
fi

# Resolve existing symlinks before checking scope, including paths that will be
# created below. Session artifacts must never make any part of source writable.
session_dir="$(realpath -m "$session_dir")"
within() { [[ "$2" == "/" || "$1" == "$2" || "$1" == "$2/"* ]]; }
if within "$workspace" "$session_dir" || within "$session_dir" "$workspace"; then
    echo "Error: session and source directories must not overlap." >&2
    exit 1
fi

if [[ -z "$output_dir" ]]; then
    output_dir="$session_dir/log"
fi
if [[ -z "$task_name" ]]; then
    task_name="$(date +%Y%m%d-%H%M%S)"
fi
if [[ "$task_name" == "." || "$task_name" == ".." || "$task_name" == */* ]]; then
    echo "Error: --name must be a single directory name." >&2
    exit 1
fi
output_dir="$(realpath -m "$output_dir")"
task_dir="$(realpath -m "$output_dir/$task_name")"
for d in "$output_dir" "$task_dir" "${add_dirs[@]}"; do
    resolved="$(realpath -m "$d")"
    if ! within "$resolved" "$session_dir"; then
        echo "Error: writable directory must be inside the session: $d" >&2
        exit 1
    fi
done
output_file="$task_dir/output.md"
stream_file="$task_dir/stream.jsonl"
meta_file="$task_dir/meta.json"
for artifact in "$output_file" "$stream_file" "$meta_file"; do
    if ! within "$(realpath -m "$artifact")" "$session_dir"; then
        echo "Error: output artifact escapes the session: $artifact" >&2
        exit 1
    fi
done
mkdir -p "$task_dir"
# Recheck after creation, so Codex receives canonical existing directories.
session_dir="$(realpath "$session_dir")"
task_dir="$(realpath "$task_dir")"
if ! within "$task_dir" "$session_dir"; then
    echo "Error: task directory escaped the session." >&2
    exit 1
fi

start_time="$(date -Iseconds)"
pgid="$(ps -o pgid= -p "$$" | tr -d ' ' || true)"

if command -v jq >/dev/null; then
    jq -n \
        --arg model "$model" \
        --arg reasoning_effort "$reasoning_effort" \
        --arg fast_mode "$fast_mode" \
        --arg workspace "$workspace" \
        --arg session_dir "$session_dir" \
        --arg working_directory "$task_dir" \
        --arg prompt "$prompt" \
        --arg start "$start_time" \
        --arg timeout "$timeout_secs" \
        --arg sandbox "$sandbox_mode" \
        --arg pid "$$" \
        --arg pgid "$pgid" \
        --arg supervisor_pid "${PEANUT_SUPERVISOR_PID:-}" \
        '{runner: "codex", model: $model, reasoning_effort: $reasoning_effort,
          fast_mode: ($fast_mode == "true"),
          workspace: $workspace, session_dir: $session_dir,
          working_directory: $working_directory, prompt: $prompt,
          start: $start, timeout: ($timeout | tonumber), sandbox: $sandbox,
          pid: ($pid | tonumber),
          pgid: (if $pgid == "" then null else ($pgid | tonumber) end),
          supervisor_pid: (if $supervisor_pid == "" then null else ($supervisor_pid | tonumber) end)}' \
        > "$meta_file"
fi

echo "codex-task" >&2
echo "  Runner:    codex (codex exec)" >&2
echo "  Model:     ${model:-<codex default>}" >&2
echo "  Reasoning: ${reasoning_effort:-<codex default>}" >&2
echo "  Fast mode: $fast_mode" >&2
echo "  Workspace: $workspace" >&2
echo "  Session:   $session_dir" >&2
echo "  Sandbox:   $sandbox_mode" >&2
echo "  Output:    $output_file" >&2
echo "  Timeout:   ${timeout_secs}s" >&2
echo "" >&2

# Build the command. --output-last-message captures the agent's final reply
# verbatim (this is what we expose as output.md). --json gives a structured
# event stream we tee into stream.jsonl for debugging.
cmd=(codex exec
     --disable multi_agent
     --disable apps
     --disable browser_use
     --disable computer_use
     -c 'web_search="disabled"'
     --ignore-user-config
     --ignore-rules
     --ephemeral
     --cd "$task_dir"
     --sandbox "$sandbox_mode"
     -c 'approval_policy="never"'
     -c 'sandbox_workspace_write.writable_roots=[]'
     -c 'sandbox_workspace_write.exclude_slash_tmp=true'
     -c 'sandbox_workspace_write.exclude_tmpdir_env_var=true'
     -c 'sandbox_workspace_write.network_access=false'
     --add-dir "$session_dir"
     --skip-git-repo-check
     --json
     --output-last-message "$output_file")

if [[ -n "$model" ]]; then
    cmd+=(--model "$model")
fi
if [[ -n "$reasoning_effort" ]]; then
    cmd+=(-c "model_reasoning_effort=\"$reasoning_effort\"")
fi
if [[ "$fast_mode" == "true" ]]; then
    cmd+=(--enable fast_mode)
elif [[ "$fast_mode" == "false" ]]; then
    cmd+=(--disable fast_mode)
fi

cmd+=("$prompt")

if (( dry_run )); then
    printf '%q ' "${cmd[@]}" >&2
    echo >&2
    exit 0
fi

# `codex exec` reads stdin when no prompt arg is given OR when stdin is piped
# (it appends as `<stdin>` block). Close stdin explicitly so codex doesn't
# block waiting for input that will never arrive. Final metadata and timeout
# cleanup are handled by the Python supervisor.
# Keep tool temporary files in the writable session instead of /tmp. This
# legacy sandbox restricts writes, not reads; it is not a private-data boundary.
export TMPDIR="$task_dir/tmp"
mkdir -p "$TMPDIR"
exec "${cmd[@]}" > "$stream_file" 2>&1 < /dev/null
