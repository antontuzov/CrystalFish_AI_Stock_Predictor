"""
CrystalFish - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import structlog

from app.core.config import get_settings
from app.core.database import init_db
from app.api import auth, simulations, agents

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    logger.info("Starting up CrystalFish API...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CrystalFish API...")


def create_application() -> FastAPI:
    """Create FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI Swarm Intelligence for Stock/Crypto Prediction",
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(simulations.router, prefix="/api/v1")
    app.include_router(agents.router, prefix="/api/v1")
    
    # Health check
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": settings.APP_VERSION}
    
    # Root
    @app.get("/")
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "description": "AI Swarm Intelligence for Stock/Crypto Prediction",
            "docs": "/docs"
        }
    
    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)