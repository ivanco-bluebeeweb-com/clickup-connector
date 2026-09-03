"""Pydantic schemas for ClickUp Connector (API v2)."""
from __future__ import annotations
from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field

class NoParams(BaseModel):
    """Empty parameter model."""
    pass

class ConnectClickUpParams(BaseModel):
    label: str = Field(default="", description="Friendly connection label, e.g. Engineering ClickUp.")
    api_token: str = Field(..., description="ClickUp Personal API token (pk_...) or OAuth Bearer token.")

class DisconnectClickUpParams(BaseModel):
    connection_id: str = Field(..., description="Connection ID to remove.")

class ListTeamsParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")

class ListSpacesParams(BaseModel):
    team_id: str = Field(..., description="ClickUp Team (Workspace) ID.")
    connection_id: str = Field(default="", description="Optional connection ID.")

class ListFoldersParams(BaseModel):
    space_id: str = Field(..., description="Space ID.")
    connection_id: str = Field(default="", description="Optional connection ID.")

class ListListsParams(BaseModel):
    space_id: Optional[str] = Field(default=None, description="Space ID (for folderless lists).")
    folder_id: Optional[str] = Field(default=None, description="Folder ID (if lists belong to a folder).")
    connection_id: str = Field(default="", description="Optional connection ID.")

class ListTasksParams(BaseModel):
    list_id: str = Field(..., description="List ID to query tasks from.")
    connection_id: str = Field(default="", description="Optional connection ID.")
    page: int = Field(default=0, description="Page index (0-based).")
    archived: bool = Field(default=False, description="Include archived tasks.")

class GetTaskParams(BaseModel):
    task_id: str = Field(..., description="Task ID.")
    connection_id: str = Field(default="", description="Optional connection ID.")

class CreateTaskParams(BaseModel):
    list_id: str = Field(..., description="Target List ID.")
    name: str = Field(..., description="Task title / name.")
    description: Optional[str] = Field(default="", description="Task markdown description.")
    priority: Optional[int] = Field(default=None, description="Priority: 1=Urgent, 2=High, 3=Normal, 4=Low.")
    connection_id: str = Field(default="", description="Optional connection ID.")

class UpdateTaskParams(BaseModel):
    task_id: str = Field(..., description="Task ID to update.")
    name: Optional[str] = Field(default=None, description="Updated task name.")
    description: Optional[str] = Field(default=None, description="Updated description.")
    status: Optional[str] = Field(default=None, description="Updated status string.")
    priority: Optional[int] = Field(default=None, description="Updated priority (1-4).")
    connection_id: str = Field(default="", description="Optional connection ID.")

class DeleteTaskParams(BaseModel):
    task_id: str = Field(..., description="Task ID to delete.")
    connection_id: str = Field(default="", description="Optional connection ID.")

class ListCommentsParams(BaseModel):
    task_id: str = Field(..., description="Task ID.")
    connection_id: str = Field(default="", description="Optional connection ID.")

class CreateTaskCommentParams(BaseModel):
    task_id: str = Field(..., description="Task ID.")
    comment_text: str = Field(..., description="Text of comment to add.")
    notify_all: bool = Field(default=False, description="Whether to notify all watchers.")
    connection_id: str = Field(default="", description="Optional connection ID.")

class CreateWebhookParams(BaseModel):
    team_id: str = Field(..., description="ClickUp Team / Workspace ID.")
    endpoint: str = Field(..., description="Target HTTPS webhook URL.")
    events: List[str] = Field(default=["*"], description="Event types to subscribe to.")
    connection_id: str = Field(default="", description="Optional connection ID.")

class AuditHealthParams(BaseModel):
    connection_id: str = Field(default="", description="Optional connection ID.")

# Return / Data models
class ClickUpConnection(BaseModel):
    id: str = Field(..., description="Connection ID")
    label: str = Field(..., description="Connection label")
    api_token_preview: str = Field(..., description="Masked token")
    is_active: bool = Field(default=True, description="Active status")

class ConnectionList(BaseModel):
    connections: List[ClickUpConnection] = Field(default_factory=list)
    count: int = Field(default=0)

class ConnectResult(BaseModel):
    id: str = Field(..., description="Connection ID")
    label: str = Field(..., description="Connection label")
    status: str = Field(default="connected")

class DeleteResult(BaseModel):
    connection_id: str = Field(..., description="Deleted connection ID")
    status: str = Field(default="disconnected")

class GenericListResult(BaseModel):
    items: List[Dict[str, Any]] = Field(default_factory=list)
    count: int = Field(default=0)

class GenericRecordResult(BaseModel):
    data: Dict[str, Any] = Field(default_factory=dict)

class HealthAuditResult(BaseModel):
    status: str = Field(..., description="Audit status: healthy, degraded, or error")
    user: str = Field(default="Unknown", description="ClickUp user or organization name")
    teams_count: int = Field(default=0, description="Number of teams accessible")
    summary: str = Field(..., description="Human-readable health summary")

class TaskRecord(BaseModel):
    id: str = Field(..., description="Task ID")
    name: str = Field(..., description="Task name")
    status: Optional[str] = Field(default=None, description="Task status")

class TaskList(BaseModel):
    tasks: List[Dict[str, Any]] = Field(default_factory=list)
    count: int = Field(default=0)

class CommentRecord(BaseModel):
    id: str = Field(..., description="Comment ID")
    comment_text: str = Field(..., description="Comment content")

class CommentList(BaseModel):
    comments: List[Dict[str, Any]] = Field(default_factory=list)
    count: int = Field(default=0)

class WebhookRecord(BaseModel):
    id: str = Field(..., description="Webhook ID")
    endpoint: str = Field(..., description="Target endpoint")
