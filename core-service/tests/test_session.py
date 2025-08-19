import pytest

from database.session import Base, SessionLocal, engine


class TestDatabaseSession:
    
    def test_engine_exists(self):
        """Test that SQLAlchemy engine exists"""
        assert engine is not None

    def test_session_local_creation(self):
        """Test that SessionLocal is properly configured"""
        assert SessionLocal is not None
        session = SessionLocal()
        assert hasattr(session, 'query')
        assert hasattr(session, 'add')
        assert hasattr(session, 'commit')
        session.close()

    def test_base_declarative(self):
        """Test that Base is properly configured for model inheritance"""
        assert Base is not None
        assert hasattr(Base, 'metadata')

    def test_session_factory_configuration(self):
        """Test SessionLocal factory basic configuration"""
        session = SessionLocal()
        
        # Verify session can be created and closed
        assert session is not None
        assert session.bind == engine
        
        session.close() 