import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration variables
ENVIRONMENT = os.getenv("APP_ENV", "development")
DATABASE_URL = os.getenv("DATABASE_URL", "duckdb:///default_dev.db")

# Global variables to store engine and session
_engine = None
_SessionLocal = None

def get_engine():
    """
    Create or retrieve the SQLAlchemy engine.

    This function initializes the SQLAlchemy engine using the `DATABASE_URL` 
    from environment variables. The engine is configured with pooling options 
    and echo settings. If the engine is already created, it returns the 
    existing instance.

    Returns:
        sqlalchemy.engine.Engine: The SQLAlchemy engine instance.
    """
    global _engine
    if _engine is None:
        _engine = create_engine(
            DATABASE_URL,
            echo=os.getenv("SQLALCHEMY_ECHO", "False") == "True",
            pool_size=int(os.getenv("SQLALCHEMY_POOL_SIZE", 5)),
            max_overflow=int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", 10)),
            future=True,
        )
    return _engine

def get_session():
    """
    Create or retrieve a SQLAlchemy session.

    This function initializes a scoped session using the SQLAlchemy sessionmaker.
    The session is tied to the engine created by `get_engine()`. If the session 
    is already created, it returns the existing instance.

    Returns:
        sqlalchemy.orm.scoped_session: The SQLAlchemy scoped session instance.
    """
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
        )
    return _SessionLocal

def get_db():
    """
    Dependency to get DB session.

    This generator function provides a database session and ensures it is 
    properly closed after use. It is typically used in dependency injection 
    for web frameworks like FastAPI.

    Yields:
        sqlalchemy.orm.scoped_session: The SQLAlchemy scoped session instance.
    """
    db = get_session()
    try:
        yield db
    finally:
        db.close()
