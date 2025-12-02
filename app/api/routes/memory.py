from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from ..schemas.base import QueryRequest, MemoryEntry, ApiResponse
from ...core.memory import query_memory, add_memory_entry, get_recent_entries
from ...core.reflector import reflect_on_last_entries, summarize_by_tag

router = APIRouter(prefix="/memory", tags=["Memory"])


@router.post("/query", response_model=ApiResponse)
async def query(req: QueryRequest):
    """Interroge la mémoire avec une question"""
    response = query_memory(req.question)
    return ApiResponse(data={"response": response})


@router.get("/recent", response_model=ApiResponse)
async def get_recent(limit: int = 10):
    """Récupère les entrées récentes de la mémoire"""
    try:
        entries = get_recent_entries(limit)
        return ApiResponse(data={"entries": entries})
    except Exception as e:
        return ApiResponse(status="error", message=str(e))


@router.post("/add", response_model=ApiResponse)
async def add_entry(entry: MemoryEntry):
    """Ajoute une nouvelle entrée dans la mémoire"""
    try:
        success = add_memory_entry(
            entry.content, 
            entry.tags, 
            entry.source
        )
        if success:
            return ApiResponse(message="Entrée ajoutée avec succès")
        else:
            return ApiResponse(status="error", message="Échec de l'ajout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reflect", response_model=ApiResponse)
async def reflect():
    """Génère une réflexion sur les dernières entrées"""
    try:
        reflection = reflect_on_last_entries()
        return ApiResponse(data={"reflection": reflection})
    except Exception as e:
        return ApiResponse(status="error", message=str(e))


@router.get("/summarize", response_model=ApiResponse)
async def summarize(tag: str = Query(..., description="Tag à résumer")):
    """Génère un résumé des entrées avec un tag spécifique"""
    try:
        summary = summarize_by_tag(tag)
        return ApiResponse(data={"summary": summary})
    except Exception as e:
        return ApiResponse(status="error", message=str(e)) 