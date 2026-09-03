"""Panel UI for ClickUp Connector."""
from __future__ import annotations
from imperal_sdk import ui
from app import ext
import handlers_connection as h

def _settings_button() -> ui.UINode:
    return ui.Button(
        "App settings",
        variant="secondary",
        size="sm",
        icon="settings",
        on_click=ui.Call("__clickup_settings")
    )

def _help_modal() -> ui.UINode:
    return ui.Modal(
        trigger=ui.Button("How do I set this up?", variant="ghost", size="sm"),
        title="Connecting ClickUp",
        children=[
            ui.Text(
                "1. Sign in to your ClickUp account and navigate to Settings > Apps.\n"
                "2. Generate or copy your Personal API token (pk_...).\n"
                "3. Enter the token below and click Connect ClickUp.",
                variant="body"
            )
        ]
    )

@ext.panel("clickup_sidebar", slot="left")
async def clickup_sidebar(ctx, **kwargs) -> ui.UINode:
    connections = await h._load_connections(ctx)
    conn_items = [
        ui.Text(c.get("label") or "ClickUp Account", variant="body")
        for c in connections
    ] if connections else [ui.Text("No ClickUp accounts connected yet.", variant="caption")]

    return ui.Stack(
        direction="v",
        gap=3,
        children=[
            ui.Stack(
                direction="h",
                justify="between",
                align="center",
                children=[
                    ui.Text("ClickUp", variant="heading"),
                    _settings_button()
                ]
            ),
            ui.Divider(),
            _help_modal(),
            ui.Stack(
                direction="v",
                gap=2,
                children=[
                    ui.Text("Active Connections", variant="caption"),
                    *conn_items
                ]
            ),
            ui.Divider(),
            ui.Form(
                submit_label="Connect ClickUp",
                action=ui.Call("connect_clickup"),
                children=[
                    ui.Input(
                        param_name="label",
                        placeholder="Friendly connection label (optional)"
                    ),
                    ui.Input(
                        param_name="api_token",
                        placeholder="ClickUp Personal API Token (pk_...)"
                    )
                ]
            )
        ]
    )
