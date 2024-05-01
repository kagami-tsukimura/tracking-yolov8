# flake8: noqa: E402
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

parent_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(parent_dir)

from config import get_settings

DATABASE_URL = get_settings().database_url


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    Returns a database session object that can be used to interact with the database.

    This function creates a new database session using the `SessionLocal` object from the SQLAlchemy ORM. The session is yielded to the caller, allowing them to perform database operations within a context manager. Once the context manager is exited, the session is automatically closed to release any resources associated with it.

    Returns:
        A context manager that yields a database session object.

    Example:
        with get_db() as db:
            # Perform database operations using the 'db' session object.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
