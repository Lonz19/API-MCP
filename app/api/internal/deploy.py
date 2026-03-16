import os
import subprocess
from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/internal/ping", include_in_schema=False)
async def ping():
    return {"ok": True, "deploy_token_set": bool(os.getenv("DEPLOY_TOKEN"))}


@router.post("/internal/redeploy", include_in_schema=False)
async def redeploy(authorization: str | None = Header(default=None)):
    token = os.getenv("DEPLOY_TOKEN")
    if not token or authorization != f"Bearer {token}":
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        cwd = os.getcwd()
        subprocess.Popen(
            ["bash", "-c", "sleep 1 && git pull origin deploy && kill 1"],
            cwd=cwd,
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e), "cwd": cwd})

    return {"status": "redeploy triggered", "cwd": cwd}
