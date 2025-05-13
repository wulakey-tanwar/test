import os
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import time
from typing import Callable

from .database import Database
from .routes import post, timeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Post Service API",
    description="API for managing posts and user timeline",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Custom validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

# Startup event
@app.on_event("startup")
async def startup_db_client():
    try:
        await Database.connect_db()
        logger.info("Connected to MongoDB")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_db_client():
    await Database.close_db()
    logger.info("Disconnected from MongoDB")

# Root endpoint
@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    return {"message": "Post Service API", "status": "running"}

# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    # Check database connection
    try:
        # Simple ping to verify DB connection
        await Database.client.admin.command('ping')
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "database": db_status}
        )
    
    return {"status": "healthy", "database": db_status}

# Include routers
app.include_router(post.router)
app.include_router(timeline.router)