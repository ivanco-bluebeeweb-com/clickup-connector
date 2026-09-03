"""Panel Settings for ClickUp Connector."""
from __future__ import annotations
from imperal_sdk import ui
from app import ext
import handlers_connection as h

@ext.panel("clickup_settings", slot="center")
async def clickup_settings(ctx, **kwargs) -> ui.UINode:
    conns = await h._load_connections(ctx)
    items = []
    for c in conns:
        items.append(
            ui.Stack(
                direction="h",
                gap=2,
                children=[
                    ui.Text(f"{c.get('label')} ({c.get('id')})", variant="body"),
                    ui.Button(
                        "Disconnect",
                        variant="danger",
                        size="sm",
                        on_click=ui.Call("disconnect_clickup", connection_id=c.get("id"))
                    )
                ]
            )
        )
    return ui.Stack(
        direction="v",
        gap=3,
        children=[
            ui.Text("ClickUp Settings & Accounts", variant="heading"),
            ui.Divider(),
            *(items if items else [ui.Text("No active connections to configure.", variant="caption")]),
        ]
    )
