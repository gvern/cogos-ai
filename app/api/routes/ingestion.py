"""
Knowledge Ingestion API Routes
Provides endpoints for file upload, processing, and management of the ingestion pipeline
"""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import json
import os
import tempfile
import asyncio
import logging
from datetime import datetime

from ..ingestion.ingestion_coordinator import IngestionCoordinator
from ..schemas.ingestion import (
    IngestionJobResponse, 
    IngestionConfig, 
    FileProcessingResponse,
    BatchProcessingRequest,
    SearchRequest,
    SearchResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ingestion", tags=["Knowledge Ingestion"])

# Global ingestion coordinator instance
ingestion_coordinator = None

def get_ingestion_coordinator():
    """Get or create the global ingestion coordinator"""
    global ingestion_coordinator
    if ingestion_coordinator is None:
        # Load default config or from environment
        config_path = os.getenv('INGESTION_CONFIG_PATH', 'config/ingestion_config.json')
        ingestion_coordinator = IngestionCoordinator(config_path)
    return ingestion_coordinator

@router.post("/upload/single", response_model=FileProcessingResponse)
async def upload_single_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    collection_name: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # JSON string of tags list
    metadata: Optional[str] = Form(None)  # JSON string of metadata dict
):
    """Upload and process a single file"""
    try:
        coordinator = get_ingestion_coordinator()
        
        # Parse optional JSON fields
        tags_list = json.loads(tags) if tags else []
        metadata_dict = json.loads(metadata) if metadata else {}
        
        # Create temporary file
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file.filename)
        
        # Save uploaded file
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process file in background
        job_id = f"single_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        
        background_tasks.add_task(
            process_single_file_background,
            coordinator,
            temp_file_path,
            job_id,
            collection_name,
            user_id,
            tags_list,
            metadata_dict
        )
        
        return FileProcessingResponse(
            job_id=job_id,
            filename=file.filename,
            status="processing",
            message="File uploaded successfully and processing started"
        )
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/upload/batch", response_model=IngestionJobResponse)
async def upload_batch_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    collection_name: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None)
):
    """Upload and process multiple files as a batch"""
    try:
        coordinator = get_ingestion_coordinator()
        
        # Parse optional JSON fields
        tags_list = json.loads(tags) if tags else []
        metadata_dict = json.loads(metadata) if metadata else {}
        
        # Create temporary directory for batch
        temp_dir = tempfile.mkdtemp()
        file_paths = []
        
        # Save all uploaded files
        for file in files:
            temp_file_path = os.path.join(temp_dir, file.filename)
            with open(temp_file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            file_paths.append(temp_file_path)
        
        # Process batch in background
        job_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(files)}_files"
        
        background_tasks.add_task(
            process_batch_files_background,
            coordinator,
            file_paths,
            job_id,
            collection_name,
            user_id,
            tags_list,
            metadata_dict
        )
        
        return IngestionJobResponse(
            job_id=job_id,
            status="processing",
            total_files=len(files),
            processed_files=0,
            message="Batch upload successful, processing started"
        )
        
    except Exception as e:
        logger.error(f"Error uploading batch: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch upload failed: {str(e)}")

@router.post("/process/cloud-sync")
async def sync_cloud_drives(
    background_tasks: BackgroundTasks,
    config: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
):
    """Sync and process files from configured cloud drives"""
    try:
        coordinator = get_ingestion_coordinator()
        
        # Start cloud sync in background
        job_id = f"cloud_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        background_tasks.add_task(
            sync_cloud_drives_background,
            coordinator,
            job_id,
            config or {},
            user_id
        )
        
        return IngestionJobResponse(
            job_id=job_id,
            status="processing",
            message="Cloud sync started"
        )
        
    except Exception as e:
        logger.error(f"Error starting cloud sync: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cloud sync failed: {str(e)}")

