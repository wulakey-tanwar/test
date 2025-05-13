from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .routes import profiles, followers
from .database import init_db, close_db
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="User Service API",
    description="API for user profiles and follower relationships",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    # Log request details
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    
    return response

# Include routers
app.include_router(profiles.router, prefix="/api/users", tags=["profiles"])
app.include_router(followers.router, prefix="/api/users", tags=["followers"])

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy", "service": "user-service"}

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    await init_db()
    logger.info("User service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()
    logger.info("User service shutdown gracefully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)