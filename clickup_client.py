"""HTTP client for ClickUp API v2."""
from __future__ import annotations
import httpx
import time
from typing import Any, Optional

DEFAULT_BASE = "https://api.clickup.com/api/v2"

class ClickUpClient:
    def __init__(self, api_token: str, base_url: str = ""):
        self.api_token = api_token.strip()
        self.base_url = (base_url.strip() if base_url else DEFAULT_BASE).rstrip('/')
        self.headers = {
            "Authorization": self.api_token,
            "Content-Type": "application/json",
            "User-Agent": "Imperal-ClickUp-Connector/1.0.0"
        }
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    async def _req(self, method: str, path: str, json: Any = None, params: Any = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.request(method, url, headers=self.headers, json=json, params=params)
            resp.raise_for_status()
            if resp.status_code == 204 or not resp.content:
                return {"status": "ok"}
            return resp.json()

    async def get_user(self) -> dict[str, Any]:
        return await self._req("GET", "/user")

    async def get_teams(self) -> list[dict[str, Any]]:
        res = await self._req("GET", "/team")
        return res.get("teams", [])

    async def get_spaces(self, team_id: str) -> list[dict[str, Any]]:
        res = await self._req("GET", f"/team/{team_id}/space")
        return res.get("spaces", [])

    async def get_folders(self, space_id: str) -> list[dict[str, Any]]:
        res = await self._req("GET", f"/space/{space_id}/folder")
        return res.get("folders", [])

    async def get_lists(self, folder_id: Optional[str] = None, space_id: Optional[str] = None) -> list[dict[str, Any]]:
        if folder_id:
            res = await self._req("GET", f"/folder/{folder_id}/list")
            return res.get("lists", [])
        if space_id:
            res = await self._req("GET", f"/space/{space_id}/list")
            return res.get("lists", [])
        return []

    async def get_tasks(self, list_id: str, archived: bool = False, page: int = 0, statuses: Optional[list[str]] = None) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"archived": str(archived).lower(), "page": page}
        if statuses:
            params["statuses[]"] = statuses
        res = await self._req("GET", f"/list/{list_id}/task", params=params)
        return res.get("tasks", [])

    async def get_task(self, task_id: str) -> dict[str, Any]:
        return await self._req("GET", f"/task/{task_id}")

    async def create_task(self, list_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._req("POST", f"/list/{list_id}/task", json=payload)

    async def update_task(self, task_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._req("PUT", f"/task/{task_id}", json=payload)

    async def delete_task(self, task_id: str) -> dict[str, Any]:
        return await self._req("DELETE", f"/task/{task_id}")

    async def get_task_comments(self, task_id: str) -> list[dict[str, Any]]:
        res = await self._req("GET", f"/task/{task_id}/comment")
        return res.get("comments", [])

    async def create_task_comment(self, task_id: str, comment_text: str) -> dict[str, Any]:
        return await self._req("POST", f"/task/{task_id}/comment", json={"comment_text": comment_text})

    async def create_webhook(self, team_id: str, endpoint: str, events: list[str]) -> dict[str, Any]:
        return await self._req("POST", f"/team/{team_id}/webhook", json={"endpoint": endpoint, "events": events})

    async def audit_health(self) -> dict[str, Any]:
        t0 = time.time()
        user_data = await self.get_user()
        teams = await self.get_teams()
        lat = (time.time() - t0) * 1000
        return {
            "status": "healthy",
            "user": user_data.get("user", {}).get("username", "Unknown"),
            "teams_count": len(teams),
            "latency_ms": round(lat, 2),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
