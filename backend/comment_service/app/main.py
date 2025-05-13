from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import comments
from .database import init_db
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("comment-service")

app = FastAPI(
    title="Comment Service",
    description="Microservice for managing comments across the platform",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(comments.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_db_client():
    await init_db()
    logger.info("Database connection established")

@app.on_event("shutdown")
async def shutdown_db_client():
    # Database connection cleanup will be handled in database.py
    logger.info("Database connection closed")

@app.get("/health")
async def health_check():
    """Health check endpoint for the service"""
    return {"status": "healthy", "service": "comment-service"}