@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get the status of an ingestion job"""
    try:
        coordinator = get_ingestion_coordinator()
        
        # Get job status from coordinator
        status = await coordinator.get_job_status(job_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

@router.get("/jobs")
async def list_jobs(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """List ingestion jobs with optional filtering"""
    try:
        coordinator = get_ingestion_coordinator()
        
        jobs = await coordinator.list_jobs(
            user_id=user_id,
            status=status,
            limit=limit
        )
        
        return {"jobs": jobs}
        
    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")

@router.post("/search", response_model=SearchResponse)
async def search_knowledge(request: SearchRequest):
    """Search through ingested knowledge using semantic similarity"""
    try:
        coordinator = get_ingestion_coordinator()
        
        results = await coordinator.search_knowledge(
            query=request.query,
            collection_name=request.collection_name,
            user_id=request.user_id,
            limit=request.limit,
            min_similarity=request.min_similarity,
            filters=request.filters
        )
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results)
        )
        
    except Exception as e:
        logger.error(f"Error searching knowledge: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/collections")
async def list_collections(user_id: Optional[str] = None):
    """List available knowledge collections"""
    try:
        coordinator = get_ingestion_coordinator()
        
        collections = await coordinator.list_collections(user_id=user_id)
        
        return {"collections": collections}
        
    except Exception as e:
        logger.error(f"Error listing collections: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list collections: {str(e)}")

@router.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str, user_id: Optional[str] = None):
    """Delete a knowledge collection and all its documents"""
    try:
        coordinator = get_ingestion_coordinator()
        
        success = await coordinator.delete_collection(
            collection_name=collection_name,
            user_id=user_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Collection not found")
        
        return {"message": f"Collection '{collection_name}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting collection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete collection: {str(e)}")

@router.get("/stats")
async def get_ingestion_stats(user_id: Optional[str] = None):
    """Get ingestion pipeline statistics"""
    try:
        coordinator = get_ingestion_coordinator()
        
        stats = await coordinator.get_stats(user_id=user_id)
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.post("/config")
async def update_ingestion_config(config: IngestionConfig):
    """Update ingestion configuration"""
    try:
        coordinator = get_ingestion_coordinator()
        
        success = await coordinator.update_config(config.dict())
        
        if not success:
            raise HTTPException(status_code=400, detail="Invalid configuration")
        
        return {"message": "Configuration updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update config: {str(e)}")

@router.get("/health")
async def ingestion_health_check():
    """Check the health of the ingestion system"""
    try:
        coordinator = get_ingestion_coordinator()
        
        health = await coordinator.health_check()
        
        return health
        
    except Exception as e:
        logger.error(f"Error checking health: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Background task functions
async def process_single_file_background(
    coordinator: IngestionCoordinator,
    file_path: str,
    job_id: str,
    collection_name: Optional[str],
    user_id: Optional[str],
    tags: List[str],
    metadata: Dict[str, Any]
):
    """Background task to process a single file"""
    try:
        await coordinator.process_single_file(
            file_path=file_path,
            job_id=job_id,
            collection_name=collection_name,
            user_id=user_id,
            tags=tags,
            metadata=metadata
        )
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
    finally:
        # Clean up temporary file
        try:
            os.remove(file_path)
            os.rmdir(os.path.dirname(file_path))
        except:
            pass

async def process_batch_files_background(
    coordinator: IngestionCoordinator,
    file_paths: List[str],
    job_id: str,
    collection_name: Optional[str],
    user_id: Optional[str],
    tags: List[str],
    metadata: Dict[str, Any]
):
    """Background task to process multiple files"""
    try:
        await coordinator.process_batch_files(
            file_paths=file_paths,
            job_id=job_id,
            collection_name=collection_name,
            user_id=user_id,
            tags=tags,
            metadata=metadata
        )
    except Exception as e:
        logger.error(f"Error processing batch: {str(e)}")
    finally:
        # Clean up temporary files
        for file_path in file_paths:
            try:
                os.remove(file_path)
            except:
                pass
        try:
            os.rmdir(os.path.dirname(file_paths[0]))
        except:
            pass

async def sync_cloud_drives_background(
    coordinator: IngestionCoordinator,
    job_id: str,
    config: Dict[str, Any],
    user_id: Optional[str]
):
    """Background task to sync cloud drives"""
    try:
        await coordinator.sync_cloud_drives(
            job_id=job_id,
            config=config,
            user_id=user_id
        )
    except Exception as e:
        logger.error(f"Error syncing cloud drives: {str(e)}")
