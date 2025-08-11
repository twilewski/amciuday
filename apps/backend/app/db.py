import os
from sqlmodel import SQLModel, create_engine, Session
from app.core.settings import settings


def get_engine():
    """Create database engine with PostgreSQL for production or SQLite for development."""
    database_url = settings.database_url
    
    if database_url.startswith("postgresql"):
        # PostgreSQL configuration for production
        engine = create_engine(
            database_url,
            echo=settings.log_level == "DEBUG"
        )
    else:
        # SQLite configuration for development
        os.makedirs(os.path.dirname(settings.db_path), exist_ok=True)
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            echo=settings.log_level == "DEBUG"
        )
    
    return engine


def create_db_and_tables(engine):
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session dependency."""
    engine = get_engine()
    with Session(engine) as session:
        yield session


# Initialize database on import
engine = get_engine()
create_db_and_tables(engine)