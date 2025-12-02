#!/usr/bin/env python3
"""
Simple test server for CogOS ingestion API
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the ingestion routes
from app.api.routes.ingestion import router as ingestion_router
from app.api.schemas.ingestion import *

# Create FastAPI app
app = FastAPI(
    title="CogOS Ingestion API",
    description="Knowledge ingestion system for CogOS",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the ingestion routes
app.include_router(ingestion_router, prefix="/api/ingestion", tags=["ingestion"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "CogOS Ingestion API"}

@app.get("/")
async def root():
    return {"message": "CogOS Ingestion API", "docs": "/docs"}

if __name__ == "__main__":
    print("🧠 Starting CogOS Ingestion API Server on http://localhost:8001")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("🔍 Health Check: http://localhost:8001/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=True
    )
