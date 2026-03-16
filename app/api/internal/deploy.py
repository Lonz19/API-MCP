import os
import subprocess
from fastapi import APIRouter, Header, HTTPException

router = APIRouter()


@router.get("/internal/ping", include_in_schema=False)
async def ping():
    return {"ok": True}


@router.post("/internal/redeploy", include_in_schema=False)
async def redeploy(authorization: str | None = Header(default=None)):
    token = os.getenv("DEPLOY_TOKEN")
    if not token or authorization != f"Bearer {token}":
        raise HTTPException(status_code=403, detail="Unauthorized")

    cwd = os.getcwd()

    # Step 1: check git status
    git_status = subprocess.run(
        ["git", "status", "--short"],
        cwd=cwd,
        capture_output=True,
        text=True,
    )

    # Step 2: check current branch and remote
    git_remote = subprocess.run(
        ["git", "remote", "-v"],
        cwd=cwd,
        capture_output=True,
        text=True,
    )

    # Step 3: try git pull and capture output
    git_pull = subprocess.run(
        ["git", "pull", "origin", "deploy"],
        cwd=cwd,
        capture_output=True,
        text=True,
    )

    return {
        "cwd": cwd,
        "git_status": git_status.stdout or git_status.stderr,
        "git_remote": git_remote.stdout or git_remote.stderr,
        "git_pull_stdout": git_pull.stdout,
        "git_pull_stderr": git_pull.stderr,
        "git_pull_returncode": git_pull.returncode,
    }
