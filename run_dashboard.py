"""Run the KLTN FastAPI backend and serve the built SPA dashboard."""

from __future__ import annotations

import os

import uvicorn


def main() -> None:
    """Start the application using environment-configurable host and port."""
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload_enabled = os.getenv("APP_ENV", "development").lower() == "development"

    uvicorn.run(
        "backend.app.main:app",
        host=host,
        port=port,
        reload=reload_enabled,
    )


if __name__ == "__main__":
    main()
