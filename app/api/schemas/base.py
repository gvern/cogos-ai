from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class QueryRequest(BaseModel):
    """Requête pour interroger la mémoire"""
    question: str


class AgentAction(BaseModel):
    """Modèle d'une action suggérée par l'agent"""
    id: str = Field(default_factory=lambda: f"{datetime.now().timestamp():.0f}")
    title: str
    description: str
    action_type: str
    priority: int = 1
    deadline: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    completed: bool = False


class ContextData(BaseModel):
    """Modèle de données pour le contexte"""
    name: str
    role: str
    tone: str
    goals: List[str]
    focus: List[str]
    domains: Dict[str, float] = Field(default_factory=dict)


class AudioTranscriptResponse(BaseModel):
    """Réponse de transcription audio"""
    text: str
    success: bool
    audio_file: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class MemoryEntry(BaseModel):
    """Entrée dans la mémoire"""
    content: str
    timestamp: str
    tags: List[str] = []
    source: Optional[str] = None
    embedding_id: Optional[str] = None


class ApiResponse(BaseModel):
    """Réponse API générique"""
    status: str = "success"
    data: Any = None
    message: Optional[str] = None 