"""
Idempotent startup seeding. Runs every time the app boots, but only ever
inserts data once:
  - the first admin account (from ADMIN_EMAIL / ADMIN_PASSWORD env vars)
  - sample testimonials for homepage

NOTE: sample testimonials are placeholder demo content. Replace them from
Admin → Testimonials panel before site goes live.
"""
from . import models, security
from .config import settings
from .database import SessionLocal


def seed_data() -> None:
    db = SessionLocal()
    try:
        # Seed admin account if it doesn't exist
        if not db.query(models.Admin).filter(models.Admin.email == settings.ADMIN_EMAIL).first():
            if not settings.ADMIN_PASSWORD:
                raise ValueError(
                    "ADMIN_PASSWORD environment variable not set. "
                    "Add ADMIN_PASSWORD to your .env file."
                )

            db.add(
                models.Admin(
                    email=settings.ADMIN_EMAIL,
                    hashed_password=security.hash_password(settings.ADMIN_PASSWORD),
                )
            )

        # Seed sample testimonials if none exist
        if db.query(models.Testimonial).count() == 0:
            db.add_all(
                [
                    models.Testimonial(
                        client_name="Sample Client — Nairobi",
                        message=(
                            "Placeholder testimonial. Replace this with real client "
                            "feedback from Admin → Testimonials once your first "
                            "reviews come in."
                        ),
                        rating=5,
                        project_type="Steel Fabrication",
                    ),
                    models.Testimonial(
                        client_name="Sample Client — Upcountry",
                        message=(
                            "Placeholder testimonial. Replace this with real client "
                            "feedback from Admin → Testimonials once your first "
                            "reviews come in."
                        ),
                        rating=5,
                        project_type="Interior Fittings",
                    ),
                    models.Testimonial(
                        client_name="Sample Client — Kenya",
                        message=(
                            "Placeholder testimonial. Replace this with real client "
                            "feedback from Admin → Testimonials once your first "
                            "reviews come in."
                        ),
                        rating=5,
                        project_type="Construction",
                    ),
                ]
            )

        db.commit()
    finally:
        db.close()