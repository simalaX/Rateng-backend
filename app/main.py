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
    """Ensure admin account exists with correct password."""
    try:
        # Wait for admin table to exist
        inspector = inspect(engine)
        if "admins" not in inspector.get_table_names():
            print("⚠ Admin table not found, skipping admin creation")
            return

        with engine.connect() as conn:
            admin_email = settings.ADMIN_EMAIL
            hashed = security.hash_password(settings.ADMIN_PASSWORD)

            # Check if admin exists
            result = conn.execute(
                text("SELECT id FROM admins WHERE email = :email"),
                {"email": admin_email}
            )
            admin = result.fetchone()

            if admin:
                # Update password
                conn.execute(
                    text("UPDATE admins SET hashed_password = :hashed WHERE email = :email"),
                    {"email": admin_email, "hashed": hashed}
                )
                conn.commit()
                print(f"✓ Admin password updated: {admin_email}")
            else:
                # Create new admin
                conn.execute(
                    text("INSERT INTO admins (email, hashed_password) VALUES (:email, :hashed)"),
                    {"email": admin_email, "hashed": hashed}
                )
                conn.commit()
                print(f"✓ Admin account created: {admin_email}")
    except Exception as e:
        print(f"⚠ Admin error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[STARTUP] Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("[STARTUP] ✓ Tables created")
    except Exception as e:
        print(f"[STARTUP] ✗ Failed to create tables: {e}")

    print("[STARTUP] Seeding data...")
    seed_data()

    print("[STARTUP] Fixing admin...")
    fix_admin()

    print("[STARTUP] ✓ Startup complete")
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