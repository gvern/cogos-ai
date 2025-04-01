from typing import Dict, Any, List
from .context_loader import get_raw_context, update_context

def update_short_term_memory(new_items: List[str]) -> None:
    """Update the short-term memory with new items."""
    current_context = get_raw_context()
    current_context['memory']['short_term'] = new_items
    update_context(current_context)

def add_to_long_term_memory(category: str, items: List[str]) -> None:
    """Add items to a specific long-term memory category."""
    current_context = get_raw_context()
    if category not in current_context['memory']['long_term']:
        current_context['memory']['long_term'][category] = []
    current_context['memory']['long_term'][category].extend(items)
    update_context(current_context)

def update_goals(new_goals: List[str]) -> None:
    """Update the user's goals."""
    current_context = get_raw_context()
    current_context['goals'] = new_goals
    update_context(current_context)

def update_persona(role: str = None, tone: str = None) -> None:
    """Update the persona settings."""
    current_context = get_raw_context()
    if role:
        current_context['persona']['role'] = role
    if tone:
        current_context['persona']['tone'] = tone
    update_context(current_context)

def get_memory_summary() -> Dict[str, Any]:
    """Get a summary of the current memory state."""
    current_context = get_raw_context()
    return {
        'short_term': current_context['memory']['short_term'],
        'long_term': current_context['memory']['long_term']
    } 