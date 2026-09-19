import json
import os
import secrets
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import httpx
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from backend.src.master_gen import MasterManager
from backend.src.pdf_gen import generate_typst_resume


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOCAL_DATA_DIR = PROJECT_ROOT / "backend" / "data"
LOCAL_DATA_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Resume Builder API", version="1.0.0")
bearer = HTTPBearer(auto_error=False)


class MasterDocument(BaseModel):
    profile: Dict[str, Any] = Field(default_factory=dict)
    summaries: Dict[str, str] = Field(default_factory=dict)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    experiences: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[Dict[str, Any]] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    skills: Dict[str, Any] = Field(default_factory=dict)


class BuildRequest(BaseModel):
    target_title: str = ""
    selected_exp_ids: List[str] = Field(default_factory=list)


def _local_path(user_id: str) -> Path:
    safe_user_id = "".join(char for char in user_id if char.isalnum() or char in "-_")
    return LOCAL_DATA_DIR / f"{safe_user_id}.json"


def _empty_master() -> Dict[str, Any]:
    return {
        "profile": {},
        "summaries": {},
        "education": [],
        "experiences": [],
        "certifications": [],
        "projects": [],
        "skills": {},
    }


async def _current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> str:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")

    token = credentials.credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")

    if supabase_url and supabase_key:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{supabase_url.rstrip('/')}/auth/v1/user",
                headers={"apikey": supabase_key, "Authorization": f"Bearer {token}"},
                timeout=5,
            )
        if response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user_id = response.json().get("id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has no user")
        return user_id

    # Development-only auth keeps local API work possible without weakening production auth.
    if os.getenv("APP_ENV", "development") == "production":
        raise HTTPException(status_code=503, detail="Supabase authentication is not configured")
    expected = os.getenv("DEV_API_TOKEN", "local-development-token")
    if not secrets.compare_digest(token, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid development token")
    return os.getenv("DEV_USER_ID", "local-user")


async def _load_master(user_id: str) -> Dict[str, Any]:
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if supabase_url and service_key:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{supabase_url.rstrip('/')}/rest/v1/master_documents",
                params={"user_id": f"eq.{user_id}", "select": "document", "limit": 1},
                headers={"apikey": service_key, "Authorization": f"Bearer {service_key}"},
                timeout=5,
            )
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail="Database read failed")
        rows = response.json()
        return rows[0]["document"] if rows else _empty_master()

    path = _local_path(user_id)
    if not path.exists():
        return _empty_master()
    return json.loads(path.read_text(encoding="utf-8"))


async def _save_master(user_id: str, document: Dict[str, Any]) -> None:
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if supabase_url and service_key:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{supabase_url.rstrip('/')}/rest/v1/master_documents",
                params={"on_conflict": "user_id"},
                headers={
                    "apikey": service_key,
                    "Authorization": f"Bearer {service_key}",
                    "Content-Type": "application/json",
                    "Prefer": "resolution=merge-duplicates,return=minimal",
                },
                json={"user_id": user_id, "document": document},
                timeout=5,
            )
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail="Database write failed")
        return

    _local_path(user_id).write_text(json.dumps(document, indent=2), encoding="utf-8")


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/me/master", response_model=MasterDocument)
async def get_master(user_id: str = Depends(_current_user)) -> Dict[str, Any]:
    return await _load_master(user_id)


@app.put("/api/v1/me/master", response_model=MasterDocument)
async def put_master(document: MasterDocument, user_id: str = Depends(_current_user)) -> MasterDocument:
    await _save_master(user_id, document.model_dump())
    return document


@app.post("/api/v1/me/build")
async def build_resume(
    request: BuildRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(_current_user),
) -> FileResponse:
    document = await _load_master(user_id)
    experiences = [
        experience
        for experience in document.get("experiences", [])
        if not request.selected_exp_ids or experience.get("id") in request.selected_exp_ids
    ]
    output = Path(tempfile.mkdtemp(prefix="resume-build-")) / "resume.pdf"
    if not generate_typst_resume(document.get("profile", {}), experiences, request.target_title, str(output)):
        raise HTTPException(status_code=500, detail="Resume compilation failed")
    background_tasks.add_task(shutil.rmtree, output.parent, ignore_errors=True)
    return FileResponse(
        output,
        media_type="application/pdf",
        filename="resume.pdf",
        background=background_tasks,
    )