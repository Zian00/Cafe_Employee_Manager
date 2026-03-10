import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.orm import Session

from app.api.dependencies import MediatorDep
from app.application.commands.cafes.create_cafe import CreateCafeCommand
from app.application.commands.cafes.delete_cafe import DeleteCafeCommand
from app.application.commands.cafes.update_cafe import UpdateCafeCommand
from app.application.dtos.cafe_dto import (
    CafeResponse,
    CreateCafeRequest,
    UpdateCafeRequest,
)
from app.application.queries.cafes.get_cafes import GetCafesQuery
from app.infrastructure.db.models.cafe_model import CafeModel
from app.infrastructure.db.session import get_db
from app.infrastructure.storage.supabase_storage import SupabaseStorageClient

router = APIRouter()

_MAX_LOGO_BYTES = 2 * 1024 * 1024  # 2 MB


async def _upload_logo(logo: UploadFile, storage: SupabaseStorageClient) -> str:
    content = await logo.read()
    if len(content) > _MAX_LOGO_BYTES:
        raise HTTPException(
            status_code=422, detail="Logo file must not exceed 2 MB."
        )
    ext = logo.filename.rsplit(".", 1)[-1] if logo.filename and "." in logo.filename else "png"
    path = f"cafes/{uuid.uuid4()}.{ext}"
    return storage.upload(path, content, logo.content_type or "image/png")


@router.get("/cafes", response_model=list[CafeResponse])
def get_cafes(
    mediator: MediatorDep,
    location: str | None = None,
):
    """List all cafes sorted by employee count desc. Filter by location if provided."""
    return mediator.send(GetCafesQuery(location=location))


@router.post("/cafes", response_model=CafeResponse, status_code=201)
async def create_cafe(
    mediator: MediatorDep,
    name: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    logo: UploadFile | None = File(None),
):
    """Create a new cafe. Logo upload is optional (multipart/form-data)."""
    try:
        req = CreateCafeRequest(name=name, description=description, location=location)
    except PydanticValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    logo_url: str | None = None
    if logo and logo.filename:
        logo_url = await _upload_logo(logo, SupabaseStorageClient())

    return mediator.send(
        CreateCafeCommand(
            name=req.name,
            description=req.description,
            location=req.location,
            logo=logo_url,
        )
    )


@router.put("/cafes/{id}", response_model=CafeResponse)
async def update_cafe(
    id: str,
    mediator: MediatorDep,
    db: Session = Depends(get_db),
    name: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    logo: UploadFile | None = File(None),
):
    """Update an existing cafe. Omit logo to keep the existing one."""
    try:
        req = UpdateCafeRequest(name=name, description=description, location=location)
    except PydanticValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    # Preserve existing logo when no new file is uploaded
    existing = db.get(CafeModel, id)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Cafe '{id}' not found.")

    if logo and logo.filename:
        logo_url: str | None = await _upload_logo(logo, SupabaseStorageClient())
    else:
        logo_url = existing.logo  # keep current

    return mediator.send(
        UpdateCafeCommand(
            id=id,
            name=req.name,
            description=req.description,
            location=req.location,
            logo=logo_url,
        )
    )


@router.delete("/cafes/{id}", status_code=204)
def delete_cafe(id: str, mediator: MediatorDep):
    """Delete a cafe and cascade-delete all its employees."""
    mediator.send(DeleteCafeCommand(id=id))
