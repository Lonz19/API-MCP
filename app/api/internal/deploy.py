import os
import subprocess
from pathlib import Path
from fastapi import APIRouter, Header, HTTPException

router = APIRouter()

# Repo root is two levels up from this file (app/api/internal/deploy.py)
REPO_ROOT = Path(__file__).resolve().parents[3]


@router.post("/internal/redeploy", include_in_schema=False)
async def redeploy(authorization: str = Header(None)):
    token = os.getenv("DEPLOY_TOKEN")
    if not token or authorization != f"Bearer {token}":
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        subprocess.Popen(
            ["bash", "-c", "sleep 1 && git pull origin deploy && kill 1"],
            cwd=str(REPO_ROOT),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "redeploy triggered", "repo_root": str(REPO_ROOT)}
