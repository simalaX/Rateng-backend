from typing import Tuple

import cloudinary
import cloudinary.uploader

from ..config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


def upload_image(file_obj, folder: str = "rateng/gallery") -> Tuple[str, str]:
    """Upload an image file object to Cloudinary.

    Returns (secure_url, public_id).
    """
    result = cloudinary.uploader.upload(
        file_obj,
        folder=folder,
        resource_type="image",
        overwrite=False,
    )
    return result["secure_url"], result["public_id"]


def delete_image(public_id: str) -> None:
    """Best-effort delete. We don't want a Cloudinary hiccup to block a
    database update, so failures here are swallowed."""
    try:
        cloudinary.uploader.destroy(public_id, resource_type="image")
    except Exception:
        pass
