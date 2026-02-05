import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core import config
from ..database import get_session
from ..models import Image, User, JobStatus
from ..models import Image, User, JobStatus
from ..helpers import api_response_helper as responses
from . import deps

router = APIRouter()

@router.get("/images")
async def list_images(
    session: AsyncSession = Depends(get_session),
    current_user: Optional[User] = Depends(deps.get_current_user_optional) # Optional auth
):
    try:
        """Lists generated images. Public feed."""
        # TODO: This hardcoded URL needs to be dynamic or from config
        base_url = "http://127.0.0.1:8000/images"
        
        # Query DB sorted by created_at desc
        statement = select(Image, User).join(User, isouter=True).order_by(Image.created_at.desc())
        results = await session.execute(statement)
        # Results is list of (Image, User) tuples
        
        response_list = []
        for img, user in results:
            # Construct URL based on predictable structure: /images/{category}/{filename}
            if img.status == JobStatus.COMPLETED:
                # properly encode category? simplified for now
                safe_category = img.category.replace("\\", "/") if img.category else "uncategorized"
                url = f"{base_url}/{safe_category}/{img.filename}"
            else:
                url = None

            response_list.append({
                "id": img.id,
                "filename": img.filename,
                "category": img.category,
                "url": url,
                "prompt": img.prompt,
                "model": img.model,
                "created_at": img.created_at.isoformat(),
                "created_by": user.username if user else "Anonymous",
                "is_public": img.is_public,
                "status": img.status
            })
            
        return responses.api_success(
            message="Images List Retrieved",
            data={"images": response_list}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return responses.api_error(status_code=500, message="Failed to list images", error=str(e))

@router.get("/api/images/{image_id}")
async def get_image(
    image_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: Optional[User] = Depends(deps.get_current_user_optional)
):
    try:
        """Get a single image detail."""
        base_url = "http://127.0.0.1:8000/images"
        
        # Query with User join
        statement = select(Image, User).where(Image.id == image_id).join(User, isouter=True)
        result = await session.execute(statement)
        row = result.first()
        
        if not row:
            return responses.api_error(status_code=404, message="Not Found", error="Image not found")
            
        img, user = row
        
        url = None
        if img.status == JobStatus.COMPLETED:
            safe_category = img.category.replace("\\", "/") if img.category else "uncategorized"
            url = f"{base_url}/{safe_category}/{img.filename}"

        return responses.api_success(
            message="Image Detail Retrieved",
            data={
                "id": img.id,
                "filename": img.filename,
                "category": img.category,
                "url": url,
                "prompt": img.prompt,
                "width": img.width,
                "height": img.height,
                "model": img.model,
                "provider": img.provider,
                "created_at": img.created_at.isoformat(),
                "created_by": user.username if user else "Anonymous",
                "is_public": img.is_public,
                "status": img.status
            }
        )
    except Exception as e:
        return responses.api_error(status_code=500, message="Failed to retrieve image", error=str(e))

@router.get("/images/recent")
async def get_recent_images(
    session: AsyncSession = Depends(get_session),
    limit: int = 8
):
    """Get recent COMPLETED images for the home page showcase."""
    try:
        base_url = "http://127.0.0.1:8000/images"
        
        # Query only completed images, newest first, limited
        statement = (
            select(Image, User)
            .join(User, isouter=True)
            .where(Image.status == JobStatus.COMPLETED)
            .order_by(Image.created_at.desc())
            .limit(limit)
        )
        results = await session.execute(statement)
        
        response_list = []
        for img, user in results:
            safe_category = img.category.replace("\\", "/") if img.category else "uncategorized"
            url = f"{base_url}/{safe_category}/{img.filename}"
            
            response_list.append({
                "id": img.id,
                "filename": img.filename,
                "url": url,
                "prompt": img.prompt,
                "category": img.category,
                "model": img.model,
                "created_by": user.username if user else "Anonymous"
            })
        
        return responses.api_success(
            message="Recent Images Retrieved",
            data={"images": response_list, "count": len(response_list)}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return responses.api_error(status_code=500, message="Failed to get recent images", error=str(e))

