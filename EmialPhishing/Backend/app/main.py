from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.config.settings import settings
from app.utils.logger import setup_logging
from app.routes.analysis import router as analysis_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Phishing Detection API...")
    logger.info(f"App version: {settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # You can add startup initialization here
    # For example, loading the model
    
    yield
    
    # Shutdown
    logger.info("Shutting down Phishing Detection API...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-grade phishing email detection system using TinyBERT and OSINT analysis",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis_router, prefix=settings.api_v1_str, tags=["analysis"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Phishing Detection API",
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "health": f"{settings.api_v1_str}/health"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "status_code": 500
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
