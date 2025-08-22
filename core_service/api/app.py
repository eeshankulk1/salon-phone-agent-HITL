import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv, find_dotenv

from api.routes import help_requests, knowledge_base

# Load environment variables from repo root
load_dotenv(find_dotenv())

# Configure logging to show supervisor communication logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI app
app = FastAPI(title="Core Service")

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/healthz")
def health_check():
    return {"status": "ok"}

# Include routers with /api prefix
app.include_router(help_requests.router, prefix="/api/help-requests", tags=["help-requests"])
app.include_router(knowledge_base.router, prefix="/api/knowledge-base", tags=["knowledge-base"]) 