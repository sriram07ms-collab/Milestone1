"""FastAPI main application"""
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from config.settings import LOG_LEVEL
from database.models import init_db
from scripts.seed_database import seed_database_from_file

logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize database on startup
try:
    init_db()
    logger.info("Database initialized successfully")
    seeded = seed_database_from_file()
    if seeded:
        logger.info("Database seeded with default data")
except Exception as e:
    logger.warning(f"Database initialization warning: {e}")

# Create FastAPI app
app = FastAPI(
    title="ICICI Prudential Mutual Fund FAQ Assistant",
    description="FAQ chatbot for ICICI Prudential Mutual Funds using Groww data",
    version="1.0.0"
)

# Add CORS middleware (restrict in production)
_cors_env = os.getenv("BACKEND_CORS_ORIGINS", "")
_default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
allow_origins = [o.strip() for o in _cors_env.split(",") if o.strip()] or _default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api", tags=["FAQ"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ICICI Prudential Mutual Fund FAQ Assistant API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.head("/")
async def root_head():
    """HEAD root for platform health probes"""
    return {}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

