from fastapi import APIRouter, HTTPException, Body
from typing import Dict, List, Any

from ..schemas.base import ContextData, ApiResponse
from ...core.context_loader import get_raw_context, update_context
from ...core.context_builder import get_domain_scores

router = APIRouter(prefix="/context", tags=["Context"])


@router.get("", response_model=ApiResponse)
async def get_context():
    """Récupère le contexte complet"""
    try:
        context = get_raw_context()
        return ApiResponse(data=context)
    except Exception as e:
        return ApiResponse(status="error", message=str(e))


@router.get("/domains", response_model=ApiResponse)
async def get_domains():
    """Récupère les scores de domaines"""
    try:
        domains = get_domain_scores()
        return ApiResponse(data={"domains": domains})
    except Exception as e:
        return ApiResponse(status="error", message=str(e))


@router.put("/update", response_model=ApiResponse)
async def update_context_handler(data: ContextData):
    """Met à jour le contexte"""
    try:
        context_dict = data.dict()
        success = update_context(context_dict)
        if success:
            return ApiResponse(message="Contexte mis à jour avec succès")
        else:
            return ApiResponse(status="error", message="Échec de la mise à jour du contexte")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/goals", response_model=ApiResponse)
async def update_goals(goals: List[str] = Body(...)):
    """Met à jour uniquement les objectifs du contexte"""
    try:
        context = get_raw_context()
        context["goals"] = goals
        success = update_context(context)
        if success:
            return ApiResponse(message="Objectifs mis à jour avec succès")
        else:
            return ApiResponse(status="error", message="Échec de la mise à jour des objectifs")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/focus", response_model=ApiResponse)
async def update_focus(focus: List[str] = Body(...)):
    """Met à jour uniquement les items de focus du contexte"""
    try:
        context = get_raw_context()
        context["focus"] = focus
        success = update_context(context)
        if success:
            return ApiResponse(message="Focus mis à jour avec succès")
        else:
            return ApiResponse(status="error", message="Échec de la mise à jour du focus")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 