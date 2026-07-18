import enum

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Integer, String, Text, func

from .database import Base


class ServiceCategory(str, enum.Enum):
    """The four service disciplines Rateng offers. Used to tag and filter
    gallery images, videos, and testimonials."""

    construction = "construction"
    steel_fabrication = "steel_fabrication"
    glass_and_aluminium = "glass_and_aluminium"
    interior_fittings = "interior_fittings"


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class GalleryItem(Base):
    """A single uploaded project photo, stored in Cloudinary."""

    __tablename__ = "gallery_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(SAEnum(ServiceCategory), nullable=False, index=True)
    image_url = Column(String(500), nullable=False)
    cloudinary_public_id = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class VideoItem(Base):
    """A YouTube video the admin has linked, with its own description."""

    __tablename__ = "video_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(SAEnum(ServiceCategory), nullable=False, index=True)
    youtube_url = Column(String(500), nullable=False)
    youtube_id = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class Testimonial(Base):
    __tablename__ = "testimonials"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False, default=5)
    project_type = Column(String(150), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Inquiry(Base):
    """A message submitted through the public contact form."""

    __tablename__ = "inquiries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=True)
    service_interested = Column(String(100), nullable=True)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
