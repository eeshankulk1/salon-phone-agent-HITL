# Import all CRUD functions to maintain backward compatibility
# When importing from core_service.database.crud, all functions will be available

# Base functionality
from .base import get_db_session

# Help Requests CRUD
from .help_requests_crud import (
    list_help_requests,
    create_help_request,
    create_supervisor_response,
    update_help_request_status,
    get_help_request_with_answer,
)

# Knowledge Base CRUD
from .knowledge_base_crud import (
    list_kb,
    create_kb,
    update_kb,
    delete_kb,
    search_kb_by_embedding,
)

# Customer CRUD
from .customer_crud import (
    create_customer,
)

# Followup CRUD
from .followup_crud import (
    create_followup,
    get_followup_by_help_request,
    list_followups,
    update_followup_status,
)

# Make all functions available at module level for backward compatibility
__all__ = [
    # Base functionality
    "get_db_session",
    
    # Help Requests CRUD
    "list_help_requests",
    "create_help_request", 
    "create_supervisor_response",
    "update_help_request_status",
    "get_help_request_with_answer",
    
    # Knowledge Base CRUD
    "list_kb",
    "create_kb",
    "update_kb", 
    "delete_kb",
    "search_kb_by_embedding",
    
    # Customer CRUD
    "create_customer",
    
    # Followup CRUD
    "create_followup",
    "get_followup_by_help_request",
    "list_followups",
    "update_followup_status",
] 