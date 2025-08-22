from ..session import SessionLocal
from ..models import Customer


def create_customer(data: dict) -> Customer:
    """Create a new customer"""
    session = SessionLocal()
    try:
        customer = Customer(**data)
        session.add(customer)
        session.commit()
        session.refresh(customer)
        return customer
    finally:
        session.close() 