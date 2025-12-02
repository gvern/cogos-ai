from .reflector import reflect_on_last_entries
from .context_loader import get_raw_context

def generate_briefing():
    ctx = get_raw_context()
    short_focus = ", ".join(ctx.get("memory", {}).get("short_term", []))
    goals = ", ".join(ctx.get("goals", []))
    reflection = reflect_on_last_entries()

    return f"""
🎯 Objectifs : {goals}
🧠 Focus du moment : {short_focus}

📚 Derniers apprentissages :
{reflection}
""" 