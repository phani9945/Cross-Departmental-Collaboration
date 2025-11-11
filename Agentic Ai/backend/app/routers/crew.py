from __future__ import annotations

import hmac
import hashlib
from typing import Dict, Any

from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models import CrewJob

router = APIRouter()


def verify_signature(payload: bytes, signature: str | None) -> bool:
    if not signature:
        return False
    secret = settings.CREW_WEBHOOK_SECRET.encode("utf-8")
    digest = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, signature)


@router.post("/webhook")
async def crew_webhook(
    raw_body: bytes,
    x_signature: str | None = Header(default=None, convert_underscores=True),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    if not verify_signature(raw_body, x_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Expect JSON body like: { "id": "<external_id>", "status": "running|completed|failed", "data": {...} }
    # FastAPI will parse body again if we try to accept it as dict directly; use raw then re-parse:
    import json

    data = json.loads(raw_body.decode("utf-8"))
    external_id = data.get("id")
    status = data.get("status")
    if not external_id:
        raise HTTPException(status_code=400, detail="Missing id")

    job = db.query(CrewJob).filter(CrewJob.external_id == external_id).first()
    if not job:
        # Upsert behavior: ignore unknown job in this demo
        return {"ok": True, "ignored": True}

    if status:
        job.status = status
    job.payload = json.dumps(data)
    db.commit()
    return {"ok": True}


