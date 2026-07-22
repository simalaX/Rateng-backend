from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, schemas, security
from ..dependencies import get_current_admin, get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        print(f"[LOGIN] Attempting login with email: {form_data.username}")
        admin = db.query(models.Admin).filter(models.Admin.email == form_data.username).first()

        if not admin:
            print(f"[LOGIN] Admin not found: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        if not security.verify_password(form_data.password, admin.hashed_password):
            print(f"[LOGIN] Invalid password for: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        print(f"[LOGIN] ✓ Login successful for: {form_data.username}")
        token = security.create_access_token({"sub": str(admin.id)})
        return {"access_token": token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"[LOGIN] ✗ Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        )


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
    db.add(current_admin)
    db.commit()
    return {"detail": "Password updated successfully"}