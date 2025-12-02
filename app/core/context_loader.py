from pathlib import Path
import json
from typing import Dict, Any

CONTEXT_PATH = Path("memory/context_mcp.json")

def load_context() -> str:
    """Load and format the MCP context for LLM prompts."""
    if not CONTEXT_PATH.exists():
        return ""
    
    with open(CONTEXT_PATH, "r", encoding="utf-8") as f:
        ctx = json.load(f)

    # Convert MCP to text block for prompt
    context_str = f"""# User Context:
- Name: {ctx.get('name')}
- Role: {ctx['persona']['role']}
- Tone: {ctx['persona']['tone']}
- Goals: {', '.join(ctx.get('goals', []))}
- Current Focus: {', '.join(ctx['memory'].get('short_term', []))}"""
    return context_str

def get_raw_context() -> Dict[str, Any]:
    """Load the raw MCP context as a dictionary."""
    if not CONTEXT_PATH.exists():
        return {}
    
    with open(CONTEXT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def update_context(new_context: Dict[str, Any]) -> None:
    """Update the MCP context with new values."""
    current_context = get_raw_context()
    current_context.update(new_context)
    
    with open(CONTEXT_PATH, "w", encoding="utf-8") as f:
        json.dump(current_context, f, indent=2, ensure_ascii=False) 