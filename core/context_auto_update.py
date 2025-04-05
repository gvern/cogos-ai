import json
from pathlib import Path
from datetime import datetime
from core.context_loader import get_raw_context, update_context
from config.secrets import get_api_key
from openai import OpenAI
from core.reflector import reflect_on_last_entries

MEMORY_PATH = Path("ingested/memory.jsonl")
client = OpenAI(api_key=get_api_key())

def update_context_intelligently():
    ctx = get_raw_context()

    # Auto-reflexion persistée
    reflection = reflect_on_last_entries()
    ctx["memory"]["last_reflection"] = reflection

    # Exemple de progression par domaine (à automatiser plus tard)
    ctx["progress"] = {
        "Data Science": 85,
        "Philosophie": 60,
        "LLM": 95,
        "Musique": 40,
        "Vie perso": 70
    }

    update_context(ctx)
    print("✅ Contexte enrichi avec réflexion et progression.")

def summarize_recent_entries(n=5) -> str:
    if not MEMORY_PATH.exists():
        return "No memory available"
    entries = [json.loads(line) for line in MEMORY_PATH.open()]
    latest = sorted(entries, key=lambda x: x["metadata"]["created_at"], reverse=True)[:n]
    content = "\n\n".join([e["text"] for e in latest])

    prompt = f"""
Tu es une IA personnelle qui synthétise les dernières pensées de l'utilisateur.
Voici ses dernières notes :

{content}

Résume les sujets récents, identifie les préoccupations ou centres d'intérêt dominants, et génère un focus cognitif à jour.
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def auto_update_context():
    context = get_raw_context()
    summary = summarize_recent_entries()
    today = datetime.now().strftime("%Y-%m-%d")

    # Mise à jour du focus et historique
    context["memory"]["short_term"] = [f"Résumé du {today} : {summary}"]
    update_context(context)
    print("✅ Contexte MCP mis à jour automatiquement.")

if __name__ == "__main__":
    auto_update_context()
