"""Provider-agnostic Scalekit Agent Auth helper.

This follows Scalekit's Agent Auth shape without assuming Gmail. Use
SCALEKIT_CONNECTION_NAME for the non-Gmail connection configured in the
Scalekit dashboard, such as a Microsoft/Teams connector.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from scalekit.client import ScalekitClient


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(WORKSPACE_ROOT / ".env")


def env_value(*names: str, required: bool = True) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip()
    if required:
        joined = " or ".join(names)
        raise SystemExit(f"Missing required environment variable: {joined}")
    return None


def load_json(value: str | None, field_name: str) -> Any:
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{field_name} must be valid JSON: {exc}") from exc


def model_to_dict(model: Any) -> dict[str, Any]:
    if hasattr(model, "to_dict"):
        return model.to_dict()
    if hasattr(model, "model_dump"):
        return model.model_dump(mode="json")
    return {"value": str(model)}


def print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, default=str))


def client() -> ScalekitClient:
    return ScalekitClient(
        env_url=env_value("SCALEKIT_ENV_URL", "SCALEKIT_ENVIRONMENT_URL"),
        client_id=env_value("SCALEKIT_CLIENT_ID"),
        client_secret=env_value("SCALEKIT_CLIENT_SECRET"),
    )


def connection_name(args: argparse.Namespace) -> str:
    return args.connection_name or env_value(
        "SCALEKIT_CONNECTION_NAME", "SCALEKIT_TEAMS_CONNECTION_NAME"
    )


def identifier(args: argparse.Namespace) -> str:
    return args.identifier or env_value(
        "SCALEKIT_CONNECTED_ACCOUNT_IDENTIFIER", "SCALEKIT_TEAMS_ACCOUNT_IDENTIFIER"
    )


def optional_user_verify_url(args: argparse.Namespace) -> str | None:
    return args.user_verify_url or env_value("SCALEKIT_USER_VERIFY_URL", required=False)


def optional_state(args: argparse.Namespace) -> str | None:
    return args.state or env_value("SCALEKIT_STATE", required=False)


def cmd_show_config(_args: argparse.Namespace) -> None:
    config = {
        "env_url": env_value(
            "SCALEKIT_ENV_URL", "SCALEKIT_ENVIRONMENT_URL", required=False
        ),
        "client_id_present": bool(env_value("SCALEKIT_CLIENT_ID", required=False)),
        "client_secret_present": bool(
            env_value("SCALEKIT_CLIENT_SECRET", required=False)
        ),
        "connection_name": env_value("SCALEKIT_CONNECTION_NAME", required=False),
        "teams_connection_name": env_value(
            "SCALEKIT_TEAMS_CONNECTION_NAME", required=False
        ),
        "identifier": env_value(
            "SCALEKIT_CONNECTED_ACCOUNT_IDENTIFIER", required=False
        ),
        "teams_identifier": env_value(
            "SCALEKIT_TEAMS_ACCOUNT_IDENTIFIER", required=False
        ),
        "user_verify_url": env_value("SCALEKIT_USER_VERIFY_URL", required=False),
        "state_present": bool(env_value("SCALEKIT_STATE", required=False)),
    }
    print_json(config)


def cmd_authorize(args: argparse.Namespace) -> None:
    scalekit = client()
    conn = connection_name(args)
    account_identifier = identifier(args)

    account = scalekit.actions.get_or_create_connected_account(
        connection_name=conn,
        identifier=account_identifier,
        organization_id=args.organization_id,
        user_id=args.user_id,
        api_config=load_json(args.api_config, "--api-config"),
    )
    account_dict = model_to_dict(account).get("connected_account")
    account_status = (account_dict or {}).get("status")
    auth_link = None
    if args.force_link or account_status != "ACTIVE":
        auth_link = scalekit.actions.get_authorization_link(
            connection_name=conn,
            identifier=account_identifier,
            state=optional_state(args),
            user_verify_url=optional_user_verify_url(args),
        )
    print_json(
        {
            "connected_account": account_dict,
            "authorization_link": model_to_dict(auth_link) if auth_link else None,
        }
    )


def cmd_request(args: argparse.Namespace) -> None:
    scalekit = client()
    response = scalekit.actions.request(
        connection_name=connection_name(args),
        identifier=identifier(args),
        path=args.path,
        method=args.method,
        query_params=load_json(args.query_params, "--query-params"),
        body=load_json(args.body, "--body"),
        headers=load_json(args.headers, "--headers"),
    )
    try:
        body: Any = response.json()
    except ValueError:
        body = response.text
    print_json(
        {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": body,
        }
    )


def cmd_execute_tool(args: argparse.Namespace) -> None:
    scalekit = client()
    response = scalekit.actions.execute_tool(
        tool_name=args.tool_name,
        tool_input=load_json(args.params, "--params") or {},
        identifier=identifier(args),
        connection_name=connection_name(args),
    )
    print_json(model_to_dict(response))


def cmd_teams_me(args: argparse.Namespace) -> None:
    run_teams_request(args, "/v1.0/me")


def cmd_teams_joined(args: argparse.Namespace) -> None:
    run_teams_request(args, "/v1.0/me/joinedTeams")


def cmd_teams_channels(args: argparse.Namespace) -> None:
    run_teams_request(args, f"/v1.0/teams/{args.team_id}/channels")


def cmd_teams_messages(args: argparse.Namespace) -> None:
    query_params = None
    if args.top:
        query_params = {"$top": args.top}
    run_teams_request(
        args,
        f"/v1.0/teams/{args.team_id}/channels/{args.channel_id}/messages",
        query_params=query_params,
    )


def run_teams_request(
    args: argparse.Namespace,
    path: str,
    query_params: dict[str, Any] | None = None,
) -> None:
    scalekit = client()
    response = scalekit.actions.request(
        connection_name=connection_name(args),
        identifier=identifier(args),
        path=path,
        method="GET",
        query_params=query_params,
    )
    try:
        body: Any = response.json()
    except ValueError:
        body = response.text
    print_json(
        {
            "path": path,
            "status_code": response.status_code,
            "body": body,
        }
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run Scalekit Agent Auth flows without Gmail-specific assumptions. "
            "Includes Microsoft Teams smoke-test helpers."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    show_config = subparsers.add_parser(
        "show-config", help="Print non-secret Scalekit configuration."
    )
    show_config.set_defaults(func=cmd_show_config)

    authorize = subparsers.add_parser(
        "authorize", help="Get or create a connected account and print its auth link."
    )
    add_account_args(authorize)
    authorize.add_argument("--api-config", help="Optional connected-account API config JSON.")
    authorize.add_argument(
        "--force-link",
        action="store_true",
        help="Generate an authorization link even if the account is already ACTIVE.",
    )
    authorize.set_defaults(func=cmd_authorize)

    request = subparsers.add_parser(
        "request", help="Call a provider API through Scalekit's connected-account proxy."
    )
    add_account_args(request)
    request.add_argument("--path", required=True, help="Provider API path, e.g. /v1.0/me.")
    request.add_argument("--method", default="GET", help="HTTP method. Defaults to GET.")
    request.add_argument("--query-params", help="JSON object of query parameters.")
    request.add_argument("--body", help="JSON request body.")
    request.add_argument("--headers", help="JSON object of additional request headers.")
    request.set_defaults(func=cmd_request)

    execute_tool = subparsers.add_parser(
        "execute-tool", help="Execute a Scalekit tool for the connected account."
    )
    add_account_args(execute_tool)
    execute_tool.add_argument("--tool-name", required=True)
    execute_tool.add_argument("--params", default="{}", help="Tool input as JSON.")
    execute_tool.set_defaults(func=cmd_execute_tool)

    teams_me = subparsers.add_parser(
        "teams-me", help="Smoke test the Teams/Microsoft Graph connection with /v1.0/me."
    )
    add_account_args(teams_me)
    teams_me.set_defaults(func=cmd_teams_me)

    teams_joined = subparsers.add_parser(
        "teams-joined", help="List Teams joined by the connected account."
    )
    add_account_args(teams_joined)
    teams_joined.set_defaults(func=cmd_teams_joined)

    teams_channels = subparsers.add_parser(
        "teams-channels", help="List channels for a Microsoft Teams team."
    )
    add_account_args(teams_channels)
    teams_channels.add_argument("--team-id", required=True)
    teams_channels.set_defaults(func=cmd_teams_channels)

    teams_messages = subparsers.add_parser(
        "teams-messages", help="List recent messages for a Teams channel."
    )
    add_account_args(teams_messages)
    teams_messages.add_argument("--team-id", required=True)
    teams_messages.add_argument("--channel-id", required=True)
    teams_messages.add_argument("--top", type=int, default=10)
    teams_messages.set_defaults(func=cmd_teams_messages)

    return parser


def add_account_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--connection-name",
        help="Scalekit connection name. Defaults to SCALEKIT_CONNECTION_NAME.",
    )
    parser.add_argument(
        "--identifier",
        help=(
            "Connected account identifier. Defaults to "
            "SCALEKIT_CONNECTED_ACCOUNT_IDENTIFIER."
        ),
    )
    parser.add_argument("--organization-id")
    parser.add_argument("--user-id")
    parser.add_argument("--user-verify-url")
    parser.add_argument("--state")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
