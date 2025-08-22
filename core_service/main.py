import os
import uvicorn
from dotenv import load_dotenv, find_dotenv

from api.app import app

# Load environment variables from repo root
load_dotenv(find_dotenv())

if __name__ == "__main__":
    api_host = os.getenv("API_HOST", "0.0.0.0")
    api_port = int(os.getenv("API_PORT", "8000"))
    
    uvicorn.run(
        "main:app",
        host=api_host,
        port=api_port,
        reload=True
    ) 