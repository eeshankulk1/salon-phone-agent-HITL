from ..session import SessionLocal


def get_db_session():
    """Get database session with proper cleanup"""
    session = SessionLocal()
    try:
        return session
    finally:
        session.close() 