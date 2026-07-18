from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_current_admin, get_db

router = APIRouter(prefix="/api/testimonials", tags=["testimonials"])


@router.get("/", response_model=List[schemas.TestimonialOut])
def list_testimonials(limit: int = Query(default=20, le=50), db: Session = Depends(get_db)):
    return (
        db.query(models.Testimonial)
        .order_by(models.Testimonial.created_at.desc())
        .limit(limit)
        .all()
    )


@router.post("/", response_model=schemas.TestimonialOut, status_code=201)
def create_testimonial(
    payload: schemas.TestimonialCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    item = models.Testimonial(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=schemas.TestimonialOut)
def update_testimonial(
    item_id: int,
    payload: schemas.TestimonialCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    item = db.query(models.Testimonial).filter(models.Testimonial.id == item_id).first()
    if not item:
        raise HTTPException(404, "Testimonial not found")
    for field, value in payload.model_dump().items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_testimonial(
    item_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin),
):
    item = db.query(models.Testimonial).filter(models.Testimonial.id == item_id).first()
    if not item:
        raise HTTPException(404, "Testimonial not found")
    db.delete(item)
    db.commit()
    return None
