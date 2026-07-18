from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, schemas, security
from ..dependencies import get_current_admin, get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.email == form_data.username).first()
    if not admin or not security.verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    token = security.create_access_token({"sub": str(admin.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.AdminOut)
def read_current_admin(current_admin: models.Admin = Depends(get_current_admin)):
    return current_admin


@router.put("/change-password")
def change_password(
    payload: schemas.ChangePasswordRequest,
    current_admin: models.Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if not security.verify_password(payload.current_password, current_admin.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_admin.hashed_password = security.hash_password(payload.new_password)
    db.commit()
    return {"detail": "Password updated successfully"}
