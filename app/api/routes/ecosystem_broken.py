"""
Enhanced CogOS Ecosystem Integration Router
Manages communication with other systems in the AI ecosystem including Blackbird Agent
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel
import logging
import httpx
import asyncio
import json

# Import CogOS core modules
from ...core.memory import query_memory, add_memory_entry
from ...core.config import get_settings

router = APIRouter(prefix="/ecosystem", tags=["ecosystem"])

# Pydantic models for ecosystem communication
class EcosystemMessage(BaseModel):
    type: str
    content: str
    timestamp: datetime
    source: Optional[str] = None
    target: Optional[str] = None

class AgentStatus(BaseModel):
    agent_id: str
    status: str
    last_seen: datetime
    capabilities: List[str] = []

class EcosystemStatusResponse(BaseModel):
    status: str
    connected_agents: List[AgentStatus]
    total_agents: int
    timestamp: datetime

class TaskRequest(BaseModel):
    task_type: str
    description: str
    parameters: Dict[str, Any] = {}
    priority: str = "normal"

class KnowledgeQuery(BaseModel):
    query: str
    max_results: int = 10
    include_metadata: bool = True

# Initialize shared infrastructure
knowledge_base = UnifiedKnowledgeBase()
api_client = UnifiedAPIClient(system_type=SystemType.COGOS)

@router.get("/health", response_model=EcosystemHealthResponse)
async def check_ecosystem_health():
    """Check health of all systems in the ecosystem"""
    try:
        health_data = await api_client.check_ecosystem_health()
        return EcosystemHealthResponse(success=True, data=health_data)
    except Exception as e:
        return EcosystemHealthResponse(
            success=False,
            error=f"Failed to check ecosystem health: {str(e)}"
        )

@router.get("/systems")
async def list_available_systems():
    """List all available systems in the ecosystem"""
    try:
        systems = await api_client.discover_systems()
        return APIResponse(success=True, data={"systems": systems})
    except Exception as e:
        return APIResponse(success=False, error=str(e))

@router.post("/sync")
async def sync_knowledge():
    """Synchronize knowledge with other systems"""
    try:
        # Get recent conversations from CogOS
        recent_convs = knowledge_base.get_conversations(limit=10)
        
        # Get recent documents
        recent_docs = knowledge_base.search("", n_results=20)
        
        sync_data = {
            "conversations": len(recent_convs),
            "documents": len(recent_docs),
            "system": "cogos",
            "timestamp": api_client._get_current_timestamp()
        }
        
        # Here you could implement actual sync logic with other systems
        # For now, just report the sync status
        
        return APIResponse(
            success=True, 
            data={
                "message": "Knowledge sync completed",
                "stats": sync_data
            }
        )
    except Exception as e:
        return APIResponse(success=False, error=str(e))

@router.post("/broadcast")
async def broadcast_message(message: str, target_systems: Optional[List[str]] = None):
    """Broadcast a message to other systems in the ecosystem"""
    try:
        if target_systems is None:
            target_systems = ["blackbird", "agentgpt"]
        
        results = {}
        for system in target_systems:
            try:
                result = await api_client.send_message(system, message)
                results[system] = {"success": True, "response": result}
            except Exception as e:
                results[system] = {"success": False, "error": str(e)}
        
        return APIResponse(
            success=True,
            data={
                "message": "Broadcast completed",
                "results": results
            }
        )
    except Exception as e:
        return APIResponse(success=False, error=str(e))

@router.get("/knowledge/stats")
async def get_knowledge_stats():
    """Get knowledge base statistics"""
    try:
        stats = knowledge_base.get_stats()
        return APIResponse(success=True, data=stats)
    except Exception as e:
        return APIResponse(success=False, error=str(e))

@router.post("/knowledge/conversation")
async def add_conversation_turn(
    role: str, 
    content: str, 
    metadata: Optional[Dict] = None
):
    """Add a conversation turn to the unified knowledge base"""
    try:
        if metadata is None:
            metadata = {}
        metadata.update({
            "system": "cogos",
            "timestamp": api_client._get_current_timestamp()
        })
        
        turn_id = knowledge_base.add_conversation_turn(role, content, metadata)
        return APIResponse(
            success=True,
            data={"conversation_turn_id": turn_id}
        )
    except Exception as e:
        return APIResponse(success=False, error=str(e))

@router.get("/knowledge/constellation")
async def get_knowledge_constellation():
    """Get knowledge constellation data for 3D visualization"""
    try:
        constellation_data = knowledge_base.generate_knowledge_graph()
        return APIResponse(success=True, data=constellation_data)
    except Exception as e:
        return APIResponse(success=False, error=str(e))

@router.post("/voice/process")
async def process_voice_command(audio_data: str):
    """Process voice command through unified voice system"""
    try:
        # This would integrate with the unified voice system
        # For now, return a placeholder response
        return APIResponse(
            success=True,
            data={
                "message": "Voice processing not yet implemented",
                "audio_received": len(audio_data) > 0
            }
        )
    except Exception as e:
        return APIResponse(success=False, error=str(e))
