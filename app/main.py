from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, inspect

from .config import settings
from .database import Base, engine
from .routers import auth, gallery, inquiries, testimonials, videos
from .seed import seed_data
from . import security, models


def fix_admin():
    """Ensure admin account exists in database (after tables are created)."""
    try:
        # Wait for admin table to exist
        inspector = inspect(engine)
        if "admins" not in inspector.get_table_names():
            print("⚠ Admin table not found, skipping admin creation")
            return

        with engine.connect() as conn:
            # Check if admin exists
            result = conn.execute(
                text("SELECT * FROM admins WHERE email = :email"),
                {"email": settings.ADMIN_EMAIL}
            )
            if not result.fetchone():
                hashed = security.hash_password(settings.ADMIN_PASSWORD)
                conn.execute(
                    text("INSERT INTO admins (email, hashed_password) VALUES (:email, :hashed)"),
                    {"email": settings.ADMIN_EMAIL, "hashed": hashed}
                )
                conn.commit()
                print(f"✓ Admin account created: {settings.ADMIN_EMAIL}")
            else:
                print(f"✓ Admin account already exists: {settings.ADMIN_EMAIL}")
    except Exception as e:
        print(f"⚠ Admin creation error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_data()
    fix_admin()
    yield


app = FastAPI(
    title="Rateng Construction and Interiors API",
    description="Backend API powering the Rateng Construction and Interiors website.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(gallery.router)
app.include_router(videos.router)
app.include_router(testimonials.router)
app.include_router(inquiries.router)


@app.get("/")
def root():
    return {
        "message": "Rateng Construction and Interiors API",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/api/health")
def health_check():
    return {"status": "ok"}