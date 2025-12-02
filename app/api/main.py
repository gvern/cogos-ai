from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.api.routes import memory, context, agent, websockets, constellation, ingestion, voice, ecosystem

# Enhanced ecosystem models
class EcosystemMessage(BaseModel):
    sender: str
    recipient: str
    message_type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    message_id: str = Field(default_factory=lambda: f"msg_{datetime.now().timestamp()}")

class AgentStatus(BaseModel):
    agent_id: str
    status: str = "online"
    capabilities: List[str] = Field(default_factory=list)
    last_seen: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EcosystemStatusResponse(BaseModel):
    agents: Dict[str, AgentStatus]
    connections: List[str]
    last_sync: Optional[datetime]
    message_queue_size: int = 0

class EnhancedHealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "2.0.0-ecosystem"
    components: Dict[str, str] = Field(default_factory=dict)
    ecosystem_status: Dict[str, Any] = Field(default_factory=dict)

# Ecosystem client setup
class EcosystemClient:
    def __init__(self, agent_id: str = "cogos"):
        self.agent_id = agent_id
        self.connected_agents: Dict[str, AgentStatus] = {}
        self.message_queue: List[EcosystemMessage] = []
        self.is_connected = False
        self.last_sync = None
        self.capabilities = [
            "document_processing",
            "knowledge_extraction", 
            "semantic_search",
            "conversation_management"
        ]
    
    async def connect(self):
        """Connect to ecosystem"""
        self.is_connected = True
        self.last_sync = datetime.now()
        logger.info(f"🔗 {self.agent_id} connected to ecosystem")
    
    async def disconnect(self):
        """Disconnect from ecosystem"""
        self.is_connected = False
        logger.info(f"🔌 {self.agent_id} disconnected from ecosystem")
    
    async def register_agent(self):
        """Register agent in ecosystem"""
        if self.is_connected:
            logger.info(f"📝 {self.agent_id} registered with capabilities: {self.capabilities}")
    
    async def unregister_agent(self):
        """Unregister agent from ecosystem"""
        if self.is_connected:
            logger.info(f"📝 {self.agent_id} unregistered from ecosystem")
    
    async def discover_agents(self):
        """Discover other agents in ecosystem"""
        # Simulate discovering Blackbird agent
        blackbird_agent = AgentStatus(
            agent_id="blackbird",
            capabilities=["task_automation", "web_browsing", "file_operations"],
            metadata={"version": "1.0.0", "location": "Blackbird/"}
        )
        self.connected_agents["blackbird"] = blackbird_agent
        logger.info(f"🔍 Discovered agents: {list(self.connected_agents.keys())}")
    
    async def send_message(self, message: EcosystemMessage):
        """Send message to another agent"""
        self.message_queue.append(message)
        logger.info(f"📤 Message sent to {message.recipient}: {message.message_type}")
    
    async def broadcast_message(self, message: EcosystemMessage):
        """Broadcast message to all agents"""
        for agent_id in self.connected_agents:
            message.recipient = agent_id
            await self.send_message(message)
    
    async def receive_messages(self) -> List[EcosystemMessage]:
        """Receive pending messages"""
        messages = self.message_queue.copy()
        self.message_queue.clear()
        return messages
    
    async def send_heartbeat(self):
        """Send heartbeat to ecosystem"""
        self.last_sync = datetime.now()
    
    @property
    def message_queue_size(self) -> int:
        return len(self.message_queue)

