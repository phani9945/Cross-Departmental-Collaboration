from __future__ import annotations

import os
import uuid
from typing import Any, Dict, Optional

import httpx
from pydantic import BaseModel

from ..config import settings


class CrewCreateJobResponse(BaseModel):
    id: str
    status: str
    data: Dict[str, Any] = {}


class CrewAIClient:
    def __init__(self, api_base: Optional[str] = None, api_key: Optional[str] = None) -> None:
        self.api_base = api_base or (settings.CREW_API_BASE and str(settings.CREW_API_BASE))
        self.api_key = api_key or settings.CREW_API_KEY
        self._client = httpx.AsyncClient(timeout=15)

    async def create_job(self, payload: Dict[str, Any]) -> CrewCreateJobResponse:
        # In absence of configured external endpoint, simulate a created job
        if not self.api_base or not self.api_key:
            return CrewCreateJobResponse(id=str(uuid.uuid4()), status="created", data=payload)

        url = f"{self.api_base}/jobs"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        resp = await self._client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return CrewCreateJobResponse(id=data.get("id"), status=data.get("status", "created"), data=data)

    async def get_job(self, job_id: str) -> Dict[str, Any]:
        if not self.api_base or not self.api_key:
            return {"id": job_id, "status": "created"}
        url = f"{self.api_base}/jobs/{job_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        resp = await self._client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()

    async def update_job(self, job_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_base or not self.api_key:
            return {"id": job_id, "status": payload.get("status", "updated")}
        url = f"{self.api_base}/jobs/{job_id}"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        resp = await self._client.patch(url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()


