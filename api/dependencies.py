"""API dependencies"""
from database.db_connection import get_db_session

# Re-export for convenience
__all__ = ["get_db_session"]

