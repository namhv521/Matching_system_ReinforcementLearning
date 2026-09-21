"""FastAPI Application Entrypoint for KLTN Thesis-Advisor Matching Platform."""
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.legacy_compat import compat_router
from backend.app.api.v1.router import v1_router
from backend.app.core.config import settings
from backend.app.core.exceptions import register_exception_handlers
from backend.app.core.logging import logger
from backend.app.core.security import SecurityHeadersMiddleware
from backend.app.db.session import init_db

ROOT = settings.ROOT_PATH
FRONTEND_DIR = settings.FRONTEND_DIR
DIST_DIR = settings.DIST_DIR
FIGURES_DIR = settings.FIGURES_DIR
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing application resources...")
    try:
        init_db()
    except Exception as exc:
        logger.error(f"Failed to initialize database: {exc}")
    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Dual-Engine Matching Platform: Exact Hungarian Optimization & Maskable PPO Deep Reinforcement Learning",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Exception handlers
register_exception_handlers(app)

# Security & CORS Middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers: v1 versioned and direct compatibility
app.include_router(compat_router)
app.include_router(v1_router, prefix="/api")


@app.get("/health", tags=["System Health"])
def health_check():
    return {
        "status": "ok",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "database": "connected",
    }


# Mount figures directory
app.mount("/figures", StaticFiles(directory=str(FIGURES_DIR)), name="figures")

# Mount frontend assets (support Vite dist production assets and legacy assets)
if (DIST_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(DIST_DIR / "assets")), name="assets")
elif (FRONTEND_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")


@app.get("/")
def serve_index():
    dist_index = DIST_DIR / "index.html"
    if dist_index.exists():
        return FileResponse(str(dist_index))
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Thesis Matching API is running. Access /docs for interactive documentation."}


@app.get("/style.css")
def serve_css():
    css_path = FRONTEND_DIR / "style.css"
    if not css_path.exists():
        css_path = FRONTEND_DIR / "legacy" / "style.css"
    if css_path.exists():
        return FileResponse(str(css_path), media_type="text/css")
    raise HTTPException(status_code=404, detail="style.css not found")


@app.get("/app.js")
def serve_js():
    js_path = FRONTEND_DIR / "app.js"
    if not js_path.exists():
        js_path = FRONTEND_DIR / "legacy" / "app.js"
    if js_path.exists():
        return FileResponse(str(js_path), media_type="application/javascript")
    raise HTTPException(status_code=404, detail="app.js not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
