"""Resource operation handlers for ClickUp Connector."""
from __future__ import annotations
from typing import Any
from imperal_sdk import ActionResult
from app import chat
from handlers_connection import resolve_client
from schemas import (
    DeleteResult,
    GenericListResult, GenericRecordResult,
    ListTeamsParams, ListSpacesParams, ListFoldersParams, ListListsParams,
    ListTasksParams, GetTaskParams, CreateTaskParams, UpdateTaskParams,
    DeleteTaskParams, ListCommentsParams, CreateTaskCommentParams,
    CreateWebhookParams, AuditHealthParams, TaskRecord, TaskList,
    CommentRecord, CommentList, WebhookRecord, HealthAuditResult
)

@chat.function(
    "list_teams",
    "List ClickUp workspaces (teams) accessible with the current token.",
    action_type="read",
    chain_callable=True,
    data_model=GenericListResult
)
async def list_teams(ctx, params: ListTeamsParams) -> ActionResult:
    """List ClickUp teams."""
    client = await resolve_client(ctx, params.connection_id)
    try:
        teams = await client.get_teams()
        return ActionResult.success({"teams": teams, "count": len(teams)}, summary=f"Found {len(teams)} ClickUp team(s).")
    except Exception as e:
        return ActionResult.error(f"Error listing teams: {e}")

@chat.function(
    "list_spaces",
    "List Spaces in a ClickUp team.",
    action_type="read",
    chain_callable=True,
    data_model=GenericListResult
)
async def list_spaces(ctx, params: ListSpacesParams) -> ActionResult:
    """List Spaces in a team."""
    client = await resolve_client(ctx, params.connection_id)
    try:
        spaces = await client.get_spaces(team_id=params.team_id)
        return ActionResult.success({"spaces": spaces, "count": len(spaces)}, summary=f"Found {len(spaces)} space(s).")
    except Exception as e:
        return ActionResult.error(f"Error listing spaces: {e}")

@chat.function(
    "list_folders",
    "List Folders in a ClickUp space.",
    action_type="read",
    chain_callable=True,
    data_model=GenericListResult
)
async def list_folders(ctx, params: ListFoldersParams) -> ActionResult:
    """List Folders in a space."""
    client = await resolve_client(ctx, params.connection_id)
    try:
        folders = await client.get_folders(space_id=params.space_id)
        return ActionResult.success({"folders": folders, "count": len(folders)}, summary=f"Found {len(folders)} folder(s).")
    except Exception as e:
        return ActionResult.error(f"Error listing folders: {e}")

@chat.function(
    "list_lists",
    "List Lists in a space or folder.",
    action_type="read",
    chain_callable=True,
    data_model=GenericListResult
)
async def list_lists(ctx, params: ListListsParams) -> ActionResult:
    """List Lists in a space or folder."""
    client = await resolve_client(ctx, params.connection_id)
    try:
        lists = await client.get_lists(folder_id=params.folder_id, space_id=params.space_id)
        return ActionResult.success({"lists": lists, "count": len(lists)}, summary=f"Found {len(lists)} list(s).")
    except Exception as e:
        return ActionResult.error(f"Error listing lists: {e}")

@chat.function(
    "list_tasks",
    "List tasks in a ClickUp list.",
    action_type="read",
    chain_callable=True,
    data_model=TaskList
)
async def list_tasks(ctx, params: ListTasksParams) -> ActionResult:
    """List tasks in a list."""
    client = await resolve_client(ctx, params.connection_id)
    try:
        tasks = await client.get_tasks(list_id=params.list_id, archived=params.archived, page=params.page)
        task_recs = [
            TaskRecord(
                id=t.get("id", ""),
                name=t.get("name", ""),
                status=t.get("status", {}).get("status", "") if isinstance(t.get("status"), dict) else str(t.get("status", "")),
                url=t.get("url")
            )
            for t in tasks
        ]
        return ActionResult.success(
            TaskList(tasks=task_recs, count=len(task_recs)),
            summary=f"Found {len(task_recs)} task(s) in list {params.list_id}."
        )
    except Exception as e:
        return ActionResult.error(f"Error listing tasks: {e}")

@chat.function(
    "get_task",
    "Read one task in full by task ID.",
    action_type="read",
    chain_callable=True,
    data_model=TaskRecord
)
async def get_task(ctx, params: GetTaskParams) -> ActionResult:
    """Read a task."""
    client = await resolve_client(ctx, params.connection_id)
    try:
        t = await client.get_task(task_id=params.task_id)
        st = t.get("status", {}).get("status", "") if isinstance(t.get("status"), dict) else str(t.get("status", ""))
        return ActionResult.success(
            TaskRecord(id=t.get("id", ""), name=t.get("name", ""), status=st, url=t.get("url")),
            summary=f"Retrieved task {params.task_id}: {t.get('name')}."
        )
    except Exception as e:
        return ActionResult.error(f"Error getting task: {e}")

@chat.function(
    "create_task",
    "Create a task in a ClickUp list.",
    action_type="write",
    chain_callable=True,
    event="clickup-connector.create_task",
    effects=["create:task"],
    data_model=TaskRecord
)
async def create_task(ctx, params: CreateTaskParams) -> ActionResult:
    """Create a task."""
    client = await resolve_client(ctx, params.connection_id)
    try:
        payload = {"name": params.name}
        if params.description:
            payload["description"] = params.description
        if params.priority is not None:
            payload["priority"] = params.priority
        t = await client.create_task(list_id=params.list_id, payload=payload)
        st = t.get("status", {}).get("status", "") if isinstance(t.get("status"), dict) else str(t.get("status", ""))
        return ActionResult.success(
            TaskRecord(id=t.get("id", ""), name=t.get("name", ""), status=st, url=t.get("url")),
            summary=f"Created task '{params.name}' with id {t.get('id')}."
        )
    except Exception as e:
        return ActionResult.error(f"Error creating task: {e}")

