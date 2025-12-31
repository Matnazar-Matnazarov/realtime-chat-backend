"""
File upload API routes.
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.models.user import User

router = APIRouter(prefix="/upload", tags=["upload"])




# Ensure upload directory exists
upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> dict[str, str | int]:
    """Upload a file (image or video)."""
    # Check file size
    contents = await file.read()
    file_size = len(contents)
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes",
        )

    # Check file type
    if file.content_type not in settings.ALLOWED_EXTENSIONS:
        allowed_types = ", ".join(settings.ALLOWED_EXTENSIONS)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {allowed_types}",
        )

    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename

    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)

    # Return URL (in production, use CDN or S3 URL)
    file_url = f"/api/v1/upload/{unique_filename}"

    return {
        "url": file_url,
        "filename": unique_filename,
        "content_type": file.content_type or "application/octet-stream",
        "size": file_size,
    }


@router.get("/{filename}")
async def get_file(filename: str) -> FileResponse:
    """Get uploaded file."""
    file_path = upload_dir / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    return FileResponse(file_path)
