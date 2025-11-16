"""Database connection utilities"""
from database.models import SessionLocal, init_db
from contextlib import contextmanager

@contextmanager
def get_db_session():
    """Context manager for database session"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