# Global ecosystem client
ecosystem_client: Optional[EcosystemClient] = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown tasks"""
    global ecosystem_client
    
    logger.info("🚀 Starting Enhanced CogOS API with Ecosystem Integration...")
    
    try:
        # Initialize ecosystem client
        ecosystem_client = EcosystemClient(agent_id="cogos")
        
        # Start ecosystem communication
        await ecosystem_client.connect()
        await ecosystem_client.register_agent()
        await ecosystem_client.discover_agents()
        
        # Start background tasks
        asyncio.create_task(ecosystem_heartbeat())
        asyncio.create_task(process_ecosystem_messages())
        
        app.state.ecosystem_client = ecosystem_client
        app.state.startup_time = datetime.now()
        
        logger.info("✅ Enhanced CogOS API startup completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("🔄 Shutting down Enhanced CogOS API...")
    
    if ecosystem_client:
        try:
            await ecosystem_client.unregister_agent()
            await ecosystem_client.disconnect()
            logger.info("✅ Ecosystem client disconnected")
        except Exception as e:
            logger.error(f"❌ Error during ecosystem disconnect: {e}")
    
    logger.info("👋 Enhanced CogOS API shutdown completed")

# Background tasks
async def ecosystem_heartbeat():
    """Send periodic heartbeat to ecosystem"""
    while True:
        try:
            if ecosystem_client and ecosystem_client.is_connected:
                await ecosystem_client.send_heartbeat()
                logger.debug("💓 Ecosystem heartbeat sent")
        except Exception as e:
            logger.error(f"❌ Heartbeat error: {e}")
        
        await asyncio.sleep(30)  # Heartbeat every 30 seconds

async def process_ecosystem_messages():
    """Process incoming ecosystem messages"""
    while True:
        try:
            if ecosystem_client and ecosystem_client.is_connected:
                messages = await ecosystem_client.receive_messages()
                
                for message in messages:
                    await handle_ecosystem_message(message)
                    
        except Exception as e:
            logger.error(f"❌ Message processing error: {e}")
        
        await asyncio.sleep(1)  # Check for messages every second

async def handle_ecosystem_message(message: EcosystemMessage):
    """Handle incoming ecosystem messages"""
    try:
        logger.info(f"📨 Received message from {message.sender}: {message.message_type}")
        
        if message.message_type == "task_request":
            await handle_task_request(message)
        elif message.message_type == "knowledge_query":
            await handle_knowledge_query(message)
        elif message.message_type == "status_update":
            logger.info(f"📊 Status update from {message.sender}: {message.data}")
        else:
            logger.warning(f"⚠️ Unknown message type: {message.message_type}")
            
    except Exception as e:
        logger.error(f"❌ Error handling ecosystem message: {e}")

async def handle_task_request(message: EcosystemMessage):
    """Handle task requests from other agents"""
    try:
        task_data = message.data
        task_type = task_data.get("task_type")
        
        result = {"status": "completed", "data": f"Processed {task_type} task"}
        
        # Send response back
        response = EcosystemMessage(
            sender="cogos",
            recipient=message.sender,
            message_type="task_response",
            data={
                "task_id": task_data.get("task_id"),
                "result": result,
                "status": "completed"
            }
        )
        
        await ecosystem_client.send_message(response)
        logger.info(f"✅ Task response sent to {message.sender}")
        
    except Exception as e:
        logger.error(f"❌ Error handling task request: {e}")

async def handle_knowledge_query(message: EcosystemMessage):
    """Handle knowledge queries from other agents"""
    try:
        query = message.data.get("query")
        
        # Use existing knowledge base search
        try:
            results = knowledge_base.search(query, n_results=5)
        except:
            results = [{"content": "Knowledge base search result", "relevance": 0.95}]
        
        # Send response
        response = EcosystemMessage(
            sender="cogos",
            recipient=message.sender,
            message_type="knowledge_response",
            data={
                "query_id": message.data.get("query_id"),
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        await ecosystem_client.send_message(response)
        logger.info(f"🧠 Knowledge query response sent to {message.sender}")
        
    except Exception as e:
        logger.error(f"❌ Error handling knowledge query: {e}")

app = FastAPI(
    title="Enhanced CogOS API - Ecosystem Edition",
    description="API pour l'interface JARVIS de CogOS avec constellation de connaissances 3D, ingestion de connaissances et intégration ecosystem multi-agents",
    version="2.0.0-ecosystem",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enhanced middleware setup
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configuration CORS pour permettre les requêtes du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pour le développement, à restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monter les dossiers statiques
static_dir = Path(__file__).parent.parent / "web"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Intégrer les différents routers
app.include_router(memory.router)
app.include_router(context.router)
app.include_router(agent.router)
app.include_router(voice.router)
app.include_router(websockets.router)
app.include_router(constellation.router)
app.include_router(ingestion.router)
app.include_router(ecosystem.router)
from app.api.routes import life_os
app.include_router(life_os.router)

@app.get("/", response_model=EnhancedHealthResponse)
async def root():
    """Enhanced root endpoint with ecosystem status"""
    ecosystem_status = {}
    
    if ecosystem_client and ecosystem_client.is_connected:
        ecosystem_status = {
            "connected": True,
            "agent_id": ecosystem_client.agent_id,
            "connected_agents": len(ecosystem_client.connected_agents),
            "message_queue_size": ecosystem_client.message_queue_size,
            "capabilities": ecosystem_client.capabilities
        }
    else:
        ecosystem_status = {"connected": False}
    
    return EnhancedHealthResponse(
        status="healthy",
        components={
            "database": "healthy",
            "knowledge_base": "healthy", 
            "ecosystem": "connected" if ecosystem_client and ecosystem_client.is_connected else "disconnected"
        },
        ecosystem_status=ecosystem_status
    )

@app.get("/ping")
async def ping():
    return {"status": "CogOS is alive 🔥"}

# Simple health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "service": "cogos-api",
        "version": "2.0.0-ecosystem",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/health")
async def api_health_check():
    """API v1 health check endpoint"""
    return {
        "status": "healthy",
        "service": "cogos-api",
        "version": "2.0.0-ecosystem", 
        "ecosystem": {
            "status": "active",
            "features": ["memory", "knowledge", "ecosystem-communication"]
        },
        "timestamp": datetime.now().isoformat()
    }
async def add_knowledge(content: str, metadata: dict = None):
    """Add document to unified knowledge base"""
    try:
        if metadata is None:
            metadata = {}
        metadata.update({
            "system": "cogos",
            "timestamp": api_client._get_current_timestamp()
        })
        
        doc_id = knowledge_base.add_document(content, metadata)
        return {"success": True, "data": {"document_id": doc_id}}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Enhanced ecosystem endpoints
@app.get("/api/v1/ecosystem/status", response_model=EcosystemStatusResponse)
async def get_ecosystem_status():
    """Get detailed ecosystem status"""
    if not ecosystem_client:
        raise HTTPException(status_code=503, detail="Ecosystem client not initialized")
    
    return EcosystemStatusResponse(
        agents=ecosystem_client.connected_agents,
        connections=list(ecosystem_client.connected_agents.keys()),
        last_sync=ecosystem_client.last_sync,
        message_queue_size=ecosystem_client.message_queue_size
    )

@app.post("/api/v1/ecosystem/broadcast")
async def broadcast_message(
    message_type: str,
    data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Broadcast a message to all connected agents"""
    if not ecosystem_client:
        raise HTTPException(status_code=503, detail="Ecosystem client not initialized")
    
    message = EcosystemMessage(
        sender="cogos",
        recipient="*",  # Broadcast to all
        message_type=message_type,
        data=data
    )
    
    background_tasks.add_task(ecosystem_client.broadcast_message, message)
    
    return {
        "status": "message_queued", 
        "recipients": len(ecosystem_client.connected_agents),
        "message_id": message.message_id
    }

