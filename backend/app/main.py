from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.session import init_db
from app.api.routers import auth, profile, jobs, codequest, aptitude, personality, documents, interview, events, admin, notifications


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    print(f"[INFO] {settings.APP_NAME} v{settings.APP_VERSION} started")
    yield
    # Shutdown
    print("[INFO] Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-driven Career Advising Platform for students and early-career professionals",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Job Board"])
app.include_router(codequest.router, prefix="/api/codequest", tags=["Code Quest"])
app.include_router(aptitude.router, prefix="/api/aptitude", tags=["Aptitude Quest"])
app.include_router(personality.router, prefix="/api/personality", tags=["Personality Test"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(interview.router, prefix="/api/interview", tags=["Interview Coach"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}
