#!/usr/bin/env python3
"""
Minimal test server with just ingestion routes
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add current directory to path
sys.path.append('.')
sys.path.append('..')

# Import just the ingestion routes
from app.api.routes.ingestion import router as ingestion_router

app = FastAPI(title="Test Ingestion API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only the ingestion router
app.include_router(ingestion_router)

@app.get("/")
async def root():
    return {"message": "Test Ingestion API", "status": "online"}

@app.get("/ping")
async def ping():
    return {"status": "alive"}

if __name__ == "__main__":
    import uvicorn
    print("Starting test ingestion server...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