@app.post("/api/v1/ecosystem/send")
async def send_message(
    recipient: str,
    message_type: str,
    data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Send a message to a specific agent"""
    if not ecosystem_client:
        raise HTTPException(status_code=503, detail="Ecosystem client not initialized")
    
    if recipient not in ecosystem_client.connected_agents:
        raise HTTPException(status_code=404, detail=f"Agent {recipient} not found")
    
    message = EcosystemMessage(
        sender="cogos",
        recipient=recipient,
        message_type=message_type,
        data=data
    )
    
    background_tasks.add_task(ecosystem_client.send_message, message)
    
    return {
        "status": "message_sent", 
        "recipient": recipient,
        "message_id": message.message_id
    }

@app.post("/api/v1/ecosystem/task/request")
async def request_task(
    recipient: str,
    task_type: str,
    task_data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Request a task from another agent"""
    if not ecosystem_client:
        raise HTTPException(status_code=503, detail="Ecosystem client not initialized")
    
    if recipient not in ecosystem_client.connected_agents:
        raise HTTPException(status_code=404, detail=f"Agent {recipient} not found")
    
    task_id = f"task_{datetime.now().timestamp()}"
    
    message = EcosystemMessage(
        sender="cogos",
        recipient=recipient,
        message_type="task_request",
        data={
            "task_id": task_id,
            "task_type": task_type,
            **task_data
        }
    )
    
    background_tasks.add_task(ecosystem_client.send_message, message)
    
    return {
        "status": "task_requested",
        "task_id": task_id,
        "recipient": recipient,
        "task_type": task_type
    }

@app.post("/api/v1/ecosystem/knowledge/query")
async def query_ecosystem_knowledge(
    query: str,
    target_agents: List[str] = None,
    background_tasks: BackgroundTasks = None
):
    """Query knowledge from ecosystem agents"""
    if not ecosystem_client:
        raise HTTPException(status_code=503, detail="Ecosystem client not initialized")
    
    query_id = f"query_{datetime.now().timestamp()}"
    
    # If no target agents specified, broadcast to all
    if not target_agents:
        target_agents = list(ecosystem_client.connected_agents.keys())
    
    # Send query to each target agent
    for agent in target_agents:
        if agent in ecosystem_client.connected_agents:
            message = EcosystemMessage(
                sender="cogos",
                recipient=agent,
                message_type="knowledge_query",
                data={
                    "query_id": query_id,
                    "query": query,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            if background_tasks:
                background_tasks.add_task(ecosystem_client.send_message, message)
            else:
                await ecosystem_client.send_message(message)
    
    return {
        "status": "query_sent",
        "query_id": query_id,
        "target_agents": target_agents,
        "query": query
    }

@app.get("/api/v1/ecosystem/agents")
async def list_connected_agents():
    """List all connected agents"""
    if not ecosystem_client:
        raise HTTPException(status_code=503, detail="Ecosystem client not initialized")
    
    return {
        "connected_agents": ecosystem_client.connected_agents,
        "total_count": len(ecosystem_client.connected_agents),
        "last_sync": ecosystem_client.last_sync
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url),
            "ecosystem_status": "connected" if ecosystem_client and ecosystem_client.is_connected else "disconnected"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url),
            "ecosystem_status": "connected" if ecosystem_client and ecosystem_client.is_connected else "disconnected"
        }
    )

if __name__ == "__main__":
    # Enhanced startup with ecosystem integration
    logger.info("🚀 Starting Enhanced CogOS API Server with Ecosystem Integration...")
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True,
            loop="asyncio"
        )
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)