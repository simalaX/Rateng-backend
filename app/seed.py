"""Idempotent startup seeding.

Runs every time the app boots, but only ever inserts data once:
  - the first admin account (from ADMIN_EMAIL / ADMIN_PASSWORD)
  - a handful of sample testimonials, so the homepage isn't empty on day one

NOTE: the sample testimonials are placeholder demo content, clearly not
real client names. Replace or delete them from Admin -> Testimonials
before the site goes live.
"""
from . import models, security
from .config import settings
from .database import SessionLocal


def seed_data() -> None:
    db = SessionLocal()
    try:
        if not db.query(models.Admin).filter(models.Admin.email == settings.ADMIN_EMAIL).first():
            db.add(
                models.Admin(
                    email=settings.ADMIN_EMAIL,
                    hashed_password=security.hash_password(settings.ADMIN_PASSWORD),
                )
            )

        if db.query(models.Testimonial).count() == 0:
            db.add_all(
                [
                    models.Testimonial(
                        client_name="Sample Client — Nairobi",
                        message=(
                            "Placeholder testimonial. Replace this with real client "
                            "feedback from Admin \u2192 Testimonials once your first "
                            "reviews come in."
                        ),
                        rating=5,
                        project_type="Steel Fabrication",
                    ),
                    models.Testimonial(
                        client_name="Sample Client — Upcountry",
                        message=(
                            "Placeholder testimonial. Replace this with real client "
                            "feedback from Admin \u2192 Testimonials once your first "
                            "reviews come in."
                        ),
                        rating=5,
                        project_type="Interior Fittings",
                    ),
                    models.Testimonial(
                        client_name="Sample Client — Nairobi",
                        message=(
                            "Placeholder testimonial. Replace this with real client "
                            "feedback from Admin \u2192 Testimonials once your first "
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
