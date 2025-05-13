from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db, get_users_collection
from .routers import users, validate
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("auth-service")

app = FastAPI(
    title="Auth Service",
    description="Authentication service with JWT tokens",
    version="1.0.0"
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
app.include_router(users.router, prefix="/api")
app.include_router(validate.router)

@app.on_event("startup")
async def startup_db_client():
    logger.info("Connecting to MongoDB")
    await init_db()

@app.get("/health")
async def health_check():
    return {"status": "ok"}