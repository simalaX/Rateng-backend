import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_current_admin, get_db

router = APIRouter(prefix="/api/videos", tags=["videos"])

YOUTUBE_PATTERNS = [
    r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/shorts/)([A-Za-z0-9_-]{11})",
]


def extract_youtube_id(url: str) -> Optional[str]:
    for pattern in YOUTUBE_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


@router.get("/", response_model=schemas.VideoListResponse)
def list_videos(
    search: Optional[str] = None,
    category: Optional[models.ServiceCategory] = None,
    skip: int = 0,
    limit: int = Query(default=12, le=50),
    db: Session = Depends(get_db),
):
    query = db.query(models.VideoItem)
    if category:
        query = query.filter(models.VideoItem.category == category)
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(models.VideoItem.title.ilike(like), models.VideoItem.description.ilike(like))
        )
    total = query.count()
    items = query.order_by(models.VideoItem.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.get("/{item_id}", response_model=schemas.VideoItemOut)
def get_video(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.VideoItem).filter(models.VideoItem.id == item_id).first()
    if not item:
        raise HTTPException(404, "Video not found")
    return item


@router.post("/", response_model=schemas.VideoItemOut, status_code=201)
def create_video(
    payload: schemas.VideoItemCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    youtube_id = extract_youtube_id(payload.youtube_url)
    if not youtube_id:
        raise HTTPException(400, "Please provide a valid YouTube video URL")

    item = models.VideoItem(
        title=payload.title,
        description=payload.description,
        category=payload.category,
        youtube_url=payload.youtube_url,
        youtube_id=youtube_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=schemas.VideoItemOut)
def update_video(
    item_id: int,
    payload: schemas.VideoItemCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    item = db.query(models.VideoItem).filter(models.VideoItem.id == item_id).first()
    if not item:
        raise HTTPException(404, "Video not found")

    youtube_id = extract_youtube_id(payload.youtube_url)
    if not youtube_id:
        raise HTTPException(400, "Please provide a valid YouTube video URL")

    item.title = payload.title
    item.description = payload.description
    item.category = payload.category
    item.youtube_url = payload.youtube_url
    item.youtube_id = youtube_id
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_video(
    item_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    item = db.query(models.VideoItem).filter(models.VideoItem.id == item_id).first()
    if not item:
        raise HTTPException(404, "Video not found")
    db.delete(item)
    db.commit()
    return None
