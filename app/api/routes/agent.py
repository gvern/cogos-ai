from fastapi import APIRouter, HTTPException, Path, Body
from typing import List, Optional

from ..schemas.base import AgentAction, ApiResponse
from ...core.agent import (
    get_actions_for_display, 
    generate_action_suggestions, 
    mark_action_completed, 
    delete_action,
    save_agent_actions
)

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.get("/actions", response_model=ApiResponse)
async def get_actions(include_completed: bool = False):
    """Récupère la liste des actions de l'agent"""
    try:
        actions = get_actions_for_display(include_completed)
        return ApiResponse(data={"actions": [AgentAction(**action.__dict__) for action in actions]})
    except Exception as e:
        return ApiResponse(status="error", message=str(e))


@router.post("/generate", response_model=ApiResponse)
async def generate_actions(count: int = Body(3)):
    """Génère de nouvelles suggestions d'actions"""
    try:
        new_actions = generate_action_suggestions(count)
        
        # Conversion pour la réponse API
        actions_data = [AgentAction(**action.__dict__) for action in new_actions]
        
        return ApiResponse(
            data={"actions": actions_data}, 
            message=f"{len(new_actions)} actions générées avec succès"
        )
    except Exception as e:
        return ApiResponse(status="error", message=str(e))


@router.post("/actions", response_model=ApiResponse)
async def create_action(action: AgentAction):
    """Crée une nouvelle action personnalisée"""
    try:
        # Récupérer les actions existantes
        actions = get_actions_for_display(include_completed=True)
        
        # Créer un objet d'action du backend depuis celui de l'API
        from ...core.agent import AgentAction as CoreAgentAction
        new_action = CoreAgentAction(
            title=action.title,
            description=action.description,
            action_type=action.action_type,
            priority=action.priority,
            deadline=action.deadline,
            completed=action.completed,
            id=action.id
        )
        
        # Ajouter et sauvegarder
        actions.append(new_action)
        save_agent_actions(actions)
        
        return ApiResponse(message="Action créée avec succès")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/actions/{action_id}/complete", response_model=ApiResponse)
async def complete_action(action_id: str = Path(...)):
    """Marque une action comme terminée"""
    try:
        # Trouver l'index de l'action par son ID
        actions = get_actions_for_display(include_completed=True)
        action_index = -1
        
        for i, action in enumerate(actions):
            if getattr(action, 'id', '') == action_id:
                action_index = i
                break
                
        if action_index >= 0:
            mark_action_completed(action_index)
            return ApiResponse(message="Action marquée comme terminée")
        else:
            return ApiResponse(status="error", message="Action non trouvée")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/actions/{action_id}", response_model=ApiResponse)
async def remove_action(action_id: str = Path(...)):
    """Supprime une action"""
    try:
        # Trouver l'index de l'action par son ID
        actions = get_actions_for_display(include_completed=True)
        action_index = -1
        
        for i, action in enumerate(actions):
            if getattr(action, 'id', '') == action_id:
                action_index = i
                break
                
        if action_index >= 0:
            delete_action(action_index)
            return ApiResponse(message="Action supprimée avec succès")
        else:
            return ApiResponse(status="error", message="Action non trouvée")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 