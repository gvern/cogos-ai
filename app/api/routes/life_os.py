from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import os
from pathlib import Path
from datetime import datetime

router = APIRouter(
    prefix="/api/v1/life-os",
    tags=["life-os"],
    responses={404: {"description": "Not found"}},
)

# Data file path
DATA_FILE = Path(__file__).parent.parent.parent / "data" / "life_os_goals.json"

# Models
class Category(BaseModel):
    id: str
    name: str
    icon: str
    color: str

class Goal(BaseModel):
    id: str
    categoryId: str
    title: str
    status: str = "todo"  # todo, in_progress, completed
    progress: int = 0
    notes: Optional[str] = None
    deadline: Optional[str] = None

class LifeOSData(BaseModel):
    categories: List[Category]
    goals: List[Goal]

# Helper functions
def load_data() -> LifeOSData:
    if not DATA_FILE.exists():
        return LifeOSData(categories=[], goals=[])
    
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return LifeOSData(**data)
    except Exception as e:
        print(f"Error loading data: {e}")
        return LifeOSData(categories=[], goals=[])

def save_data(data: LifeOSData):
    try:
        # Ensure directory exists
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data.dict(), f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save data: {str(e)}")

# Endpoints
@router.get("/goals", response_model=LifeOSData)
async def get_goals():
    """Get all goals and categories"""
    return load_data()

@router.post("/goals/update", response_model=Goal)
async def update_goal(goal_update: Goal):
    """Update a specific goal"""
    data = load_data()
    
    # Find and update
    found = False
    for i, goal in enumerate(data.goals):
        if goal.id == goal_update.id:
            data.goals[i] = goal_update
            found = True
            break
    
    if not found:
        # If not found, add it (could be a new goal)
        data.goals.append(goal_update)
    
    save_data(data)
    return goal_update

@router.post("/goals/delete/{goal_id}")
async def delete_goal(goal_id: str):
    """Delete a goal"""
    data = load_data()
    
    initial_len = len(data.goals)
    data.goals = [g for g in data.goals if g.id != goal_id]
    
    if len(data.goals) == initial_len:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    save_data(data)
    return {"status": "success", "message": "Goal deleted"}

@router.get("/stats")
async def get_stats():
    """Get statistics about goals"""
    data = load_data()
    
    total_goals = len(data.goals)
    completed = len([g for g in data.goals if g.status == "completed"])
    in_progress = len([g for g in data.goals if g.status == "in_progress"])
    todo = len([g for g in data.goals if g.status == "todo"])
    
    return {
        "total": total_goals,
        "completed": completed,
        "in_progress": in_progress,
        "todo": todo,
        "completion_rate": round((completed / total_goals) * 100) if total_goals > 0 else 0
    }
