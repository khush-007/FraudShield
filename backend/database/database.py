from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# SQLite database URL
DATABASE_URL = "sqlite:///./fraudshield.db"


# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


# Create database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for database models
class Base(DeclarativeBase):
    pass


# Dependency for getting database sessions
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()