@chat.function(
    "update_task",
    "Update selected fields of an existing task.",
    action_type="write",
    chain_callable=True,
    event="clickup-connector.update_task",
    effects=["update:task"],
    data_model=TaskRecord
)
async def update_task(ctx, params: UpdateTaskParams) -> ActionResult:
    """Update a task."""
    client = await resolve_client(ctx, params.connection_id)
    try:
        fields = {}
        if params.name is not None: fields["name"] = params.name
        if params.description is not None: fields["description"] = params.description
        if params.status is not None: fields["status"] = params.status
        if params.priority is not None: fields["priority"] = params.priority
        t = await client.update_task(task_id=params.task_id, payload=fields)
        st = t.get("status", {}).get("status", "") if isinstance(t.get("status"), dict) else str(t.get("status", ""))
        return ActionResult.success(
            TaskRecord(id=t.get("id", ""), name=t.get("name", ""), status=st, url=t.get("url")),
            summary=f"Updated task {params.task_id}."
        )
    except Exception as e:
        return ActionResult.error(f"Error updating task: {e}")

@chat.function(
    "delete_task",
    "Delete a task from ClickUp.",
    action_type="write",
    chain_callable=True,
    event="clickup-connector.delete_task",
    effects=["delete:task"],
    data_model=DeleteResult
)
async def delete_task(ctx, params: DeleteTaskParams) -> ActionResult:
    """Delete a task."""
    client = await resolve_client(ctx, params.connection_id)
    try:
        await client.delete_task(task_id=params.task_id)
        return ActionResult.success({"task_id": params.task_id, "deleted": True}, summary=f"Deleted task {params.task_id}.")
    except Exception as e:
        return ActionResult.error(f"Error deleting task: {e}")

@chat.function(
    "list_comments",
    "List comments on a task.",
    action_type="read",
    chain_callable=True,
    data_model=CommentList
)
async def list_comments(ctx, params: ListCommentsParams) -> ActionResult:
    """List comments on a task."""
    client = await resolve_client(ctx, params.connection_id)
    try:
        comments = await client.get_task_comments(task_id=params.task_id)
        recs = [
            CommentRecord(id=c.get("id", ""), comment_text=c.get("comment_text", ""))
            for c in comments
        ]
        return ActionResult.success(
            CommentList(comments=recs, count=len(recs)),
            summary=f"Found {len(recs)} comment(s) on task {params.task_id}."
        )
    except Exception as e:
        return ActionResult.error(f"Error listing comments: {e}")

@chat.function(
    "create_task_comment",
    "Post a comment to a ClickUp task.",
    action_type="write",
    chain_callable=True,
    event="clickup-connector.create_task_comment",
    effects=["create:comment"],
    data_model=CommentRecord
)
async def create_task_comment(ctx, params: CreateTaskCommentParams) -> ActionResult:
    """Post a comment to a task."""
    client = await resolve_client(ctx, params.connection_id)
    try:
        c = await client.create_task_comment(task_id=params.task_id, comment_text=params.comment_text)
        return ActionResult.success(
            CommentRecord(id=c.get("id", ""), comment_text=params.comment_text),
            summary=f"Posted comment to task {params.task_id}."
        )
    except Exception as e:
        return ActionResult.error(f"Error posting comment: {e}")

@chat.function(
    "create_webhook",
    "Subscribe to ClickUp events via webhook.",
    action_type="write",
    chain_callable=True,
    event="clickup-connector.create_webhook",
    effects=["create:webhook"],
    data_model=WebhookRecord
)
async def create_webhook(ctx, params: CreateWebhookParams) -> ActionResult:
    """Register a webhook in ClickUp."""
    client = await resolve_client(ctx, params.connection_id)
    try:
        wh = await client.create_webhook(team_id=params.team_id, endpoint=params.endpoint, events=params.events)
        return ActionResult.success(
            WebhookRecord(id=wh.get("id", ""), endpoint=params.endpoint),
            summary=f"Created webhook {wh.get('id')} for team {params.team_id}."
        )
    except Exception as e:
        return ActionResult.error(f"Error creating webhook: {e}")

@chat.function(
    "audit_clickup_health",
    "Audit ClickUp connectivity, workspace count, and accessible spaces.",
    action_type="read",
    chain_callable=True,
    data_model=HealthAuditResult
)
async def audit_clickup_health(ctx, params: AuditHealthParams) -> ActionResult:
    """Perform health and connectivity audit for ClickUp."""
    client = await resolve_client(ctx, params.connection_id)
    try:
        user = await client.get_user()
        teams = await client.get_teams()
        return ActionResult.success(
            HealthAuditResult(
                status="healthy",
                user=user.get("user", {}).get("username", "Unknown") if isinstance(user, dict) else "Connected",
                teams_count=len(teams),
                summary=f"ClickUp connection healthy. {len(teams)} team(s) accessible."
            ),
            summary=f"ClickUp audit healthy: {len(teams)} team(s) reachable."
        )
    except Exception as e:
        return ActionResult.error(f"ClickUp health audit failed: {e}")
