from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.core.config import settings
from backend.app.core.logging import logger, RequestIdMiddleware
from backend.app.core.errors import AppException, format_error_response
from backend.app.db.base import Base
from backend.app.db.session import engine, SessionLocal
from backend.app.db.models.user import User, UserRole
from backend.app.core.security import get_password_hash
from backend.app.api.v1 import api_v1_router
from backend.app.api.v1.health import router as health_root_router


def seed_admin_if_needed():
    """Ensure the system always boots with an initial active Administrator."""
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == settings.FIRST_SUPERUSER_EMAIL.lower()).first()
        if not admin:
            admin = User(
                email=settings.FIRST_SUPERUSER_EMAIL.lower(),
                name=settings.FIRST_SUPERUSER_NAME,
                hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(admin)
            db.commit()
            logger.info("Seeded initial administrator account: %s", settings.FIRST_SUPERUSER_EMAIL)
    except Exception as e:
        logger.error("Failed to seed initial admin: %s", e)
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and seed admin
    logger.info("Initializing %s v%s...", settings.PROJECT_NAME, settings.VERSION)
    Base.metadata.create_all(bind=engine)
    seed_admin_if_needed()
    logger.info("Database initialized. Ready to accept requests.")
    yield
    # Shutdown
    logger.info("Shutting down %s...", settings.PROJECT_NAME)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent stock-out prediction, multi-step demand forecasting, and decision support for retail pharmacies.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Request ID tracing middleware
app.add_middleware(RequestIdMiddleware)

# CORS Middleware (localhost:5173 frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers conforming to Section 3.5 & RFC 7807
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(exc.code, exc.message, exc.details),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            code="HTTP_ERROR",
            message=str(exc.detail),
            details={"status_code": exc.status_code},
        ),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=format_error_response(
            code="VALIDATION_ERROR",
            message="Request body or query parameter validation failed.",
            details={"errors": exc.errors()},
        ),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server exception during request %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=format_error_response(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected server error occurred. Please contact system support.",
        ),
    )


# Mount routes
app.include_router(health_root_router) # exposes /health directly at root as well
app.include_router(api_v1_router)      # exposes /api/v1/*
