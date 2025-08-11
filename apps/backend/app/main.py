from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import recipes, ingredients, history, seed
from app.db import create_db_and_tables, get_engine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Amciu Day API",
    description="API for the Amciu Day recipe spinning app",
    version="1.0.0"
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for deployed app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(recipes.router)
app.include_router(ingredients.router)
app.include_router(history.router)
app.include_router(seed.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting Amciu Day API...")
    engine = get_engine()
    create_db_and_tables(engine)
    logger.info("Database initialized")


@app.get("/")
async def root():
    return {"message": "Amciu Day API is running!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}