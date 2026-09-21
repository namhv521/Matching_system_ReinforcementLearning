"""Main entry point for KLTN AI Agent Application."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.config import agent_settings
from src.api.routes import agent_router

logging.basicConfig(
    level=agent_settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ai_agent.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown hooks."""
    logger.info(f"Starting {agent_settings.APP_NAME} v{agent_settings.APP_VERSION}")
    logger.info(f"LLM Provider: {agent_settings.LLM_PROVIDER}")
    yield
    logger.info(f"Shutting down {agent_settings.APP_NAME}")


app = FastAPI(
    title=agent_settings.APP_NAME,
    version=agent_settings.APP_VERSION,
    description="LangGraph-powered Thesis-Advisor Matching and Consultation Agent",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=agent_settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Agent Routes
app.include_router(agent_router)


@app.get("/", tags=["System"])
async def root():
    """Root landing endpoint."""
    return {
        "message": f"Welcome to {agent_settings.APP_NAME}",
        "version": agent_settings.APP_VERSION,
        "docs_url": "/docs",
        "health_check": "/api/v1/agent/health",
    }


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=agent_settings.HOST,
        port=agent_settings.PORT,
        reload=agent_settings.DEBUG,
    )
