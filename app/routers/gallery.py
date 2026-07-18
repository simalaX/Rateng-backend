from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_current_admin, get_db
from ..utils.cloudinary_utils import delete_image, upload_image

router = APIRouter(prefix="/api/gallery", tags=["gallery"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}


@router.get("/", response_model=schemas.GalleryListResponse)
def list_gallery_items(
    search: Optional[str] = None,
    category: Optional[models.ServiceCategory] = None,
    skip: int = 0,
    limit: int = Query(default=12, le=50),
    db: Session = Depends(get_db),
):
    query = db.query(models.GalleryItem)
    if category:
        query = query.filter(models.GalleryItem.category == category)
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(models.GalleryItem.title.ilike(like), models.GalleryItem.description.ilike(like))
        )
    total = query.count()
    items = query.order_by(models.GalleryItem.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.get("/{item_id}", response_model=schemas.GalleryItemOut)
def get_gallery_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.GalleryItem).filter(models.GalleryItem.id == item_id).first()
    if not item:
        raise HTTPException(404, "Gallery item not found")
    return item


@router.post("/", response_model=schemas.GalleryItemOut, status_code=201)
def create_gallery_item(
    title: str = Form(...),
    description: str = Form(...),
    category: models.ServiceCategory = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(400, "Only JPEG, PNG, or WEBP images are allowed")

    secure_url, public_id = upload_image(file.file)
    item = models.GalleryItem(
        title=title,
        description=description,
        category=category,
        image_url=secure_url,
        cloudinary_public_id=public_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=schemas.GalleryItemOut)
def update_gallery_item(
    item_id: int,
    title: str = Form(...),
    description: str = Form(...),
    category: models.ServiceCategory = Form(...),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    item = db.query(models.GalleryItem).filter(models.GalleryItem.id == item_id).first()
    if not item:
        raise HTTPException(404, "Gallery item not found")

    item.title = title
    item.description = description
    item.category = category

    if file is not None and file.filename:
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(400, "Only JPEG, PNG, or WEBP images are allowed")
        old_public_id = item.cloudinary_public_id
        secure_url, public_id = upload_image(file.file)
        item.image_url = secure_url
        item.cloudinary_public_id = public_id
        delete_image(old_public_id)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_gallery_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    item = db.query(models.GalleryItem).filter(models.GalleryItem.id == item_id).first()
    if not item:
        raise HTTPException(404, "Gallery item not found")
    delete_image(item.cloudinary_public_id)
    db.delete(item)
    db.commit()
    return None
