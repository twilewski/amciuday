from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # Database settings - PostgreSQL for production, SQLite for local
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/amciuday.db")
    db_path: str = "./data/amciuday.db"  # Fallback for SQLite
    seed_json: str = "./recipes_expanded.json"
    log_level: str = "INFO"
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = int(os.getenv("PORT", "8000"))
    
    # CORS settings - allow all origins for deployed app
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:5174",
        "http://localhost:5175",
        "capacitor://localhost",
        "https://*.onrender.com"  # Allow all Render subdomains
    ]

    class Config:
        env_file = ".env"


settings = Settings()