import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()


SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise RuntimeError("db url env variable is not set")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # test connections before user
    pool_size=10,  # keep 10 connections ready
    max_overflow=20,  # allow 20 extra during traffic spikes
    echo=False,  # no sql logging (True for debug)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Session:
    """
    dependency for getting database session
    automatically handles session lifecycle
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    create all tables defined in models
    in production alembuc migrations will be used
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    only for development/testing
    """
    Base.metadata.drop_all(bind=engine)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    enable foreign key constaints for sqlite
    """
    if "sqlite" in SQLALCHEMY_DATABASE_URL:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
