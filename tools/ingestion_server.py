#!/usr/bin/env python3
"""
Minimal FastAPI server for testing the ingestion system
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import only the ingestion components
try:
    from app.api.ingestion.ingestion_coordinator import IngestionCoordinator
    from app.api.schemas.ingestion import *
    from app.api.routes.ingestion import router as ingestion_router
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

app = FastAPI(
    title="CogOS Ingestion API",
    description="Knowledge Ingestion System for CogOS",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the ingestion routes
app.include_router(ingestion_router, prefix="/api/v1/ingestion", tags=["ingestion"])

@app.get("/")
async def root():
    return {"message": "CogOS Ingestion API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ingestion-api"}

if __name__ == "__main__":
    print("🧠 Starting CogOS Ingestion API Server")
    print("📝 Port: 8001")
    print("🌐 Environment: development")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
