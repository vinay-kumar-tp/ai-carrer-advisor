from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.session import init_db
from app.api.routers import auth, profile, jobs, codequest, aptitude, personality, documents, interview, events, admin, notifications, position_ai


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    if settings.SEED_ON_STARTUP:
        from app.core.startup_seed import run_startup_seed
        await run_startup_seed()
    print(f"[INFO] {settings.APP_NAME} v{settings.APP_VERSION} started (debug={settings.DEBUG})")
    yield
    # Shutdown
    print("[INFO] Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-driven Career Advising Platform for students and early-career professionals",
    lifespan=lifespan,
    # Swagger/Redoc/OpenAPI schema are only exposed in DEBUG mode so a
    # production deploy doesn't hand out a full API map to anyone who asks.
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
)

# CORS — locked to the explicit origin list from settings (see CORS_ORIGINS_RAW).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Baseline hardening headers on every response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(self), microphone=(self), geolocation=()"
    if not settings.DEBUG:
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    return response

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
app.include_router(position_ai.router, prefix="/api/position-ai", tags=["Position AI"])
app.include_router(position_ai.candidate_router, prefix="/api/candidate", tags=["Position AI"])


@app.get("/api/health")
async def health_check():
    from app.ai import gemini
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        # True once an AI provider key is configured. When False, AI features
        # (conversational interview, grading, resume optimizer) run on
        # deterministic local fallbacks instead.
        "ai_enabled": gemini.is_enabled(),
    }
