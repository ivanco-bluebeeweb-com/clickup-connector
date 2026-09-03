"""Connection lifecycle handlers for ClickUp Connector."""
from __future__ import annotations
import json, uuid
from imperal_sdk import ActionResult
from app import chat
from schemas import (
    ConnectClickUpParams, DisconnectClickUpParams, NoParams,
    ConnectionList, ClickUpConnection, ConnectResult, DeleteResult
)
from clickup_client import ClickUpClient

SECRET_KEY = "clickup_connections"

async def _load_connections(ctx) -> list[dict]:
    raw = await ctx.secrets.get(SECRET_KEY)
    if not raw:
        return []
    try:
        return json.loads(raw)
    except Exception:
        return []

async def _save_connections(ctx, connections: list[dict]) -> None:
    await ctx.secrets.set(SECRET_KEY, json.dumps(connections))

async def resolve_client(ctx, connection_id: str = "") -> ClickUpClient:
    connections = await _load_connections(ctx)
    if not connections:
        raise ValueError("No ClickUp connections found. Please connect an account first.")
    if connection_id:
        for c in connections:
            if c.get("id") == connection_id:
                return ClickUpClient(api_token=c["api_token"])
        raise ValueError(f"Connection ID {connection_id} not found.")
    c = connections[0]
    return ClickUpClient(api_token=c["api_token"])

@chat.function(
    "connect_clickup",
    "Connect your own ClickUp account by saving your Personal API token.",
    action_type="write",
    chain_callable=True,
    event="clickup-connector.connect_clickup",
    effects=["create:connection"],
    data_model=ConnectResult
)
async def connect_clickup(ctx, params: ConnectClickUpParams) -> ActionResult:
    """Connect a ClickUp account after verifying API token."""
    client = ClickUpClient(api_token=params.api_token)
    try:
        user_info = await client.get_user()
    except Exception as e:
        return ActionResult.error(f"Failed to authenticate with ClickUp: {e}")

    connections = await _load_connections(ctx)
    conn_id = str(uuid.uuid4())
    username = user_info.get("user", {}).get("username", "User") if isinstance(user_info, dict) else "User"
    label = params.label or f"ClickUp ({username})"

    connections.append({
        "id": conn_id,
        "label": label,
        "api_token": params.api_token
    })
    await _save_connections(ctx, connections)

    return ActionResult.success(
        ConnectResult(id=conn_id, label=label, status="connected"),
        summary=f"Connected to ClickUp as {username}."
    )

@chat.function(
    "list_connections",
    "List connected ClickUp accounts without exposing credentials.",
    action_type="read",
    chain_callable=True,
    data_model=ConnectionList
)
async def list_connections(ctx, params: NoParams) -> ActionResult:
    """List registered ClickUp accounts."""
    connections = await _load_connections(ctx)
    records = []
    for c in connections:
        tok = c.get("api_token", "")
        preview = f"{tok[:4]}...{tok[-4:]}" if len(tok) > 8 else "***"
        records.append(ClickUpConnection(
            id=c.get("id", ""),
            label=c.get("label", ""),
            api_token_preview=preview,
            is_active=True
        ))
    return ActionResult.success(
        ConnectionList(connections=records, count=len(records)),
        summary=f"Found {len(records)} ClickUp connection(s)."
    )

@chat.function(
    "disconnect_clickup",
    "Disconnect a ClickUp account.",
    action_type="write",
    chain_callable=True,
    event="clickup-connector.disconnect_clickup",
    effects=["delete:connection"],
    data_model=DeleteResult
)
async def disconnect_clickup(ctx, params: DisconnectClickUpParams) -> ActionResult:
    """Disconnect and remove a ClickUp account."""
    connections = await _load_connections(ctx)
    new_connections = [c for c in connections if c.get("id") != params.connection_id]
    if len(new_connections) == len(connections):
        return ActionResult.error(f"Connection {params.connection_id} not found.")
    await _save_connections(ctx, new_connections)
    return ActionResult.success(
        DeleteResult(connection_id=params.connection_id, status="disconnected"),
        summary=f"Connection {params.connection_id} removed."
    )
