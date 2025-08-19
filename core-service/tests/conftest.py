import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone

# Set test DATABASE_URL before importing  
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from database.session import Base
from database.models import Customer, HelpRequest, KnowledgeBaseEntry
from api.app import app


@pytest.fixture(scope="function")
def test_engine():
    """Create in-memory SQLite engine for testing"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create test database session"""
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestSessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function") 
def client():
    """Create test client for API route testing"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_customer(test_session):
    """Create a sample customer for testing"""
    customer = Customer(
        display_name="Test Customer",
        phone_e164="+1234567890"
    )
    test_session.add(customer)
    test_session.commit()
    test_session.refresh(customer)
    return customer


@pytest.fixture
def sample_help_request(test_session, sample_customer):
    """Create a sample help request for testing"""
    help_request = HelpRequest(
        customer_id=sample_customer.id,
        question_text="How do I reset my password?",
        status="pending",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    test_session.add(help_request)
    test_session.commit()
    test_session.refresh(help_request)
    return help_request


@pytest.fixture
def sample_kb_entry(test_session):
    """Create a sample knowledge base entry for testing"""
    kb_entry = KnowledgeBaseEntry(
        question_text_example="How to reset password?",
        answer_text="Go to settings and click reset password"
    )
    test_session.add(kb_entry)
    test_session.commit()
    test_session.refresh(kb_entry)
    return kb_entry 