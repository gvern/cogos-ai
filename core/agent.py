"""
CogOS Agent - Module intelligent qui propose des actions, défis et apprentissages
basés sur l'état actuel du contexte et de la mémoire.
"""
import json
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

from core.context_loader import get_raw_context
from core.memory import query_memory

# Type d'actions que l'agent peut proposer
ACTION_TYPES = [
    "apprentissage", 
    "défi", 
    "rappel", 
    "exploration", 
    "consolidation",
    "création"
]

class AgentAction:
    """Représente une action suggérée par l'agent."""
    def __init__(self, 
                 title: str, 
                 description: str, 
                 action_type: str, 
                 priority: int = 1,
                 deadline: str = None,
                 completed: bool = False,
                 id: str = None):
        self.title = title
        self.description = description
        self.action_type = action_type
        self.priority = priority  # 1-5 (5 étant le plus important)
        self.deadline = deadline  # Format ISO: YYYY-MM-DD
        self.created_at = datetime.now().isoformat()
        self.completed = completed
        self.id = id or f"{datetime.now().timestamp():.0f}_{random.randint(1000, 9999)}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'action en dictionnaire pour la sérialisation."""
        return {
            "title": self.title,
            "description": self.description,
            "action_type": self.action_type,
            "priority": self.priority,
            "deadline": self.deadline,
            "created_at": self.created_at,
            "completed": self.completed,
            "id": self.id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentAction':
        """Crée une action à partir d'un dictionnaire."""
        return cls(
            title=data["title"],
            description=data["description"],
            action_type=data["action_type"],
            priority=data.get("priority", 1),
            deadline=data.get("deadline"),
            completed=data.get("completed", False),
            id=data.get("id")
        )


def load_agent_actions() -> List[AgentAction]:
    """Charge les actions enregistrées."""
    actions_file = Path("data/agent_actions.json")
    
    if not actions_file.exists():
        return []
    
    try:
        with open(actions_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return [AgentAction.from_dict(action_data) for action_data in data]
    except Exception as e:
        print(f"Erreur lors du chargement des actions de l'agent: {e}")
        return []


def save_agent_actions(actions: List[AgentAction]) -> bool:
    """Enregistre les actions de l'agent."""
    actions_file = Path("data/agent_actions.json")
    actions_file.parent.mkdir(exist_ok=True)
    
    try:
        with open(actions_file, "w", encoding="utf-8") as f:
            json.dump([action.to_dict() for action in actions], f, indent=2)
        return True
    except Exception as e:
        print(f"Erreur lors de l'enregistrement des actions de l'agent: {e}")
        return False


def mark_action_completed(action_index: int) -> bool:
    """Marque une action comme terminée."""
    actions = load_agent_actions()
    
    if 0 <= action_index < len(actions):
        actions[action_index].completed = True
        return save_agent_actions(actions)
    
    return False


def delete_action(action_index: int) -> bool:
    """Supprime une action."""
    actions = load_agent_actions()
    
    if 0 <= action_index < len(actions):
        actions.pop(action_index)
        return save_agent_actions(actions)
    
    return False


def generate_action_suggestions(count: int = 3) -> List[AgentAction]:
    """Génère des suggestions d'actions basées sur le contexte et la mémoire."""
    ctx = get_raw_context()
    actions = []
    
    # Vérifier les objectifs
    goals = ctx.get("goals", [])
    
    # Vérifier les focus actuels
    focus_items = ctx.get("memory", {}).get("short_term", [])
    
    # Génération d'actions basées sur les objectifs
    for goal in goals[:2]:  # Prendre jusqu'à 2 objectifs
        action_type = random.choice(ACTION_TYPES)
        
        # Générer une suggestion liée à l'objectif
        if action_type == "apprentissage":
            query = f"Que devrais-je apprendre pour progresser sur mon objectif: {goal}"
            response = query_memory(query)
            
            actions.append(AgentAction(
                title=f"Apprendre sur: {goal}",
                description=response[:200] + "...",
                action_type="apprentissage",
                priority=random.randint(2, 4)
            ))
        
        elif action_type == "défi":
            # Générer un défi associé à l'objectif
            actions.append(AgentAction(
                title=f"Défi: {goal}",
                description=f"Réalise un petit projet qui te permet d'avancer sur: {goal}",
                action_type="défi",
                priority=random.randint(2, 5),
                deadline=(datetime.now() + timedelta(days=7)).date().isoformat()
            ))
    
    # Génération basée sur le focus actuel
    for focus in focus_items[:2]:
        action_type = random.choice(["exploration", "consolidation", "création"])
        
        if action_type == "exploration":
            actions.append(AgentAction(
                title=f"Explorer: {focus}",
                description=f"Recherche de nouvelles informations sur {focus} pour élargir ta compréhension.",
                action_type="exploration",
                priority=random.randint(1, 3)
            ))
        
        elif action_type == "consolidation":
            actions.append(AgentAction(
                title=f"Consolider: {focus}",
                description=f"Révise et synthétise tes connaissances actuelles sur {focus}.",
                action_type="consolidation",
                priority=2
            ))
        
        elif action_type == "création":
            actions.append(AgentAction(
                title=f"Créer avec: {focus}",
                description=f"Utilise tes connaissances sur {focus} pour créer quelque chose de nouveau.",
                action_type="création",
                priority=random.randint(2, 4),
                deadline=(datetime.now() + timedelta(days=5)).date().isoformat()
            ))
    
    # Compléter avec des suggestions générales si nécessaire
    while len(actions) < count:
        actions.append(AgentAction(
            title="Exploration libre",
            description="Découvre un nouveau domaine qui pourrait enrichir ta base de connaissances.",
            action_type="exploration",
            priority=1
        ))
    
    return actions[:count]  # Retourner le nombre demandé d'actions


def get_actions_for_display(include_completed: bool = False) -> List[AgentAction]:
    """Récupère les actions pour affichage dans l'UI."""
    # Charger les actions existantes
    actions = load_agent_actions()
    
    # Filtrer les actions complétées si demandé
    if not include_completed:
        actions = [action for action in actions if not action.completed]
    
    # Si moins de 3 actions actives, générer de nouvelles suggestions
    if len(actions) < 3:
        new_actions = generate_action_suggestions(3 - len(actions))
        actions.extend(new_actions)
        save_agent_actions(actions)
    
    return actions 