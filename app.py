"""Extension declaration, capabilities, health check for ClickUp Connector."""
from __future__ import annotations
import json
from imperal_sdk import ChatExtension, Extension

ext = Extension(
    "clickup-connector",
    version="0.1.0",
    display_name="ClickUp",
    icon="icon.svg",
    capabilities=["clickup:manage"],
    description="Official Imperal connector for ClickUp: spaces, folders, lists, tasks, comments, and webhooks via ClickUp API v2."
)

chat = ChatExtension(ext)

@ext.health_check
async def health_check(ctx) -> dict:
    raw = await ctx.secrets.get("clickup_connections")
    try:
        count = len(json.loads(raw)) if raw else 0
    except Exception:
        count = 0
    return {
        "healthy": True,
        "detail": f"{count} ClickUp connection(s) configured." if count else "Not connected yet."
    }
