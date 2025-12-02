"""
CogOS Ecosystem Integration Router
Manages communication with other systems in the AI ecosystem including Blackbird Agent
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel
import logging
import httpx
import asyncio
import json

# Import CogOS core modules
from ...core.memory import query_memory, add_memory_entry

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

class BroadcastMessage(BaseModel):
    message: str
    type: str = "broadcast"
    metadata: Dict[str, Any] = {}

class SendMessageRequest(BaseModel):
    target_agent: str
    message: str
    type: str = "direct"
    metadata: Dict[str, Any] = {}

# In-memory storage for connected agents (in production, use Redis or database)
connected_agents: Dict[str, AgentStatus] = {}
message_queue: List[EcosystemMessage] = []

@router.get("/status", response_model=EcosystemStatusResponse)
async def get_ecosystem_status():
    """Get current ecosystem status"""
    try:
        current_time = datetime.now()
        agents_list = list(connected_agents.values())
        
        return EcosystemStatusResponse(
            status="active",
            connected_agents=agents_list,
            total_agents=len(agents_list),
            timestamp=current_time
        )
    except Exception as e:
        logging.error(f"Error getting ecosystem status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents")
async def list_connected_agents():
    """List all connected agents in the ecosystem"""
    try:
        return {
            "success": True,
            "agents": list(connected_agents.values()),
            "count": len(connected_agents)
        }
    except Exception as e:
        logging.error(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register")
async def register_agent(agent_status: AgentStatus):
    """Register a new agent in the ecosystem"""
    try:
        agent_status.last_seen = datetime.now()
        connected_agents[agent_status.agent_id] = agent_status
        
        logging.info(f"Agent {agent_status.agent_id} registered successfully")
        return {
            "success": True,
            "message": f"Agent {agent_status.agent_id} registered",
            "agent": agent_status
        }
    except Exception as e:
        logging.error(f"Error registering agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/broadcast")
async def broadcast_message(broadcast_req: BroadcastMessage, background_tasks: BackgroundTasks):
    """Broadcast a message to all connected agents"""
    try:
        message = EcosystemMessage(
            type=broadcast_req.type,
            content=broadcast_req.message,
            timestamp=datetime.now(),
            source="cogos"
        )
        
        # Add to message queue
        message_queue.append(message)
        
        # In a real implementation, you would send this to all connected agents
        # For now, we'll just log it
        logging.info(f"Broadcasting message: {broadcast_req.message}")
        
        # Add to background task for processing
        background_tasks.add_task(process_broadcast_message, message)
        
        return {
            "success": True,
            "message": "Broadcast queued successfully",
            "message_id": len(message_queue),
            "recipients": len(connected_agents)
        }
    except Exception as e:
        logging.error(f"Error broadcasting message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send")
async def send_message(send_req: SendMessageRequest):
    """Send a message to a specific agent"""
    try:
        if send_req.target_agent not in connected_agents:
            raise HTTPException(status_code=404, detail=f"Agent {send_req.target_agent} not found")
        
        message = EcosystemMessage(
            type=send_req.type,
            content=send_req.message,
            timestamp=datetime.now(),
            source="cogos",
            target=send_req.target_agent
        )
        
        message_queue.append(message)
        
        logging.info(f"Message sent to {send_req.target_agent}: {send_req.message}")
        
        return {
            "success": True,
            "message": f"Message sent to {send_req.target_agent}",
            "message_id": len(message_queue)
        }
    except Exception as e:
        logging.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/task/request")
async def request_task(task_req: TaskRequest):
    """Request a task to be performed by another agent"""
    try:
        # Create a task message
        task_message = EcosystemMessage(
            type="task_request",
            content=json.dumps({
                "task_type": task_req.task_type,
                "description": task_req.description,
                "parameters": task_req.parameters,
                "priority": task_req.priority
            }),
            timestamp=datetime.now(),
            source="cogos"
        )
        
        message_queue.append(task_message)
        
        logging.info(f"Task request created: {task_req.task_type}")
        
        return {
            "success": True,
            "message": "Task request created",
            "task_id": len(message_queue),
            "task": task_req
        }
    except Exception as e:
        logging.error(f"Error creating task request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge/query")
async def query_ecosystem_knowledge(query_req: KnowledgeQuery):
    """Query knowledge from the ecosystem"""
    try:
        # Use CogOS memory system to query knowledge
        results = await query_memory(
            query_req.query,
            limit=query_req.max_results
        )
        
        response_data = {
            "query": query_req.query,
            "results": results,
            "total_results": len(results),
            "timestamp": datetime.now()
        }
        
        if query_req.include_metadata:
            response_data["metadata"] = {
                "source": "cogos_memory",
                "query_time": datetime.now(),
                "ecosystem_agents": len(connected_agents)
            }
        
        return {
            "success": True,
            "data": response_data
        }
    except Exception as e:
        logging.error(f"Error querying knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/messages")
async def get_messages(limit: int = 10, message_type: Optional[str] = None):
    """Get recent messages from the ecosystem"""
    try:
        messages = message_queue
        
        if message_type:
            messages = [msg for msg in messages if msg.type == message_type]
        
        # Get most recent messages
        recent_messages = messages[-limit:] if len(messages) > limit else messages
        
        return {
            "success": True,
            "messages": recent_messages,
            "total_messages": len(message_queue),
            "filtered_count": len(recent_messages)
        }
    except Exception as e:
        logging.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/agent/{agent_id}")
async def unregister_agent(agent_id: str):
    """Unregister an agent from the ecosystem"""
    try:
        if agent_id not in connected_agents:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        del connected_agents[agent_id]
        
        logging.info(f"Agent {agent_id} unregistered")
        
        return {
            "success": True,
            "message": f"Agent {agent_id} unregistered",
            "remaining_agents": len(connected_agents)
        }
    except Exception as e:
        logging.error(f"Error unregistering agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task functions
async def process_broadcast_message(message: EcosystemMessage):
    """Process broadcast message in background"""
    try:
        # In a real implementation, this would send the message to all connected agents
        # For now, we'll just add it to memory
        await add_memory_entry({
            "content": f"Ecosystem broadcast: {message.content}",
            "type": "ecosystem_communication",
            "timestamp": message.timestamp.isoformat(),
            "source": message.source
        })
        
        logging.info(f"Processed broadcast message: {message.content}")
    except Exception as e:
        logging.error(f"Error processing broadcast message: {e}")

async def heartbeat_check():
    """Check heartbeat of all connected agents"""
    try:
        current_time = datetime.now()
        inactive_agents = []
        
        for agent_id, agent in connected_agents.items():
            # If agent hasn't been seen for more than 5 minutes, mark as inactive
            if (current_time - agent.last_seen).total_seconds() > 300:
                inactive_agents.append(agent_id)
        
        # Remove inactive agents
        for agent_id in inactive_agents:
            del connected_agents[agent_id]
            logging.warning(f"Removed inactive agent: {agent_id}")
            
    except Exception as e:
        logging.error(f"Error in heartbeat check: {e}")
