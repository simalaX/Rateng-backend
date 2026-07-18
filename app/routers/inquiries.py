from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_current_admin, get_db

router = APIRouter(prefix="/api/inquiries", tags=["inquiries"])


@router.post("/", response_model=schemas.InquiryOut, status_code=201)
def create_inquiry(payload: schemas.InquiryCreate, db: Session = Depends(get_db)):
    """Public endpoint — anyone can submit the contact form, no auth needed."""
    item = models.Inquiry(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=schemas.InquiryListResponse)
def list_inquiries(
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    query = db.query(models.Inquiry)
    total = query.count()
    unread = query.filter(models.Inquiry.is_read.is_(False)).count()
    items = query.order_by(models.Inquiry.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "unread": unread, "items": items}


@router.patch("/{item_id}/read", response_model=schemas.InquiryOut)
def mark_inquiry_read(
    item_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    item = db.query(models.Inquiry).filter(models.Inquiry.id == item_id).first()
    if not item:
        raise HTTPException(404, "Inquiry not found")
    item.is_read = True
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_inquiry(
    item_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    item = db.query(models.Inquiry).filter(models.Inquiry.id == item_id).first()
    if not item:
        raise HTTPException(404, "Inquiry not found")
    db.delete(item)
    db.commit()
    return None
