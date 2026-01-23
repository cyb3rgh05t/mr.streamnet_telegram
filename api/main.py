"""
FastAPI application for Telegram Bot Web UI
Modern async API with SPA frontend
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load config
CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "config", "config.json"
)
with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

WEB_ENABLED = config.get("web", {}).get("ENABLED", True)
WEB_PORT = config.get("web", {}).get("PORT", 5000)
WEB_HOST = config.get("web", {}).get("HOST", "0.0.0.0")
WEB_AUTH_ENABLED = config.get("web", {}).get("AUTH_ENABLED", False)
WEB_SECRET_KEY = config.get("web", {}).get("SECRET_KEY", "change-me-in-production")
WEB_VERBOSE_LOGGING = config.get("web", {}).get("VERBOSE_LOGGING", False)

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "api.log")

logging.basicConfig(
    level=logging.DEBUG if WEB_VERBOSE_LOGGING else logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

# Bot instance (set by main bot.py)
bot_instance = None
bot_start_time = None


def set_bot_instance(bot, start_time=None):
    """Set the Telegram bot instance for API access"""
    global bot_instance, bot_start_time
    bot_instance = bot
    bot_start_time = start_time
    logger.info("Bot instance registered with API")


def get_bot_instance():
    """Get the Telegram bot instance"""
    return bot_instance


def get_bot_start_time():
    """Get the bot start time"""
    return bot_start_time


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("FastAPI starting up...")
    logger.info("FastAPI started successfully")
    yield
    logger.info("FastAPI shutting down...")


# Initialize FastAPI
app = FastAPI(
    title="Telegram Bot API",
    description="Modern async API for Telegram bot management",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if WEB_VERBOSE_LOGGING else None,
    redoc_url="/api/redoc" if WEB_VERBOSE_LOGGING else None,
    redirect_slashes=False,
)


# Add logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    if WEB_VERBOSE_LOGGING:
        logger.debug(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    if WEB_VERBOSE_LOGGING:
        logger.debug(f"Response: {response.status_code}")
    return response


# CORS middleware - configure for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5000",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register routers
from api.routers import (
    auth,
    dashboard,
    settings,
    media,
    groups,
    about,
)

# Register API routers FIRST (before catch-all routes)
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(media.router, prefix="/api/media", tags=["Media"])
app.include_router(groups.router, prefix="/api/groups", tags=["Groups"])
app.include_router(about.router, prefix="/api/about", tags=["About"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "bot_connected": bot_instance is not None,
    }


# Serve static files from frontend/dist
frontend_dist = Path(__file__).parent / "static"
if frontend_dist.exists():
    app.mount(
        "/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets"
    )
    logger.info(f"Serving static files from {frontend_dist}")


# Serve favicon
@app.get("/favicon.png")
async def serve_favicon():
    """Serve the favicon"""
    favicon_file = frontend_dist / "favicon.png"
    if favicon_file.exists():
        return FileResponse(favicon_file, media_type="image/png")
    raise HTTPException(status_code=404, detail="Favicon not found")


# Frontend routes LAST (after all API routes)
@app.get("/")
async def serve_frontend():
    """Serve the React frontend"""
    index_file = frontend_dist / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return JSONResponse(
        status_code=404,
        content={
            "error": "Frontend not built. Run 'npm run build' in frontend directory"
        },
    )


# Catch-all route for SPA - must be LAST after all API routes
@app.get("/{full_path:path}")
async def catch_all(full_path: str, request: Request):
    """Catch-all route for SPA routing - serves index.html for all non-API routes"""
    logger.debug(f"Catch-all route hit: {full_path}")

    # If it's an API or asset request, let it 404 naturally
    if full_path.startswith("api/") or full_path.startswith("assets/"):
        logger.debug(f"Returning 404 for API/asset path: {full_path}")
        raise HTTPException(status_code=404, detail="Not found")

    # For all other routes, serve the SPA index.html
    index_file = frontend_dist / "index.html"
    if index_file.exists():
        logger.debug(f"Serving index.html for path: {full_path}")
        return FileResponse(index_file)

    logger.error(f"Frontend not built - index.html missing at: {index_file}")
    return JSONResponse(status_code=404, content={"error": "Frontend not built"})


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Custom 500 handler"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=WEB_HOST,
        port=WEB_PORT,
        reload=WEB_VERBOSE_LOGGING,
        log_level="debug" if WEB_VERBOSE_LOGGING else "info",
    )
