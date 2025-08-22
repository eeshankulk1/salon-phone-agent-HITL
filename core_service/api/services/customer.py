from core_service.database import crud


def create_customer_for_session(display_name: str = None, phone_e164: str = None):
    """
    Create a customer record for a new session.
    
    Args:
        display_name: Optional display name for the customer
        phone_e164: Optional phone number in E164 format
    
    Returns:
        Created customer object or None if creation fails
    """
    try:
        customer_data = {}
        
        if display_name:
            customer_data["display_name"] = display_name
        if phone_e164:
            customer_data["phone_e164"] = phone_e164
            
        return crud.create_customer(customer_data)
    except Exception as e:
        print(f"Error creating customer: {e}")
        return None 