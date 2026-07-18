from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, computed_field

from .models import ServiceCategory

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


# ---------------------------------------------------------------------------
# Gallery (images)
# ---------------------------------------------------------------------------


class GalleryItemOut(BaseModel):
    id: int
    title: str
    description: str
    category: ServiceCategory
    image_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class GalleryListResponse(BaseModel):
    total: int
    items: List[GalleryItemOut]


# ---------------------------------------------------------------------------
# Videos (YouTube links)
# ---------------------------------------------------------------------------


class VideoItemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)
    category: ServiceCategory
    youtube_url: str = Field(min_length=1, max_length=500)


class VideoItemOut(BaseModel):
    id: int
    title: str
    description: str
    category: ServiceCategory
    youtube_url: str
    youtube_id: str
    created_at: datetime

    @computed_field
    @property
    def embed_url(self) -> str:
        return f"https://www.youtube.com/embed/{self.youtube_id}"

    @computed_field
    @property
    def thumbnail_url(self) -> str:
        return f"https://img.youtube.com/vi/{self.youtube_id}/hqdefault.jpg"

    class Config:
        from_attributes = True


class VideoListResponse(BaseModel):
    total: int
    items: List[VideoItemOut]


# ---------------------------------------------------------------------------
# Testimonials
# ---------------------------------------------------------------------------


class TestimonialCreate(BaseModel):
    client_name: str = Field(min_length=1, max_length=150)
    message: str = Field(min_length=1, max_length=2000)
    rating: int = Field(ge=1, le=5, default=5)
    project_type: Optional[str] = Field(default=None, max_length=150)


class TestimonialOut(BaseModel):
    id: int
    client_name: str
    message: str
    rating: int
    project_type: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Inquiries (contact form)
# ---------------------------------------------------------------------------


class InquiryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=30)
    service_interested: Optional[str] = Field(default=None, max_length=100)
    message: str = Field(min_length=1, max_length=5000)


class InquiryOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    service_interested: Optional[str] = None
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class InquiryListResponse(BaseModel):
    total: int
    unread: int
    items: List[InquiryOut]
